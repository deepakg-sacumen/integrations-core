# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
# pylint: disable=W1633
from __future__ import division

import re
from collections import defaultdict

from datadog_checks.base import AgentCheck
from datadog_checks.base.utils.subprocess_output import get_subprocess_output

EVENT_TYPE = SOURCE_TYPE_NAME = 'cassandra_nodetool'
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '7199'
TO_BYTES = {
    'B': 1,
    'KB': 1e3,
    'MB': 1e6,
    'GB': 1e9,
    'TB': 1e12,
    # only available in cassandra 3.11 or later
    'iB': 1,
    'KiB': 1e3,
    'MiB': 1e6,
    'GiB': 1e9,
    'TiB': 1e12,
}


class CassandraNodetoolCheck(AgentCheck):
    datacenter_name_re = re.compile('^Datacenter: (.*)')
    # 1.
    # --  Address    Load       Tokens  Owns    Host ID                               Rack
    # UN  127.0.0.1  47.66 KB   1       33.3%   aaa1b7c1-6049-4a08-ad3e-3697a0e30e10  rack1
    # 2. old nodetool output format
    # --  Address    Load       Owns    Host ID                               Token                     Rack
    # UN  127.0.0.1  47.66 KB   33.3%   aaa1b7c1-6049-4a08-ad3e-3697a0e30e10  4035225268091337308       rack1
    node_status_re = re.compile(
        r'^(?P<status>[UD])[NLJM] +(?P<address>\d+\.\d+\.\d+\.\d+) +'
        r'(?P<load>\d+(\.\d*)?) (?P<load_unit>(K|M|G|T)?i?B) +(\d+ +)?'
        r'(?P<owns>(\d+(\.\d+)?)|\?)%? +(?P<id>[a-fA-F0-9-]*) +(-?\d+ +)?'
        r'(?P<rack>.*)'
    )

    def __init__(self, name, init_config, instances):
        super(CassandraNodetoolCheck, self).__init__(name, init_config, instances)
        # Allow to specify a complete command for nodetool such as `docker exec container nodetool`
        default_nodetool_cmd = init_config.get("nodetool", "/usr/bin/nodetool")
        nodetool_cmd = self.instance.get('nodetool', default_nodetool_cmd).split()
        host = self.instance.get("host", DEFAULT_HOST)
        port = self.instance.get("port", DEFAULT_PORT)
        username = self.instance.get("username", "")
        password = self.instance.get("password", "")
        ssl = self.instance.get("ssl", False)

        # Build the nodetool command
        cmd = nodetool_cmd + ['-h', host, '-p', str(port)]
        if username and password:
            cmd += ['-u', username, '-pw', password]
        # add ssl if requested
        if ssl:
            cmd += ['--ssl']
        self.nodetool_cmd = cmd

        self.tags = self.instance.get("tags", [])
        self.keyspaces = self.instance.get("keyspaces", [])

    def check(self, _):
        # Flag to send service checks only once and not for every keyspace
        send_service_checks = True

        if not self.keyspaces:
            self.log.info("No keyspaces set in the configuration: no metrics will be sent")

        for keyspace in self.keyspaces:
            cmd = self.nodetool_cmd + ['status', '--', keyspace]

            # Execute the command
            out, err, code = get_subprocess_output(cmd, self.log, False, log_debug=False)
            if err or 'Error:' in out or code != 0:
                self.log.error('Error executing nodetool status: %s', err or out)
                continue
            nodes = self._process_nodetool_output(out)

            percent_up_by_dc = defaultdict(float)
            percent_total_by_dc = defaultdict(float)
            # Send the stats per node and compute the stats per datacenter
            for node in nodes:
                node_tags = [
                    'node_address:%s' % node['address'],
                    'node_id:%s' % node['id'],
                    'datacenter:%s' % node['datacenter'],
                    'rack:%s' % node['rack'],
                ]

                # nodetool prints `?` when it can't compute the value of `owns` for certain keyspaces (e.g. system)
                # don't send metric in this case
                if node['owns'] != '?':
                    owns = float(node['owns'])
                    if node['status'] == 'U':
                        percent_up_by_dc[node['datacenter']] += owns
                    percent_total_by_dc[node['datacenter']] += owns
                    self.gauge(
                        'cassandra.nodetool.status.owns', owns, tags=self.tags + node_tags + ['keyspace:%s' % keyspace]
                    )

                # Send service check only once for each node
                if send_service_checks:
                    status = AgentCheck.OK if node['status'] == 'U' else AgentCheck.CRITICAL
                    self.service_check('cassandra.nodetool.node_up', status, self.tags + node_tags)

                self.gauge(
                    'cassandra.nodetool.status.status', 1 if node['status'] == 'U' else 0, tags=self.tags + node_tags
                )
                self.gauge(
                    'cassandra.nodetool.status.load',
                    float(node['load']) * TO_BYTES[node['load_unit']],
                    tags=self.tags + node_tags,
                )

            # All service checks have been sent, don't resend
            send_service_checks = False

            # Send the stats per datacenter
            for datacenter, percent_up in percent_up_by_dc.items():
                self.gauge(
                    'cassandra.nodetool.status.replication_availability',
                    percent_up,
                    tags=self.tags + ['keyspace:%s' % keyspace, 'datacenter:%s' % datacenter],
                )
            for datacenter, percent_total in percent_total_by_dc.items():
                self.gauge(
                    'cassandra.nodetool.status.replication_factor',
                    int(round(percent_total / 100)),
                    tags=self.tags + ['keyspace:%s' % keyspace, 'datacenter:%s' % datacenter],
                )

    def _process_nodetool_output(self, output):
        nodes = []
        datacenter_name = ""
        for line in output.splitlines():
            # Output of nodetool
            # Datacenter: dc1
            # ===============
            # Status=Up/Down
            # |/ State=Normal/Leaving/Joining/Moving
            # --  Address     Load       Tokens  Owns (effective)  Host ID                               Rack
            # UN  172.21.0.3  184.8 KB   256     38.4%             7501ef03-eb63-4db0-95e6-20bfeb7cdd87  RAC1
            # UN  172.21.0.4  223.34 KB  256     39.5%             e521a2a4-39d3-4311-a195-667bf56450f4  RAC1

            match = self.datacenter_name_re.search(line)
            if match:
                datacenter_name = match.group(1)
                continue

            match = self.node_status_re.search(line)
            if match:
                node = {
                    'status': match.group('status'),
                    'address': match.group('address'),
                    'load': match.group('load'),
                    'load_unit': match.group('load_unit'),
                    'owns': match.group('owns'),
                    'id': match.group('id'),
                    'rack': match.group('rack'),
                    'datacenter': datacenter_name,
                }
                nodes.append(node)

        return nodes
