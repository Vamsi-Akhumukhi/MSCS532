import random
import statistics
import time
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


# Sorting algorithms

def heapsort(data: List[Any]) -> List[Any]:
    """Sort data in place using a max-heap and return the same list."""
    n = len(data)

    def sift_down(root: int, heap_size: int) -> None:
        while True:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < heap_size and data[left] > data[largest]:
                largest = left
            if right < heap_size and data[right] > data[largest]:
                largest = right
            if largest == root:
                return

            data[root], data[largest] = data[largest], data[root]
            root = largest

    # Build a max-heap.
    for root in range(n // 2 - 1, -1, -1):
        sift_down(root, n)

    # Move the largest item to the end, then restore the heap.
    for end in range(n - 1, 0, -1):
        data[0], data[end] = data[end], data[0]
        sift_down(0, end)

    return data


def quicksort(data: List[Any], seed: Optional[int] = None) -> List[Any]:
    if len(data) < 2:
        return data

    rng = random.Random(seed)
    pending_ranges = [(0, len(data) - 1)]

    while pending_ranges:
        low, high = pending_ranges.pop()

        while low < high:
            pivot = data[rng.randrange(low, high + 1)]

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

            # Process the smaller side immediately to limit stack growth.
            if left_size < right_size:
                if right_range[0] < right_range[1]:
                    pending_ranges.append(right_range)
                low, high = left_range
            else:
                if left_range[0] < left_range[1]:
                    pending_ranges.append(left_range)
                low, high = right_range

    return data


def merge_sort(data: List[Any]) -> List[Any]:
    """Return a sorted copy of data using Merge Sort."""
    if len(data) < 2:
        return data.copy()

    auxiliary = [None] * len(data)

    def sort_range(start: int, end: int) -> None:
        if end - start <= 1:
            return

        middle = (start + end) // 2
        sort_range(start, middle)
        sort_range(middle, end)

        left = start
        right = middle
        output = start

        while left < middle and right < end:
            if data[left] <= data[right]:
                auxiliary[output] = data[left]
                left += 1
            else:
                auxiliary[output] = data[right]
                right += 1
            output += 1

        while left < middle:
            auxiliary[output] = data[left]
            left += 1
            output += 1

        while right < end:
            auxiliary[output] = data[right]
            right += 1
            output += 1

        for index in range(start, end):
            data[index] = auxiliary[index]

    result = data.copy()
    data[:] = result
    sort_range(0, len(data))
    return data


# Priority queue using a max-heap

@dataclass
class Task:
    task_id: str
    priority: int
    arrival_time: int
    deadline: int
    duration: int


class PriorityQueue:


    def __init__(self) -> None:
        self._heap: List[Task] = []
        self._positions = {}

    def _higher_priority(self, first: Task, second: Task) -> bool:
        if first.priority != second.priority:
            return first.priority > second.priority
        if first.arrival_time != second.arrival_time:
            return first.arrival_time < second.arrival_time
        return first.task_id < second.task_id

    def _swap(self, first_index: int, second_index: int) -> None:
        self._heap[first_index], self._heap[second_index] = (
            self._heap[second_index],
            self._heap[first_index],
        )
        self._positions[self._heap[first_index].task_id] = first_index
        self._positions[self._heap[second_index].task_id] = second_index

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if not self._higher_priority(self._heap[index], self._heap[parent]):
                break
            self._swap(index, parent)
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._heap)

        while True:
            highest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if (
                left < size
                and self._higher_priority(self._heap[left], self._heap[highest])
            ):
                highest = left

            if (
                right < size
                and self._higher_priority(self._heap[right], self._heap[highest])
            ):
                highest = right

            if highest == index:
                return

            self._swap(index, highest)
            index = highest

    def insert(self, task: Task) -> None:
        """Add a task. Task IDs must be unique in the queue."""
        if task.task_id in self._positions:
            raise ValueError(f"Task ID already exists: {task.task_id}")

        self._heap.append(task)
        index = len(self._heap) - 1
        self._positions[task.task_id] = index
        self._sift_up(index)

    def extract_max(self) -> Task:
        """Remove and return the task with the highest priority."""
        if self.is_empty():
            raise IndexError("Cannot extract from an empty priority queue")

        highest = self._heap[0]
        last = self._heap.pop()
        del self._positions[highest.task_id]

        if self._heap:
            self._heap[0] = last
            self._positions[last.task_id] = 0
            self._sift_down(0)

        return highest

    def increase_key(self, task_id: str, new_priority: int) -> None:
        """Increase a task's priority and restore the max-heap property."""
        if task_id not in self._positions:
            raise KeyError(f"Task not found: {task_id}")

        index = self._positions[task_id]
        if new_priority < self._heap[index].priority:
            raise ValueError("New priority is lower; use decrease_key instead")

        self._heap[index].priority = new_priority
        self._sift_up(index)

    def decrease_key(self, task_id: str, new_priority: int) -> None:
        """Decrease a task's priority and restore the max-heap property."""
        if task_id not in self._positions:
            raise KeyError(f"Task not found: {task_id}")

        index = self._positions[task_id]
        if new_priority > self._heap[index].priority:
            raise ValueError("New priority is higher; use increase_key instead")

        self._heap[index].priority = new_priority
        self._sift_down(index)

    def is_empty(self) -> bool:
        """Return True if the queue has no tasks."""
        return len(self._heap) == 0


