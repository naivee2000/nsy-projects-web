from datetime import date, datetime, timedelta
from copy import deepcopy


def inputs(k, i, r, seed):
    t = deepcopy(seed)

    def day(j):
        return (date(2024, 1, 1) + timedelta(days=j)).isoformat()

    def stamp(h):
        return (datetime(2024, 1, 1) + timedelta(hours=h)).isoformat(sep=" ")

    if k in (3262, 3268):
        return {
            "EmployeeShifts": [
                (1, stamp(0), stamp(4)),
                (1, stamp(1), stamp(3)),
                (1, stamp(2), stamp(5)),
                (1, stamp(5), stamp(6)),
            ]
            + [(10 + j, stamp(0), stamp(1 + j % 7)) for j in range(i)]
        }
    if k == 3278:
        return {
            "Projects": [(1, "SQL", 3), (1, "Python", 3), (2, "SQL", 4)],
            "Candidates": [
                (1, "SQL", 4),
                (1, "Python", 2),
                (2, "SQL", 2),
                (2, "Python", 4),
                (3, "SQL", 5),
            ]
            + [(10 + j, "R", 3) for j in range(i)],
        }
    if k == 3293:
        return {
            "Products": [(j, ("A" if j % 2 else "B"), 20 + j * 5) for j in range(1, i + 3)],
            "Discounts": [("A", 10)],
        }
    if k == 3308:
        return {
            "Drivers": [(1, "A", 30, 6, 0), (2, "B", 35, 10, 1), (3, "C", 40, 15, 0)],
            "Vehicles": [(11, 1, "A", "Gas", 2000), (12, 2, "A", "Gas", 2000), (13, 3, "B", "EV", 2000)],
            "Trips": [(1, 11, 40, 20, 5), (2, 12, 60, 30, 5), (3, 13, 10, 8, 3)]
            + [(5 + j, 13, 20 + j, 10, 5) for j in range(i)],
        }
    if k == 3322:
        return {
            "SeasonStats": [
                (s, j, f"T{j:02}", 10, j % 3, j % 2, 10 - j % 3 - j % 2, 3 * j, 2 + (j % 3))
                for j in range(1, 4 + i)
                for s in (2020, 2021)
            ]
        }
    if k == 3328:
        return {
            "cities": [
                ("Alabama", "Ada"),
                ("Alabama", "Blue"),
                ("Alabama", "Hill"),
                ("Texas", "Austin"),
                ("Texas", "Blue"),
                ("Texas", "Red"),
                ("Utah", "Ute"),
            ]
            + [("Oregon", f"Oak{j:02}") for j in range(i)]
        }
    if k == 3338:
        return {
            "employees": [(1, 100, "A"), (2, 100, "A"), (3, 95, "A"), (4, 95, "A"), (5, 90, "A")]
            + [(10 + j, 30 + j, "B") for j in range(i)]
        }
    if k == 3358:
        return {
            "books": [(1, "A", "K", 2020, None), (2, "B", "M", 2021, 3.5)]
            + [(5 + j, f"B{j}", "X", 2020 + j % 4, None) for j in range(i)]
        }
    if k in (3368, 3374):
        txt = (
            ["hello  WORLD", "  ALL Caps  ", "a bCD", "Z"]
            if k == 3368
            else ["top-RATED  WORD", "ABC!dEF", "9HELLO world", "-LOUD  a--B", " FR-ONT-end "]
        )
        return {
            "user_content": list(enumerate(txt + [f"sTudy " + ("A " * j) + "wORD" for j in range(i)], 1))
        }
    if k in (3384, 3390):
        teams = [(1, "A"), (2, "A"), (3, "B"), (4, "B")]
        passes = [(1, "01:00", 2), (2, "02:00", 1), (1, "45:00", 3), (3, "45:01", 4), (4, "48:00", 2)]
        passes += [(1 if j % 2 == 0 else 2, f"{50 + j}:00", 2 if j % 2 == 0 else 1) for j in range(i)]
        return {"Teams": teams, "Passes": passes}
    if k == 3401:
        return {
            "SecretSanta": [
                (1, 2, 20 + i),
                (2, 3, 30),
                (3, 1, 10),
                (4, 5, 14),
                (5, 4, 11),
                (6, 7, 12),
                (7, 6, 13),
            ]
        }
    if k == 3415:
        names = ["P123A", "P1234A", "P12A", "123", "n123z456"]
        return {"Products": list(enumerate(names + [f"P{200 + j}X" for j in range(i)], 1))}
    if k == 3421:
        return {
            "Scores": [
                (u, "Math", v, d)
                for u, seq in [(1, [60, 95, 80]), (2, [80, 90, 80]), (3, [85])]
                + [(10 + j, [50, 60]) for j in range(i)]
                for d, v in zip([day(0), day(1), day(2)], seq)
            ]
        }
    if k == 3436:
        emails = ["1_a@aa.com", "a.b@abc.com", "a@a1.com", "a@@a.com", "x@example.org"]
        return {"Users": list(enumerate(emails + [f"a{j}@study.com" for j in range(i)], 1))}
    if k == 3451:
        ips = ["1.2.3.4", "0.0.0.0", "01.2.3.4", "256.0.0.1", "1.2.3", "01.2.3.4"]
        return {"logs": [(j, s, 200) for j, s in enumerate(ips + [f"0{j}.0.0.1" for j in range(i)], 1)]}
    if k == 3465:
        texts = ["SN1234-5678", "sn1234-5678", "SN1234-56789", "here SN1234-5678!", "SN123-5678"]
        return {
            "products": [
                (j, f"P{j}", s)
                for j, s in enumerate(texts + [f"check SN{1000 + j}-9832" for j in range(i)], 1)
            ]
        }
    if k == 3475:
        texts = ["ATGATATTAA", "AATGG", "GGGTAG", "TGAC", "GGTGA"]
        return {
            "Samples": [
                (j, s, "Sample") for j, s in enumerate(texts + ["AC" * j + "TG" for j in range(i)], 1)
            ]
        }
    if k == 3497:
        return {
            "UserActivity": [
                (1, day(0), "free_trial", 20),
                (1, day(1), "free_trial", 40),
                (1, day(7), "paid", 70),
                (2, day(0), "free_trial", 25),
            ]
            + [(10 + j, day(0), "free_trial", 20 + j) for j in range(i)]
        }
    if k in (3521, 3554):
        info = [(1, "Clothes", 5), (2, "Food", 6), (3, "Clothes", 4), (4, "Books", 5)]
        rows = (
            [(u, p, 1) for u in (1, 2, 3) for p in (1, 2, 3)]
            + [(1, 4, 2), (2, 4, 3)]
            + [(10 + j, 4, 1) for j in range(i)]
        )
        return {"ProductInfo": info, "ProductPurchases": rows}
    if k == 3564:
        return {
            "products": [(1, "A", "Home"), (2, "B", "Food"), (3, "C", "Games")],
            "sales": [(1, 1, "2023-12-31", 2, 2), (2, 2, "2024-01-01", 2, 3), (3, 3, "2024-04-01", 1, 9)]
            + [(5 + j, 1, "2024-04-01", 1, 2) for j in range(i)],
        }
    if k == 3570:
        books = [
            (1, "A", "X", "Tech", 2010, 2),
            (2, "B", "X", "Art", 2020, 2),
            (3, "C", "Y", "Tech", 2018, 1),
        ]
        records = [
            (1, 1, "R1", day(0), None),
            (2, 1, "R2", day(0), None),
            (3, 2, "R3", day(0), None),
            (4, 3, "R4", day(0), day(1)),
        ]
        records += [(5 + j, 3, f"R{j}", day(j + 2), day(j + 3)) for j in range(i)]
        return {"library_books": books, "borrowing_records": records}
    if k == 3580:
        reviews = [
            (u, day(j), rating)
            for u, seq in [(1, [5, 1, 2, 4]), (2, [1, 2, 2]), (3, [1, 3])]
            + [(10 + j, [2, 3, 5]) for j in range(i)]
            for j, rating in enumerate(seq)
        ]
        return {
            "employees": [(u, f"E{u}") for u in sorted({u for u, _, _ in reviews})],
            "performance_reviews": [(n, u, d, v) for n, (u, d, v) in enumerate(reviews, 1)],
        }
    if k == 3586:
        pts = [(j, f"P{j}", 30 + j) for j in range(1, 3 + i)]
        tests = [
            (1, 1, day(0), "Negative"),
            (2, 1, day(1), "Positive"),
            (3, 1, day(3), "Positive"),
            (4, 1, day(5), "Negative"),
            (5, 1, day(7), "Negative"),
        ]
        tests.extend((10 + j, p, day(j), "Positive") for j, (p, *_) in enumerate(pts[1:]))
        return {"patients": pts, "covid_tests": tests}
    if k == 3601:
        trips = [
            (1, 1, "2023-06-30", 100, 10),
            (2, 1, "2023-07-01", 120, 10),
            (3, 2, "2023-04-01", 120, 10),
            (4, 2, "2023-10-01", 100, 10),
        ]
        trips.extend((5 + j, 1, "2023-08-01", 25 + j, 2) for j in range(i))
        return {"drivers": [(1, "Ada"), (2, "Bo")], "trips": trips}
    if k == 3611:
        people = [(1, "A", "Sales"), (2, "B", "Tech"), (3, "C", "Sales")]
        rows = []
        for u, hours in [(1, 21), (2, 20), (3, 19)]:
            for week in range(2 + i % 3):
                for d, v in enumerate([8, 8, hours - 16]):
                    rows.append((len(rows) + 1, u, day(week * 7 + d), "Team", v))
        for j in range(i):
            rows.append((100 + j, 3, day(40 + j * 7), "Team", 1))
        return {"employees": people, "meetings": rows}
    if k == 3617:
        people = [(1, "A", "CS"), (2, "B", "Art"), (3, "C", "Math")]
        rows = []
        for u, seq in [(1, ["X", "Y", "Z"] * 2), (2, ["X", "Y"] * 3), (3, ["A", "B", "C"] * 2)]:
            for j, s in enumerate(seq):
                d = j + (3 if u == 3 and j >= 3 else 0)
                rows.append((len(rows) + 1, u, s, day(d), 1 + (i + j) % 4))
        rows[0] = (*rows[0][:-1], 1 + i / 4)
        return {"students": people, "study_sessions": rows}
    if k == 3626:
        shops = [(1, "A", "West"), (2, "B", "East"), (3, "C", "East")]
        items = [
            (1, 1, "High", 2, 100),
            (2, 1, "Low", 8 + i, 5),
            (3, 1, "Mid", 4, 30),
            (4, 2, "Hi", 1, 100),
            (5, 2, "Lo", 20, 10),
            (6, 3, "Upper", 10, 90),
            (7, 3, "Lower", 5, 10),
            (8, 3, "Middle", 6, 50),
        ]
        return {"stores": shops, "inventory": items}
    if k == 3642:
        books = [(1, "A", "X", "Art", 120), (2, "B", "Y", "Tech", 180), (3, "C", "X", "Art", 120)]
        rows = []
        for b, ratings in [(1, [1, 5, 2, 3, 3]), (2, [1, 5, 3, 3, 3]), (3, [2, 4, 4, 3] + [3] * i)]:
            for n, v in enumerate(ratings):
                rows.append((len(rows) + 1, b, f"R{n}", 40, v))
        return {"books": books, "reading_sessions": rows}
    return t
