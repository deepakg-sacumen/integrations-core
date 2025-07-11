# (C) Datadog, Inc. 2019-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import datetime as dt
import json
import logging
import os
import time

import pytest
from mock import MagicMock, mock, patch
from pyVmomi import vim, vmodl

from datadog_checks.base import to_string
from datadog_checks.base.utils.time import get_current_datetime
from datadog_checks.vsphere import VSphereCheck
from datadog_checks.vsphere.api import APIConnectionError
from datadog_checks.vsphere.config import VSphereConfig
from tests.legacy.utils import mock_alarm_event

from .common import HERE, VSPHERE_VERSION, build_rest_api_client
from .mocked_api import MockedAPI


@pytest.fixture(autouse=True)
def mock_vsan_stub():
    with patch('vsanapiutils.GetVsanVcStub') as GetStub:
        GetStub._stub.host = '0.0.0.0'
        yield GetStub


@pytest.mark.usefixtures("mock_type", "mock_threadpool", "mock_api")
def test_realtime_metrics(aggregator, dd_run_check, realtime_instance):
    """This test asserts that the same api content always produces the same metrics."""
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)

    fixture_file = os.path.join(HERE, 'fixtures', 'metrics_realtime_values.json')
    with open(fixture_file, 'r') as f:
        data = json.load(f)
        for metric in data:
            aggregator.assert_metric(
                metric['name'], metric.get('value'), hostname=metric.get('hostname'), tags=metric.get('tags')
            )

    aggregator.assert_metric('datadog.vsphere.collect_events.time', metric_type=aggregator.GAUGE, count=1)
    aggregator.assert_all_metrics_covered()


@pytest.mark.usefixtures("mock_type", "mock_threadpool", "mock_api")
def test_historical_metrics(aggregator, dd_run_check, historical_instance):
    """This test asserts that the same api content always produces the same metrics."""
    check = VSphereCheck('vsphere', {}, [historical_instance])
    dd_run_check(check)

    fixture_file = os.path.join(HERE, 'fixtures', 'metrics_historical_values.json')
    with open(fixture_file, 'r') as f:
        data = json.load(f)
        for metric in data:
            aggregator.assert_metric(metric['name'], metric.get('value'), tags=metric.get('tags'))

    aggregator.assert_all_metrics_covered()


@pytest.mark.usefixtures("mock_type", "mock_threadpool", "mock_api")
def test_historical_metrics_no_dsc_folder(aggregator, dd_run_check, historical_instance):
    """This test does the same check than test_historical_events, but deactivate the option to get datastore cluster
    folder in metrics tags"""
    check = VSphereCheck('vsphere', {}, [historical_instance])
    check._config.include_datastore_cluster_folder_tag = False
    dd_run_check(check)

    fixture_file = os.path.join(HERE, 'fixtures', 'metrics_historical_values.json')

    with open(fixture_file, 'r') as f:
        data = json.load(f)
        for metric in data:
            all_tags = metric.get('tags')
            if all_tags is not None:
                # The tag 'vsphere_folder:Datastores' is not supposed to be there anymore!
                all_tags = [tag for tag in all_tags if tag != 'vsphere_folder:Datastores']
            aggregator.assert_metric(metric['name'], metric.get('value'), tags=all_tags)

    aggregator.assert_all_metrics_covered()


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_events_only(aggregator, events_only_instance):
    check = VSphereCheck('vsphere', {}, [events_only_instance])
    check.initiate_api_connection()

    time1 = dt.datetime.now()
    event1 = mock_alarm_event(from_status='green', key=10, created_time=time1)

    check.api.mock_events = [event1]
    check.check(None)
    aggregator.assert_event("vCenter monitor status changed on this alarm, it was green and it's now red.", count=1)

    aggregator.assert_metric('datadog.vsphere.collect_events.time')

    # assert all metrics will check that we are not collecting historical and realtime metrics
    aggregator.assert_all_metrics_covered()


