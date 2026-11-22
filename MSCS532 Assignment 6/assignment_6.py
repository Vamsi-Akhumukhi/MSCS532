import random
from statistics import median
from time import perf_counter


# Part 1: Selection algorithms


def _check_rank(values, k):
    """Validate the one-based rank and return its zero-based index."""
    if not isinstance(k, int) or not 1 <= k <= len(values):
        raise ValueError("k must be an integer between 1 and the number of elements")
    return k - 1


def _partition(values, left, right, pivot):
    """Group values below, equal to, and above the pivot in place.

    Return the inclusive bounds of the group equal to the pivot.
    """
    lower = current = left
    upper = right

    while current <= upper:
        if values[current] < pivot:
            values[lower], values[current] = values[current], values[lower]
            lower += 1
            current += 1
        elif values[current] > pivot:
            values[current], values[upper] = values[upper], values[current]
            upper -= 1
        else:
            current += 1

    return lower, upper


def _median_of_medians_select(values, left, right, target):
    """Select a zero-based index within an inclusive range in place."""
    while right - left + 1 > 5:
        median_end = left

        # Sort groups of at most five and move each median into the prefix.
        for start in range(left, right + 1, 5):
            end = min(start + 5, right + 1)
            values[start:end] = sorted(values[start:end])
            middle = start + (end - start) // 2
            values[median_end], values[middle] = values[middle], values[median_end]
            median_end += 1

        # Recursively select the median of the collected group medians.
        median_index = left + (median_end - left) // 2
        pivot = _median_of_medians_select(
            values, left, median_end - 1, median_index
        )

        lower, upper = _partition(values, left, right, pivot)
        if target < lower:
            right = lower - 1
        elif target > upper:
            left = upper + 1
        else:
            return pivot

    return sorted(values[left:right + 1])[target - left]


def deterministic_select(values, k):
    """Return the kth smallest value in worst-case O(n) time.

    The rank starts at 1, and duplicates count individually.
    A working copy preserves the original input.
    """
    target = _check_rank(values, k)
    working = list(values)
    return _median_of_medians_select(working, 0, len(working) - 1, target)


def randomized_select(values, k, rng=None):
    """Return the kth smallest value in expected O(n) time.

    The rank starts at 1, and duplicates count individually.
    A working copy preserves the original input.
    """
    target = _check_rank(values, k)
    working = list(values)
    if rng is None:
        rng = random

    left = 0
    right = len(working) - 1

    while left < right:
        pivot = working[rng.randrange(left, right + 1)]
        lower, upper = _partition(working, left, right, pivot)
        if target < lower:
            right = lower - 1
        elif target > upper:
            left = upper + 1
        else:
            return pivot

    return working[left]


def _benchmark_inputs(size, rng):
    """Generate four input distributions of the same size."""
    return (
        ("Random", rng.sample(range(size * 10), size)),
        ("Sorted", list(range(size))),
        ("Reverse-sorted", list(range(size - 1, -1, -1))),
        ("Many duplicates", [rng.randrange(10) for _ in range(size)]),
    )


