from copy import deepcopy
from datetime import date, timedelta


def inputs(k, i, r, seed):
    t = deepcopy(seed)

    def dt(offset):
        return (date(2020, 1, 1) + timedelta(days=offset)).isoformat()

    if k == 1741:
        return {
            "Employees": [(1, "2023-01-01", 1, 4), (1, "2023-01-01", 10, 12)]
            + [(j + 2, "2023-01-02", 1, 2 + j) for j in range(i)]
        }
    if k == 1747:
        rows = [
            (1, 10, "2020-01-01 01:00:00", "2020-01-01 02:00:00"),
            (1, 20, "2020-01-01 02:00:00", "2020-01-01 03:00:00"),
            (2, 10, "2020-01-02 01:00:00", "2020-01-02 03:00:00"),
            (2, 10, "2020-01-02 02:00:00", "2020-01-02 04:00:00"),
        ]
        return {
            "LogInfo": rows + [(10 + j, 20, dt(j) + " 01:00:00", dt(j) + " 02:00:00") for j in range(i)]
        }
    if k == 1767:
        return {
            "Tasks": [(1, 3), (2, 2 + i)],
            "Executed": [(1, 1), (1, 2), (1, 3)] + [(2, j) for j in range(2, 2 + i, 2)],
        }
    if k == 1777:
        return {
            "Products": [(1, "store1", 12), (1, "store2", 5), (2, "store2", 0)]
            + [(5 + j, "store3", 10 + j) for j in range(i)]
        }
    if k == 1783:
        return {
            "Players": [(1, "A"), (2, "B"), (3, "C")],
            "Championships": [(2000 + j, 1, 2, 2, 1 if j % 2 else 2) for j in range(i + 1)],
        }
    if k == 1795:
        return {
            "Products": [
                (j, 0 if j % 2 else None, 11 + j, None if j % 3 else 3) for j in range(1, 3 + i)
            ]
        }
    if k == 1809:
        return {
            "Playback": [(1, 1, 10, 20), (2, 1, 30, 35), (3, 3, 10, 20)]
            + [(5 + j, 5 + j, 10, 20 + j) for j in range(i)],
            "Ads": [(1, 1, 10), (2, 3, 20), (3, 2, 31)],
        }
    if k == 1811:
        for j in range(i):
            ids = [row[0] for row in t["Users"]]
            medals = r.sample(ids, 3)
            t["Contests"].append([max(x[0] for x in t["Contests"]) + 1, *medals])
    elif k == 1821:
        return {
            "Customers": [(1, 2021, 0), (2, 2020, 10), (2, 2021, -5), (3, 2021, 10)]
            + [(4 + j, 2021, j) for j in range(i)]
        }
    elif k == 1831:
        return {
            "Transactions": [
                (1, "2022-05-01 09:00:00", 50),
                (2, "2022-05-01 18:00:00", 50),
                (3, "2022-05-01 22:00:00", 40),
            ]
            + [(5 + j, dt(j) + " 04:00:00", 20 + j) for j in range(i)]
        }
    elif k == 1841:
        return {
            "Teams": [(1, "A"), (2, "B"), (3, "C")],
            "Matches": [(1, 2, 1, 1), (2, 3, 2, 0), (3, 1, 0, 3 + i)],
        }
    elif k == 1843:
        return {
            "Accounts": [(1, 100), (2, 100), (3, 100)],
            "Transactions": [
                (1, 1, "Creditor", 110, "2020-12-01"),
                (2, 1, "Creditor", 110, "2021-01-01"),
                (3, 2, "Creditor", 100, "2021-01-01"),
                (4, 2, "Creditor", 110, "2021-02-01"),
                (5, 3, "Creditor", 110, "2021-01-01"),
                (6, 3, "Debtor", 120, "2021-02-01"),
            ]
            + [(8 + j, 1, "Debtor", 10 + j, "2021-01-20") for j in range(i)],
        }
    elif k == 1853:
        return {"Days": [(dt(30 * j + i),) for j in range(3 + i)]}
    elif k == 1867:
        return {
            "OrdersDetails": [(1, 1, 10), (1, 2, 2), (2, 1, 5), (2, 2, 7), (3, 1, 6)]
            + [(5 + j, 1, 4 + j % 3) for j in range(i)]
        }
    elif k == 1875:
        return {"Employees": [(j, f"E{j}", [30, 30, 10, 10, 20, 40][j % 6]) for j in range(1, 7 + i)]}
    elif k == 1890:
        return {
            "Logins": [
                (1, "2019-12-31 23:59:00"),
                (1, "2020-01-01 00:00:00"),
                (1, "2020-12-31 23:59:00"),
                (2, "2021-01-01 00:00:00"),
            ]
            + [(3, dt(j) + " 08:00:00") for j in range(i)]
        }
    elif k in (1892, 1949):
        edges = {(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (1, 5), (2, 5), (3, 4)}
        edges.update((1, 10 + j) for j in range(i))
        if k == 1949:
            return {"Friendship": sorted(edges)}
        return {
            "Friendship": sorted(edges),
            "Likes": [(2, 55), (3, 55), (4, 45), (1, 45)] + [(10 + j, 90 + j) for j in range(i)],
        }
    elif k == 1907:
        return {
            "Accounts": [(1, 19999), (2, 20000), (3, 50000), (4, 50001)]
            + [(j + 6, 1000 + j) for j in range(i)]
        }
    elif k in (1917, 1919):
        rows = [(u, s, "2020-01-01") for u in (1, 2, 3) for s in (1, 2, 3)] + [
            (4, 1, "2020-01-01"),
            (4, 1, "2020-01-01"),
            (4, 2, "2020-01-02"),
            (4, 3, "2020-01-02"),
        ]
        return {
            "Listens": rows + [(4, 2, "2020-01-01")] + [(5 + j, 1, dt(j)) for j in range(i)],
            "Friendship": [(1, 2), (3, 4)],
        }
    elif k in (1934, 1939):
        return {
            "Signups": [(j, "2019-01-01 00:00:00") for j in range(1, 4 + i)],
            "Confirmations": [
                (1, "2020-01-01 12:00:00", "confirmed"),
                (1, "2020-01-02 12:00:00", "timeout"),
                (2, "2020-01-01 10:00:00", "timeout"),
                (2, "2020-01-02 10:00:01", "confirmed"),
            ]
            + [(3 + j, dt(j) + " 01:00:00", "confirmed") for j in range(i)],
        }
    elif k == 1951:
        return {
            "Relations": [(j, f) for j in range(1, 4) for f in (10, 11)]
            + [(4, 11)]
            + [(5 + j, 20 + j) for j in range(i)]
        }
    elif k == 1965:
        return {
            "Employees": [(j, f"E{j}") for j in range(1, 4 + i)],
            "Salaries": [(j, j * 20) for j in range(2, 5 + i)],
        }
    elif k == 1972:
        rows = [
            (1, 2, "2020-01-01 01:00:00"),
            (1, 3, "2020-01-01 02:00:00"),
            (2, 1, "2020-01-01 03:00:00"),
            (3, 4, "2020-01-01 04:00:00"),
        ]
        return {"Calls": rows + [(6 + j, 1, dt(j + 2) + " 09:00:00") for j in range(i)]}
    elif k == 1978:
        return {
            "Employees": [
                (1, "A", None, 1000),
                (2, "B", 50, 30000),
                (3, "C", 90, 29999),
                (4, "D", 1, 2000),
            ]
            + [(5 + j, f"E{j}", 1, 2500 + j) for j in range(i)]
        }
    elif k == 1988:
        return {
            "Schools": [(1, 2), (2, 1), (3, 10)] + [(6 + j, 4 + j) for j in range(i)],
            "Exam": [(100, 2), (90, 3), (80, 10)],
        }
    elif k == 1990:
        return {
            "Experiments": [
                (j, ["IOS", "Web"][j % 2], ["Sports", "Reading"][j % 2]) for j in range(1, 3 + i)
            ]
        }
    elif k in (2004, 2010):
        return {
            "Candidates": [
                (1, "Senior", 30000),
                (2, "Senior", 40000),
                (3, "Junior", 1000),
                (4, "Junior", 2000),
            ]
            + [(5 + j, "Junior", 3000 + j) for j in range(i)]
        }
    elif k == 2020:
        return {
            "Subscriptions": [
                (1, "2020-01-01", "2022-01-01"),
                (2, "2020-01-01", "2020-12-31"),
                (3, "2021-02-01", "2022-01-01"),
                (4, "2020-01-01", "2022-12-31"),
            ]
            + [(10 + j, "2021-03-01", "2021-12-21") for j in range(i)],
            "Streams": [(1, 1, "2020-06-01"), (2, 1, "2021-06-01"), (3, 4, "2020-12-31")],
        }
    return t
