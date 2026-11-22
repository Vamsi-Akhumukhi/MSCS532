# Assignment 6: Medians and Order Statistics & Elementary Data Structures

This project implements two selection algorithms and five elementary data
structures in Python.

## Requirements

- Python 3
- Python standard library only

## How to Run

Open the repository folder in VS Code and run this command in the terminal:

```bash
python3 assignment_6.py
```

The script first prints benchmark results for Median of Medians and Randomized
Quickselect. It then demonstrates the dynamic array, matrix, array-backed stack,
circular array queue, and singly linked list.

## Benchmark

The benchmark uses arrays of 1,000, 10,000, and 50,000 elements. At each size,
both algorithms select the lower median from random, sorted, reverse-sorted,
and duplicate-heavy inputs. Each reported time is the median of five trials
in milliseconds. Each algorithm's working copy is included in the timing,
while input generation and correctness checks are performed outside it.

## Summary of Findings

- Randomized Quickselect was faster in all 12 benchmark cases. On 50,000 random
  elements, it took 8.048 ms compared with 16.655 ms for Median of Medians.
- Both algorithms recorded their lowest times on duplicate-heavy inputs at
  every tested size. Three-way partitioning groups equal values in one pass.
- Median of Medians guarantees O(n) worst-case selection time. Randomized
  Quickselect takes O(n) expected time and O(n²) worst-case time.
- The dynamic array provides constant-time indexed access. The stack uses the
  end of the array for last-in, first-out operations, and the circular queue
  uses wraparound indexing for first-in, first-out operations without shifting
  elements during dequeue.
- The singly linked list supports constant-time insertion at either end.
  Deletion by value may require a linear search.

The accompanying report contains the complete benchmark table and the
complexity analysis for both parts.