@pytest.mark.usefixtures("mock_type", 'mock_rest_api')
def test_external_host_tags(aggregator, realtime_instance):
    realtime_instance['collect_tags'] = True
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    config = VSphereConfig(realtime_instance, {}, MagicMock())
    check.api = MockedAPI(config)
    check.api_rest = build_rest_api_client(config, MagicMock())

    with check.infrastructure_cache.update():
        check.refresh_infrastructure_cache()

    fixture_file = os.path.join(HERE, 'fixtures', 'host_tags_values.json')
    with open(fixture_file, 'r') as f:
        expected_tags = json.load(f)

    check.set_external_tags = MagicMock()
    check.submit_external_host_tags()
    submitted_tags = check.set_external_tags.mock_calls[0].args[0]
    submitted_tags.sort(key=lambda x: x[0])
    expected_tags.sort(key=lambda x: x[0])
    for ex, sub in zip(expected_tags, submitted_tags):
        ex_host, sub_host = ex[0], sub[0]
        ex_tags, sub_tags = ex[1]['vsphere'], sub[1]['vsphere']
        ex_tags = [to_string(t) for t in ex_tags]  # json library loads data in unicode, let's convert back to native
        assert ex_host == sub_host
        assert sorted(ex_tags) == sorted(sub_tags)

    check._config.excluded_host_tags = ['vsphere_host']
    check.set_external_tags = MagicMock()
    check.submit_external_host_tags()
    submitted_tags = check.set_external_tags.mock_calls[0].args[0]
    submitted_tags.sort(key=lambda x: x[0])
    for ex, sub in zip(expected_tags, submitted_tags):
        ex_host, sub_host = ex[0], sub[0]
        ex_tags, sub_tags = ex[1]['vsphere'], sub[1]['vsphere']
        ex_tags = [to_string(t) for t in ex_tags if 'vsphere_host:' not in t]
        assert ex_host == sub_host
        assert sorted(ex_tags) == sorted(sub_tags)

    check.set_external_tags = MagicMock()
    check.submit_external_host_tags()


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api')
def test_collect_metric_instance_values(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update(
        {
            'collect_per_instance_filters': {
                'vm': [r'cpu\.usagemhz\.avg', r'disk\..*'],
                'host': [r'cpu\.coreUtilization\..*', r'sys\.uptime\..*', r'disk\..*'],
            }
        }
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)

    # Following metrics should match and have instance value tag
    aggregator.assert_metric('vsphere.cpu.usagemhz.avg', tags=['cpu_core:6', 'vcenter_server:FAKE'])
    aggregator.assert_metric(
        'vsphere.cpu.coreUtilization.avg', hostname='10.0.0.104', tags=['cpu_core:16', 'vcenter_server:FAKE']
    )

    # Following metrics should NOT match and do NOT have instance value tag
    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'])
    aggregator.assert_metric('vsphere.cpu.totalCapacity.avg', tags=['vcenter_server:FAKE'])

    # None of `vsphere.disk.usage.avg` metrics have instance values for specific metric+resource_type
    # Hence the aggregated metric IS collected
    aggregator.assert_metric('vsphere.disk.usage.avg', tags=['vcenter_server:FAKE'], hostname='VM4-1', count=1)

    # Some of `vsphere.disk.read.avg` metrics have instance values for specific metric+resource_type
    # Hence the aggregated metric IS NOT collected
    aggregator.assert_metric('vsphere.disk.read.avg', tags=['vcenter_server:FAKE'], hostname='VM4-1', count=0)
    for instance_tag in ['device_path:value-aa', 'device_path:value-bb']:
        aggregator.assert_metric(
            'vsphere.disk.read.avg', tags=['vcenter_server:FAKE'] + [instance_tag], hostname='VM4-1', count=1
        )


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api')
def test_collect_metric_instance_values_historical(aggregator, dd_run_check, historical_instance):
    historical_instance.update(
        {
            'collect_per_instance_filters': {
                'datastore': [r'disk\..*'],
                # datacenter metric group doesn't have any instance tags so this has no effect
                'datacenter': [r'cpu\.usagemhz\.avg'],
                'cluster': [r'cpu\.usagemhz\.avg'],
            }
        }
    )

    check = VSphereCheck('vsphere', {}, [historical_instance])
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usagemhz.avg',
        tags=[
            'cpu_core:16',
            'vcenter_server:FAKE',
            'vsphere_cluster:Cluster2',
            'vsphere_datacenter:Datacenter2',
            'vsphere_folder:Datacenters',
            'vsphere_folder:host',
            'vsphere_type:cluster',
        ],
    )

    aggregator.assert_metric(
        'vsphere.disk.used.latest',
        tags=[
            'device_path:value-aa',
            'vcenter_server:FAKE',
            'vsphere_datacenter:Datacenter2',
            'vsphere_datastore:NFS Share',
            'vsphere_folder:Datacenters',
            'vsphere_folder:datastore',
            'vsphere_type:datastore',
        ],
    )

    # Following metrics should NOT match and do NOT have instance value tag
    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=[
            'vcenter_server:FAKE',
            'vsphere_cluster:Cluster2',
            'vsphere_datacenter:Datacenter2',
            'vsphere_folder:Datacenters',
            'vsphere_folder:host',
            'vsphere_type:cluster',
        ],
    )


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_collect_tags(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update({'collect_tags': True, 'excluded_host_tags': ['my_cat_name_1', 'my_cat_name_2']})
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='VM4-4',
    )
    aggregator.assert_metric(
        'vsphere.rescpu.samplePeriod.latest',
        tags=['my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='10.0.0.104',
    )
    aggregator.assert_metric(
        'vsphere.datastore.maxTotalLatency.latest',
        tags=['my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='10.0.0.104',
    )
    aggregator.assert_metric('datadog.vsphere.query_tags.time', tags=['vcenter_server:FAKE'])


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_tag_prefix(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update(
        {'collect_tags': True, 'tags_prefix': 'ABC_', 'excluded_host_tags': ['ABC_my_cat_name_1', 'ABC_my_cat_name_2']}
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['ABC_my_cat_name_1:my_tag_name_1', 'ABC_my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='VM4-4',
    )


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api')
def test_continue_if_tag_collection_fail(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update({'collect_tags': True})
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    check.log = MagicMock()

    with mock.patch('requests.Session.post', side_effect=Exception, autospec=True):
        dd_run_check(check)

    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'], hostname='10.0.0.104')

    check.log.error.assert_called_once_with(
        "Cannot connect to vCenter REST API. Tags won't be collected. Error: %s", mock.ANY
    )


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api')
def test_refresh_tags_cache_should_not_raise_exception(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update({'collect_tags': True})
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    check.log = MagicMock()
    check.api_rest = MagicMock()
    check.api_rest.get_resource_tags_for_mors.side_effect = APIConnectionError("Some error")

    check.collect_tags({})

    # Error logged, but `refresh_tags_cache` should NOT raise any exception
    check.log.error.assert_called_once_with("Failed to collect tags: %s", mock.ANY)


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_renew_rest_api_session_on_failure(aggregator, dd_run_check, realtime_instance):
    realtime_instance.update({'collect_tags': True})
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    config = VSphereConfig(realtime_instance, {}, MagicMock())
    check.api_rest = build_rest_api_client(config, MagicMock())
    check.api_rest.make_batch = MagicMock(side_effect=[Exception, []])
    check.api_rest.smart_connect = MagicMock()

    tags = check.collect_tags({})
    assert tags
    assert check.api_rest.make_batch.call_count == 2
    assert check.api_rest.smart_connect.call_count == 1


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_tags_filters_integration_tags(aggregator, dd_run_check, historical_instance):
    historical_instance['collect_tags'] = True
    historical_instance['resource_filters'] = [
        {
            'resource': 'cluster',
            'property': 'tag',
            'patterns': [
                r'vsphere_datacenter:Datacenter2',
            ],
        },
        {
            'resource': 'datastore',
            'property': 'tag',
            'patterns': [
                r'vsphere_datastore:Datastore 1',
            ],
        },
    ]

    check = VSphereCheck('vsphere', {}, [historical_instance])
    dd_run_check(check)

    aggregator.assert_metric('vsphere.cpu.usage.avg', count=1)
    aggregator.assert_metric_has_tag('vsphere.cpu.usage.avg', 'vsphere_datacenter:Datacenter2', count=1)
    aggregator.assert_metric_has_tag('vsphere.cpu.usage.avg', 'vsphere_datacenter:Dätacenter', count=0)

    aggregator.assert_metric('vsphere.disk.used.latest', count=2)
    aggregator.assert_metric('vsphere.disk.used.latest', count=1, hostname='VM4-2')
    aggregator.assert_metric_has_tag('vsphere.disk.used.latest', 'vsphere_datastore:Datastore 1', count=1)
    aggregator.assert_metric_has_tag('vsphere.disk.used.latest', 'vsphere_datastore:Datastore 2', count=0)


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_tags_filters_when_tags_are_not_yet_collected(aggregator, dd_run_check, realtime_instance):
    realtime_instance['collect_tags'] = True
    realtime_instance['resource_filters'] = [
        {'resource': 'vm', 'property': 'tag', 'patterns': [r'my_cat_name_1:my_tag_name_1']},
        {'resource': 'host', 'property': 'name', 'type': 'blacklist', 'patterns': [r'.*']},
    ]

    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)
    # Assert that only a single resource was collected
    aggregator.assert_metric('vsphere.cpu.usage.avg', count=1)
    # Assert that the resource that was collected is the one with the correct tag
    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'], hostname='VM4-4')


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_tags_filters_with_prefix_when_tags_are_not_yet_collected(aggregator, dd_run_check, realtime_instance):
    realtime_instance['collect_tags'] = True
    realtime_instance['resource_filters'] = [
        {'resource': 'vm', 'property': 'tag', 'patterns': [r'foo_my_cat_name_1:my_tag_name_1']},
        {'resource': 'host', 'property': 'name', 'type': 'blacklist', 'patterns': [r'.*']},
    ]
    realtime_instance['tags_prefix'] = 'foo_'

    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)
    # Assert that only a single resource was collected
    aggregator.assert_metric('vsphere.cpu.usage.avg', count=1)
    # Assert that the resource that was collected is the one with the correct tag
    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'], hostname='VM4-4')


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api')
def test_attributes_filters(aggregator, dd_run_check, realtime_instance):
    realtime_instance['collect_attributes'] = True
    realtime_instance['attributes_prefix'] = 'vattr_'
    realtime_instance['resource_filters'] = [
        {'resource': 'vm', 'property': 'attribute', 'patterns': [r'vattr_foo:bar\d']},
        {'resource': 'host', 'property': 'name', 'type': 'blacklist', 'patterns': [r'.*']},
    ]
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)
    # Assert that only a single resource was collected
    aggregator.assert_metric('vsphere.cpu.usage.avg', count=2)
    # Assert that the resource that was collected is the one with the correct tag
    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'], hostname='VM4-15')
    # Assert that the resource that was collected is the one with the correct tag
    aggregator.assert_metric('vsphere.cpu.usage.avg', tags=['vcenter_server:FAKE'], hostname='VM4-9')


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_version_metadata(aggregator, dd_run_check, realtime_instance, datadog_agent):
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    check.check_id = 'test:123'
    dd_run_check(check)

    major, minor, patch = VSPHERE_VERSION.split('.')
    version_metadata = {
        'version.scheme': 'semver',
        'version.major': major,
        'version.minor': minor,
        'version.patch': patch,
        'version.build': '123456789',
        'version.raw': '{}+123456789'.format(VSPHERE_VERSION),
    }

    datadog_agent.assert_metadata('test:123', version_metadata)


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_specs_start_time(aggregator, dd_run_check, historical_instance):
    mock_time = dt.datetime.now()

    check = VSphereCheck('vsphere', {}, [historical_instance])
    dd_run_check(check)

    check.api.server_time = mock_time

    start_times = []
    for specs in check.make_query_specs():
        for spec in specs:
            start_times.append(spec.startTime)

    assert len(start_times) != 0
    for start_time in start_times:
        assert start_time == (mock_time - dt.timedelta(hours=2))


@pytest.mark.parametrize(
    'test_timeout, expected_result',
    [
        (1, False),
        (2, False),
        (20, True),
    ],
)
@pytest.mark.usefixtures('mock_type', 'mock_api')
def test_connection_refresh(aggregator, dd_run_check, realtime_instance, test_timeout, expected_result):
    # This test is to ensure that the connection is refreshed after a specified period of time.
    # We run the check initially to get a connection object, sleep for a period of time, and then
    # rerun the check and compare and see if the connection objects are the same.
    realtime_instance['connection_reset_timeout'] = test_timeout
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    dd_run_check(check)
    first_connection = check.api

    time.sleep(2)

    dd_run_check(check)

    same_object = False
    if first_connection == check.api:
        same_object = True

    assert same_object == expected_result


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_vm_hostname_suffix_tag(aggregator, dd_run_check, realtime_instance, caplog):
    realtime_instance.update(
        {
            'collect_tags': True,
            'vm_hostname_suffix_tag': 'my_cat_name_1',
            'excluded_host_tags': ['my_cat_name_1', 'my_cat_name_2'],
        }
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    caplog.set_level(logging.DEBUG)
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='VM4-4-my_tag_name_1',
    )
    assert "Attached hostname suffix key my_cat_name_1, new hostname: VM4-4-my_tag_name_1" in caplog.text
    assert "Could not attach hostname suffix key my_cat_name_1 for host: VM-on-fake-host" in caplog.text


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_vm_hostname_suffix_tag_bad_value(aggregator, dd_run_check, realtime_instance, caplog):
    realtime_instance.update(
        {
            'collect_tags': True,
            'vm_hostname_suffix_tag': 'my_cat_name_3',
            'excluded_host_tags': ['my_cat_name_1', 'my_cat_name_2'],
        }
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    caplog.set_level(logging.DEBUG)
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='VM4-4',
    )
    assert "Could not attach hostname suffix key my_cat_name_3 for host: VM4-4" in caplog.text
    assert "Could not attach hostname suffix key my_cat_name_3 for host: VM-on-fake-host" in caplog.text


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_vm_hostname_suffix_tag_integration(aggregator, dd_run_check, realtime_instance, caplog):
    realtime_instance.update(
        {
            'collect_tags': True,
            'vm_hostname_suffix_tag': 'vsphere_host',
            'excluded_host_tags': ['my_cat_name_1', 'my_cat_name_2'],
        }
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    caplog.set_level(logging.DEBUG)
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_2:my_tag_name_2', 'vcenter_server:FAKE'],
        hostname='VM4-4-10.0.0.104',
    )
    assert "Attached hostname suffix key vsphere_host, new hostname: VM4-4-10.0.0.104" in caplog.text


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_vm_hostname_suffix_tag_custom(aggregator, dd_run_check, realtime_instance, caplog):
    realtime_instance.update({'collect_tags': True, 'vm_hostname_suffix_tag': 'test', 'tags': ['test:tag_name']})
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    caplog.set_level(logging.DEBUG)
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['test:tag_name', 'vcenter_server:FAKE'],
        hostname='VM4-4-tag_name',
    )
    assert "Attached hostname suffix key test, new hostname: VM4-4-tag_name" in caplog.text


@pytest.mark.usefixtures('mock_type', 'mock_threadpool', 'mock_api', 'mock_rest_api')
def test_vm_hostname_suffix_tag_same_key(aggregator, dd_run_check, realtime_instance, caplog):
    realtime_instance.update(
        {
            'collect_tags': True,
            'vm_hostname_suffix_tag': 'my_cat_name_1',
            'excluded_host_tags': ['my_cat_name_1'],
            'tags': ['my_cat_name_1:tag_name'],
        }
    )
    check = VSphereCheck('vsphere', {}, [realtime_instance])
    caplog.set_level(logging.DEBUG)
    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_1:tag_name', 'vcenter_server:FAKE'],
        hostname='VM4-4-my_tag_name_1',
    )
    assert "Attached hostname suffix key my_cat_name_1, new hostname: VM4-4-my_tag_name_1" in caplog.text

    dd_run_check(check)

    aggregator.assert_metric(
        'vsphere.cpu.usage.avg',
        tags=['my_cat_name_1:my_tag_name_1', 'my_cat_name_1:tag_name', 'vcenter_server:FAKE'],
        hostname='VM4-4-my_tag_name_1',
    )
    assert "Attached hostname suffix key my_cat_name_1, new hostname: VM4-4-my_tag_name_1" in caplog.text


def test_no_infra_cache(aggregator, realtime_instance, dd_run_check, caplog):
    with (
        mock.patch('pyVim.connect.SmartConnect') as mock_connect,
        mock.patch('pyVmomi.vmodl.query.PropertyCollector') as mock_property_collector,
    ):
        mock_si = mock.MagicMock()
        mock_si.content.eventManager.QueryEvents.return_value = []
        mock_si.content.perfManager.QueryPerfCounterByLevel.return_value = [
            vim.PerformanceManager.CounterInfo(
                key=100,
                groupInfo=vim.ElementDescription(key='cpu'),
                nameInfo=vim.ElementDescription(key='costop'),
                rollupType=vim.PerformanceManager.CounterInfo.RollupType.summation,
            )
        ]
        mock_si.content.perfManager.QueryPerf.return_value = [
            vim.PerformanceManager.EntityMetric(
                entity=vim.VirtualMachine(moId="vm1"),
                value=[
                    vim.PerformanceManager.IntSeries(
                        value=[47, 52],
                        id=vim.PerformanceManager.MetricId(counterId=100),
                    )
                ],
            ),
            vim.PerformanceManager.EntityMetric(
                entity=vim.VirtualMachine(moId="vm2"),
                value=[
                    vim.PerformanceManager.IntSeries(
                        value=[30, 11],
                        id=vim.PerformanceManager.MetricId(counterId=100),
                    )
                ],
            ),
        ]
        mock_property_collector.ObjectSpec.return_value = vmodl.query.PropertyCollector.ObjectSpec()
        mock_si.content.viewManagerCreateContainerView.return_value = vim.view.ContainerView(moId="cv1")
        mock_si.content.propertyCollector.RetrievePropertiesEx.return_value = None

        mock_connect.return_value = mock_si
        caplog.set_level(logging.WARNING)
        check = VSphereCheck('vsphere', {}, [realtime_instance])

        dd_run_check(check)
        assert "Did not retrieve any properties from the vCenter. "
        "Metric collection cannot continue. Ensure your user has correct permissions." in caplog.text

        aggregator.assert_metric('datadog.vsphere.collect_events.time')
        aggregator.assert_metric('datadog.vsphere.refresh_metrics_metadata_cache.time')
        aggregator.assert_metric('datadog.vsphere.refresh_infrastructure_cache.time')

        aggregator.assert_all_metrics_covered()


def test_no_infra_cache_events(aggregator, realtime_instance, dd_run_check, caplog):
    with (
        mock.patch('pyVim.connect.SmartConnect') as mock_connect,
        mock.patch('pyVmomi.vmodl.query.PropertyCollector') as mock_property_collector,
    ):
        event = vim.event.VmReconfiguredEvent()
        event.userName = "datadog"
        event.createdTime = get_current_datetime()
        event.vm = vim.event.VmEventArgument()
        event.vm.name = "vm1"
        event.configSpec = vim.vm.ConfigSpec()

        mock_si = mock.MagicMock()
        mock_si.content.eventManager.QueryEvents.return_value = [event]
        mock_si.content.perfManager.QueryPerfCounterByLevel.return_value = [
            vim.PerformanceManager.CounterInfo(
                key=100,
                groupInfo=vim.ElementDescription(key='cpu'),
                nameInfo=vim.ElementDescription(key='costop'),
                rollupType=vim.PerformanceManager.CounterInfo.RollupType.summation,
            )
        ]
        mock_si.content.perfManager.QueryPerf.return_value = [
            vim.PerformanceManager.EntityMetric(
                entity=vim.VirtualMachine(moId="vm1"),
                value=[
                    vim.PerformanceManager.IntSeries(
                        value=[47, 52],
                        id=vim.PerformanceManager.MetricId(counterId=100),
                    )
                ],
            ),
            vim.PerformanceManager.EntityMetric(
                entity=vim.VirtualMachine(moId="vm2"),
                value=[
                    vim.PerformanceManager.IntSeries(
                        value=[30, 11],
                        id=vim.PerformanceManager.MetricId(counterId=100),
                    )
                ],
            ),
        ]
        mock_property_collector.ObjectSpec.return_value = vmodl.query.PropertyCollector.ObjectSpec()
        mock_si.content.viewManagerCreateContainerView.return_value = vim.view.ContainerView(moId="cv1")
        mock_si.content.propertyCollector.RetrievePropertiesEx.return_value = None

        mock_connect.return_value = mock_si
        caplog.set_level(logging.WARNING)
        check = VSphereCheck('vsphere', {}, [realtime_instance])

        dd_run_check(check)
        assert "Did not retrieve any properties from the vCenter. "
        "Metric collection cannot continue. Ensure your user has correct permissions." in caplog.text

        aggregator.assert_metric('datadog.vsphere.collect_events.time')
        aggregator.assert_metric('datadog.vsphere.refresh_metrics_metadata_cache.time')
        aggregator.assert_metric('datadog.vsphere.refresh_infrastructure_cache.time')

        aggregator.assert_event(
            """datadog saved the new configuration:\n@@@\n""",
            exact_match=False,
            msg_title="VM vm1 configuration has been changed",
            host="vm1",
        )

        aggregator.assert_all_metrics_covered()


def test_no_infra_cache_no_perf_values(aggregator, realtime_instance, dd_run_check, caplog):
    with (
        mock.patch('pyVim.connect.SmartConnect') as mock_connect,
        mock.patch('pyVmomi.vmodl.query.PropertyCollector') as mock_property_collector,
    ):
        event = vim.event.VmReconfiguredEvent()
        event.userName = "datadog"
        event.createdTime = get_current_datetime()
        event.vm = vim.event.VmEventArgument()
        event.vm.name = "vm1"
        event.configSpec = vim.vm.ConfigSpec()

        mock_si = mock.MagicMock()
        mock_si.content.eventManager.QueryEvents.return_value = [event]
        mock_si.content.perfManager.QueryPerfCounterByLevel.return_value = []
        mock_si.content.perfManager.QueryPerf.return_value = []
        mock_property_collector.ObjectSpec.return_value = vmodl.query.PropertyCollector.ObjectSpec()
        mock_si.content.viewManagerCreateContainerView.return_value = vim.view.ContainerView(moId="cv1")
        mock_si.content.propertyCollector.RetrievePropertiesEx.return_value = None

        mock_connect.return_value = mock_si
        caplog.set_level(logging.WARNING)
        check = VSphereCheck('vsphere', {}, [realtime_instance])

        dd_run_check(check)
        assert "Did not retrieve any properties from the vCenter. "
        "Metric collection cannot continue. Ensure your user has correct permissions." in caplog.text

        aggregator.assert_metric('datadog.vsphere.collect_events.time')
        aggregator.assert_metric('datadog.vsphere.refresh_metrics_metadata_cache.time')
        aggregator.assert_metric('datadog.vsphere.refresh_infrastructure_cache.time')

        aggregator.assert_event(
            """datadog saved the new configuration:\n@@@\n""",
            exact_match=False,
            msg_title="VM vm1 configuration has been changed",
            host="vm1",
        )

        aggregator.assert_all_metrics_covered()