def benchmark_selection(sizes=(1_000, 10_000, 50_000), trials=5):
    """Compare median runtimes across input sizes and distributions."""
    input_rng = random.Random(42)
    pivot_rng = random.Random(314)
    algorithms = (
        ("Deterministic", deterministic_select),
        ("Randomized", lambda values, k: randomized_select(values, k, pivot_rng)),
    )

    print(f"Part 1 | Selection benchmark (median of {trials} trials)")
    print("Times are in milliseconds and include each algorithm's input copy.")
    print("Input generation and correctness checks are outside the timed runs.")
    print(f"{'Input':<18}{'n':>8}{'k':>8}{'Deterministic':>17}{'Randomized':>15}")

    for size in sizes:
        k = (size + 1) // 2  # Lower median rank when the input size is even.
        timings = {}

        for trial in range(trials):
            # Alternate which algorithm runs first.
            order = algorithms if trial % 2 == 0 else algorithms[::-1]

            for distribution, values in _benchmark_inputs(size, input_rng):
                expected = sorted(values)[k - 1]
                results = timings.setdefault(
                    distribution, {"Deterministic": [], "Randomized": []}
                )

                for name, select in order:
                    start = perf_counter()
                    actual = select(values, k)
                    elapsed_ms = (perf_counter() - start) * 1_000

                    if actual != expected:
                        raise AssertionError(
                            f"{name} returned {actual}, expected {expected} "
                            f"for {distribution}, n={size}, k={k}"
                        )
                    results[name].append(elapsed_ms)

        for distribution, results in timings.items():
            print(
                f"{distribution:<18}{size:>8,}{k:>8,}"
                f"{median(results['Deterministic']):>17.3f}"
                f"{median(results['Randomized']):>15.3f}"
            )


# Part 2: Elementary data structures


class DynamicArray:
    """A resizable array that manages its own size, capacity, and shifts."""

    def __init__(self):
        self._storage = [None] * 4
        self._size = 0

    def __len__(self):
        return self._size

    def _check_index(self, index):
        if not 0 <= index < self._size:
            raise IndexError("array index out of range")

    def __getitem__(self, index):
        self._check_index(index)
        return self._storage[index]

    def __setitem__(self, index, value):
        self._check_index(index)
        self._storage[index] = value

    def insert(self, index, value):
        """Insert at a zero-based position, shifting later values right."""
        if not 0 <= index <= self._size:
            raise IndexError("array insertion index out of range")

        if self._size == len(self._storage):
            new_storage = [None] * (2 * len(self._storage))
            for i in range(self._size):
                new_storage[i] = self._storage[i]
            self._storage = new_storage

        for i in range(self._size, index, -1):
            self._storage[i] = self._storage[i - 1]

        self._storage[index] = value
        self._size += 1

    def append(self, value):
        """Add a value at the end in amortized O(1) time."""
        self.insert(self._size, value)

    def delete(self, index):
        """Remove and return a value, shifting later values left."""
        value = self[index]
        for i in range(index, self._size - 1):
            self._storage[i] = self._storage[i + 1]

        self._size -= 1
        self._storage[self._size] = None
        return value

    def __iter__(self):
        for i in range(self._size):
            yield self._storage[i]


class Matrix:
    """A rectangular matrix with a fixed column count and resizable rows."""

    def __init__(self, columns):
        if columns < 1:
            raise ValueError("a matrix must have at least one column")
        self._columns = columns
        self._rows = DynamicArray()

    @property
    def shape(self):
        """Return the number of rows and columns."""
        return len(self._rows), self._columns

    def get(self, row, column):
        """Read a cell at zero-based coordinates."""
        return self._rows[row][column]

    def set(self, row, column, value):
        """Update a cell at zero-based coordinates."""
        self._rows[row][column] = value

    def insert_row(self, index, values):
        """Insert a row with exactly the configured number of columns."""
        row_values = list(values)
        if len(row_values) != self._columns:
            raise ValueError("row width must match the matrix column count")

        row = DynamicArray()
        for value in row_values:
            row.append(value)
        self._rows.insert(index, row)

    def delete_row(self, index):
        """Remove and return a row as a list."""
        return list(self._rows.delete(index))

    def to_list(self):
        """Return the matrix as a nested list for display."""
        return [list(row) for row in self._rows]


class ArrayStack:
    """A last-in, first-out stack backed by a dynamic array."""

    def __init__(self):
        self._items = DynamicArray()

    def __len__(self):
        return len(self._items)

    def push(self, value):
        """Place a value on top of the stack."""
        self._items.append(value)

    def peek(self):
        """Read the top value without removing it."""
        if len(self) == 0:
            raise IndexError("peek from an empty stack")
        return self._items[len(self) - 1]

    def pop(self):
        """Remove and return the top value."""
        if len(self) == 0:
            raise IndexError("pop from an empty stack")
        return self._items.delete(len(self) - 1)


