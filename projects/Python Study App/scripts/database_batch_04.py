"""Constraint-preserving boundary and population variations for the customer and rides batch."""

from datetime import date, timedelta
from copy import deepcopy


def inputs(k, i, r, base):
    t = deepcopy(base)

    def day(start, offset):
        return (date.fromisoformat(start) + timedelta(days=offset)).isoformat()

    if k == 1468:
        return {
            "Salaries": [(j, j * 10, "Lead", cap) for j, cap in enumerate([999, 1000, 10000, 10001], 1)]
            + [(1 + j % 4, 100 + j, f"E{j}", 150 + j) for j in range(i)]
        }
    if k == 1479:
        for j in range(i):
            t["Orders"].append(
                [1000 + j, 1, day("2024-02-01", j), t["Items"][j % len(t["Items"])][0], j + 2]
            )
        t["Items"].append([600, "Unused", "Unused"])
    elif k == 1484:
        return {
            "Activities": [("2023-01-01", "Z"), ("2023-01-01", "A"), ("2023-01-01", "A")]
            + [("2023-01-02", f"P{j:02}") for j in range(i)]
        }
    elif k == 1495:
        for j in range(i):
            t["TVProgram"].append(
                [day("2020-06-01", j) + " 01:00", int(t["Content"][j % len(t["Content"])][0]), f"C{j}"]
            )
    elif k == 1501:
        return {
            "Country": [("A", "001"), ("B", "002"), ("C", "003")],
            "Person": [(1, "Ada", "001-1122334"), (2, "Ben", "002-1122334"), (3, "Cy", "003-1122334")],
            "Calls": [(1, 2, 100), (1, 3, 1)] + [(1, 3, j + 2) for j in range(i)],
        }
    elif k == 1511:
        return {
            "Customers": [(j, f"C{j}", "US") for j in range(1, 4)],
            "Product": [(1, "Toy", 25), (2, "Lamp", 10)],
            "Orders": [
                (1, 1, 1, "2020-06-30", 4),
                (2, 1, 1, "2020-07-01", 4),
                (3, 2, 1, "2020-06-15", 10),
                (4, 3, 1, "2019-07-15", 7),
            ]
            + [(5 + j, 3, 2, "2020-07-30", 1) for j in range(i)],
        }
    elif k == 1517:
        mails = [
            "abc@leetcode.com",
            "a+b@leetcode.com",
            "1a@leetcode.com",
            "abc@LeetCode.com",
            "a@leetcodexcom",
            "a.b-c_d@leetcode.com",
        ]
        return {
            "Users": [
                (j, f"U{j}", m)
                for j, m in enumerate(mails + [f"a{j}@leetcode.com" for j in range(i)], 1)
            ]
        }
    elif k == 1527:
        values = ["DIAB100", "COLD DIAB19", "XDIAB1", "DIAB2", "COLD", ""]
        return {
            "Patients": [
                (j, f"P{j}", x) for j, x in enumerate(values + [f"DIAB1{j}" for j in range(i)], 1)
            ]
        }
    elif k in (1532, 1549, 1596):
        p = t.get("Products", [])
        for j in range(i):
            t["Orders"].append(
                [
                    200 + j,
                    day("2024-01-01", j // 2 if k == 1549 else j),
                    t["Customers"][j % len(t["Customers"])][0],
                    p[j % len(p)][0] if p else 50 + j,
                ]
            )
        if k == 1549:
            t["Orders"] += [
                [500, "2024-12-01", t["Customers"][0][0], p[0][0]],
                [501, "2024-12-01", t["Customers"][1][0], p[0][0]],
            ]
    elif k == 1543:
        return {
            "Sales": [(1, " Toy ", "2020-02-10"), (2, "TOY", "2020-02-11"), (3, "Toy", "2021-02-11")]
            + [(5 + j, "pRoD " + str(j % 3), "2020-01-05") for j in range(i)]
        }
    elif k == 1555:
        return {
            "Users": [(1, "A", 20), (2, "B", 10), (3, "C", 0), (4, "D", 5), (5, "E", 0)],
            "Transactions": [(1, 1, 2, 20, "2023-01-01"), (2, 2, 3, 40, "2023-01-02")]
            + [(5 + j, 3, 1, 1, "2023-02-01") for j in range(i)],
        }
    elif k == 1565:
        return {
            "Orders": [(1, "2023-01-01", 1, 20), (2, "2023-01-01", 1, 22), (3, "2023-01-02", 1, 25)]
            + [(5 + j, "2024-01-01", j + 2, 21 + j) for j in range(i)]
        }
    elif k == 1571:
        for row in t["Warehouse"]:
            row[2] = 1 + r.randrange(2 + i)
        t["Warehouse"].append([f"New{i}", t["Products"][0][0], i + 1])
    elif k == 1581:
        return {
            "Visits": [(j, 1 + j % 3) for j in range(1, 4 + i)],
            "Transactions": [(20 + j, j, 4 + j) for j in range(1, 4 + i, 3)] + [(99, 1, 2)],
        }
    elif k == 1587:
        return {
            "Users": [(1, "A"), (2, "B"), (3, "C")],
            "Transactions": [
                (1, 1, 10000, "2023-01-01"),
                (2, 2, 11000, "2023-01-01"),
                (3, 2, -2000, "2023-01-02"),
            ]
            + [(5 + j, 3, 1000, "2023-02-01") for j in range(i)],
        }
    elif k == 1607:
        t["Seller"].append([200, "New Seller"])
        for j in range(i):
            t["Orders"].append(
                [50 + j, day("2019-12-27", j), 30, t["Customer"][0][0], t["Seller"][0][0]]
            )
    elif k == 1613:
        return {"Customers": [(j, f"C{j}") for j in [2, 4, 5] + [10 + 2 * n for n in range(i)]]}
    elif k == 1623:
        return {
            "SchoolA": [(1, "A"), (2, "B")],
            "SchoolB": [(8, "A"), (2, "X"), (3, "Y")],
            "SchoolC": [(4, "Z"), (3, "K")] + [(20 + j, f"U{j}") for j in range(i)],
        }
    elif k == 1633:
        return {
            "Users": [(j, f"U{j}") for j in range(1, 5 + i)],
            "Register": [(1, 2), (2, 2)] + [(3, j) for j in range(1, 3 + i)],
        }
    elif k in (1635, 1645, 1651):
        drivers = [(1, "2019-01-01"), (2, "2020-02-01"), (3, "2020-12-28"), (4, "2021-01-01")]
        rides = [
            (1, 9, "2019-12-18"),
            (2, 9, "2020-01-01"),
            (3, 8, "2020-02-01"),
            (4, 7, "2021-01-02"),
        ] + [(10 + j, 1, day("2020-02-15", j * 9)) for j in range(i)]
        accepted = [(1, 1, 12, 8), (2, 1, 30, 20), (3, 2, 10, 40)] + [
            (10 + j, 1 + j % 2, 10 + j, 15) for j in range(0, i, 2)
        ]
        return {"Drivers": drivers, "Rides": rides, "AcceptedRides": accepted}
    elif k == 1661:
        rows = []
        for machine in range(2):
            for j in range(1, i + 2):
                start = 2 * j + machine
                rows.extend(
                    [
                        (machine, j, "start", start),
                        (machine, j, "end", start + (0.25 if j % 2 else 0.75)),
                    ]
                )
        return {"Activity": rows}
    elif k == 1667:
        return {"Users": [(j, "aDAm" if j % 2 else "mIXED") for j in range(1, 3 + i)]}
    elif k == 1677:
        products = [(1, "A"), (2, "B"), (3, "C")]
        return {
            "Product": products,
            "Invoice": [(j, 1 + j % 2, j, 2 * j, 3 * j, 4 * j) for j in range(1, 2 + i)],
        }
    elif k == 1693:
        return {
            "DailySales": [("2020-01-01", "Car", 1, 1), ("2020-01-01", "Car", 1, 2)]
            + [("2020-01-01", "Car" if j % 2 else "Van", j % 4, j) for j in range(i)]
        }
    elif k == 1699:
        return {
            "Calls": [(1, 2, 5), (2, 1, 7), (1, 3, 2)]
            + [(1, 2 + r.randrange(2), j + 1) for j in range(i)]
        }
    elif k == 1709:
        return {
            "UserVisits": [(1, "2020-12-20"), (1, "2020-12-25"), (2, "2020-06-01")]
            + [(3, day("2020-02-01", 2 * j)) for j in range(i)]
        }
    elif k == 1715:
        return {
            "Boxes": [(1, None, 4, 5), (2, 20, 5, 7)] + [(3 + j, None, 1, 2) for j in range(i)],
            "Chests": [(20, 3, 6), (30, 100, 90)],
        }
    elif k == 1731:
        return {
            "Employees": [(1, "A", None, 50), (2, "B", 1, 30), (3, "C", 1, 31)]
            + [(5 + j, f"E{j}", 2, 20 + j) for j in range(i)]
        }
    return t