# Scheduler simulation


def simulate_scheduler(tasks: List[Task]) -> List[dict]:
    """
    Run a non-preemptive priority scheduler.

    When the CPU becomes available, the scheduler selects the highest-priority
    task among those that have arrived. If no task is ready, time advances to
    the next arrival.
    """
    tasks_by_arrival = sorted(tasks, key=lambda task: task.arrival_time)
    ready_queue = PriorityQueue()
    results = []
    next_task_index = 0
    current_time = 0

    while next_task_index < len(tasks_by_arrival) or not ready_queue.is_empty():
        while (
            next_task_index < len(tasks_by_arrival)
            and tasks_by_arrival[next_task_index].arrival_time <= current_time
        ):
            ready_queue.insert(tasks_by_arrival[next_task_index])
            next_task_index += 1

        if ready_queue.is_empty():
            current_time = tasks_by_arrival[next_task_index].arrival_time
            continue

        task = ready_queue.extract_max()
        start_time = current_time
        finish_time = start_time + task.duration

        results.append(
            {
                "task_id": task.task_id,
                "priority": task.priority,
                "start": start_time,
                "finish": finish_time,
                "waiting": start_time - task.arrival_time,
                "deadline_missed": finish_time > task.deadline,
            }
        )

        current_time = finish_time

    return results


def print_scheduler_results() -> None:
    tasks = [
        Task("T1", priority=3, arrival_time=0, deadline=8, duration=4),
        Task("T2", priority=5, arrival_time=1, deadline=7, duration=3),
        Task("T3", priority=2, arrival_time=2, deadline=10, duration=2),
        Task("T4", priority=4, arrival_time=4, deadline=12, duration=3),
        Task("T5", priority=1, arrival_time=4, deadline=15, duration=1),
    ]

    results = simulate_scheduler(tasks)

    print("Priority queue scheduler simulation")
    print(f"{'Task':<8}{'Priority':<12}{'Start':<10}{'Finish':<10}"
          f"{'Waiting':<10}{'Deadline':<12}")
    print("-" * 62)

    for result in results:
        deadline_status = "Missed" if result["deadline_missed"] else "Met"
        print(
            f"{result['task_id']:<8}"
            f"{result['priority']:<12}"
            f"{result['start']:<10}"
            f"{result['finish']:<10}"
            f"{result['waiting']:<10}"
            f"{deadline_status:<12}"
        )


# Sorting benchmark


def make_datasets(size: int, seed: int) -> dict:
    rng = random.Random(seed)
    random_values = [rng.randrange(size * 10 + 1) for _ in range(size)]

    return {
        "Random": random_values,
        "Sorted": list(range(size)),
        "Reverse-sorted": list(range(size, 0, -1)),
        "Repeated values": [rng.randrange(8) for _ in range(size)],
    }


def median_runtime(sorter, values: List[int], repeats: int = 3) -> float:
    """Return the median runtime in seconds; input-copy time is excluded."""
    timings = []

    for run in range(repeats):
        data = values.copy()
        start = time.perf_counter()
        sorter(data, run)
        timings.append(time.perf_counter() - start)

    return statistics.median(timings)


def run_sorting_benchmarks() -> None:
    algorithms = {
        "Heapsort": lambda data, seed: heapsort(data),
        "Quicksort": lambda data, seed: quicksort(data, seed=seed),
        "Merge Sort": lambda data, seed: merge_sort(data),
    }

    sizes = [100, 500, 1000, 2000, 5000]

    print("Sorting benchmark (median of 3 runs)")
    print("Times are in milliseconds; input-copy time is excluded.")
    print()
    print(
        f"{'Input':<18}{'n':>7}"
        f"{'Heapsort':>14}{'Quicksort':>14}{'Merge Sort':>14}"
    )
    print("-" * 67)

    for size in sizes:
        datasets = make_datasets(size, seed=1000 + size)

        for name, values in datasets.items():
            times_ms = {
                algorithm_name: 1000 * median_runtime(sorter, values)
                for algorithm_name, sorter in algorithms.items()
            }

            print(
                f"{name:<18}{size:>7}"
                f"{times_ms['Heapsort']:>14.3f}"
                f"{times_ms['Quicksort']:>14.3f}"
                f"{times_ms['Merge Sort']:>14.3f}"
            )

        print()


if __name__ == "__main__":
    run_sorting_benchmarks()
    print()
    print_scheduler_results()