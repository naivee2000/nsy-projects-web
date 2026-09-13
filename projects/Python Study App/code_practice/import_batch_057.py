"""Bit-DP workbook import kept separate from pending tree-interface work."""
from .import_batch_003 import entry


def oracle(args):
    return sum("11" not in bin(value) for value in range(args[0] + 1))


def generator(rng): return [rng.randint(0, 20_000)]


REFERENCE = '''\
def count_without_consecutive_ones(n):
    counts = [1, 2]
    for _ in range(2, 32):
        counts.append(counts[-1] + counts[-2])
    answer = 0
    previous = 0
    for bit in range(30, -1, -1):
        if n & (1 << bit):
            answer += counts[bit]
            if previous:
                return answer
            previous = 1
        else:
            previous = 0
    return answer + 1
'''


BATCH = {
    600: entry('count_without_consecutive_ones', [('n', 'int')], 'int', ['dynamic-programming', 'bit-manipulation'],
        ['0 <= n <= 10^9.', 'Count every integer in the inclusive range 0 through n whose binary representation contains no adjacent 1 bits.'],
        [([5], '0, 1, 2, 4, and 5 have no consecutive ones, for five values.'), ([1], 'Both 0 and 1 are valid in the inclusive range.')],
        [[0], [2], [3], [4], [6], [7], [8], [10], [15], [21], [100], [1_000], [100_000]], REFERENCE,
        [REFERENCE.replace('answer += counts[bit]', 'answer += 1'), REFERENCE.replace('return answer + 1', 'return answer')],
        ['Counts only one completion after each set bit.', 'Forgets to include n itself when it is valid.'], oracle, generator,
        ['The valid binary strings of each length follow a Fibonacci recurrence.', 'Scan n from high bit to low bit, counting valid smaller prefixes whenever n has a 1.', 'Precompute counts[k]=counts[k-1]+counts[k-2]; add counts[bit] for each set bit and stop on 11.', 'At a set bit, choosing zero yields every valid shorter suffix. Choosing one continues only if the preceding prefix did not already end in one, which gives the Fibonacci count and the early stop.'],
        'Let counts[k] be the number of length-k bit suffixes with no consecutive ones, including leading zeros. The two possible starting bits yield counts[k]=counts[k-1]+counts[k-2]. While reading n, every set bit permits a smaller prefix by selecting zero and then any valid suffix. A second consecutive set bit means the exact prefix is invalid, so no larger suffix can repair it. If the scan completes, n itself is valid and is included. The independent oracle enumerates small seeded values directly; the same reference is never used as its oracle.',
        'O(number of bits)', 'O(number of bits)', 6),
}
