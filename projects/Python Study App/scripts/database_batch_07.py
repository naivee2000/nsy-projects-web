from copy import deepcopy
from datetime import date, timedelta


def inputs(k, i, r, seed):
    t = deepcopy(seed)

    def day(j):
        return (date(2023, 1, 1) + timedelta(days=j)).isoformat()

    if k == 2480:
        return {
            "Elements": [("Na", "Metal", 1), ("Cl", "Nonmetal", 7), ("He", "Noble", 2)]
            + [(f"M{j}", "Metal", 2 + j) for j in range(i)]
        }
    if k == 2494:
        return {
            "HallEvents": [
                (1, day(1), day(10)),
                (1, day(2), day(3)),
                (1, day(10), day(12)),
                (2, day(2), day(3)),
            ]
            + [(2, day(5 + 2 * j), day(6 + 2 * j)) for j in range(i)]
        }
    if k == 2504:
        profs = [row[2] for row in t["Person"]]
        return {"Person": [(j, f"P{j}", profs[j % len(profs)]) for j in range(1, i + 3)]}
    if k == 2668:
        for j in range(i):
            t["Salary"].append([500 + j, f"A{j}", "Lee", str(300 + j), "D1"])
        old = t["Salary"][0][:]
        old[3] = str(int(old[3]) + 500)
        t["Salary"].append(old)
    elif k == 2669:
        return {
            "Spotify": [(1, "X", "A"), (2, "X", "A"), (3, "Y", "B"), (4, "Z", "B")]
            + [(5 + j, "Z", f"C{j}") for j in range(i)]
        }
    elif k == 2686:
        return {
            "Delivery": [(1, 1, day(0), day(0)), (2, 2, day(0), day(2)), (3, 1, day(1), day(1))]
            + [(5 + j, 5 + j, day(2), day(2 + j % 2)) for j in range(i)]
        }
    elif k == 2687:
        return {
            "Bikes": [
                (j, ["X001", "Y009"][j % 2], day(j) + " 02:00:00", day(j) + " 03:00:00")
                for j in range(i + 3)
            ]
        }
    elif k == 2688:
        return {
            "Users": [(1, "A", day(0), 5), (1, "B", day(7), 6), (2, "A", day(0), 3), (2, "B", day(8), 5)]
            + [(j + 5, "X", day(j), 6) for j in range(i)]
        }
    elif k in (2701, 2752):
        rows = [
            (1, 1, day(0), 5),
            (2, 1, day(1), 6),
            (3, 1, day(2), 7),
            (4, 1, day(4), 9),
            (5, 2, day(0), 5),
            (6, 2, day(1), 5),
            (7, 2, day(2), 7),
        ]
        rows.extend((10 + j, 3, day(j), 2 * j + 1) for j in range(i))
        return {"Transactions": rows}
    elif k == 2720:
        return {"Friends": [(1, 2), (2, 3), (1, 3)] + [(2, 5 + j) for j in range(i)]}
    elif k == 2738:
        return {
            "Files": [
                ("a.txt", "bull market and a bear market"),
                ("b.txt", "a bull and bull again"),
                ("c.txt", "a bullet and bears"),
            ]
            + [(f"f{j}.txt", "a bear market" if j % 2 else "bull.") for j in range(i)]
        }
    elif k in (2783, 2793):
        flights = [(1, 2), (2, 1), (3, 3)]
        pairs = [(1, 1), (2, 1), (3, 1)] + [(10 + j, 2) for j in range(i)]
        return {
            "Flights": flights,
            "Passengers": [(p, f, "2024-01-01 " + f"10:{p:02}:00") for p, f in pairs]
            if k == 2793
            else pairs,
        }
    elif k == 2820:
        if i == 1:
            return {
                "Votes": [(u, c) for u in ("V1", "V2", "V3") for c in ("A", "B", "C")]
                + [("V4", "D"), ("V5", "D")]
            }
        return {
            "Votes": [
                ("A", "X"),
                ("A", "Y"),
                ("B", "Y"),
                ("B", "Z"),
                ("C", "X"),
                ("C", "Z"),
                ("D", None),
            ]
            + [(f"N{j}", None) for j in range(i)]
        }
    elif k == 2837:
        return {
            "Users": [(j, f"U{j}") for j in range(1, 4 + i)],
            "Rides": [(1, 1, 4), (2, 1, 6)] + [(4 + j, 3 + j, 2 + j) for j in range(i)],
        }
    elif k == 2853:
        return {
            "Salaries": [
                ("A", "Engineering", 30 + i),
                ("B", "Engineering", 80 + i),
                ("C", "Marketing", 100 if i % 2 else 50),
                ("D", "Marketing", 5),
            ]
        }
    elif k == 2854:
        return {
            "Steps": [(1, 5 + j, day(j)) for j in [0, 1, 2, 4, 5, 6]]
            + [(2, 10 + j, day(j * 2)) for j in range(i)]
        }
    elif k == 2893:
        return {"Orders": [(j, 1 + (j % 3) + i) for j in range(1, 6 * (1 + i % 3) + 1)]}
    elif k == 2922:
        for j in range(i):
            t["Orders"].append([100 + j, day(j), t["Items"][j % len(t["Items"])][0], t["Users"][0][0]])
    elif k == 2978:
        return {
            "Coordinates": [(1, 2), (2, 1), (3, 3), (4, 4), (4, 4)]
            + [(10 + j, 20 + j) for j in range(i)]
        }
    elif k == 2984:
        return {
            "Calls": [
                (1 + j, 30 + j, day(j) + (" 10:05:00" if j % 2 else " 12:01:00"), "East")
                for j in range(4)
            ]
            + [(50 + j, 70 + j, day(j) + " 07:00:00", "West") for j in range(i)]
        }
    elif k == 2985:
        return {"Orders": [(1, 2, 10), (2, 6, 20)] + [(10 + j, 9 + j, 3 + j) for j in range(i)]}
    elif k == 2986:
        return {
            "Transactions": [(1, n, day(j) + " 12:00:00") for j, n in enumerate([5, 8, 9, 20])]
            + [(2, n, day(j) + " 12:00:00") for j, n in enumerate([8, 5, 8])]
            + [(10 + j, 10 + j, day(j) + " 08:00:00") for j in range(i)]
        }
    elif k == 2987:
        return {
            "Listings": [(1, "A", 10), (2, "B", 50), (3, "C", 90)] + [(5 + j, "B", 50) for j in range(i)]
        }
    elif k == 2988:
        pairs = [(1, "A"), (2, "B"), (3, "C")]
        return {
            "Employees": [(j, n, j, "Manager") for j, n in pairs]
            + [(10 + 2 * p + j, f"E{p}{j}", j, "Staff") for p in range(i) for j in (1, 2)]
        }
    elif k == 2989:
        return {
            "Scores": [(1, "A", 1, 20, 5), (2, "B", 9, 10, 20)]
            + [(5 + j, f"S{j}", 4 + j, 8, 6) for j in range(i)]
        }
    elif k == 2990:
        return {
            "Loans": [(1, 1, "Refinance"), (2, 1, "Mortgage"), (3, 2, "Mortgage"), (4, 3, "Refinance")]
            + [(5 + j, 4 + j, "Mortgage") for j in range(i)]
        }
    elif k == 2991:
        return {
            "Wineries": [(1, "US", 60, "A"), (2, "US", 65, "B"), (3, "US", 5, "A"), (4, "UK", 20, "C")]
            + [(10 + j, "IT", 50 + j, f"W{j}") for j in range(i)]
        }
    elif k in (2993, 2994):
        return {
            "Purchases": [
                (1, "2023-11-03", 5),
                (2, "2023-11-03", 7),
                (3, "2023-11-02", 10),
                (4, "2023-11-17", 8),
            ]
            + [(10 + j, "2023-11-24", 3 + j) for j in range(i)]
        }
    elif k == 2995:
        rows = []
        for user, types in [
            (1, ["Viewer", "Streamer", "Streamer"]),
            (2, ["Streamer", "Viewer"]),
            (3, ["Viewer", "Viewer"]),
        ] + [(5 + j, ["Viewer", "Streamer"]) for j in range(i)]:
            for n, kind in enumerate(types):
                rows.append((user, day(n) + " 08:00:00", day(n) + " 09:00:00", len(rows) + 1, kind))
        return {"Sessions": rows}
    return t
