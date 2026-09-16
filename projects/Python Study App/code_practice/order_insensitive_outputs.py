"""Reviewed output-order policy for workbook problems whose source permits any order."""

ORDER_INSENSITIVE_COMPARATORS = {
    582: "unordered",
    599: "unordered",
    797: "unordered",
    890: "unordered",
    1110: "unordered",
    1125: "unordered",
    1233: "unordered",
    1408: "unordered",
    1447: "unordered",
    1489: "unordered_rows",
    1606: "unordered",
    1943: "unordered",
    1992: "unordered",
    2015: "unordered",
    2100: "unordered",
    2456: "unordered",
    2942: "unordered",
    2951: "unordered",
    2961: "unordered",
    3289: "unordered",
    3310: "unordered",
    3955: "unordered",
}


CONSTRAINT_REPLACEMENTS = {
    582: {
        "ppid[i] is the parent of pid[i], with 0 for the root. Return descendants in breadth-first input-child order.":
        "ppid[i] is the parent of pid[i], with 0 for the root. Return every killed process ID in any order.",
    },
    599: {
        "Return every common string with the smallest combined index sum in list1 order.":
        "Return every common string with the smallest combined index sum in any order.",
    },
    890: {
        "Return matching words in input order.": "Return all matching words in any order.",
    },
    1110: {
        "Return surviving trees as level-order lists in root-discovery order.":
        "Return the surviving trees in any order; each individual tree remains a level-order list.",
    },
    1125: {
        "Return the lexicographically smallest index list among minimum-size teams.":
        "Return the indices of a minimum-size sufficient team in any order.",
    },
    1447: {
        "Order by increasing denominator, then numerator.":
        "Return every qualifying reduced fraction in any order.",
    },
    1408: {
        "Words are distinct; preserve input order.":
        "Words are distinct; qualifying words may be returned in any order.",
    },
    1489: {
        "Return [critical_indices, pseudo_critical_indices], each in increasing input-index order.":
        "Return [critical_indices, pseudo_critical_indices]; indices inside either category may be in any order.",
    },
    1606: {
        "Return every server handling the maximum number of requests, in increasing index order.":
        "Return every server handling the maximum number of requests in any order.",
    },
    1943: {
        "Return minimal nonoverlapping half-open intervals with positive mixed color sum, in increasing coordinate order.":
        "Return the minimal nonoverlapping half-open intervals with positive mixed color sum in any order.",
    },
    2100: {
        "Return all good indices in increasing order.": "Return all good indices in any order.",
    },
    2456: {
        "Break a creator’s video-view tie using the lexicographically smallest id; results follow creator first-appearance order.":
        "Break a creator’s video-view tie using the lexicographically smallest id; tied creator/id pairs may be returned in any order.",
    },
    2942: {
        "Indices must be returned in increasing order.": "Qualifying indices may be returned in any order.",
    },
    2951: {
        "Return all peak indices in increasing order.": "Return all peak indices in any order.",
    },
    3289: {
        "Return the two repeated values in increasing order.":
        "Return the two repeated values in either order.",
    },
    3955: {
        "Its cost is the sum of zero-based indices containing one; return every valid string with cost at most k in lexicographic order.":
        "Its cost is the sum of zero-based indices containing one; return every valid string with cost at most k in any order.",
    },
}


def apply_order_insensitive_outputs(batch):
    for source_id, comparator in ORDER_INSENSITIVE_COMPARATORS.items():
        spec = batch[source_id]
        spec["comparator"] = comparator
        replacements = CONSTRAINT_REPLACEMENTS.get(source_id, {})
        spec["constraints"] = [replacements.get(value, value) for value in spec["constraints"]]
    sneaky = batch[3289]
    sneaky["wrong"][0] = sneaky["reference"].replace(
        "if value in seen:", "if value in seen and value:"
    )
    sneaky["wrong_reasons"][0] = "Treats duplicated zero as false and omits it from the answer."
