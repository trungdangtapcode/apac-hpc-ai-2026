#!/usr/bin/env python3
"""Small CPU-only reproduction of pinned MetadataBuffers row byte widths.

This models the source shapes and `buf[0].nbytes`; it allocates no tensors and
does not claim to observe a live server's pointers or tensor strides.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Buffer:
    name: str
    row_items: int
    item_bytes: int

    @property
    def row_bytes(self) -> int:
        return self.row_items * self.item_bytes


def source_order(
    *,
    slots: int,
    hidden_size: int,
    hidden_item_bytes: int,
    max_top_logprobs_num: int = 128,
    sampling_mask: bool = False,
    max_sampling_mask_tokens: int = 0,
    dsa_indices_dim: int = 0,
) -> list[Buffer]:
    """Mirror MetadataBuffers.__init__/get_buf_infos order from pinned source."""
    del slots  # Allocation count affects data_lens, not one-row item_lens.
    buffers = [
        Buffer("output_ids", 16, 4),
        Buffer("cached_tokens", 16, 4),
        Buffer("output_token_logprobs_val", 16, 4),
        Buffer("output_token_logprobs_idx", 16, 4),
        Buffer("output_top_logprobs_val", max_top_logprobs_num, 4),
        Buffer("output_top_logprobs_idx", max_top_logprobs_num, 4),
    ]
    if sampling_mask:
        if max_sampling_mask_tokens <= 0:
            raise ValueError("enabled sampling mask requires positive width")
        buffers.extend(
            [
                Buffer("output_token_sampling_mask_len", 16, 4),
                Buffer("output_token_sampling_mask_idx", max_sampling_mask_tokens, 4),
                Buffer("output_token_sampling_logprobs", 16, 4),
            ]
        )
    buffers.extend(
        [
            Buffer("output_topk_p", 16, 4),
            Buffer("output_topk_index", 16, 8),
            Buffer("output_hidden_states", hidden_size, hidden_item_bytes),
        ]
    )
    if dsa_indices_dim > 0:
        buffers.append(Buffer("output_dsa_topk_indices", dsa_indices_dim, 4))
    buffers.append(Buffer("bootstrap_room", 8, 8))
    return buffers


def main() -> None:
    # Run 223788 configured max_running_requests=48. Pinned scheduler source
    # allocates 2x headroom on the prefill side, so the independent row count
    # is 96. The recurrent hidden-state width/dtype is a runtime model property;
    # 4096 x BF16 is shown as a conditional candidate, not a collected value.
    buffers = source_order(
        slots=96,
        hidden_size=4096,
        hidden_item_bytes=2,
        sampling_mask=False,
        dsa_indices_dim=0,
    )
    print("order,name,expected_item_bytes,expected_region_bytes_at_96_slots")
    for index, buffer in enumerate(buffers):
        print(f"{index},{buffer.name},{buffer.row_bytes},{buffer.row_bytes * 96}")
    assert [b.row_bytes for b in buffers] == [64, 64, 64, 64, 512, 512, 64, 128, 8192, 64]
    assert [b.row_bytes * 96 for b in buffers] == [
        6144,
        6144,
        6144,
        6144,
        49152,
        49152,
        6144,
        12288,
        786432,
        6144,
    ]
    print("PASS: source-shaped CPU fixture matches the retained aggregate lengths")

    # Role-asymmetry scenario for the pinned decode builder. 223055 records
    # max_running_requests=256 on D, while its actual req_to_token_pool.size
    # was not retained. The decode rule is 2 * req_to_token_pool.size for this
    # non-MiniMax model; 512 is the scenario if that pool size is 256.
    source_slots = 96
    destination_pool_slots = 256  # scenario input, not claimed as observed
    destination_slots = 2 * destination_pool_slots
    assert len(buffers) == 10  # declared source list count per role by source
    src_bytes = [buffer.row_bytes * source_slots for buffer in buffers]
    dst_bytes = [buffer.row_bytes * destination_slots for buffer in buffers]
    assert len(src_bytes) == len(dst_bytes) == 10

    for src_index, dst_index, label in [
        (0, 0, "first legal slots"),
        (source_slots - 1, destination_slots - 1, "last/highest legal slots"),
    ]:
        for buffer, src_len, dst_len in zip(buffers, src_bytes, dst_bytes):
            src_offset = buffer.row_bytes * src_index
            dst_offset = buffer.row_bytes * dst_index
            assert src_offset + buffer.row_bytes <= src_len
            assert dst_offset + buffer.row_bytes <= dst_len
        print(
            f"PASS: {label}: source slot {src_index}/{source_slots}, "
            f"destination slot {dst_index}/{destination_slots}, "
            "10 descriptor bounds fit under the equal-row-width scenario"
        )
    print(
        "NOTE: bounds arithmetic does not establish observed pool size, "
        "runtime tensor alignment/stride, or NIXL transfer success"
    )


if __name__ == "__main__":
    main()
