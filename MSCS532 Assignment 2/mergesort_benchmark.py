import random
import time
import tracemalloc


def merge_sort(values):
    """Sort values in place using recursive Merge Sort."""

    def sort_range(low, high):
        if low >= high:
            return

        middle = (low + high) // 2
        sort_range(low, middle)
        sort_range(middle + 1, high)

        # Merge the two sorted halves into a temporary list.
        merged = []
        left = low
        right = middle + 1

        while left <= middle and right <= high:
            if values[left] <= values[right]:
                merged.append(values[left])
                left += 1
            else:
                merged.append(values[right])
                right += 1

        while left <= middle:
            merged.append(values[left])
            left += 1

        while right <= high:
            merged.append(values[right])
            right += 1

        values[low : high + 1] = merged

    sort_range(0, len(values) - 1)
    return values


def make_datasets(size):
    rng = random.Random(2026)

    return {
        "Sorted": list(range(size)),
        "Reverse sorted": list(range(size, 0, -1)),
        "Random": [rng.randint(0, size * 10) for _ in range(size)],
    }


def measure_sort(sort_function, original):
    # Make the input copy before measuring, so the reported memory is
    # for the sort itself rather than the copied input list.
    values = original.copy()

    tracemalloc.start()
    start_time = time.perf_counter()

    sort_function(values)

    elapsed_seconds = time.perf_counter() - start_time
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if values != sorted(original):
        raise ValueError("The sort did not produce the expected result.")

    return elapsed_seconds, peak_bytes / (1024 * 1024)


def main():
    sizes = [1_000, 5_000, 10_000]

    print("Merge Sort benchmark")
    print(f"{'Dataset':<16} {'Items':>8} {'Time (seconds)':>16} {'Peak memory (MB)':>18}")

    for size in sizes:
        for dataset_name, data in make_datasets(size).items():
            elapsed, peak_mb = measure_sort(merge_sort, data)
            print(
                f"{dataset_name:<16} {size:>8} "
                f"{elapsed:>16.6f} {peak_mb:>18.4f}"
            )


if __name__ == "__main__":
    main()