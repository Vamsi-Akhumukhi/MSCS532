# Assignment 4: Heap Data Structures

This project implements Heapsort, an array-based priority queue using a max-heap, and a task scheduler simulation. It also compares Heapsort with randomized Quicksort and Merge Sort.

## Requirements

- Python 3
- No third-party packages

## Run the program

Open a terminal in the folder containing `assignment_4.py` and run:

    python3 assignment_4.py

The script prints:

1. A sorting benchmark for random, sorted, reverse-sorted, and repeated-value inputs, with sizes from 100 to 5,000.
2. A priority queue scheduler simulation showing each task’s priority, start time, finish time, waiting time, and deadline status.

Each benchmark timing is the median of three runs. The time to copy the input list for each run is excluded.

## Implementations

### Sorting algorithms

- **Heapsort** builds a max-heap, then repeatedly moves the maximum value to the end of the array. It sorts in place.
- **Quicksort** chooses a uniformly random pivot and uses three-way partitioning to group values below, equal to, and above the pivot.
- **Merge Sort** recursively divides the input, sorts each half, and merges the results.

### Priority queue and scheduler

The priority queue is an array-based max-heap. A higher numeric priority is selected first. For tasks with equal priority, the earlier arrival time is used as a tie-breaker, followed by the task ID.

Each task stores a task ID, priority, arrival time, deadline, and duration. The scheduler is non-preemptive: once a task starts, it runs until it finishes. When the CPU is free, the scheduler selects the highest-priority task that has arrived.

The priority queue supports:

- `insert(task)`
- `extract_max()`
- `increase_key(task_id, new_priority)`
- `decrease_key(task_id, new_priority)`
- `is_empty()`

## Complexity

| Algorithm or operation | Time complexity | Additional space |
|---|---:|---:|
| Heapsort, best/average/worst | O(n log n) | O(1) |
| Randomized Quicksort, expected | O(n log n) | Expected O(log n) stack |
| Randomized Quicksort, worst case | O(n²) | Depends on partitions |
| Merge Sort, best/average/worst | O(n log n) | O(n) |
| Priority queue insert | O(log n) | — |
| Priority queue extract maximum | O(log n) | — |
| Increase or decrease priority | O(log n) | — |
| Check whether queue is empty | O(1) | — |

## Benchmark findings

In the recorded run, all three sorting algorithms had similar runtimes on random inputs. At 5,000 elements, Quicksort took 5.785 ms, Merge Sort took 5.913 ms, and Heapsort took 7.068 ms.

Merge Sort was fastest on the sorted and reverse-sorted inputs at 5,000 elements. Quicksort was notably fast on repeated-value inputs: it took 0.777 ms at that size, compared with 5.355 ms for Heapsort and 5.278 ms for Merge Sort. Three-way partitioning helps Quicksort process equal values efficiently.

Timings can vary across computers and runs. The results show the behavior of these implementations in one run and are not universal performance guarantees.

## Scheduler findings

The simulation scheduled tasks in this order: T1, T2, T4, T3, and T5. T3 was the only task that missed its deadline. The average waiting time was 4.4 time units.