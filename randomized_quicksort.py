"""
Compare three Quicksort versions.

Randomized and first-pivot Quicksort use two-way partitioning. The
three-way version handles repeated values. All three limit stack depth by
recursing on the smaller side.

Run: python randomized_quicksort.py
"""

import random

import sys

import time

# ----------------------------------------------------------------------

# Partitioning

# ----------------------------------------------------------------------

def _partition(arr, low, high, counter=None):

    """Split the range around its last element and return the pivot index.

    Values through i are at most the pivot. Values from i+1 to j-1 are
    greater than the pivot.
    """

    pivot = arr[high]

    i = low - 1

    for j in range(low, high):

        if counter is not None:

            counter[0] += 1

        if arr[j] <= pivot:

            i += 1

            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]

    return i + 1

def _partition_3way(arr, low, high, counter=None):

    """Group values below, equal to, and above the pivot.

    Return the bounds of the equal group. The counter records one visit
    per loop, even when both < and > are tested.
    """

    pivot = arr[low]

    lt, i, gt = low, low + 1, high

    while i <= gt:

        if counter is not None:

            counter[0] += 1

        if arr[i] < pivot:

            arr[lt], arr[i] = arr[i], arr[lt]

            lt += 1

            i += 1

        elif arr[i] > pivot:

            arr[i], arr[gt] = arr[gt], arr[i]

            gt -= 1          # Check the swapped-in value next.

        else:

            i += 1

    return lt, gt

# ----------------------------------------------------------------------

# Sorts

# ----------------------------------------------------------------------

def randomized_quicksort(arr, counter=None):

    """Sort in place with a uniform random pivot in each subarray.

    Expected O(n log n) time for distinct keys; worst case O(n²).
    """

    if arr is None:

        raise TypeError("expected a list, got None")

    low, high = 0, len(arr) - 1

    while low < high:

        # Choose a random pivot and move it to the end.

        r = random.randint(low, high)

        arr[r], arr[high] = arr[high], arr[r]

        p = _partition(arr, low, high, counter)

        # Recurse on the smaller side to keep the stack short.

        # Loop over the larger side.

        if p - low < high - p:

            randomized_quicksort_range(arr, low, p - 1, counter)

            low = p + 1

        else:

            randomized_quicksort_range(arr, p + 1, high, counter)

            high = p - 1

    return arr

def randomized_quicksort_range(arr, low, high, counter=None):

    """Sort only arr[low:high+1] with random pivots."""

    while low < high:

        r = random.randint(low, high)

        arr[r], arr[high] = arr[high], arr[r]

        p = _partition(arr, low, high, counter)

        if p - low < high - p:

            randomized_quicksort_range(arr, low, p - 1, counter)

            low = p + 1

        else:

            randomized_quicksort_range(arr, p + 1, high, counter)

            high = p - 1

    return arr

def deterministic_quicksort(arr, counter=None):

    """Sort in place using the first element as the pivot.

    Sorted and reverse-sorted arrays take Θ(n²) time.
    """

    if arr is None:

        raise TypeError("expected a list, got None")

    _deterministic_range(arr, 0, len(arr) - 1, counter)

    return arr

def _deterministic_range(arr, low, high, counter=None):

    while low < high:

        # Move the first element to the pivot position.

        arr[low], arr[high] = arr[high], arr[low]

        p = _partition(arr, low, high, counter)

        if p - low < high - p:

            _deterministic_range(arr, low, p - 1, counter)

            low = p + 1

        else:

            _deterministic_range(arr, p + 1, high, counter)

            high = p - 1

def randomized_quicksort_3way(arr, counter=None):

    """Sort in place with random pivots and three-way partitioning."""

    if arr is None:

        raise TypeError("expected a list, got None")

    _three_way_range(arr, 0, len(arr) - 1, counter)

    return arr

def _three_way_range(arr, low, high, counter=None):

    while low < high:

        r = random.randint(low, high)

        arr[low], arr[r] = arr[r], arr[low]

        lt, gt = _partition_3way(arr, low, high, counter)

        # Equal values are finished. Sort only the other two groups.

        # Recurse on the smaller group.

        if lt - low < high - gt:

            _three_way_range(arr, low, lt - 1, counter)

            low = gt + 1

        else:

            _three_way_range(arr, gt + 1, high, counter)

            high = lt - 1

