# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
"""
Utilities functions abstracting common operations, specially designed to be used
by Integrations within tests.
"""

import csv
import inspect
import json
import os
import platform
import socket
from contextlib import closing, contextmanager
from io import open
from urllib.request import urlopen

import yaml

from .ci import running_on_ci, running_on_gh_actions, running_on_windows_ci  # noqa: F401
from .fs import basepath, file_exists, get_parent_dir, path_join, read_file

__platform = platform.system()
ON_MACOS = os.name == 'mac' or __platform == 'Darwin'
ON_WINDOWS = NEED_SHELL = os.name == 'nt' or __platform == 'Windows'
ON_LINUX = not (ON_MACOS or ON_WINDOWS)
GH_ANNOTATION_LEVELS = ['warning', 'error']


def get_active_env():
    return os.environ['HATCH_ENV_ACTIVE']


def ensure_bytes(s):
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    return s


def ensure_unicode(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return s


def download_file(url, fname):
    req = urlopen(url)
    with open(fname, 'wb') as f:
        while True:
            chunk = req.read(16384)
            if not chunk:
                break
            f.write(chunk)
            f.flush()


def get_next(obj):
    return next(iter(obj))


def load_jmx_config():
    # Only called in tests of a check, so just go back one frame
    root = find_check_root(depth=1)

    check = basepath(root)
    example_config_path = path_join(root, 'datadog_checks', check, 'data', 'conf.yaml.example')
    metrics_config_path = path_join(root, 'datadog_checks', check, 'data', 'metrics.yaml')

    example_config = yaml.safe_load(read_file(example_config_path))
    metrics_config = yaml.safe_load(read_file(metrics_config_path))

    if example_config['init_config'] is None:
        example_config['init_config'] = {}

    # Avoid having to potentially mount multiple files by putting the default metrics
    # in the user-defined metric location.
    example_config['init_config']['conf'] = metrics_config['jmx_metrics']

    return example_config


def find_check_root(depth=0):
    # Account for this call
    depth += 1

    frame = inspect.currentframe()
    for _ in range(depth):
        frame = frame.f_back

    root = get_parent_dir(frame.f_code.co_filename)
    while True:
        if file_exists(path_join(root, 'pyproject.toml')) or file_exists(path_join(root, 'setup.py')):
            break

        new_root = os.path.dirname(root)
        if new_root == root:
            raise OSError('No check found')

        root = new_root

    return root


def get_current_check_name(depth=0):
    # Account for this call
    depth += 1

    return os.path.basename(find_check_root(depth))


@contextmanager
def mock_context_manager(obj=None):
    yield obj


def find_free_port(ip):
    """Return a port available for listening on the given `ip`."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind((ip, 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_ip():
    """Return the IP address used to connect to external networks."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]


def get_metadata_metrics():
    # Only called in tests of a check, so just go back one frame
    root = find_check_root(depth=1)
    metadata_path = os.path.join(root, 'metadata.csv')
    metrics = {}
    with open(metadata_path) as f:
        for row in csv.DictReader(f):
            metrics[row['metric_name']] = row
    return metrics


def get_service_checks(depth=1):
    # If it's called directly we can use depth=1, otherwise the caller should pass the correct depth
    check_root = find_check_root(depth=depth)
    service_checks_path = os.path.join(check_root, 'assets', 'service_checks.json')

    with open(service_checks_path) as f:
        return json.load(f)


def assert_service_checks(aggregator):
    # The stub is in the base check, and we don't want to bump the min version for testing purposes
    # Remove this function when all checks are using a base check that includes this function, or we
    # manage to move the aggregator somewhere else
    if hasattr(aggregator, 'assert_service_checks'):
        # We use depth=2 since this function is called from the check and calls another one
        aggregator.assert_service_checks(get_service_checks(depth=2))


def get_hostname():
    """Return the socket hostname"""
    return socket.gethostname()
