"""Additional independent, constraint-preserving input families for SQL problems 180–626."""

from datetime import date, timedelta


def inputs(key, i, r):
    if key == 180:
        values = [
            str(v)
            for v in (
                [2] * 3
                + [1, 2, 1, 2]
                + [3] * (2 + i % 3)
                + [2] * 3
                + [r.randint(1, 4) for _ in range(i)]
            )
        ]
        return {"Logs": list(enumerate(values, 1))}
    if key == 184:
        return {
            "Department": [(1, "A"), (2, "B"), (3, "C")],
            "Employee": [(1, "Ada", 90, 1), (2, "Ben", 90, 1), (3, "Cy", 70, 1), (4, "Dee", 50, 2)]
            + [(10 + j, f"E{j}", r.choice([20, 50, 90, 95]), 1 + j % 2) for j in range(i)],
        }
    if key == 262:
        users = [
            (1, "No", "client"),
            (2, "Yes", "client"),
            (3, "No", "client"),
            (4, "No", "driver"),
            (5, "Yes", "driver"),
        ]
        rows = [
            (1, 1, 4, 1, "completed", "2013-10-01"),
            (2, 2, 4, 1, "cancelled_by_client", "2013-10-01"),
            (3, 1, 5, 1, "cancelled_by_driver", "2013-10-02"),
            (4, 3, 4, 1, "cancelled_by_driver", "2013-10-03"),
        ]
        for j in range(i):
            rows.append(
                (
                    10 + j,
                    r.choice([1, 2, 3]),
                    r.choice([4, 5]),
                    1,
                    r.choice(["completed", "cancelled_by_client"]),
                    (date(2013, 9, 30) + timedelta(days=r.randrange(6))).isoformat(),
                )
            )
        return {"Trips": rows, "Users": users}
    if key in (511, 512, 534, 550):
        rows = []
        for player in range(1, 4 + i):
            start = date(2023, 1, 1) + timedelta(days=r.randint(0, 12))
            for n in [0, 1, 3] if player % 3 == 0 else [0, 2, 3] if player % 3 == 1 else [0]:
                rows.append(
                    (
                        player,
                        1 + (player + n) % 5,
                        (start + timedelta(days=n)).isoformat(),
                        r.randrange(12),
                    )
                )
        return {"Activity": rows}
    if key == 569:
        return {
            "Employee": [
                (j + 1, ["A", "B", "C"][j % 3], r.choice([10, 11, 11, 15])) for j in range(6 + i)
            ]
        }
    if key == 570:
        rows = [(1, "Lead A", "Data", None), (2, "Lead B", "Sales", None)]
        rows.extend((10 + j, f"E{j}", "Data", 1) for j in range(4 + i % 3))
        rows.extend((30 + j, f"F{j}", "Sales", 2) for j in range(2 + i))
        return {"Employee": rows}
    if key == 571:
        if i == 1:
            return {"Numbers": [(1, 1), (3, 1)]}
        return {"Numbers": [(j, 1 + r.randrange(7)) for j in range(i + 2)]}
    if key == 574:
        ids = [2] * (3 + i) + [1, 3] * max(1, i // 2)
        return {"Candidate": [(1, "A"), (2, "B"), (3, "C"), (4, "D")], "Vote": list(enumerate(ids, 1))}
    if key == 577:
        rows = [(j, f"E{j}", None if j == 1 else 1, 5000 + j * 3) for j in range(1, i + 5)]
        return {
            "Employee": rows,
            "Bonus": [(j, [999, 1000, 1001, 0][j % 4]) for j in range(1, i + 4) if j % 5],
        }
    if key == 578:
        rows = []
        for q, n, answers in [(101, 4, 2), (102, 2, 1), (103, 5, 2), (200 + i, 3 + i, 1 + i % 3)]:
            for j in range(n):
                uid = len(rows) + 1
                rows.append((uid, "show", q, None, j + 1, uid))
                rows.append(
                    (
                        uid,
                        "answer" if j < answers else "skip",
                        q,
                        uid if j < answers else None,
                        j + 1,
                        len(rows) + 1,
                    )
                )
        return {"SurveyLog": rows}
    if key == 579:
        return {
            "Employee": [
                (person, m, r.randint(5, 12))
                for person in range(1, 3 + i)
                for m in r.sample(range(1, 13), 5)
            ]
        }
    if key == 580:
        return {
            "Department": [(1, "A"), (2, "B"), (3, "C"), (4, "D")],
            "Student": [(j, f"S{j}", r.choice(["F", "M"]), 1 + j % 3) for j in range(1, 3 + i)],
        }
    if key == 585:
        return {
            "Insurance": [(1, 10, 4, 1, 1), (2, 10, 7, 2, 1), (3, 20, 11, 3, 2), (4, 10, 5, 3, 2)]
            + [(5 + j, r.choice([10, 20, 30]), r.randint(5, 15), 4 + j, 2) for j in range(i)]
        }
    if key == 586:
        nums = [2] * (3 + i) + [1, 3] * max(1, i // 2)
        return {"Orders": list(enumerate(nums, 1))}
    if key == 596:
        return {
            "Courses": [
                (f"S{j}", name)
                for name, size in [("Math", 5), ("Music", 4), ("Lab", i + 2)]
                for j in range(size)
            ]
        }
    if key == 597:
        rows = [(1, 2, "2024-01-01"), (1, 2, "2024-01-02"), (2, 3, "2024-01-02")]
        rows.extend((1, 8 + j, "2024-01-03") for j in range(i))
        accepted = [(1, 2, "2024-01-03"), (1, 2, "2024-01-04")] + [
            (1, 8 + j, "2024-01-04") for j in range(0, i, 3)
        ]
        return {"FriendRequest": [] if i == 1 else rows, "RequestAccepted": accepted}
    if key == 601:
        values = [99, 100, 100, 100, 80, 120, 120, 75] + [r.choice([90, 100, 120]) for _ in range(i)]
        return {
            "Stadium": [
                (j, (date(2024, 1, 1) + timedelta(days=j + j // 4)).isoformat(), v)
                for j, v in enumerate(values, 1)
            ]
        }
    if key == 602:
        return {
            "RequestAccepted": [(1, 2, "2024-01-01"), (3, 1, "2024-01-02"), (2, 3, "2024-01-03")]
            + [(4 + j, 1, "2024-02-01") for j in range(i + 1)]
        }
    if key == 603:
        return {"Cinema": list(enumerate([0, 1, 1, 1, 0, 1, 0] + [r.randrange(2) for _ in range(i)], 1))}
    if key == 607:
        return {
            "SalesPerson": [(j, f"S{j}", 1000 + j, 10, "2020-01-01") for j in range(1, 5 + i)],
            "Company": [(1, "RED", "LA"), (2, "BLUE", "NY")],
            "Orders": [(1, "2022-01-01", 1, 1, 40), (2, "2022-01-02", 2, 1, 80)]
            + [(5 + j, "2022-01-03", 1 + j % 2, 2 + j, 20 + j) for j in range(i)],
        }
    if key == 608:
        return {"Tree": [(1, None)] + [(j, r.randrange(1, j)) for j in range(2, 2 + i)]}
    if key == 610:
        return {
            "Triangle": list(
                dict.fromkeys(
                    [(1, 2, 3), (3, 4, 5), (1, 9, 2), (4, 1, 2), (1, 2, 4)]
                    + [(j + 10, i + j + 5, 10 + j) for j in range(i)]
                )
            )
        }
    if key == 612:
        return {"Point2D": [(0, 0), (0, 2), (3, 2)] + [(j + 4, r.randrange(2, 12)) for j in range(i)]}
    if key == 613:
        return {"Point": [(x,) for x in sorted(r.sample(range(-90, 90), 3 + i))]}
    if key == 614:
        return {
            "Follow": [("A", "B"), ("D", "B"), ("B", "C"), ("B", "E"), ("C", "A")]
            + [("C" if j % 2 else "E", f"N{j}") for j in range(i)]
        }
    if key == 615:
        e = [(j, 1 + j % 3) for j in range(1, 4 + i)]
        return {
            "Employee": e,
            "Salary": [
                (10 * j + m, j, r.choice([100, 200, 300]), f"2023-0{m}-{10 + j % 4}")
                for j, _ in e
                for m in (1, 2)
            ],
        }
    if key == 618:
        return {
            "Student": [(f"A{j:02}", "America") for j in range(2 + i)]
            + [(f"S{j:02}", "Asia") for j in range(1 + i // 2)]
            + [(f"E{j:02}", "Europe") for j in range(i % 4)]
        }
    if key == 619:
        values = [5, 5, 1] if i % 3 else [5, 5]
        for j in range(i):
            values.extend([j + 7] * (1 if j % 3 == 0 and i % 3 else 2))
        return {"MyNumbers": [(n,) for n in values]}
    if key == 626:
        return {"Seat": [(j, f"S{j}") for j in range(1, 2 + i)]}
    raise KeyError(key)
