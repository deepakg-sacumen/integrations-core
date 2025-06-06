## OpenTelemetry Collector
## Overview

<div class="alert alert-danger">
  <strong>Important:</strong> OpenTelemetry Collector Contrib v0.95.0 introduces a breaking change that disables Trace Metrics computation in the Datadog Exporter. Follow Datadog's <a href="https://docs.datadoghq.com/opentelemetry/guide/migration/">migration guide</a> when upgrading.
</div>

OpenTelemetry is a vendor-agnostic standard for telemetry data. Datadog supports ingesting OpenTelemetry data through the OpenTelemetry Collector and the Datadog Agent. This tile documents how to export data to Datadog through the OpenTelemetry Collector with Datadog Exporter [OpenTelemetry collector Datadog exporter][3]. Also see [OTLP ingest in Datadog Agent][7] for further information on ingesting OTLP traces with Datadog Agent.

The OpenTelemetry Collector is a vendor-agnostic agent process that, through the Datadog exporter, exports telemetry data directly to Datadog servers (no Agent installation required). It reports metrics and traces from instrumented applications as well as general system metrics.

Host metrics are shown in the OpenTelemetry Host Metrics default dashboard, but you can send arbitrary metrics to Datadog using the OpenTelemetry Collector. Metrics under `system.*` and `process.*`, such as those generated by the host metrics receiver, are renamed to `otel.system.*` and `otel.process.*` to prevent collisions with metrics from the Datadog Agent. Additionally, OpenTelemetry Collector metrics are shown in the OpenTelemetry Collector Metrics default dashboard.

## Setup

### Installation

Follow the [OpenTelemetry Collector documentation][1] to install the `opentelemetry-collector-contrib` distribution, or any other distribution that includes the Datadog Exporter.

The Datadog Agent is **not** needed to export telemetry data to Datadog in this setup. See [OTLP Ingest in Datadog Agent][7] if you want to use the Datadog Agent instead.
### Configuration

To export telemetry data to Datadog from the OpenTelemetry Collector, add the Datadog exporter to your metrics and traces pipelines.
The only required setting is [your API key][2].

A minimal configuration file to retrieve system metrics is as follows.

``` yaml
receivers:
  hostmetrics:
    scrapers:
      load:
      cpu:
      disk:
      filesystem:
      memory:
      network:
      paging:
      process:

processors:
  batch:
    timeout: 10s

exporters:
  datadog:
    api:
      key: "<Your API key goes here>"
      
service:
  pipelines:
    metrics:
      receivers: [hostmetrics]
      processors: [batch]
      exporters: [datadog]
```

For further information on the Datadog exporter settings and how to configure the pipeline, see [Datadog exporter for OpenTelemetry Collector][3].

See the [Metrics section][5] for metrics types and [metadata.csv][8] for a list of metrics provided by this check. If you're using the `hostmetrics` receiver as in the sample configuration above. You can send arbitrary metrics with other OpenTelemetry Collector components.

Different groups of metrics can be enabled and customized by following the [hostmetrics receiver instructions][4].
CPU and disk metrics are not available on macOS.

### Validation

Check the OpenTelemetry Collector logs to see the Datadog exporter being enabled and started correctly.
For example, with the configuration above you should find logging messages similar to the following.

``` 
Exporter is enabled.	{"component_kind": "exporter", "exporter": "datadog"}
Exporter is starting...	{"component_kind": "exporter", "component_type": "datadog", "component_name": "datadog"}
Exporter started.	{"component_kind": "exporter", "component_type": "datadog", "component_name": "datadog"}
Everything is ready. Begin running and processing data.
```

## Data Collected

### Metrics

#### OpenTelemetry Collector

See [metadata.csv][8] for a list of metrics provided by this integration.

### Service Checks

The OpenTelemetry Collector does not include any service checks.

### Events

The OpenTelemetry Collector does not include any events.

## Troubleshooting

Need help? Contact [Datadog support][6].


[1]: https://opentelemetry.io/docs/collector/getting-started/
[2]: /organization-settings/api-keys
[3]: https://docs.datadoghq.com/tracing/setup_overview/open_standards/otel_collector_datadog_exporter/
[4]: https://github.com/open-telemetry/opentelemetry-collector/tree/master/receiver/
[5]: https://docs.datadoghq.com/metrics/otlp/
[6]: https://docs.datadoghq.com/help/
[7]: https://docs.datadoghq.com/tracing/setup_overview/open_standards/otlp_ingest_in_the_agent/
[8]: https://github.com/DataDog/integrations-core/blob/master/otel/metadata.csv
