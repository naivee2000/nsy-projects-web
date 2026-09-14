from __future__ import annotations

import re
from collections.abc import Iterable


LIST_NODE_DEFINITION = '''class ListNode:
    def __init__(self, val: int = 0, next: "ListNode | None" = None):
        self.val = val
        self.next = next
'''


TREE_NODE_DEFINITION = '''class TreeNode:
    def __init__(
        self,
        val: int = 0,
        left: "TreeNode | None" = None,
        right: "TreeNode | None" = None,
    ):
        self.val = val
        self.left = left
        self.right = right
'''


def with_support_classes(source: str, adapters: Iterable[str]) -> str:
    """Prepend the concrete node classes used by an adapted callable."""
    adapter_set = set(adapters)
    definitions: list[str] = []
    if adapter_set.intersection({"listnode", "listnode_ref"}) and not re.search(r"^class\s+ListNode\b", source, re.MULTILINE):
        definitions.append(LIST_NODE_DEFINITION)
    if adapter_set.intersection({"treenode", "treenode_ref", "treenode_value", "treenode_list"}) and not re.search(r"^class\s+TreeNode\b", source, re.MULTILINE):
        definitions.append(TREE_NODE_DEFINITION)
    if not definitions:
        return source
    return "# Data structure supplied to this problem.\n" + "\n\n".join(definitions) + "\n\n" + source
