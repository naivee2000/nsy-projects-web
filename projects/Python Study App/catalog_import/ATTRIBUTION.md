# Source provenance

The inventory preserves the owner's `LeetCode_Algorithm_Study_Guide_Through_4047.xlsx`
content. Its SHA-256 and worksheet row numbers appear in `ledger.json`.

Additional problem descriptions and Python implementation candidates in
`sources.jsonl` come from **Doocs and contributors, doocs/leetcode**, revision
`f85554a7ffaa91aeaae6f0ff9f9d0641731097ed`:
https://github.com/doocs/leetcode/tree/f85554a7ffaa91aeaae6f0ff9f9d0641731097ed

Each source record includes the precise reference URL and the original LeetCode
problem URL. The Doocs repository is distributed under Creative Commons
Attribution-ShareAlike 4.0 International; its license text is retained in
`SOURCE_LICENSE.txt`. The extracted source snapshot remains under that license.

Changes in this extraction: source documents are split into description HTML,
Python candidate code, topic tags, and statically inspected interface metadata;
workbook summaries/examples and audit decisions are associated by verified title
and source identifier. No candidate solution is automatically approved or run
by the study app. Reviewed reference solutions, independent oracles, tests, and
explanations are authored in `code_practice/import_batch_001.py` through
`code_practice/import_batch_023.py`. Linked-node policies and explicit-stack tree
implementations adapt the reviewed contracts to the app's isolated Python judge.
The reviewed 3Sum Closest statement corrects the workbook's compressed wording
to require distinct indices, consistent with the retained upstream description.
In-place contracts retain the upstream mutated-array and count/prefix behavior;
workbook underscore placeholders are ignored only beyond the returned prefix.
Text Justification's workbook example had collapsed spaces. Its visible output
is corrected to the retained upstream width-16 contract; the validation report
keeps the original sample, original/corrected outputs, rationale, and source URL.
In-place flattening/reordering contracts retain original nodes. Their test
metadata records required node order separately from value serialization, so
equal-valued nodes cannot hide incorrect rewiring.
Sorted-array/list BST conversions retain the upstream acceptance of multiple
balanced shapes. Their workbook trees and displayed complete-tree examples are
validated by inorder preservation and balance, not by serialized-shape equality.
Reverse Bits follows the retained revision's explicit even, nonnegative
signed-range input constraint; historical unsigned examples outside that domain
were not substituted for this source snapshot's tests.