# ----------------------------------------------------------------------

# Correctness tests

# ----------------------------------------------------------------------

def run_tests():

    rng = random.Random(0)

    cases = {

        "empty": [],

        "single element": [42],

        "two elements": [2, 1],

        "all identical": [7] * 100,

        "two distinct values": [1, 0] * 50,

        "already sorted": list(range(200)),

        "reverse sorted": list(range(200, 0, -1)),

        "many duplicates": [rng.randint(0, 4) for _ in range(200)],

        "negatives and zero": [0, -5, 3, -5, 0, 9, -1],

        "floats": [0.5, -2.25, 3.0, 0.5],

        "strings": ["pear", "apple", "fig", "apple"],

        "random": [rng.randint(-1000, 1000) for _ in range(500)],

    }

    algorithms = [

        ("randomized", randomized_quicksort),

        ("deterministic", deterministic_quicksort),

        ("randomized 3-way", randomized_quicksort_3way),

    ]

    failures = 0

    for name, data in cases.items():

        for label, fn in algorithms:

            got = fn(data.copy())

            want = sorted(data)

            if got != want:

                print(f"  FAIL {label} on {name}")

                failures += 1

    # Check that no values were lost or added.

    data = [rng.randint(0, 50) for _ in range(1000)]

    for label, fn in algorithms:

        out = fn(data.copy())

        if sorted(out) != sorted(data):

            print(f"  FAIL {label}: output is not a permutation of the input")

            failures += 1

    # None must raise TypeError.

    for label, fn in algorithms:

        try:

            fn(None)

            print(f"  FAIL {label}: None did not raise")

            failures += 1

        except TypeError:

            pass

    print(f"Correctness: {len(cases)} edge cases x {len(algorithms)} algorithms"

          f" -> {'all passed' if failures == 0 else str(failures) + ' FAILURES'}\n")

    return failures == 0

# ----------------------------------------------------------------------

# Benchmarks

# ----------------------------------------------------------------------

def make_datasets(n, seed=42):

    rng = random.Random(seed)

    return {

        "Random": [rng.randint(0, 10 * n) for _ in range(n)],

        "Sorted": list(range(n)),

        "Reverse": list(range(n, 0, -1)),

        "Repeated": [rng.randint(0, 9) for _ in range(n)],  # ten possible values

    }

def time_sort(fn, data, repeats=3):

    """Return the fastest run in milliseconds.

    Copying the input is outside the timed section.
    """

    best = float("inf")

    for _ in range(repeats):

        working = data.copy()

        start = time.perf_counter()

        fn(working)

        best = min(best, time.perf_counter() - start)

    return best * 1000

def count_comparisons(fn, data):

    counter = [0]

    fn(data.copy(), counter)

    return counter[0]

def run_benchmarks(sizes=(1000, 2000, 4000, 8000)):

    algorithms = [

        ("Randomized", randomized_quicksort),

        ("Deterministic", deterministic_quicksort),

        ("Randomized 3-way", randomized_quicksort_3way),

    ]

    print("EXECUTION TIME (ms, best of 3)")

    print(f"{'n':>6} {'Distribution':<11} " +

          " ".join(f"{name:>17}" for name, _ in algorithms))

    print("-" * 78)

    for n in sizes:

        for label, data in make_datasets(n).items():

            row = [f"{time_sort(fn, data):17.2f}" for _, fn in algorithms]

            print(f"{n:>6} {label:<11} " + " ".join(row))

        print()

    print("COMPARISON COUNTS")

    print(f"{'n':>6} {'Distribution':<11} " +

          " ".join(f"{name:>17}" for name, _ in algorithms) +

          f" {'n lg n':>12}")

    print("-" * 92)

    import math

    for n in sizes:

        for label, data in make_datasets(n).items():

            row = [f"{count_comparisons(fn, data):17,}" for _, fn in algorithms]

            print(f"{n:>6} {label:<11} " + " ".join(row) +

                  f" {int(n * math.log2(n)):12,}")

        print()

if __name__ == "__main__":

    print()

    ok = run_tests()

    if not ok:

        sys.exit(1)

    run_benchmarks()
