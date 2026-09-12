"""Reviewed linked-list filtering/partitioning and recursive word segmentation."""
from collections import Counter

from .import_batch_003 import entry


def unique_nodes_oracle(args):
    counts = Counter(args[0])
    return [value for value in args[0] if counts[value] == 1]


def partition_oracle(args):
    values, pivot = args
    # Stable key sorting is independent of the reference's pointer queues.
    return sorted(values, key=lambda value: value >= pivot)


def sentences_oracle(args):
    text, dictionary = args
    words = set(dictionary)
    result = []
    # Every mask chooses a subset of the n-1 gaps as word boundaries.
    for mask in range(1 << (len(text) - 1)):
        start, pieces = 0, []
        for end in range(1, len(text) + 1):
            if end == len(text) or mask & (1 << (end - 1)):
                word = text[start:end]
                if word not in words:
                    break
                pieces.append(word)
                start = end
        else:
            result.append(" ".join(pieces))
    return result


def break_oracle(args):
    return bool(sentences_oracle(args))


def random_unique_nodes(rng):
    return [sorted(rng.randint(-10, 10) for _ in range(rng.randrange(61)))]


def random_partition(rng):
    return [[rng.randint(-100, 100) for _ in range(rng.randrange(61))], rng.randint(-200, 200)]


def random_words(rng):
    text = "".join(rng.choice("abc") for _ in range(rng.randint(1, 9)))
    words = {"".join(rng.choice("abc") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 10))}
    if rng.random() < .6:
        index = 0
        while index < len(text):
            end = min(len(text), index + rng.randint(1, 3))
            words.add(text[index:end])
            index = end
    return [text, sorted(words)]


UNIQUE = '''\
def delete_duplicate_nodes(head):
    dummy = ListNode(0, head)
    before = dummy
    while head:
        if head.next and head.val == head.next.val:
            value = head.val
            while head and head.val == value:
                head = head.next
            before.next = head
        else:
            before = head
            head = head.next
    return dummy.next
'''
KEEP_ONE = '''\
def delete_duplicate_nodes(head):
    current = head
    while current and current.next:
        if current.val == current.next.val:
            current.next = current.next.next
        else:
            current = current.next
    return head
'''
PARTITION = '''\
def partition_list(head, x):
    small, large = ListNode(), ListNode()
    low, high = small, large
    while head:
        following = head.next
        head.next = None
        if head.val < x:
            low.next = head
            low = head
        else:
            high.next = head
            high = head
        head = following
    low.next = large.next
    return small.next
'''
BREAK = '''\
def word_break(s, word_dict):
    words = set(word_dict)
    longest = max(map(len, word_dict))
    possible = [True] + [False] * len(s)
    for end in range(1, len(s) + 1):
        for start in range(max(0, end - longest), end):
            if possible[start] and s[start:end] in words:
                possible[end] = True
                break
    return possible[-1]
'''
GREEDY_BREAK = '''\
def word_break(s, word_dict):
    words = sorted(word_dict, key=len, reverse=True)
    index = 0
    while index < len(s):
        for word in words:
            if s.startswith(word, index):
                index += len(word)
                break
        else:
            return False
    return True
'''
SENTENCES = '''\
def word_break_sentences(s, word_dict):
    from functools import cache
    words = set(word_dict)
    longest = max(map(len, word_dict))
    @cache
    def build(start):
        if start == len(s):
            return [""]
        result = []
        for end in range(start + 1, min(len(s), start + longest) + 1):
            word = s[start:end]
            if word in words:
                for suffix in build(end):
                    result.append(word + (" " + suffix if suffix else ""))
        return result
    return build(0)
'''

WORD_CASES = [["a", ["a"]], ["a", ["b"]], ["aa", ["a"]], ["aa", ["aa"]],
              ["aaa", ["a", "aa"]], ["aaaa", ["a", "aa", "aaa"]], ["abcd", ["abc", "ab", "cd"]],
              ["catsandog", ["cats", "dog", "sand", "and", "cat"]], ["ab", ["a", "b", "ab"]],
              ["aba", ["ab", "a"]], ["abca", ["a", "bc"]], ["abc", ["ab", "bc"]]]

