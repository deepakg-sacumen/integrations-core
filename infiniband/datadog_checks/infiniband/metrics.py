# (C) Datadog, Inc. 2025-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
IB_COUNTERS = {
    "VL15_dropped",
    "link_downed",
    "link_error_recovery",
    "local_link_integrity_errors",
    "port_multicast_rcv_packets",
    "port_multicast_xmit_packets",
    "port_rcv_constraint_errors",
    "port_rcv_data",
    "port_rcv_errors",
    "port_rcv_packets",
    "port_rcv_remote_physical_errors",
    "port_rcv_switch_relay_errors",
    "port_unicast_rcv_packets",
    "port_unicast_xmit_packets",
    "port_xmit_constraint_errors",
    "port_xmit_data",
    "port_xmit_discards",
    "port_xmit_packets",
    "port_xmit_packets_64",
    "port_xmit_wait",
    "symbol_error",
    ## Legacy counters
    "excessive_buffer_overrun_errors",
    "multicast_rcv_packets",
    "multicast_xmit_packets",
    "unicast_rcv_packets",
    "unicast_xmit_packets",
    "port_rcv_data_64",
    "port_rcv_packets_64",
    "port_xmit_data_64",
    "port_rcv_discards",
}

RDMA_COUNTERS = {
    "duplicate_request",
    "implied_nak_seq_err",
    "lifespan",
    "local_ack_timeout_err",
    "np_cnp_sent",
    "np_ecn_marked_roce_packets",
    "out_of_buffer",
    "out_of_sequence",
    "packet_seq_err",
    "req_cqe_error",
    "req_cqe_flush_error",
    "req_remote_access_errors",
    "req_remote_invalid_request",
    "resp_cqe_error",
    "resp_cqe_flush_error",
    "resp_local_length_error",
    "resp_remote_access_errors",
    "rnr_nak_retry_err",
    "roce_adp_retrans",
    "roce_adp_retrans_to",
    "roce_slow_restart",
    "roce_slow_restart_cnps",
    "roce_slow_restart_trans",
    "rp_cnp_handled",
    "rp_cnp_ignored",
    "rx_atomic_requests",
    "rx_dct_connect",
    "rx_icrc_encapsulated",
    "rx_read_requests",
    "rx_write_requests",
    "link_down_events_phy",
    "rx_buff_alloc_err",
    "rx_cqe_compress_blks",
    "rx_cqe_compress_pkts",
    "rx_mpwqe_filler",
    "rx_mpwqe_frag",
    "rx_out_of_buffer",
    "rx_vport_multicast_bytes",
    "rx_vport_multicast_packets",
    "rx_vport_unicast_bytes",
    "rx_vport_unicast_packets",
    "rx_wqe_err",
    "tx_vport_unicast_bytes",
    "tx_vport_unicast_packets",
    # EFA Counters
    "tx_pkts",
    "tx_bytes",
    "send_wrs",
    "send_bytes",
    "rx_pkts",
    "rx_drops",
    "rx_bytes",
    "recv_wrs",
    "recv_bytes",
    "rdma_write_wrs",
    "rdma_write_wr_err",
    "rdma_write_recv_bytes",
    "rdma_write_bytes",
    "rdma_read_wrs",
    "rdma_read_wr_err",
    "rdma_read_resp_bytes",
    "rdma_read_bytes",
}

STATUS_COUNTERS = {"state", "phys_state"}  # "4: ACTIVE"  # "5: LinkUp"
