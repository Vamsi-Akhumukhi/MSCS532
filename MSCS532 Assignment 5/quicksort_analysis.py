import random
import statistics
import time
from typing import List, Optional


def partition(values: List[int], low: int, high: int) -> int:
    """Partition values[low:high + 1] around the last item as the pivot."""
    pivot = values[high]
    smaller_boundary = low - 1

    for current in range(low, high):
        if values[current] <= pivot:
            smaller_boundary += 1
            values[smaller_boundary], values[current] = (
                values[current],
                values[smaller_boundary],
            )

    pivot_position = smaller_boundary + 1
    values[pivot_position], values[high] = values[high], values[pivot_position]
    return pivot_position


def quicksort_deterministic(values: List[int]) -> List[int]:
    """
    Sort values using Quicksort with the last item as the pivot.
    """

    def sort_range(low: int, high: int) -> None:
        while low < high:
            pivot_position = partition(values, low, high)

            left_size = pivot_position - low
            right_size = high - pivot_position

            # Recurse into the smaller partition and loop over the larger one.
            if left_size < right_size:
                sort_range(low, pivot_position - 1)
                low = pivot_position + 1
            else:
                sort_range(pivot_position + 1, high)
                high = pivot_position - 1

    sort_range(0, len(values) - 1)
    return values


def randomized_partition(
    values: List[int],
    low: int,
    high: int,
    rng: random.Random,
) -> int:
    """Choose a random pivot, move it to the end, and partition the subarray."""
    random_pivot_position = rng.randint(low, high)
    values[random_pivot_position], values[high] = (
        values[high],
        values[random_pivot_position],
    )
    return partition(values, low, high)


def quicksort_randomized(
    values: List[int],
    rng: Optional[random.Random] = None,
) -> List[int]:
    """
    Sort values using Quicksort with a randomly selected pivot.

    Pass a random.Random instance to make runs reproducible.
    """

    if rng is None:
        rng = random.Random()

    def sort_range(low: int, high: int) -> None:
        while low < high:
            pivot_position = randomized_partition(values, low, high, rng)

            left_size = pivot_position - low
            right_size = high - pivot_position

            # Recurse into the smaller partition and loop over the larger one.
            if left_size < right_size:
                sort_range(low, pivot_position - 1)
                low = pivot_position + 1
            else:
                sort_range(pivot_position + 1, high)
                high = pivot_position - 1

    sort_range(0, len(values) - 1)
    return values


def make_inputs(size: int, seed: int) -> dict[str, List[int]]:
    """Create the three input distributions used in the benchmark."""
    rng = random.Random(seed)
    random_values = [rng.randint(0, size * 10) for _ in range(size)]

    return {
        "Random": random_values,
        "Sorted": list(range(size)),
        "Reverse-sorted": list(range(size, 0, -1)),
    }


def median_runtime_ms(sort_function, source: List[int], repetitions: int = 3) -> float:
    """Return the median sort time in milliseconds; copying is not timed."""
    measurements = []

    for run in range(repetitions):
        values = source.copy()  # Keep input-copy time out of the measurement.

        if sort_function is quicksort_randomized:
            rng = random.Random(10_000 + run)
            start = time.perf_counter()
            sort_function(values, rng)
        else:
            start = time.perf_counter()
            sort_function(values)

        measurements.append((time.perf_counter() - start) * 1000)

    return statistics.median(measurements)


def run_benchmarks() -> None:
    sizes = [500, 1_000, 2_000, 4_000]
    repetitions = 3

    print(f"Median of {repetitions} runs; input-copy time is excluded.")
    print(
        f"{'Distribution':<18}"
        f"{'n':>8}"
        f"{'Deterministic (ms)':>22}"
        f"{'Randomized (ms)':>20}"
    )
    print("-" * 68)

    for size in sizes:
        inputs = make_inputs(size, seed=42 + size)

        for distribution, source in inputs.items():
            deterministic_ms = median_runtime_ms(
                quicksort_deterministic, source, repetitions
            )
            randomized_ms = median_runtime_ms(
                quicksort_randomized, source, repetitions
            )

            print(
                f"{distribution:<18}"
                f"{size:>8}"
                f"{deterministic_ms:>22.3f}"
                f"{randomized_ms:>20.3f}"
            )

        print()


if __name__ == "__main__":
    run_benchmarks()