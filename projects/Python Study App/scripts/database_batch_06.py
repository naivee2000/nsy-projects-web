from datetime import date, timedelta


def inputs(k, i, r, seed):
    def day(j):
        return (date(2023, 1, 1) + timedelta(days=j)).isoformat()

    if k == 2026:
        return {
            "Problems": [(1, 3, 2), (2, 2, 2), (3, 4, 1)] + [(5 + j, 3 + j, 4 + j) for j in range(i)]
        }
    if k == 2041:
        return {
            "Candidates": [(1, "A", 2, 11), (2, "B", 3, 12), (3, "C", 1, 13)]
            + [(5 + j, f"C{j}", 3, None) for j in range(i)],
            "Rounds": [(11, 1, 7), (11, 2, 9), (12, 1, 15), (13, 1, 17)],
        }
    if k == 2051:
        return {
            "Members": [(j, f"M{j}") for j in range(1, 5 + i)],
            "Visits": [(n + 10 * u, u, day(n)) for u in (1, 2, 3) for n in range(5 if u != 2 else 2)],
            "Purchases": [(10 + n, 20 + n) for n in range(4)] + [(20, 5), (30, 5)],
        }
    if k == 2066:
        return {
            "Transactions": [
                (u, day(j), "Deposit" if j % 3 == 0 else "Withdraw", 100 if j % 3 == 0 else j)
                for u in (1, 2)
                for j in range(i + 2)
            ]
        }
    if k == 2072:
        return {
            "NewYork": [(1, 90), (2, 95)] + [(5 + j, j) for j in range(i)],
            "California": [(1, 91)] + [(2, 100)] * (i % 2),
        }
    if k == 2082:
        return {
            "Store": [(1, 1, 500), (2, 2, 600), (3, 2, 650)]
            + [(j + 4, 4 + j, 300 + i) for j in range(i)]
        }
    if k == 2084:
        return {
            "Orders": [(1, 1, 0), (2, 1, 1), (3, 2, 1), (4, 3, 0)]
            + [(j + 5, 4 + j, 1) for j in range(i)]
        }
    if k == 2112:
        return {"Flights": [(1, 2, 10 + i), (2, 1, 10 + i), (3, 4, 15), (4, 3, 14)]}
    if k == 2118:
        return {"Terms": [(0, -1), (1, 2)] + [(j + 2, ((-1) ** j) * (2 + j)) for j in range(i)]}
    if k in (2142, 2153):
        ts = [(1, 4), (2, 8), (3, 12), (4, 20)]
        return {
            "Buses": [(*b, 2 if b[0] % 2 else 3) for b in ts] if k == 2153 else ts,
            "Passengers": [
                (n + 1, v) for n, v in enumerate([3, 4, 4, 4, 5, 12, 21] + [10 + j for j in range(i)])
            ],
        }
    if k == 2159:
        return {"Data": [(j, 5 + j % 3) for j in range(1, 4 + i)]}
    if k == 2173:
        rows = []
        for u, seq in [(1, ["Win", "Win", "Draw", "Win", "Lose"] + ["Win"] * i), (2, ["Draw", "Lose"])]:
            rows.extend((u, day(j), v) for j, v in enumerate(seq))
        return {"Matches": rows}
    if k == 2175:
        return {
            "TeamPoints": [(1, "Alpha", 100), (2, "Beta", 100), (3, "Cy", 80 + i), (4, "Delta", 92)],
            "PointsChange": [(1, -10), (2, -5), (3, 30), (4, 0)],
        }
    if k == 2199:
        return {
            "Keywords": [(1, "ball"), (2, "ball"), (3, "plan"), (3, "ideas")],
            "Posts": [(1, "BALL and plan"), (2, "football only"), (3, "plan plan ideas")]
            + [(5 + j, f"plan {j}") for j in range(i)],
        }
    if k == 2228:
        return {
            "Purchases": [(1, 1, day(1)), (2, 1, day(8)), (3, 2, day(0)), (4, 2, day(8))]
            + [(10 + j, 3, day(j * 10)) for j in range(i)]
        }
    if k == 2238:
        return {"Rides": [(1, 1, 2), (2, 1, 2), (3, 2, 3)] + [(5 + j, j + 5, 1) for j in range(i)]}
    if k == 2292:
        rows = []
        for p, years in [(1, [2019, 2020]), (2, [2019, 2021]), (3, [2019, 2020])]:
            for yr in years:
                for n in range(2 if p == 3 and yr == 2019 else 3):
                    rows.append((len(rows) + 1, p, 3 + n, f"{yr}-01-{n + 1:02}"))
        rows.extend((100 + j, 4, 2, day(j)) for j in range(i))
        return {"Orders": rows}
    if k == 2298:
        return {"Tasks": [(j, 1, day(j)) for j in range(i + 7)]}
    if k == 2308:
        return {
            "Genders": [
                (j * 3 + n, g)
                for j in range(i + 1)
                for n, g in enumerate(["male", "female", "other"], 1)
            ]
        }
    if k == 2314:
        return {
            "Weather": [(1, day(0), 12), (1, day(1), 12), (2, day(0), 20), (2, day(1), 30)]
            + [(3, day(j), j + 1) for j in range(i)]
        }
    if k in (2324, 2329, 2362):
        prices = [(1, 10), (2, 5), (3, 12)]
        if k == 2362:
            return {
                "Products": prices,
                "Purchases": [(1, 1, 2), (2, 2, 4)] + [(10 + j, 3, 1) for j in range(i)],
            }
        return {
            "Product": prices,
            "Sales": [(1, 1, 1, 1), (2, 2, 1, 2), (3, 1, 2, 4), (4, 2, 2, 1)]
            + [(5 + j, 3, 8 + j, 1) for j in range(i)],
        }
    if k == 2339:
        return {"Teams": [(f"Team{j}",) for j in range(i + 2)]}
    if k == 2346:
        return {
            "Students": [(1, 1, 100), (2, 1, 100), (3, 1, 75), (4, 2, 80)]
            + [(10 + j, 3, 60 + j) for j in range(i)]
        }
    if k == 2356:
        return {
            "Teacher": [(1, 10, 1), (1, 10, 2), (1, 11, 2), (1, 13, 2)]
            + [(3 + j, 20 + j, 2) for j in range(i)]
        }
    if k == 2372:
        return {
            "Salesperson": [(1, "A"), (2, "B"), (3, "C")],
            "Customer": [(1, 1), (2, 1), (3, 2)],
            "Sales": [(1, 1, 40), (2, 2, 30)] + [(4 + j, 3, 10 + j) for j in range(i)],
        }
    if k == 2377:
        return {
            "Olympic": [("A", 1, 2, 3), ("B", 1, 2, 3), ("C", 1, 2, 4), ("D", 1, 3, 0), ("E", 2, 0, 0)]
            + [(f"X{j}", 0, j, 1) for j in range(i)]
        }
    if k == 2388:
        ids = r.sample(range(1000), 4 + i)
        return {
            "CoffeeShop": [
                (d, "Tea" if j == 0 else "Water" if j % 4 == 0 else None) for j, d in enumerate(ids)
            ]
        }
    if k == 2394:
        return {
            "Employees": [(1, 1), (2, 2), (3, 1)] + [(5 + j, 2) for j in range(i)],
            "Logs": [
                (1, "2023-01-01 01:00:00", "2023-01-01 01:59:01"),
                (2, "2023-01-01 01:00:00", "2023-01-01 02:00:00"),
            ],
        }
    if k == 2474:
        rows = [
            (1, 1, "2019-01-01", 10),
            (2, 1, "2020-01-01", 15),
            (3, 2, "2019-01-01", 10),
            (4, 2, "2021-01-01", 20),
            (5, 3, "2019-01-01", 20),
            (6, 3, "2020-01-01", 20),
        ] + [(10 + j, 5 + j, day(j), 10 + j) for j in range(i)]
        return {"Orders": rows}
    raise KeyError(k)