class ArrayQueue:
    """A first-in, first-out queue backed by a resizable circular array."""

    def __init__(self):
        self._storage = [None] * 4
        self._front = 0
        self._size = 0

    def __len__(self):
        return self._size

    def enqueue(self, value):
        """Add a value at the back in amortized O(1) time."""
        capacity = len(self._storage)

        if self._size == capacity:
            new_storage = [None] * (2 * capacity)
            # Copy elements in queue order, including any that wrapped around.
            for i in range(self._size):
                new_storage[i] = self._storage[(self._front + i) % capacity]
            self._storage = new_storage
            self._front = 0
            capacity = len(self._storage)

        back = (self._front + self._size) % capacity
        self._storage[back] = value
        self._size += 1

    def peek(self):
        """Read the front value without removing it."""
        if self._size == 0:
            raise IndexError("peek from an empty queue")
        return self._storage[self._front]

    def dequeue(self):
        """Remove and return the front value in O(1) time."""
        if self._size == 0:
            raise IndexError("dequeue from an empty queue")

        value = self._storage[self._front]
        self._storage[self._front] = None
        self._front = (self._front + 1) % len(self._storage)
        self._size -= 1
        return value


class _Node:
    """A singly linked list node."""

    def __init__(self, value):
        self.value = value
        self.next = None


class SinglyLinkedList:
    """A singly linked list with constant-time insertion at either end."""

    def __init__(self):
        self._head = None
        self._tail = None

    def prepend(self, value):
        """Insert a value at the front."""
        node = _Node(value)
        node.next = self._head
        self._head = node

        if self._tail is None:
            self._tail = node

    def append(self, value):
        """Insert a value at the back."""
        node = _Node(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node

    def delete(self, value):
        """Delete the first matching value and return whether it was found."""
        previous = None
        current = self._head

        while current is not None:
            if current.value == value:
                if previous is None:
                    self._head = current.next
                else:
                    previous.next = current.next

                if current is self._tail:
                    self._tail = previous
                return True

            previous = current
            current = current.next

        return False

    def __iter__(self):
        """Traverse the list from head to tail."""
        current = self._head
        while current is not None:
            yield current.value
            current = current.next


def demonstrate_data_structures():
    """Show how each data structure stores and removes values."""
    print("\nPart 2 | Data structure demonstrations")

    array = DynamicArray()
    array.append(10)
    array.append(30)
    array.insert(1, 20)
    print(f"Array: {list(array)}, index 1 = {array[1]}")
    removed = array.delete(0)
    print(f"Array: deleted {removed}, remaining = {list(array)}")

    matrix = Matrix(3)
    matrix.insert_row(0, [1, 2, 3])
    matrix.insert_row(1, [4, 5, 6])
    matrix.set(1, 0, 40)
    print(f"Matrix: {matrix.to_list()}, cell (1, 0) = {matrix.get(1, 0)}")
    removed_row = matrix.delete_row(0)
    print(f"Matrix: deleted {removed_row}, remaining = {matrix.to_list()}")

    stack = ArrayStack()
    stack.push("first")
    stack.push("second")
    print(f"Stack: top = {stack.peek()}, pop order = {[stack.pop(), stack.pop()]}")

    queue = ArrayQueue()
    queue.enqueue("first")
    queue.enqueue("second")
    print(
        f"Queue: front = {queue.peek()}, "
        f"dequeue order = {[queue.dequeue(), queue.dequeue()]}"
    )

    linked = SinglyLinkedList()
    linked.append(20)
    linked.prepend(10)
    linked.append(30)
    print(f"Linked list traversal: {list(linked)}")
    linked.delete(20)
    print(f"Linked list after deleting 20: {list(linked)}")


if __name__ == "__main__":
    benchmark_selection()
    demonstrate_data_structures()