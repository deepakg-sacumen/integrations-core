# (C) Datadog, Inc. 2022-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from __future__ import annotations

import os
import sys
from collections.abc import Callable
from functools import lru_cache
from importlib import import_module


@lru_cache(maxsize=None)
def get_platform_name():
    import platform

    return normalize_platform_name(platform.system())


def normalize_platform_name(platform_name):
    platform_name = platform_name.lower()
    return 'macos' if platform_name == 'darwin' else platform_name


class Platform:
    def __init__(self, display_func=print):
        self.__display_func = display_func

        # Lazily loaded constants
        self.__default_shell = None
        self.__format_file_uri = None
        self.__join_command_args = None
        self.__name = None

        # Whether or not an interactive status is being displayed
        self.displaying_status = False

        self.__modules = LazilyLoadedModules()

    @property
    def modules(self):
        """
        Accessor for lazily loading modules that either take multiple milliseconds to import
        (like `shutil` and `subprocess`) or are not used on all platforms (like `shlex`).
        """
        return self.__modules

    def format_for_subprocess(self, command: str | list[str], *, shell: bool):
        """
        Format the given command in a cross-platform manner for immediate consumption by subprocess utilities.
        """
        if self.windows:
            # Manually locate executables on Windows to avoid multiple cases in which `shell=True` is required:
            #
            # - If the `PATH` environment variable has been modified, see: https://bugs.python.org/issue8557
            # - Executables that do not have the extension `.exe`, see:
            #   https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw
            if not shell and not isinstance(command, str):
                executable = command[0]
                new_command = [self.modules.shutil.which(executable) or executable]
                new_command.extend(command[1:])
                return new_command
        else:
            if not shell and isinstance(command, str):
                return self.modules.shlex.split(command)

        return command

    def exit_with_code(self, code):
        return sys.exit(code)

    def _run_command_integrated(self, command: str | list[str], shell=False, **kwargs):
        with self.capture_process(command, shell=shell, **kwargs) as process:
            for line in self.stream_process_output(process):
                self.__display_func(line, end='')

            stdout, stderr = process.communicate()

        return self.modules.subprocess.CompletedProcess(process.args, process.poll(), stdout, stderr)

    def run_command(self, command: str | list[str], shell=False, **kwargs):
        """
        Equivalent to the standard library's `subprocess.run`, with the command first being properly formatted.
        """
        if self.displaying_status and not kwargs.get('capture_output'):
            return self._run_command_integrated(command, shell=shell, **kwargs)

        return self.modules.subprocess.run(self.format_for_subprocess(command, shell=shell), shell=shell, **kwargs)

    def check_command(
        self, command: str | list[str], shell=False, on_error: Callable[[int], None] | None = None, **kwargs
    ):
        """
        Equivalent to `run_command`, but non-zero exit codes will gracefully end program execution.

        If `on_error` is provided, it will be called with the exit code.
        """
        process = self.run_command(command, shell=shell, **kwargs)
        if process.returncode:
            if on_error is not None:
                on_error(process.returncode)
            self.exit_with_code(process.returncode)

        return process

    def check_command_output(
        self,
        command: str | list[str],
        shell=False,
        on_error: Callable[[int, str], None] | None = None,
        print_output: bool = False,
        **kwargs,
    ) -> str:
        """
        Equivalent to the output from the process returned by `capture_process`,
        but non-zero exit codes will gracefully end program execution.

        If `on_error` is provided, it will be called with the exit code and the stdout of the command.

        The `print_output` parameter is used to control whether the output of the command is printed to the console
        in real-time.

        The output will always be printed to the console if the command fails, even if `print_output` is False.
        """
        if print_output:
            kwargs["bufsize"] = 1
            kwargs["encoding"] = "utf-8"

        with self.capture_process(command, shell=shell, **kwargs) as process:
            if print_output:
                stdout = ""
                for line in iter(process.stdout.readline, ""):
                    stdout += line
                    self.__display_func(line, end='')
            else:
                stdout, _ = process.communicate()

        if process.returncode:
            if not print_output:
                # Print output if it has not been printed yet
                self.__display_func(stdout)

            if on_error is not None:
                on_error(process.returncode, stdout)
            self.exit_with_code(process.returncode)

        return stdout

    def capture_process(self, command: str | list[str], shell=False, **kwargs):
        """
        Equivalent to the standard library's `subprocess.Popen`, with all output
        captured by `stdout` and the command first being properly formatted.
        """
        return self.modules.subprocess.Popen(
            self.format_for_subprocess(command, shell=shell),
            shell=shell,
            stdout=self.modules.subprocess.PIPE,
            stderr=self.modules.subprocess.STDOUT,
            **kwargs,
        )

    @staticmethod
    def stream_process_output(process):
        # To avoid blocking never use a pipe's file descriptor iterator. See https://bugs.python.org/issue3907
        for line in iter(process.stdout.readline, b''):
            yield line.decode('utf-8')

    @property
    def format_file_uri(self):
        if self.__format_file_uri is None:
            if self.windows:
                self.__format_file_uri = lambda p: f'file:///{p}'.replace('\\', '/')
            else:
                self.__format_file_uri = lambda p: f'file://{p}'

        return self.__format_file_uri

    @property
    def windows(self):
        """
        Indicates whether ddev is running on Windows.
        """
        return self.name == 'windows'

    @property
    def macos(self):
        """
        Indicates whether ddev is running on macOS.
        """
        return self.name == 'macos'

    @property
    def linux(self):
        """
        Indicates whether ddev is running on neither Windows nor macOS.
        """
        return not (self.windows or self.macos)

    def exit_with_command(self, command: list[str]):
        """
        Run the given command and exit with its exit code. On non-Windows systems, this uses the standard library's
        `os.execvp`.
        """
        if self.windows:
            process = self.run_command(command)
            self.exit_with_code(process.returncode)
        else:
            return os.execvp(command[0], command)

    @property
    def name(self):
        """
        One of the following:

        - `linux`
        - `windows`
        - `macos`
        """
        if self.__name is None:
            self.__name = get_platform_name()

        return self.__name


class LazilyLoadedModules:
    def __getattr__(self, name):
        module = import_module(name)
        setattr(self, name, module)
        return module
