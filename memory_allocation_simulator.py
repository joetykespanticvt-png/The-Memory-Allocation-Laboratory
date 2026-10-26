
"""
The Memory Allocation Laboratory
Operating Systems LEC — Midterm research output
Python 3

Modeling assumptions:
- Initial holes are separate regions and are not physically merged.
- Allocation requests use variable-sized blocks.
- Internal fragmentation is zero.
- A free process releases its exact allocated block.
- Adjacent free blocks within the same original hole
  are merged after deallocation.
"""

INITIAL_HOLES = [100, 500, 200, 300, 600]  # KB, in order

REQUESTS = [
    ("ALLOC", "P1", 212),
    ("ALLOC", "P2", 417),
    ("ALLOC", "P3", 112),
    ("ALLOC", "P4", 426),
    ("FREE", "P2", None),
    ("ALLOC", "P5", 200),
]


def run(strategy):
    # Each initial hole contains allocated/free blocks.
    regions = [
        [{"size": size, "pid": None}]
        for size in INITIAL_HOLES
    ]
    outcomes = []
    locations = {}

    for action, pid, size in REQUESTS:
        if action == "FREE":
            if pid not in locations:
                outcomes.append(
                    f"{pid}: deallocation failed "
                    "(process not allocated)"
                )
                continue

            region_index = locations.pop(pid)
            region = regions[region_index]

            block_index = next(
                i for i, block in enumerate(region)
                if block["pid"] == pid
            )

            region[block_index] = {
                "size": region[block_index]["size"],
                "pid": None
            }

            # Merge adjacent free blocks in this region.
            if (
                block_index > 0
                and region[block_index - 1]["pid"] is None
            ):
                region[block_index - 1]["size"] += (
                    region[block_index]["size"]
                )
                region.pop(block_index)
                block_index -= 1

            if (
                block_index + 1 < len(region)
                and region[block_index + 1]["pid"] is None
            ):
                region[block_index]["size"] += (
                    region[block_index + 1]["size"]
                )
                region.pop(block_index + 1)

            outcomes.append(f"{pid}: deallocated")
            continue

        candidates = []

        for region_index, region in enumerate(regions):
            for block_index, block in enumerate(region):
                if block["pid"] is None and block["size"] >= size:
                    candidates.append(
                        (block["size"], region_index, block_index)
                    )

        if not candidates:
            outcomes.append(
                f"{pid} ({size} KB): REJECTED — "
                "no single hole is large enough"
            )
            continue

        if strategy == "First-Fit":
            chosen = candidates[0]

        elif strategy == "Best-Fit":
            chosen = min(
                candidates,
                key=lambda candidate: candidate[0]
            )

        elif strategy == "Worst-Fit":
            chosen = max(
                candidates,
                key=lambda candidate: candidate[0]
            )

        else:
            raise ValueError(
                "Strategy must be First-Fit, Best-Fit, or Worst-Fit"
            )

        hole_size, region_index, block_index = chosen
        region = regions[region_index]

        region[block_index] = {
            "size": size,
            "pid": pid
        }

        if hole_size > size:
            region.insert(
                block_index + 1,
                {"size": hole_size - size, "pid": None}
            )

        locations[pid] = region_index

        outcomes.append(
            f"{pid} ({size} KB): allocated "
            f"from a {hole_size} KB hole"
        )

    free_holes = [
        block["size"]
        for region in regions
        for block in region
        if block["pid"] is None
    ]

    memory_map = []

    for index, region in enumerate(regions, start=1):
        parts = []

        for block in region:
            if block["pid"] is None:
                parts.append(f"Free {block['size']} KB")
            else:
                parts.append(
                    f"{block['pid']} {block['size']} KB"
                )

        memory_map.append(
            f"Initial hole {index}: " + " | ".join(parts)
        )

    total_free = sum(free_holes)
    largest_hole = max(free_holes, default=0)

    external_indicator = total_free - largest_hole

    return (
        outcomes,
        memory_map,
        total_free,
        largest_hole,
        external_indicator
    )


if __name__ == "__main__":
    for policy in ("First-Fit", "Best-Fit", "Worst-Fit"):
        (
            outcomes,
            memory_map,
            total_free,
            largest_hole,
            external_indicator
        ) = run(policy)

        print("\n" + "=" * 58)
        print(policy)

        print("Allocation sequence:")
        for outcome in outcomes:
            print("  " + outcome)

        print("Final memory map:")
        for line in memory_map:
            print("  " + line)

        print(f"Total free memory: {total_free} KB")
        print(f"Largest free hole: {largest_hole} KB")

        print(
            "External fragmentation indicator "
            f"(total free - largest hole): "
            f"{external_indicator} KB"
        )

        print(
            "Internal fragmentation: 0 KB "
            "(variable-sized allocation model)"
        )
