import random

from code_practice.catalog import get_catalog
from code_practice.content_solutions import ListNode
from code_practice.import_batch_012 import BATCH, PARTITION
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import compare, run_source


def test_linked_word_generators_and_deterministic_inputs_stay_in_source_domains():
    for pid, spec in BATCH.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for args in cases:
            if pid in (82, 86):
                values = args[0]
                assert len(values) <= (300 if pid == 82 else 200)
                assert all(-100 <= value <= 100 for value in values)
                if pid == 82:
                    assert values == sorted(values)
                else:
                    assert -200 <= args[1] <= 200
            else:
                text, words = args
                assert 1 <= len(text) <= (300 if pid == 139 else 20)
                assert set(text) <= set("abcdefghijklmnopqrstuvwxyz")
                assert 1 <= len(words) == len(set(words)) <= 1000
                assert all(1 <= len(word) <= (20 if pid == 139 else 10)
                           and set(word) <= set("abcdefghijklmnopqrstuvwxyz") for word in words)
                if pid == 140 and len(text) <= 9:
                    sentences = spec["oracle"](args)
                    assert len(sentences) <= 100000 and sum(map(len, sentences)) <= 100000
    for _, expected in BATCH[140]["stress"]:
        assert len(expected) <= 100000 and sum(map(len, expected)) <= 100000


def test_partition_reference_preserves_original_order_even_between_equal_values():
    nodes = [ListNode(value) for value in [2, 3, 2, 1, 3]]
    for first, second in zip(nodes, nodes[1:]):
        first.next = second
    namespace = {"ListNode": ListNode}
    exec(PARTITION, namespace)
    current = namespace["partition_list"](nodes[0], 3)
    returned = []
    while current:
        assert len(returned) < len(nodes)
        returned.append(current)
        current = current.next
    assert returned == [nodes[index] for index in (0, 2, 3, 1, 4)]
    problem = get_catalog()["leetcode-86"]
    assert problem.signature.node_policy == "reuse_input_nodes"
    assert review_focus_boost(problem) >= 60


def test_deleting_all_duplicate_nodes_is_not_keep_one_and_word_answers_are_complete():
    problem = get_catalog()["leetcode-82"]
    case = Case(id="remove-every-duplicate", arguments=[[1, 1, 2, 3, 3]], expected=[2])
    assert run_source(problem.reference_solution, problem, case) == (True, None)
    decision = get_catalog()["leetcode-139"]
    enumeration = get_catalog()["leetcode-140"]
    arguments = ["aaaa", ["a", "aa"]]
    sentences = BATCH[140]["oracle"](arguments)
    assert len(sentences) == 5 and "a a a a" in sentences
    assert run_source(decision.reference_solution, decision, Case(id="reused-word", arguments=arguments, expected=True)) == (True, None)
    assert run_source(enumeration.reference_solution, enumeration, Case(id="all-sentences", arguments=arguments, expected=sentences, comparator="unordered")) == (True, None)
    assert compare(sentences[::-1], sentences, "unordered")
    assert not compare(sentences[:1], sentences, "unordered")
    assert not compare(sentences + sentences[:1], sentences, "unordered")
    assert enumeration.difficulty >= 8 and review_focus_boost(enumeration) >= 50
    assert not prerequisites_met(enumeration, {"recursion": 69, "dynamic-programming": 100})
    assert prerequisites_met(enumeration, {"recursion": 70, "dynamic-programming": 70})
