"""Input families for dated intervals, zero-count joins, rankings and grouped calculations."""

from datetime import date, timedelta


def inputs(k, i, r):
    if k == 1211:
        return {
            "Queries": [
                ("Search", "A", 1, 5),
                ("Search", "A", 1, 5),
                ("Search", "B", 2, 3),
                ("Other", "X", 3, 2),
            ]
            + [("Search", f"R{j}", j + 3, r.randint(1, 5)) for j in range(i)]
        }
    if k == 1212:
        return {
            "Teams": [(j, f"T{j}") for j in range(1, 5)],
            "Matches": [(1, 1, 2, 2, 2), (2, 2, 3, 2, 0)] + [(5 + j, 1, 3, j % 3, 1) for j in range(i)],
        }
    if k == 1225:
        days = [(date(2018, 12, 28) + timedelta(days=j)).isoformat() for j in range(10 + i)]
        return {
            t: [(d,) for j, d in enumerate(days) if (j % 7 in (1, 2, 5)) == failed]
            for t, failed in [("Failed", True), ("Succeeded", False)]
        }
    if k == 1241:
        return {
            "Submissions": [(1, None), (1, None), (2, None), (3, 1), (3, 1)]
            + [(5 + j, 1 if j % 2 else None) for j in range(i)]
        }
    if k == 1251:
        prices = [(j, "2023-01-01", "2023-01-15", 3 + j) for j in range(1, 4)] + [
            (j, "2023-01-16", "2023-02-15", 10 + j) for j in range(1, 4)
        ]
        return {
            "Prices": prices,
            "UnitsSold": [(1, "2023-01-15", 1), (1, "2023-01-16", 4)]
            + [(2, "2023-01-20", j + 1) for j in range(i)],
        }
    if k == 1264:
        return {
            "Friendship": [(1, 2), (3, 1), (2, 4)],
            "Likes": [(1, 2), (2, 2), (2, 3), (3, 3), (3, 4), (4, 7)] + [(3, 10 + j) for j in range(i)],
        }
    if k == 1270:
        return {
            "Employees": [
                (1, "CEO", 1),
                (2, "Second", 1),
                (3, "Third", 2),
                (4, "Fourth", 3),
                (5, "Other", 5),
            ]
            + [(6 + j, f"E{j}", r.choice([1, 2, 3, 5])) for j in range(i)]
        }
    if k == 1280:
        return {
            "Students": [(1, "Ana"), (2, "Kim"), (3, "Yu")],
            "Subjects": [("Math",), ("Physics",)],
            "Examinations": [(1, "Math"), (1, "Math"), (2, "Physics")] + [(2, "Math") for j in range(i)],
        }
    if k == 1285:
        return {"Logs": [(x,) for x in [1, 2, 3, 6, 8, 9] + [12 + j + (j // 3) for j in range(i)]]}
    if k == 1294:
        return {
            "Countries": [(1, "A"), (2, "B"), (3, "C")],
            "Weather": [
                (1, 15, "2019-11-01"),
                (2, 25, "2019-11-02"),
                (3, 20, "2019-11-01"),
                (1, 90, "2019-12-01"),
            ]
            + [(3, 20 + j % 3, f"2019-11-{3 + j:02}") for j in range(i)],
        }
    if k == 1303:
        return {"Employee": [(j, 1 + j % 3) for j in range(1, 4 + i)]}
    if k == 1308:
        return {
            "Scores": [
                (f"P{j}{g}", g, (date(2023, 1, 1) + timedelta(days=j)).isoformat(), 1 + r.randrange(10))
                for j in range(i + 2)
                for g in ("F", "M")
            ]
        }
    if k == 1322:
        return {
            "Ads": [
                (1, 1, "Viewed"),
                (1, 2, "Clicked"),
                (1, 3, "Ignored"),
                (2, 1, "Ignored"),
                (3, 1, "Clicked"),
            ]
            + [(4, j + 5, "Viewed" if j % 2 else "Clicked") for j in range(i)]
        }
    if k == 1327:
        return {
            "Products": [(1, "A", "C"), (2, "B", "C"), (3, "C", "C")],
            "Orders": [
                (1, "2020-02-01", 90),
                (1, "2020-02-29", 10),
                (2, "2020-01-31", 120),
                (2, "2020-02-15", 5),
            ]
            + [(3, "2020-02-03", 10 + j) for j in range(i)],
        }
    if k == 1336:
        visits = [(j, "2022-01-01") for j in range(1, i + 4)]
        return {
            "Visits": visits,
            "Transactions": [
                (j, "2022-01-01", v + 1) for j, _ in visits for v in range(j % 4) if j % 4 != 2
            ],
        }
    if k == 1341:
        users = [(j, f"U{j:02}") for j in range(1, i + 4)]
        return {
            "Movies": [(1, "Amber"), (2, "Blue"), (3, "Cyan")],
            "Users": users,
            "MovieRating": [
                (movie, u, 1 + (movie + u) % 5, "2019-01-01" if movie == 3 else "2020-02-15")
                for u, _ in users
                for movie in (1, 2, 3)
            ],
        }
    if k == 1350:
        return {
            "Departments": [(2, "A"), (4, "B")],
            "Students": [(j, f"S{j}", 2 + j % 4) for j in range(i + 3)],
        }
    if k == 1355:
        return {
            "Activities": [(1, "Ski"), (2, "Run"), (3, "Swim")],
            "Friends": [
                (j, f"P{j}", act) for j, act in enumerate(["Ski"] + ["Run"] * 2 + ["Swim"] * (3 + i), 1)
            ],
        }
    if k == 1364:
        customers = [(j, f"C{j}", f"c{j}@test.example") for j in range(1, 4 + i)]
        contacts = [(1, "Friend", "external@test.example"), (1, "C2", "c2@test.example")] + [
            (2, f"C{j}", f"c{j}@test.example") for j in range(3, 3 + i)
        ]
        return {
            "Customers": customers,
            "Contacts": contacts,
            "Invoices": [(j, 10 + j, j) for j, _, _ in customers],
        }
    if k == 1369:
        return {
            "UserActivity": [("Solo", "Read", "2023-01-01", "2023-01-02")]
            + [
                (
                    "Ana",
                    f"A{j}",
                    (date(2023, 1, 1) + timedelta(days=3 * j)).isoformat(),
                    (date(2023, 1, 2) + timedelta(days=3 * j)).isoformat(),
                )
                for j in range(2 + i)
            ]
        }
    if k == 1378:
        return {
            "Employees": [(j, f"E{j}") for j in range(1, 3 + i)],
            "EmployeeUNI": [(j, j + 100) for j in range(1, 3 + i) if j % 2],
        }
    if k == 1384:
        return {
            "Product": [(1, "A"), (2, "B")],
            "Sales": [
                (1, "2018-12-31", "2019-01-01", 5 + i),
                (2, "2020-02-28", (date(2020, 3, 1) + timedelta(days=i)).isoformat(), 3),
            ],
        }
    if k == 1393:
        return {
            "Stocks": [
                (f"S{j}", op, j * 4 + n, 10 + r.randrange(10))
                for j in range(1, 2 + i)
                for n, op in enumerate(["Buy", "Sell", "Buy", "Sell"])
            ]
        }
    if k == 1398:
        pairs = [(1, "A"), (1, "B"), (2, "A"), (2, "B"), (2, "C"), (3, "A")] + [
            (4 + j, "B") for j in range(i)
        ]
        return {
            "Customers": [(j, f"C{j}") for j in range(1, 4 + i)],
            "Orders": [(n, u, p) for n, (u, p) in enumerate(pairs, 1)],
        }
    if k == 1407:
        return {
            "Users": [(j, f"U{j:02}") for j in range(1, 4 + i)],
            "Rides": [(1, 1, 10), (2, 1, 5), (3, 2, 15)] + [(4 + j, 3 + j, 1 + j) for j in range(i)],
        }
    if k == 1412:
        return {
            "Student": [(j, f"S{j}") for j in range(1, 6 + i)],
            "Exam": [
                (test, j, score) for j in range(1, 4 + i) for test, score in [(1, j), (2, j % 4 + 10)]
            ],
        }
    if k == 1421:
        return {
            "NPV": [(1, 2020, 14), (1, 2021, 19)] + [(j + 3, 2020, 4 + j) for j in range(i)],
            "Queries": [(1, 2020), (2, 2020), (1, 2019)] + [(j + 3, 2020) for j in range(i)],
        }
    if k == 1435:
        return {
            "Sessions": list(
                enumerate([299, 300, 600, 900] + [r.randrange(20, 1200) for j in range(i)], 1)
            )
        }
    if k == 1440:
        return {
            "Variables": [("x", i), ("y", i), ("z", i + 1)],
            "Expressions": [("x", "=", "y"), ("x", ">", "y"), ("x", "<", "z"), ("z", ">", "y")],
        }
    if k == 1445:
        return {
            "Sales": [
                (
                    (date(2023, 1, 1) + timedelta(days=j)).isoformat(),
                    fruit,
                    (j + 1) * (2 if fruit == "apples" else 3),
                )
                for j in range(i + 1)
                for fruit in ("apples", "oranges")
            ]
        }
    if k == 1454:
        rows = [
            (p, (date(2022, 1, 1) + timedelta(days=d)).isoformat())
            for p, days in [(1, range(5)), (2, [0, 1, 2, 4, 5]), (3, range(3 + i))]
            for d in days
        ]
        return {"Accounts": [(1, "Ada"), (2, "B"), (3, "C")], "Logins": rows + [rows[0], rows[-1]]}
    if k == 1459:
        return {
            "Points": [(1, 0, 0), (2, 0, 2), (3, 3, 2)]
            + [(5 + j, 5 + j, r.randrange(1, 9)) for j in range(i)]
        }
    raise KeyError(k)
