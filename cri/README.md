# Agent Check: CRI

## Overview

This check monitors a Container Runtime Interface

## Setup

### Installation

CRI is a core [Datadog Agent][1] check that needs to be configured in the `datadog.yaml` with the `cri.d/conf.yaml`.

In `datadog.yaml`, configure your `cri_socket_path` for the Agent to query your current CRI (you can also configure default timeouts). In `cri.d/conf.yaml`, configure the check instance settings such as `collect_disk` if your CRI (such as `containerd`) reports disk usage metrics.

**Note**: If you're using the Agent in a container, set the `DD_CRI_SOCKET_PATH` environment variable to automatically enable the `CRI` check with the default configuration.

#### Installation on containers

If you are using the Agent in a container, setting the `DD_CRI_SOCKET_PATH` environment variable to the CRI socket automatically enables the `CRI` integration with the default configuration.

For example, to install the integration on Kubernetes, edit your daemonset to mount the CRI socket from the host node to the Agent container and set the `DD_CRI_SOCKET_PATH` env var to the daemonset mountPath:

```yaml
apiVersion: extensions/v1beta1
kind: DaemonSet
metadata:
  name: datadog-agent
spec:
  template:
    spec:
      containers:
        - name: datadog-agent
          # ...
          env:
            - name: DD_CRI_SOCKET_PATH
              value: /var/run/crio/crio.sock
          volumeMounts:
            - name: crisocket
              mountPath: /var/run/crio/crio.sock
            - mountPath: /host/var/run
              name: var-run
              readOnly: true
          volumes:
            - hostPath:
                path: /var/run/crio/crio.sock
              name: crisocket
            - hostPath:
                path: /var/run
              name: var-run
```

**Note:** The `/var/run` directory must be mounted from the host to run the integration without issues.

### Configuration

1. Edit the `cri.d/conf.yaml` file, in the `conf.d/` folder at the root of your Agent's configuration directory to start collecting your crio performance data. See the [sample cri.d/conf.yaml][2] for all available configuration options.

2. [Restart the Agent][3].

### Validation

Run the Agent's [status subcommand][3] and look for `cri` under the Checks section.

## Data Collected

### Metrics

CRI collect metrics about the resource usage of your containers running through the CRI.

CPU and memory metrics are collected out of the box and you can additionally collect some disk metrics if they are supported by your CRI (CRI-O doesn't support them).

See [metadata.csv][4] for a list of metrics provided by this integration.

### Service Checks

CRI does not include service checks.

### Events

CRI does not include any events.

## Troubleshooting

Need help? Contact [Datadog support][5].

[1]: /account/settings/agent/latest
[2]: https://github.com/DataDog/datadog-agent/blob/master/cmd/agent/dist/conf.d/cri.d/conf.yaml.default
[3]: https://docs.datadoghq.com/agent/guide/agent-commands/#start-stop-and-restart-the-agent
[4]: https://github.com/DataDog/integrations-core/blob/master/cri/metadata.csv
[5]: https://docs.datadoghq.com/help/
