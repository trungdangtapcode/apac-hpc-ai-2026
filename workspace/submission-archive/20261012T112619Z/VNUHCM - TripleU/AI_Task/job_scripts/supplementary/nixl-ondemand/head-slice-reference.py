from __future__ import annotations

# Exact helper extracted from the supplied image; used by CPU equivalence tests.
def compute_head_slice_params(
    src_attn_tp_size: int,
    dst_attn_tp_size: int,
    src_tp_rank: int,
    dst_tp_rank: int,
    total_kv_heads: int,
) -> Tuple[int, int, int, int]:
    """Compute head slicing parameters for heterogeneous TP transfer.

    Returns:
        (src_head_start, num_heads_to_send, dst_head_start, num_heads_to_send)
    """
    src_heads_per_rank = max(1, total_kv_heads // src_attn_tp_size)
    dst_heads_per_rank = max(1, total_kv_heads // dst_attn_tp_size)

    local_tp_rank = src_tp_rank % src_attn_tp_size
    dst_tp_rank_in_group = dst_tp_rank % dst_attn_tp_size

    if src_attn_tp_size > dst_attn_tp_size:
        src_head_start = 0
        num_heads_to_send = src_heads_per_rank
        src_replication = max(1, src_attn_tp_size // total_kv_heads)
        unique_head_idx = local_tp_rank // src_replication
        dst_head_start = (unique_head_idx * src_heads_per_rank) % dst_heads_per_rank
    else:
        # GQA replication: consecutive decode ranks share a KV head
        # (tp_rank // num_kv_head_replicas), so map by integer division not modulo.
        dst_replication = max(1, dst_attn_tp_size // total_kv_heads)
        unique_dst_head_idx = dst_tp_rank_in_group // dst_replication
        src_head_start = (unique_dst_head_idx * dst_heads_per_rank) % src_heads_per_rank
        num_heads_to_send = dst_heads_per_rank
        dst_head_start = 0

    return src_head_start, num_heads_to_send, dst_head_start, num_heads_to_send
