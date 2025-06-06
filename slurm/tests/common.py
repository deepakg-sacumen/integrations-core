# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import os

from datadog_checks.slurm.constants import (
    GPU_PARAMS,
    GPU_TOTAL,
    SINFO_ADDITIONAL_NODE_PARAMS,
    SINFO_NODE_PARAMS,
    SINFO_PARTITION_PARAMS,
)

SLURM_VERSION = '21.08.6'
DEFAULT_SINFO_PATH = ['/usr/bin/sinfo']

# Testing for params addition in sinfo
SINFO_1_F = SINFO_PARTITION_PARAMS
SINFO_2_F = SINFO_NODE_PARAMS
SINFO_3_F = [SINFO_NODE_PARAMS[0], SINFO_NODE_PARAMS[-1] + SINFO_ADDITIONAL_NODE_PARAMS]
SINFO_1_T = [SINFO_PARTITION_PARAMS[0], SINFO_PARTITION_PARAMS[-1] + GPU_TOTAL]
SINFO_2_T = [SINFO_NODE_PARAMS[0], SINFO_NODE_PARAMS[-1] + GPU_PARAMS]
SINFO_3_T = [SINFO_NODE_PARAMS[0], SINFO_NODE_PARAMS[-1] + (SINFO_ADDITIONAL_NODE_PARAMS + GPU_PARAMS)]


def mock_output(filename):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(fixture_path, 'r') as f:
        return f.read().strip()


"""
These expected values below are really strict and are hardcoded. I opted for this approach because this whole check
relies on the output and proper parsing of each field. I believe that the most accurate way was to ensure we know
exactly what is being parsed out and what is being submitted to the agent.

If the fixtures are ever updated, then these expected results below will need to be updated as well.
"""

