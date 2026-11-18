"""Inputs for product sales, user activity, surveys, monthly aggregates and recommendation tasks."""

from datetime import date, timedelta
from calendar import month_abbr
from .database_batch_01 import inputs as earlier_inputs


def inputs(key, i, r):
    if key == 1045:
        products = list(range(1, 3 + i % 3))
        pairs = (
            [(1, p) for p in products]
            + [(2, products[0])] * len(products)
            + [(3, p) for p in products[:-1]]
        )
        return {
            "Product": [(p,) for p in products],
            "Customer": pairs + [(5 + j, r.choice(products)) for j in range(i)],
        }
    if key in (1068, 1069, 1070):
        rows = [(1, 1, 2020, 2, 10), (2, 1, 2020, 2, 10), (3, 1, 2023, 9, 25), (4, 2, 2022, 1, 15)]
        rows += [(5 + j, 1 + j % 2, 2021 + j % 2, r.randrange(1, 8), 10 + j) for j in range(i)]
        result = {"Sales": rows}
        if key != 1070:
            result["Product"] = [(1, "Widget"), (2, "Pump"), (3, "Motor")]
        return result
    if key in (1075, 1076, 1077):
        n = i + 4
        employees = [(j, f"E{j}", 2 + j % 3) for j in range(1, n + 1)]
        assignments = (
            [(1, j) for j in range(1, n + 1)]
            + [(2, j) for j in range(1, n + 1 if i % 2 else n)]
            + [(3, 1)]
        )
        return {"Project": assignments, "Employee": employees}
    if key in (1082, 1083, 1084):
        products = [(1, "S8", 90), (2, "iPhone", 40), (3, "Other", 50), (4, "Legacy", 5)]
        rows = [
            (1, 1, 10, "2019-01-01", 1, 90),
            (2, 1, 11, "2019-03-31", 1, 90),
            (2, 2, 11, "2019-04-01", 1, 40),
            (1, 2, 12, "2018-12-31", 1, 40),
            (3, 3, 13, "2019-02-01", 1, 50),
        ]
        for j in range(i):
            rows += [(5 + j, 3, 35 + j, "2019-02-07", 1, 50)]
        return {"Product": products, "Sales": rows}
    if key == 1097:
        return earlier_inputs(550, i, r)
    if key == 1098:
        books = [
            (1, "A", "2018-01-20"),
            (2, "B", "2019-05-23"),
            (3, "C", "2019-01-10"),
            (4, "D", "2019-02-05"),
        ]
        rows = [(1, 1, 10, "2018-06-23"), (2, 3, 20, "2018-06-22")] + [
            (5 + j, 3, 1, "2019-06-05") for j in range(i)
        ]
        return {"Books": books, "Orders": rows}
    if key == 1107:
        rows = [
            (1, "login", "2019-04-01"),
            (1, "login", "2019-06-30"),
            (2, "login", "2019-03-31"),
            (2, "login", "2019-05-19"),
            (3, "logout", "2019-04-01"),
            (3, "login", "2019-06-30"),
        ]
        return {
            "Traffic": rows
            + [
                (4 + j, "login", (date(2019, 4, 1) + timedelta(days=r.randrange(80))).isoformat())
                for j in range(i)
            ]
        }
    if key == 1112:
        return {
            "Enrollments": [
                (j, c, 80 if c > 1 else 75 + j % 3) for j in range(1, i + 3) for c in (1, 2, 3)
            ]
        }
    if key in (1113, 1132):
        rows = [
            (1, 1, "2019-07-04", "report", "spam"),
            (2, 1, "2019-07-04", "report", "spam"),
            (1, 2, "2019-07-05", "report", "spam"),
            (1, 4, "2019-07-04", "report", "racism"),
            (3, 7, "2019-07-04", "view", None),
        ]
        rows += [(3 + j, 10 + j, "2019-07-05", "report", "spam") for j in range(i)]
        result = {"Actions": rows}
        if key == 1132:
            result["Removals"] = [(1, "2019-07-08"), (2, "2019-07-07"), (4, "2019-07-07")]
        return result
    if key == 1126:
        return {
            "Events": [
                (j, event, 2 + (j % 3 if event in ("click", "open") else j % 2))
                for j in range(1, 4 + i)
                for event in ("click", "open", "share")
            ]
        }
    if key == 1127:
        rows = [
            (1, "2024-01-01", "mobile", 10),
            (1, "2024-01-01", "desktop", 20),
            (2, "2024-01-01", "mobile", 15),
        ]
        rows += [
            (5 + j, "2024-01-02", r.choice(["desktop", "mobile"]), r.randrange(1, 15)) for j in range(i)
        ]
        return {"Spending": rows}
    if key in (1141, 1142):
        rows = [
            (1, 1, "2019-06-27", "open_session"),
            (2, 2, "2019-06-28", "open_session"),
            (2, 2, "2019-06-28", "scroll_down"),
            (3, 3, "2019-07-28", "open_session"),
            (2, 4, "2019-07-27", "open_session"),
        ]
        rows += [(2 + j % 2, 10 + j, "2019-07-20", "open_session") for j in range(i)]
        return {"Activity": rows}
    if key in (1148, 1149):
        rows = [
            (1, 1, 1, "2024-01-01"),
            (1, 1, 1, "2024-01-01"),
            (2, 2, 1, "2024-01-02"),
            (2, 2, 3, "2024-01-03"),
            (1, 1, 3, "2024-01-03"),
        ]
        rows += [(1, 1, 8 + j, "2024-01-02") for j in range(i)]
        return {"Views": rows}
    if key in (1158, 1159):
        users = [(j, "2018-01-01", ["A", "B", "C"][j % 3]) for j in range(1, 6 + i)]
        rows = [
            (1, "2018-01-01", 1, 1, 2),
            (2, "2019-01-01", 3, 4, 2),
            (3, "2020-01-01", 2, 2, 1),
            (4, "2019-02-01", 1, 3, 1),
        ]
        rows += [
            (5 + j, (date(2019, 3, 1) + timedelta(days=j)).isoformat(), 1 + j % 3, 5 + j, 2)
            for j in range(i)
        ]
        return {"Users": users, "Orders": rows, "Items": [(1, "A"), (2, "B"), (3, "C")]}
    if key == 1164:
        rows = [
            (1, 15, "2019-08-16"),
            (1, 8, "2019-08-14"),
            (1, 30, "2019-08-17"),
            (2, 99, "2019-08-18"),
        ]
        rows += [(j + 5, 12 + j, "2019-08-13") for j in range(i)]
        return {"Products": rows}
    if key in (1173, 1174):
        rows = []
        for j in range(2 + i):
            rows += [
                (2 * j + 1, j + 1, "2023-01-01", "2023-01-01" if j % 3 == 0 else "2023-01-05"),
                (2 * j + 2, j + 1, "2023-01-10", "2023-01-11" if j % 3 == 0 else "2023-01-10"),
            ]
        return {"Delivery": rows}
    if key == 1179:
        return {
            "Department": [(j, 50 + j, str(month_abbr[1 + (j + i) % 12])) for j in range(1, 3 + i)]
            + [(1, 200, "Dec" if 1 + (1 + i) % 12 != 12 else "Jan")]
        }
    if key in (1193, 1205):
        rows = [
            (1, "US", "approved", 100, "2022-01-01"),
            (2, "US", "declined", 30, "2022-02-01"),
            (3, "CA", "approved", 30, "2022-01-12"),
        ]
        rows += [
            (
                5 + j,
                "CA" if j % 2 else "US",
                "approved" if j % 3 else "declined",
                40 + j,
                f"2022-02-{j + 1:02}",
            )
            for j in range(i)
        ]
        result = {"Transactions": rows}
        if key == 1205:
            result["Chargebacks"] = [(1, "2022-03-01"), (3, "2022-02-01")]
        return result
    if key == 1194:
        players = [(1, 1), (2, 1), (3, 2), (4, 2)]
        matches = [(1, 1, 2, 1, 1), (2, 3, 4, 0, 2)]
        matches += [(3 + j, 1, 2, j % 3, j % 3) for j in range(i)]
        return {"Players": players, "Matches": matches}
    if key == 1204:
        weights = [200, 400, 400, 150] + [r.randrange(10, 50) for j in range(i)]
        return {"Queue": [(100 + i - j, f"P{j}", weight, j + 1) for j, weight in enumerate(weights)]}
    raise KeyError(key)