BATCH = {
    82: entry("delete_duplicate_nodes", [("head", "ListNode | None")], "ListNode | None", ["linked-lists", "two-pointers"],
        ["0–300 nodes sorted in nondecreasing order, with values from -100 to 100.",
         "Delete every node whose value occurs more than once, not just the extra copies. Return the remaining head, or None for an empty result."],
        [([[1, 2, 3, 3, 4, 4, 5]], "Both 3 nodes and both 4 nodes are removed, leaving 1→2→5."),
         ([[1, 1, 1, 2, 3]], "The duplicated run at the original head is entirely removed; return the node holding 2, followed by 3.")],
        [[values] for values in ([], [0], [1, 1], [1, 2], [1, 1, 2], [1, 2, 2], [1, 1, 2, 2],
                                 [-2, -2, -1, 0, 0, 1], [-100, 0, 100], [0, 0, 0], [1, 2, 3, 3], [1, 1, 2, 3, 4, 4])],
        UNIQUE, [KEEP_ONE, UNIQUE.replace("return dummy.next", "return head")],
        ["Keeps one node from each duplicated run instead of removing that value entirely.",
         "Returns the exhausted scanning pointer instead of the retained list's head."], unique_nodes_oracle, random_unique_nodes,
        ["Sorted input groups every occurrence of a value into one contiguous run.",
         "Keep a sentinel and a pointer immediately before the current run. Skip the entire run when it contains duplicates.",
         "If current equals its next node, scan past all equal values and reconnect before.next to the first different node; otherwise advance before.",
         "Do not advance the retained predecessor when removing a run, and return sentinel.next so head removals work."],
        "A sentinel handles deletion at the beginning without a special return case. The before pointer is the last retained node. A repeated value causes the scan to bypass its entire run while before stays put; a singleton becomes the new before. Reconnect only at those run boundaries. Every node is scanned once and no replacement result nodes are allocated. The independent oracle counts occurrences on the JSON values and retains only values with count one, distinguishing this from the original keep-one linked-list exercise.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([[0] * 300], [])]),
    86: entry("partition_list", [("head", "ListNode | None"), ("x", "int")], "ListNode | None", ["linked-lists", "two-pointers"],
        ["0–200 nodes with values from -100 to 100; -200<=x<=200.",
         "Reconnect the original nodes so values <x precede values >=x. Preserve original relative order within each partition, retain every node, and do not rewrite node values."],
        [([[1, 4, 3, 2, 5, 2], 3], "The lower partition is 1→2→2 and the other partition is 4→3→5; join them without sorting within either group."),
         ([[2, 1], 2], "The value equal to x belongs in the second group, so the result is 1→2.")],
        [[[], 0], [[1], 1], [[1], 2], [[1], 0], [[3, 1, 2], 3], [[3, 2, 1], 4],
         [[3, 2, 1], 0], [[2, 3, 2, 1], 2], [[0, -1, 0, -2], 0], [[1, 1, 1], 1],
         [[-100, 100, 0], -200], [[100, -100, 0], 200]], PARTITION,
        [PARTITION.replace("head.val < x", "head.val <= x"),
         PARTITION.replace("low.next = large.next\n    return small.next", "high.next = small.next\n    return large.next")],
        ["Groups values equal to x with the lower partition, changing their relative placement.",
         "Concatenates the greater-or-equal group before the less-than group."], partition_oracle, random_partition,
        ["Partitioning is not sorting; keep the encounter order within each group.",
         "Append nodes to two temporary chains with tail pointers, then connect the chains.",
         "Save the next pointer, detach the node, append to the <x or >=x tail, and continue with the saved pointer. Join the low chain to the high chain at the end.",
         "Detaching nodes prevents stale next pointers from creating a cycle or dragging nodes into the wrong group."],
        "Maintain sentinel heads and tails for two chains. Detach each visited node and append it to the appropriate tail. Appending, rather than prepending, preserves order. Joining the low tail to the high head handles empty groups naturally through the sentinels. The reference reconnects all original nodes exactly once without modifying their values; the judge checks node reuse as well as the output values. The oracle uses a stable sort on a Boolean group key, independently of pointer operations.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([[1, -1] * 100, 0], [-1] * 100 + [1] * 100)]),
    139: entry("word_break", [("s", "str"), ("word_dict", "list[str]")], "bool", ["strings", "dynamic-programming"],
        ["s has 1–300 lowercase letters. The dictionary contains 1–1000 distinct nonempty lowercase words, each at most 20 letters long.",
         "Use one or more dictionary words to cover all of s in order. Words may be reused; return only whether a complete segmentation exists."],
        [(["leetcode", ["leet", "code"]], "The complete split leet|code uses dictionary words, so return True."),
         (["applepenapple", ["apple", "pen"]], "Split apple|pen|apple. Reusing apple is permitted.")],
        WORD_CASES, BREAK, [GREEDY_BREAK, BREAK.replace("return possible[-1]", "return any(possible[1:])")],
        ["Always chooses the longest matching word, which can leave an impossible suffix.",
         "Accepts a segmentable prefix even when the entire string cannot be covered."], break_oracle, random_words,
        ["A successful first word does not guarantee that the remaining suffix can be segmented.",
         "Record which prefix lengths are reachable by complete dictionary words.",
         "Start with prefix length zero reachable. Mark end reachable if an earlier reachable start has s[start:end] in the dictionary; return reachability at len(s).",
         "Limit candidate word lengths by the longest dictionary word. Reusing a word requires no removal from the dictionary."],
        "A prefix of length end is segmentable exactly when some earlier segmentable prefix is followed by a dictionary word. Fill these reachability states left-to-right, considering only starts within the maximum dictionary-word length L. Set membership handles dictionary lookup; Python slicing and hashing make the conservative bound O(nL²), plus dictionary construction. The independent oracle enumerates all subsets of the string's gaps as potential cut positions on small inputs. The 300-character stress cases use directly established answers.",
        "O(nL² + dictionary characters)", "O(n + dictionary characters)", difficulty=5,
        stress=[(["a" * 300, ["a"]], True), (["a" * 299 + "b", ["a" * length for length in range(1, 21)]], False)]),
    140: entry("word_break_sentences", [("s", "str"), ("word_dict", "list[str]")], "list[str]", ["strings", "recursion", "backtracking", "dynamic-programming"],
        ["s has 1–20 lowercase letters. The dictionary contains 1–1000 distinct lowercase words, each 1–10 letters long.",
         "Return every complete segmentation as a sentence with single spaces between words and no leading/trailing space. Word reuse is allowed; answer order is unrestricted.",
         "The source guarantees answer length at most 100000. Do not return duplicate sentences, a partial prefix, or only the first valid answer."],
        [(["catsanddog", ["cat", "cats", "and", "sand", "dog"]], "Two splits work: cats|and|dog and cat|sand|dog, producing two complete sentences."),
         (["pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]], "The three sentences are pine apple pen apple, pineapple pen apple, and pine applepen apple; each covers the full string.")],
        WORD_CASES, SENTENCES,
        [SENTENCES.replace("return build(0)", "return build(0)[:1]"),
         SENTENCES.replace('result.append(word + (" " + suffix if suffix else ""))', 'if word not in suffix.split():\n                        result.append(word + (" " + suffix if suffix else ""))')],
        ["Stops after one valid segmentation rather than returning every sentence.",
         "Forbids reuse of a dictionary word within the same sentence."], sentences_oracle, random_words,
        ["Choosing a dictionary prefix leaves a smaller instance: all sentences for the remaining suffix.",
         "Use recursive suffix solving with memoization by starting position.",
         "For each matching next word, prepend it to every sentence from the suffix. At the end return one empty suffix so completed words form a sentence.",
         "Add a space only when the suffix is nonempty. Cache suffix results, but do not stop after the first successful branch."],
        "Recursively enumerate matching next words and combine each with every sentence available from its suffix. Caching by the starting index avoids solving identical suffixes repeatedly. The base case is a list containing an empty string, representing one completed choice, not an empty list representing failure. Depth is at most 20. Output generation can be exponential and must be included in complexity: if C is total text held across cached suffix sentences, the reference takes O(nL² + C + dictionary characters) time and O(C+n+dictionary characters) storage. The independent oracle enumerates cut masks, not recursive suffix combinations.",
        "O(nL² + cached/output text + dictionary characters)", "O(cached/output text + n + dictionary characters)", difficulty=8,
        stress=[(["a" * 20, ["aa"]], [" ".join(["aa"] * 10)]),
                (["a" * 19 + "b", ["a" * length for length in range(1, 11)]], [])]),
}

for pid in (82, 86):
    BATCH[pid]["params"][0] = ("head", "ListNode | None", "listnode")
    BATCH[pid]["adapter"] = "listnode"
BATCH[86]["node_policy"] = "reuse_input_nodes"
BATCH[140]["comparator"] = "unordered"
BATCH[140]["prerequisites"] = ["recursion", "dynamic-programming"]