SINFO_MAP = {
    'metrics': [
        {
            'name': 'slurm.sinfo.node.enabled',
            'value': 1,
            'tags': [],
        },
        # Node metrics
        # PARTITION  |AVAIL |NODELIST |CPUSTATE(A/I/O/T) |MEMORY |CLUSTER |CPU_LOAD |FREE_MEM |TMP_DISK |STATE |REASON |ACTIVE_FEATURES |THREADS |ALLOCMEM|GRES        |GRES_USED    # noqa: E501
        # normal*    |up    |c1       |0/1/0/1        |  1000 |N/A     |    1.46 |    4076 |       0 |idle  |none   |(null)          |      1 |0       |gpu:tesla:4 |gpu:tesla:3(IDX:0,2-3)   # noqa: E501
        {
            'name': 'slurm.node.cpu.allocated',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.idle',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.other',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.total',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu_load',
            'value': 1.46,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.free_mem',
            'value': 4076,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.memory',
            'value': 1000,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.alloc_mem',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.gpu_total',
            'value': 4,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.gpu_used',
            'value': 3,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.info',
            'value': 1,
            'tags': [
                'slurm_node_active_features:null',
                'slurm_node_availability:up',
                'slurm_cluster_name:N/A',
                'slurm_node_memory:1000',
                'slurm_node_name:c1',
                'slurm_node_state_reason:none',
                'slurm_node_state:idle',
                'slurm_node_threads:1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_node_gpu_used_idx:0,2-3',
            ],
        },
        {
            'name': 'slurm.node.tmp_disk',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        # PARTITION |AVAIL |NODELIST |CPUSTATE(A/I/O/T) |MEMORY |CLUSTER |CPU_LOAD |FREE_MEM |TMP_DISK |STATE  |REASON |ACTIVE_FEATURES |THREADS |ALLOCMEM|GRES        |GRES_USED    # noqa: E501
        # normal*   |up    |c2       |0/1/0/1        |  1000 |N/A     |    1.46 |    4076 |       0 |idle#  |none   |(null)          |      1 |0       |gpu:tesla:4 |gpu:tesla:4(IDX:0-3) # noqa: E501
        {
            'name': 'slurm.node.cpu.allocated',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.idle',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.other',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu.total',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.cpu_load',
            'value': 1.46,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.free_mem',
            'value': 4076,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.memory',
            'value': 1000,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.alloc_mem',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.gpu_total',
            'value': 4,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.gpu_used',
            'value': 4,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        {
            'name': 'slurm.node.info',
            'value': 1,
            'tags': [
                'sinfo_state_code:powering_up_configured',
                'slurm_node_active_features:null',
                'slurm_node_availability:up',
                'slurm_cluster_name:N/A',
                'slurm_node_memory:1000',
                'slurm_node_name:c2',
                'slurm_node_state_reason:none',
                'slurm_node_state:idle',
                'slurm_node_threads:1',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_node_gpu_used_idx:0-3',
            ],
        },
        {
            'name': 'slurm.node.tmp_disk',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_node_name:c2',
                'slurm_partition_name:normal',
                'slurm_node_gpu_type:tesla',
                'slurm_default_partition:true',
            ],
        },
        # PARTITION |AVAIL |NODELIST |CPUSTATE(A/I/O/T) |MEMORY |CLUSTER |CPU_LOAD |FREE_MEM |TMP_DISK |STATE  |REASON |ACTIVE_FEATURES |THREADS |ALLOCMEM|GRES        |GRES_USED    # noqa: E501
        # buz       |up    |c3       |1/2/3/4        |  5000 |bar     |    2.46 |    5076 |       5 |idle$  |test   |foo             |      6 |0       |(null)      |(null)   # noqa: E501
        {
            'name': 'slurm.node.cpu.allocated',
            'value': 1,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.cpu.idle',
            'value': 2,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.cpu.other',
            'value': 3,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.cpu.total',
            'value': 4,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.cpu_load',
            'value': 2.46,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.free_mem',
            'value': 5076,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.memory',
            'value': 5000,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.alloc_mem',
            'value': 0,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.node.info',
            'value': 1,
            'tags': [
                'sinfo_state_code:maintenance',
                'slurm_node_active_features:foo',
                'slurm_node_availability:up',
                'slurm_cluster_name:bar',
                'slurm_node_memory:5000',
                'slurm_node_name:c3',
                'slurm_node_state_reason:test',
                'slurm_node_state:idle',
                'slurm_node_threads:6',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
                'slurm_node_gpu_used_idx:null',
            ],
        },
        {
            'name': 'slurm.node.tmp_disk',
            'value': 5,
            'tags': [
                'slurm_cluster_name:bar',
                'slurm_node_name:c3',
                'slurm_partition_name:buz',
                'slurm_node_gpu_type:null',
            ],
        },
        {
            'name': 'slurm.sinfo.partition.enabled',
            'value': 1,
            'tags': [],
        },
        # partition metrics
        # PARTITION   | CLUSTER | NODES(A/I/O/T)| GRES         | GRES_USED
        # test-queue* | N/A     | 1/2/0/3       | gpu:tesla:4  | gpu:tesla:3(IDX:0, 2-3)    # noqa: E501
        {
            'name': 'slurm.partition.node.allocated',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        {
            'name': 'slurm.partition.node.idle',
            'value': 2,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        {
            'name': 'slurm.partition.node.other',
            'value': 0,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        {
            'name': 'slurm.partition.node.total',
            'value': 3,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        # PARTITION    | CLUSTER | NODELIST | AVAIL | CPUS | MEMORY | STATE     | NODES | GRES         | GRES_USED     # noqa: E501
        # test-queue*  | N/A     | c[1-2]   | up    | 1    | 972    | allocated | 10    | gpu:tesla:4  | gpu:tesla:3(IDX:0, 2-3)    # noqa: E501
        {
            'name': 'slurm.partition.nodes.count',
            'value': 10,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_cpus_assigned:1',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_memory_assigned:972',
                'slurm_partition_name:test-queue',
                'slurm_partition_node_list:c[1-2]',
                'slurm_partition_state:allocated',
                'slurm_partition_availability:up',
                'slurm_partition_gpu_used_idx:0,2-3',
            ],
        },
        {
            'name': 'slurm.partition.gpu_total',
            'value': 4,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        {
            'name': 'slurm.partition.gpu_used',
            'value': 3,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_name:test-queue',
            ],
        },
        {
            'name': 'slurm.partition.info',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_cpus_assigned:1',
                'slurm_partition_gpu_type:tesla',
                'slurm_default_partition:true',
                'slurm_partition_memory_assigned:972',
                'slurm_partition_name:test-queue',
                'slurm_partition_node_list:c[1-2]',
                'slurm_partition_state:allocated',
                'slurm_partition_availability:up',
                'slurm_partition_gpu_used_idx:0,2-3',
            ],
        },
        # PARTITION    | CLUSTER | NODELIST | AVAIL | CPUS | MEMORY | STATE     | NODES | GRES         | GRES_USED    # noqa: E501
        # foo          | N/A     | c[3-4]   | down  | 1    | 2000   | idle*     | 11    | (null)       | (null)     # noqa: E501
        {
            'name': 'slurm.partition.nodes.count',
            'value': 11,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_cpus_assigned:1',
                'slurm_partition_gpu_type:null',
                'slurm_partition_memory_assigned:2000',
                'slurm_partition_name:foo',
                'slurm_partition_node_list:c[3-4]',
                'slurm_partition_state:idle',
                'slurm_partition_availability:down',
                'sinfo_state_code:non_responsive',
                'slurm_partition_gpu_used_idx:null',
            ],
        },
        {
            'name': 'slurm.partition.info',
            'value': 1,
            'tags': [
                'slurm_cluster_name:N/A',
                'slurm_partition_cpus_assigned:1',
                'slurm_partition_gpu_type:null',
                'slurm_partition_memory_assigned:2000',
                'slurm_partition_name:foo',
                'slurm_partition_node_list:c[3-4]',
                'slurm_partition_state:idle',
                'slurm_partition_availability:down',
                'sinfo_state_code:non_responsive',
                'slurm_partition_gpu_used_idx:null',
            ],
        },
    ]
}

SQUEUE_MAP = {
    'metrics': [
        {
            'name': 'slurm.squeue.enabled',
            'value': 1,
            'tags': [],
        },
        # JOBID |USER |NAME    |STATE   |NODELIST |CPUS |NODELIST(REASON) |MIN_MEMORY | PARTITION # noqa: E501
        #    42 |root |wrap    |RUNNING |c1       |   1 |c1               |300M       | foo       # noqa: E501
        {
            'name': 'slurm.squeue.job.info',
            'value': 1,
            'tags': [
                'slurm_job_cpus:1',
                'slurm_job_id:42',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_reason:c1',
                'slurm_job_state:RUNNING',
                'slurm_job_tres_per_node:300M',
                'slurm_job_user:root',
                'slurm_partition_name:foo',
            ],
        },
        # JOBID |USER |NAME    |STATE   |NODELIST |CPUS |NODELIST(REASON) |MIN_MEMORY | PARTITION # noqa: E501
        #    44 |root |wrap    |RUNNING |c2       |   1 |c2               |400M       | foo       # noqa: E501
        {
            'name': 'slurm.squeue.job.info',
            'value': 1,
            'tags': [
                'slurm_job_cpus:1',
                'slurm_job_id:44',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c2',
                'slurm_job_reason:c2',
                'slurm_job_state:RUNNING',
                'slurm_job_tres_per_node:400M',
                'slurm_job_user:root',
                'slurm_partition_name:foo',
            ],
        },
        # JOBID |USER |NAME    |STATE   |NODELIST |CPUS |NODELIST(REASON) |MIN_MEMORY | PARTITION # noqa: E501
        #    45 |root |test.py |PENDING |         |   1 |(Resources)      |100M       | foo       # noqa: E501
        {
            'name': 'slurm.squeue.job.info',
            'value': 1,
            'tags': [
                'slurm_job_cpus:1',
                'slurm_job_id:45',
                'slurm_job_name:test.py',
                'slurm_job_node_list:null',
                'slurm_job_reason:Resources',
                'slurm_job_state:PENDING',
                'slurm_job_tres_per_node:100M',
                'slurm_job_user:root',
                'slurm_partition_name:foo',
            ],
        },
        # JOBID |USER |NAME    |STATE   |NODELIST |CPUS |NODELIST(REASON) |MIN_MEMORY | PARTITION # noqa: E501
        #    46 |root |test.py |PENDING |         |   1 |(Priority)       |200M       | foo       # noqa: E501
        {
            'name': 'slurm.squeue.job.info',
            'value': 1,
            'tags': [
                'slurm_job_cpus:1',
                'slurm_job_id:46',
                'slurm_job_name:test.py',
                'slurm_job_node_list:null',
                'slurm_job_reason:Priority',
                'slurm_job_state:PENDING',
                'slurm_job_tres_per_node:200M',
                'slurm_job_user:root',
                'slurm_partition_name:foo',
            ],
        },
    ]
}

SACCT_MAP = {
    'metrics': [
        {
            'name': 'slurm.sacct.enabled',
            'value': 1,
            'tags': [],
        },
        # JobID    |JobName |Partition |Account |AllocCPUS |AllocTRES                       |Elapsed  |CPUTimeRAW |MaxRSS  | MaxVMSize |  AveCPU   | AveRSS |State     |ExitCode |Start               |End                 |NodeList | AveDiskRead| MaxDiskRead, # noqa: E501
        # 56       |wrap    |normal    |root    |        1 |billing=1,cpu=1,mem=500M,node=1 |00:12:34 |        10 |    11K |       12K |  00:07:56 |    14K |COMPLETED |0:0      |2024-10-20T22:14:25 |2024-10-20T22:14:25 |c1       | 0.9M       | 0.9M       # noqa: E501
        {
            'name': 'slurm.sacct.job.duration',
            'value': 754,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.job.info',
            'value': 1,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_cputime',
            'value': 10,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_maxrss',
            'value': 11000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_avgcpu',
            'value': 476,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_avgrss',
            'value': 14000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_ave_disk_read',
            'value': 900000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_max_disk_read',
            'value': 900000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_maxvm',
            'value': 12000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_name:wrap',
                'slurm_job_node_list:c1',
                'slurm_job_partition:normal',
                'slurm_partition_name:normal',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:billing=1,cpu=1,mem=500M,node=1',
            ],
        },
        # JobID    |JobName |Partition |Account |AllocCPUS |AllocTRES                       |Elapsed  |CPUTimeRAW |MaxRSS  |MaxVMSize  |AveCPU       |AveRSS  |State     |ExitCode |Start               |End                 |NodeList | AveDiskRead| MaxDiskRead, # noqa: E501
        # 56.batch |batch   |          |root    |        1 |cpu=1,mem=500M,node=1           |01:23:45 |        20 |    21K |       22K |    00:09:56 |    24K |COMPLETED |0:0      |2024-10-20T22:14:25 |2024-10-20T22:14:25 |c1       | 0.9M       | 0.9M       # noqa: E501
        {
            'name': 'slurm.sacct.job.duration',
            'value': 5025,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.job.info',
            'value': 1,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_cputime',
            'value': 20,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_maxrss',
            'value': 21000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_avgcpu',
            'value': 596,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_avgrss',
            'value': 24000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_ave_disk_read',
            'value': 900000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_max_disk_read',
            'value': 900000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
        {
            'name': 'slurm.sacct.slurm_job_maxvm',
            'value': 22000,
            'tags': [
                'slurm_job_account:root',
                'slurm_job_cpus:1',
                'slurm_job_exitcode:0:0',
                'slurm_job_id:56',
                'slurm_job_id_suffix:batch',
                'slurm_job_name:batch',
                'slurm_job_node_list:c1',
                'slurm_job_partition:null',
                'slurm_partition_name:null',
                'slurm_job_state:COMPLETED',
                'slurm_job_tres_per_node:cpu=1,mem=500M,node=1',
            ],
        },
    ]
}

SDIAG_MAP = {
    'metrics': [
        {
            'name': 'slurm.sdiag.enabled',
            'value': 1,
            'tags': [],
        },
        {'name': 'slurm.sdiag.server_thread_count', 'value': 1, 'tags': []},
        {'name': 'slurm.sdiag.agent_queue_size', 'value': 2, 'tags': []},
        {'name': 'slurm.sdiag.agent_count', 'value': 3, 'tags': []},
        {'name': 'slurm.sdiag.agent_thread_count', 'value': 4, 'tags': []},
        {'name': 'slurm.sdiag.dbd_agent_queue_size', 'value': 5, 'tags': []},
        {'name': 'slurm.sdiag.jobs_submitted', 'value': 6, 'tags': []},
        {'name': 'slurm.sdiag.jobs_started', 'value': 7, 'tags': []},
        {'name': 'slurm.sdiag.jobs_completed', 'value': 8, 'tags': []},
        {'name': 'slurm.sdiag.jobs_canceled', 'value': 9, 'tags': []},
        {'name': 'slurm.sdiag.jobs_failed', 'value': 10, 'tags': []},
        {'name': 'slurm.sdiag.jobs_pending', 'value': 11, 'tags': []},
        {'name': 'slurm.sdiag.jobs_running', 'value': 12, 'tags': []},
        {'name': 'slurm.sdiag.last_cycle', 'value': 144, 'tags': []},
        {'name': 'slurm.sdiag.max_cycle', 'value': 3605, 'tags': []},
        {'name': 'slurm.sdiag.total_cycles', 'value': 88, 'tags': []},
        {'name': 'slurm.sdiag.mean_cycle', 'value': 198, 'tags': []},
        {'name': 'slurm.sdiag.mean_depth_cycle', 'value': 13, 'tags': []},
        {'name': 'slurm.sdiag.cycles_per_minute', 'value': 14, 'tags': []},
        {'name': 'slurm.sdiag.last_queue_length', 'value': 15, 'tags': []},
        {'name': 'slurm.sdiag.backfill.total_jobs_since_start', 'value': 16, 'tags': []},
        {'name': 'slurm.sdiag.backfill.total_jobs_since_cycle_start', 'value': 17, 'tags': []},
        {'name': 'slurm.sdiag.backfill.total_heterogeneous_components', 'value': 18, 'tags': []},
        {'name': 'slurm.sdiag.backfill.total_cycles', 'value': 19, 'tags': []},
        {'name': 'slurm.sdiag.backfill.last_cycle', 'value': 20, 'tags': []},
        {'name': 'slurm.sdiag.backfill.max_cycle', 'value': 21, 'tags': []},
        {'name': 'slurm.sdiag.backfill.last_depth_cycle', 'value': 22, 'tags': []},
        {'name': 'slurm.sdiag.backfill.last_depth_try_schedule', 'value': 23, 'tags': []},
        {'name': 'slurm.sdiag.backfill.last_queue_length', 'value': 24, 'tags': []},
        {'name': 'slurm.sdiag.backfill.last_table_size', 'value': 25, 'tags': []},
        {'name': 'slurm.sdiag.backfill.mean_cycle', 'value': 2411, 'tags': []},
        {'name': 'slurm.sdiag.backfill.depth_mean', 'value': 26, 'tags': []},
        {'name': 'slurm.sdiag.backfill.depth_mean_try_depth', 'value': 27, 'tags': []},
        {'name': 'slurm.sdiag.backfill.queue_length_mean', 'value': 28, 'tags': []},
        {'name': 'slurm.sdiag.backfill.mean_table_size', 'value': 29, 'tags': []},
        {
            'name': 'slurm.sdiag.backfill.last_cycle_seconds_ago',
            'value': 1000,
            'tags': [],
        },  # mocked to be 1000 seconds in the test
    ]
}

SSHARE_MAP = {
    'metrics': [
        {
            'name': 'slurm.sshare.enabled',
            'value': 1,
            'tags': [],
        },
        # Account |User |RawShares |NormShares |RawUsage |NormUsage |EffectvUsage |FairShare |LevelFS  |GrpTRESMins |TRESRunMins                                                    | # noqa: E501
        # root    |root |        1 |         2 |       3 |        4 |    5.000000 | 6.000000 |7.000000 |            |cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0 | # noqa: E501
        {
            'name': 'slurm.share.raw_shares',
            'value': 1,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.norm_shares',
            'value': 2,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.raw_usage',
            'value': 3,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.norm_usage',
            'value': 4,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.effective_usage',
            'value': 5,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.fair_share',
            'value': 6,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
        {
            'name': 'slurm.share.level_fs',
            'value': 7,
            'tags': [
                'slurm_account:root',
                'slurm_group_tres_mins:null',
                'slurm_tres_run_mins:cpu=0,mem=0,energy=0,node=0,billing=0,fs/disk=0,vmem=0,pages=0',
                'slurm_user:root',
            ],
        },
    ]
}

SCONTROL_MAP = {
    # PID      JOBID    STEPID   LOCALID GLOBALID
    # 3771     14       batch    0       0
    # 3772     14       batch    -       -
    'metrics': [
        {
            'name': 'slurm.scontrol.jobs.info',
            'value': 1,
            'tags': [
                "pid:3771",
                "slurm_global_id:0",
                "slurm_job_id:14",
                "slurm_local_id:0",
                "slurm_node_name:c1",
                "slurm_step_id:batch",
                "slurm_job_name:my_job",
                "slurm_job_state:RUNNING",
                "slurm_job_user:root",
            ],
        },
        {
            'name': 'slurm.scontrol.jobs.info',
            'value': 1,
            'tags': [
                "pid:3772",
                "slurm_global_id:-",
                "slurm_job_id:14",
                "slurm_local_id:-",
                "slurm_node_name:c1",
                "slurm_step_id:batch",
                "slurm_job_name:my_job",
                "slurm_job_state:RUNNING",
                "slurm_job_user:root",
            ],
        },
        {
            'name': 'slurm.scontrol.jobs.info',
            'value': 1,
            'tags': [
                "pid:3773",
                "slurm_global_id:0",
                "slurm_job_id:15",
                "slurm_local_id:0",
                "slurm_node_name:c1",
                "slurm_step_id:batch",
                "slurm_job_name:my_job2",
                "slurm_job_state:RUNNING",
                "slurm_job_user:root",
            ],
        },
    ]
}
