# Assignment 3: Algorithm Efficiency and Scalability

This project contains implementations of:

- Randomized Quicksort
- Deterministic Quicksort using the first element as the pivot
- A hash table with chaining for collision resolution

The script also benchmarks both sorting algorithms on random, sorted, reverse-sorted, and repeated-value arrays.

## Requirements

- Python 3
- No third-party packages

## Run the script

Open a terminal in the folder containing `assignment_3.py` and run:

    python3 assignment_3.py

The script prints a timing table comparing the two Quicksort implementations. It tests input sizes of 100, 500, 1,000, and 2,000, and reports the median of three runs for each case.

The hash table is implemented in the script but does not print output when the script runs. Its methods can be used from another Python file or in an interactive Python session.

## Hash table usage

    from assignment_3 import ChainedHashTable

    table = ChainedHashTable(seed=42)

    table.insert(101, "Alice")
    table.insert(202, "Bob")

    print(table.search(101))  # Alice

    deleted = table.delete(202)
    print(deleted)            # True
    print(table.search(202))  # None

Hash table keys must be integers. Values can be any Python object.

## Complexity summary

### Quicksort

- Randomized Quicksort expected time: O(n log n)
- Quicksort worst-case time: O(n²)
- First-element pivot on sorted or reverse-sorted data can produce the worst case

### Hash table with chaining

Let α be the load factor, or the number of entries divided by the number of buckets.

- Expected search, insert, and delete time: O(1 + α)
- Worst-case operation time: O(n), if many keys fall into the same bucket
- Resizing: O(n), because entries are reinserted into the new bucket array