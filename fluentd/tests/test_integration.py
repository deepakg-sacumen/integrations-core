# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import copy

import pytest

from datadog_checks.fluentd import Fluentd

from .common import BAD_PORT, BAD_URL, CHECK_NAME, DEFAULT_INSTANCE, HOST
from .util import _get_metrics_by_version

pytestmark = [pytest.mark.usefixtures("dd_environment"), pytest.mark.integration]


def test_fluentd_exception(aggregator, dd_run_check):
    instance = {"monitor_agent_url": BAD_URL, "plugin_ids": ["plg2"], "tags": ["test"]}
    check = Fluentd(CHECK_NAME, {}, [instance])
    with pytest.raises(Exception):
        dd_run_check(check)

    sc_tags = ['fluentd_host:{}'.format(HOST), 'fluentd_port:{}'.format(BAD_PORT), 'test']
    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, status=Fluentd.CRITICAL, tags=sc_tags, count=1)

    aggregator.assert_all_metrics_covered()


def test_fluentd_with_tag_by_type(aggregator, dd_run_check):
    instance = copy.deepcopy(DEFAULT_INSTANCE)
    instance["tag_by"] = "type"
    check = Fluentd(CHECK_NAME, {}, [instance])
    dd_run_check(check)

    for m in _get_metrics_by_version():
        metric_name = '{0}.{1}'.format(CHECK_NAME, m)
        aggregator.assert_metric(metric_name)

        aggregator.assert_metric_has_tag_prefix(metric_name, 'type')

    sc_tags = ['fluentd_host:{}'.format(HOST), 'fluentd_port:24220']
    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, status=Fluentd.OK, tags=sc_tags, count=1)

    aggregator.assert_all_metrics_covered()


def test_fluentd_with_tag_by_plugin_id(aggregator, dd_run_check):
    instance = copy.deepcopy(DEFAULT_INSTANCE)
    instance["tag_by"] = "plugin_id"

    check = Fluentd(CHECK_NAME, {}, [instance])
    dd_run_check(check)

    for m in _get_metrics_by_version():
        metric_name = '{0}.{1}'.format(CHECK_NAME, m)
        aggregator.assert_metric(metric_name, tags=['plugin_id:plg1'])
        aggregator.assert_metric(metric_name, tags=['plugin_id:plg2'])

    sc_tags = ['fluentd_host:{}'.format(HOST), 'fluentd_port:24220']
    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, status=Fluentd.OK, tags=sc_tags, count=1)

    aggregator.assert_all_metrics_covered()


def test_fluentd_with_custom_tags(aggregator, dd_run_check):
    instance = copy.deepcopy(DEFAULT_INSTANCE)
    custom_tags = ['test', 'tast:tast']
    instance["tags"] = custom_tags
    check = Fluentd(CHECK_NAME, {}, [instance])

    dd_run_check(check)

    for m in _get_metrics_by_version():
        metric_name = '{0}.{1}'.format(CHECK_NAME, m)
        aggregator.assert_metric(metric_name, tags=['plugin_id:plg1'] + custom_tags)
        aggregator.assert_metric(metric_name, tags=['plugin_id:plg2'] + custom_tags)

    sc_tags = ['fluentd_host:{}'.format(HOST), 'fluentd_port:24220'] + custom_tags
    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, status=Fluentd.OK, tags=sc_tags, count=1)

    aggregator.assert_all_metrics_covered()


def test_default_timeout(instance):
    # test default timeout
    check = Fluentd(CHECK_NAME, {}, [instance])
    check.check(None)

    assert check.http.options['timeout'] == (5, 5)


def test_init_config_old_timeout(instance):
    # test init_config timeout
    check = Fluentd(CHECK_NAME, {'default_timeout': 2}, [instance])
    check.check(None)
    assert check.http.options['timeout'] == (2, 2)


def test_init_config_timeout(instance):
    # test init_config timeout
    check = Fluentd(CHECK_NAME, {'timeout': 7}, [instance])
    check.check(None)

    assert check.http.options['timeout'] == (7, 7)


def test_instance_old_timeout(instance):
    # test instance default_timeout
    instance['default_timeout'] = 13
    check = Fluentd(CHECK_NAME, {'default_timeout': 9}, [instance])
    check.check(None)

    assert check.http.options['timeout'] == (13, 13)


def test_instance_timeout(instance):
    # test instance timeout
    instance['timeout'] = 15
    check = Fluentd(CHECK_NAME, {}, [instance])
    check.check(None)

    assert check.http.options['timeout'] == (15, 15)
