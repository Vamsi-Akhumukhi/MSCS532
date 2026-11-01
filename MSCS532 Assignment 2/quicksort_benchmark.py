import random
import time
import tracemalloc


def quick_sort(values):
    """Sort values in place using randomized three-way Quick Sort."""
    rng = random.Random(2026)

    def sort_range(low, high):
        while low < high:
            pivot = values[rng.randint(low, high)]

            # Partition into values below, equal to, and above the pivot.
            smaller = low
            current = low
            larger = high

            while current <= larger:
                if values[current] < pivot:
                    values[smaller], values[current] = (
                        values[current],
                        values[smaller],
                    )
                    smaller += 1
                    current += 1
                elif values[current] > pivot:
                    values[current], values[larger] = (
                        values[larger],
                        values[current],
                    )
                    larger -= 1
                else:
                    current += 1

            # Recurse into the smaller side and process the larger side
            # in the loop. This limits the recursion stack.
            left_size = smaller - low
            right_size = high - larger

            if left_size < right_size:
                sort_range(low, smaller - 1)
                low = larger + 1
            else:
                sort_range(larger + 1, high)
                high = smaller - 1

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

    print("Quick Sort benchmark")
    print(f"{'Dataset':<16} {'Items':>8} {'Time (seconds)':>16} {'Peak memory (MB)':>18}")

    for size in sizes:
        for dataset_name, data in make_datasets(size).items():
            elapsed, peak_mb = measure_sort(quick_sort, data)
            print(
                f"{dataset_name:<16} {size:>8} "
                f"{elapsed:>16.6f} {peak_mb:>18.4f}"
            )


if __name__ == "__main__":
    main()