# Agent Integration: {integration_name}

## Overview

This integration monitors [{integration_name}][4].

## Setup

### Installation

{install_info}

### Configuration

!!! Add list of steps to set up this integration !!!

### Validation

!!! Add steps to validate integration is functioning as expected !!!

## Data Collected

### Metrics

{integration_name} does not include any metrics.

### Log Collection


1. Collecting logs is disabled by default in the Datadog Agent. Enable it in the `datadog.yaml` file with:

    ```yaml
      logs_enabled: true
    ```

2. Add this configuration block to your `{check_name}.d/conf.yaml` file to start collecting your {integration_name} logs:

    ```yaml
      logs:
        - type: file
          path:  /var/log/{integration_name}.log
          source: {check_name}
          service: <SERVICE_NAME>
    ```

    Change the `path` and `service` parameter values and configure them for your environment.

3. [Restart the Agent][3].

### Events

The {integration_name} integration does not include any events.

## Troubleshooting

Need help? Contact [Datadog support][1].

{integration_links}
