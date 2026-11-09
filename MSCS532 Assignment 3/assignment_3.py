import random
import statistics
import time
from typing import Any, List, Optional, Tuple


# Part 1: Randomized and deterministic Quicksort


def _quicksort(data: List[Any], randomized: bool, rng: random.Random) -> List[Any]:

    if len(data) < 2:
        return data

    pending_ranges = [(0, len(data) - 1)]

    while pending_ranges:
        low, high = pending_ranges.pop()

        while low < high:
            if randomized:
                pivot = data[rng.randrange(low, high + 1)]
            else:
                pivot = data[low]

            # Partition into values less than, equal to, and greater than pivot.
            less = low
            current = low
            greater = high

            while current <= greater:
                if data[current] < pivot:
                    data[less], data[current] = data[current], data[less]
                    less += 1
                    current += 1
                elif data[current] > pivot:
                    data[current], data[greater] = data[greater], data[current]
                    greater -= 1
                else:
                    current += 1

            left_range = (low, less - 1)
            right_range = (greater + 1, high)

            left_size = left_range[1] - left_range[0] + 1
            right_size = right_range[1] - right_range[0] + 1

            # Process the smaller range immediately and save the larger range.
            if left_size < right_size:
                if right_range[0] < right_range[1]:
                    pending_ranges.append(right_range)
                low, high = left_range
            else:
                if left_range[0] < left_range[1]:
                    pending_ranges.append(left_range)
                low, high = right_range

    return data


def randomized_quicksort(
    data: List[Any],
    seed: Optional[int] = None
) -> List[Any]:
    """Sort data in place using a uniformly random pivot."""
    return _quicksort(data, randomized=True, rng=random.Random(seed))


def deterministic_quicksort(data: List[Any]) -> List[Any]:
    """Sort data in place using the first element as the pivot."""
    return _quicksort(data, randomized=False, rng=random.Random())


# Part 2: Hash table with chaining

class ChainedHashTable:
    """
    Hash table for integer keys using separate chaining.

    Hash function:
        h(k) = ((a * k + b) mod p) mod table_size

    The coefficients a and b are selected randomly. The table resizes to
    maintain its load factor within the configured bounds.
    """

    _PRIME = (1 << 61) - 1

    def __init__(
        self,
        initial_capacity: int = 8,
        max_load_factor: float = 0.75,
        min_load_factor: float = 0.20,
        seed: Optional[int] = None
    ) -> None:
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be at least 1")
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be positive")
        if not 0 <= min_load_factor < max_load_factor:
            raise ValueError(
                "min_load_factor must be nonnegative and less than "
                "max_load_factor"
            )

        self._rng = random.Random(seed)
        self._max_load_factor = max_load_factor
        self._min_load_factor = min_load_factor
        self._minimum_capacity = initial_capacity
        self._buckets: List[List[Tuple[int, Any]]] = [
            [] for _ in range(initial_capacity)
        ]
        self._size = 0
        self._choose_hash_parameters()

    def _choose_hash_parameters(self) -> None:
        self._a = self._rng.randrange(1, self._PRIME)
        self._b = self._rng.randrange(0, self._PRIME)

    def _bucket_index(self, key: int) -> int:
        if not isinstance(key, int):
            raise TypeError("ChainedHashTable keys must be integers")

        return ((self._a * key + self._b) % self._PRIME) % len(self._buckets)

    @property
    def load_factor(self) -> float:
        """Return the number of stored keys divided by the number of buckets."""
        return self._size / len(self._buckets)

    def __len__(self) -> int:
        return self._size

    def insert(self, key: int, value: Any) -> None:
        """Add a key-value pair, or update the value if the key exists."""
        index = self._bucket_index(key)
        bucket = self._buckets[index]

        for position, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[position] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

        if self.load_factor > self._max_load_factor:
            self._resize(len(self._buckets) * 2)

    def search(self, key: int) -> Any:
        """Return the value for key, or None if the key is not present."""
        index = self._bucket_index(key)

        for existing_key, value in self._buckets[index]:
            if existing_key == key:
                return value

        return None

    def delete(self, key: int) -> bool:
        """Remove key and return True, or return False if it is not present."""
        index = self._bucket_index(key)
        bucket = self._buckets[index]

        for position, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[position]
                self._size -= 1

                if (
                    len(self._buckets) > self._minimum_capacity
                    and self.load_factor < self._min_load_factor
                ):
                    new_capacity = max(
                        self._minimum_capacity,
                        len(self._buckets) // 2
                    )
                    self._resize(new_capacity)

                return True

        return False

    def _resize(self, new_capacity: int) -> None:
        """Resize the bucket array and reinsert all stored key-value pairs."""
        old_entries = [
            item
            for bucket in self._buckets
            for item in bucket
        ]

        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        self._choose_hash_parameters()

        for key, value in old_entries:
            index = self._bucket_index(key)
            self._buckets[index].append((key, value))
            self._size += 1



# Part 1: Empirical sorting comparison

def _make_inputs(size: int, seed: int) -> dict:
    rng = random.Random(seed)
    random_values = [rng.randrange(size * 10 + 1) for _ in range(size)]

    return {
        "Random": random_values,
        "Sorted": list(range(size)),
        "Reverse-sorted": list(range(size, 0, -1)),
        "Repeated values": [rng.randrange(8) for _ in range(size)],
    }


def _median_sort_time(sort_function, values: List[int], repeats: int = 3) -> float:
    """Return median runtime in seconds, excluding the list-copy time."""
    timings = []

    for run in range(repeats):
        data = values.copy()
        start = time.perf_counter()
        sort_function(data, run)
        timings.append(time.perf_counter() - start)

    return statistics.median(timings)


def run_sort_benchmarks() -> None:
    print("Quicksort timing comparison (median of 3 runs)")
    print("Times are in milliseconds; list-copy time is excluded.")
    print()

    sizes = [100, 500, 1000, 2000]

    print(
        f"{'Input':<18} {'n':>6} "
        f"{'Randomized (ms)':>18} {'First-pivot (ms)':>18}"
    )
    print("-" * 66)

    for size in sizes:
        inputs = _make_inputs(size, seed=1000 + size)

        for name, values in inputs.items():
            randomized_ms = 1000 * _median_sort_time(
                lambda data, seed: randomized_quicksort(data, seed=seed),
                values
            )
            deterministic_ms = 1000 * _median_sort_time(
                lambda data, seed: deterministic_quicksort(data),
                values
            )

            print(
                f"{name:<18} {size:>6} "
                f"{randomized_ms:>18.3f} {deterministic_ms:>18.3f}"
            )

        print()


if __name__ == "__main__":
    run_sort_benchmarks()