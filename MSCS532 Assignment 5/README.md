# Quicksort Implementation and Analysis

This project implements and compares deterministic and randomized versions of Quicksort in Python.

## Files

- `quicksort_analysis.py` — contains both sorting implementations and the benchmarking code.

## Requirements

- Python 3
- No external packages are required

## Run the program

Open a terminal in the project folder and run:

```bash
python3 quicksort_analysis.py
```

The program compares both versions on random, sorted, and reverse-sorted inputs of 500, 1,000, 2,000, and 4,000 items. It prints the median runtime from three runs for each input. Input-copy time is excluded from the measurements.

## Implementations

- **Deterministic Quicksort** selects the last item in each subarray as the pivot.
- **Randomized Quicksort** selects a random item in each subarray as the pivot.

Both versions sort the list in place. They recursively process the smaller partition and use a loop for the larger partition to limit call-stack growth.

## Complexity

| Case | Deterministic Quicksort | Randomized Quicksort |
|---|---|---|
| Best | O(n log n) | O(n log n) |
| Average / expected | O(n log n) | O(n log n) |
| Worst | O(n²) | O(n²) |

Randomization makes repeatedly unbalanced partitions unlikely, but it does not eliminate the theoretical worst case.

## Benchmark Results

Times are in milliseconds. Each value is the median of three runs; input-copy time is excluded.

| Distribution | n | Deterministic | Randomized |
|---|---:|---:|---:|
| Random | 500 | 0.205 | 0.281 |
| Sorted | 500 | 4.242 | 0.278 |
| Reverse-sorted | 500 | 3.863 | 0.289 |
| Random | 1,000 | 0.498 | 0.632 |
| Sorted | 1,000 | 17.607 | 0.595 |
| Reverse-sorted | 1,000 | 12.996 | 0.601 |
| Random | 2,000 | 1.056 | 1.362 |
| Sorted | 2,000 | 72.907 | 1.189 |
| Reverse-sorted | 2,000 | 51.770 | 1.299 |
| Random | 4,000 | 2.292 | 2.892 |
| Sorted | 4,000 | 303.532 | 2.677 |
| Reverse-sorted | 4,000 | 208.057 | 2.742 |

## Findings

On random inputs, both implementations had similar scaling. At 4,000 items, deterministic Quicksort took 2.292 ms and randomized Quicksort took 2.892 ms. The deterministic version was faster in these runs, while randomized pivot selection added some overhead.

The ordered inputs exposed the deterministic version’s weakness. At 4,000 items, it took 303.532 ms on sorted data and 208.057 ms on reverse-sorted data. Randomized Quicksort took 2.677 ms and 2.742 ms on those same inputs.

These results are consistent with the theory: choosing the last item as the pivot repeatedly creates unbalanced partitions for sorted and reverse-sorted inputs, leading toward O(n²) behavior. Random pivot selection avoided that pattern in these runs and performed much closer to the expected O(n log n) behavior.