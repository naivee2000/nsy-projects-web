from copy import deepcopy
from datetime import date, datetime, timedelta


def inputs(k, i, r, seed):
    t = deepcopy(seed)

    def day(j):
        return (date(2024, 2, 1) + timedelta(days=j)).isoformat()

    def stamp(hours):
        return (datetime(2024, 2, 1) + timedelta(hours=hours)).isoformat(sep=" ")

    if k == 3050:
        return {"Toppings": [(f"T{j:02}", 2 + j % 4 + i / 100) for j in range(3 + i % 5)]}
    if k == 3051:
        pairs = [
            (1, "Python"),
            (1, "Tableau"),
            (1, "PostgreSQL"),
            (2, "Python"),
            (2, "Tableau"),
            (2, "C++"),
        ]
        return {"Candidates": pairs + [(10 + j, "Python") for j in range(i)]}
    if k == 3052:
        return {
            "Inventory": [
                (1, "prime_eligible", "A", 5000 + i * 100),
                (2, "prime_eligible", "B", 2500),
                (3, "not_prime", "C", 100),
                (4, "not_prime", "D", 150),
            ]
        }
    if k == 3053:
        return {
            "Triangles": [(1, 1, 2), (2, 2, 2), (2, 2, 3), (3, 4, 5), (1, 2, 9)]
            + [(6 + j, 6 + j, 8 + j) for j in range(i)]
        }
    if k == 3054:
        return {"Tree": [(1, None)] + [(j, r.randrange(1, j)) for j in range(2, 3 + i)]}
    if k == 3056:
        return {
            "Activities": [(1, 1, "send", 2), (2, 1, "open", 8), (3, 2, "open", 5)]
            + [(10 + j, 3, "send" if j % 2 else "open", i + j + 1) for j in range(i)],
            "Age": [(1, "21-25"), (2, "21-25"), (3, "26-30")],
        }
    if k == 3057:
        employees = [(1, "A", "X"), (2, "B", "X"), (3, "C", "X"), (4, "D", "Y")]
        projects = [(1, 1, 20), (2, 2, 40), (1, 3, 60), (2, 4, 80)]
        for j in range(i):
            employees.append((5 + j, f"Peer{j}", "Y"))
            projects.append((3 + j, 5 + j, 80))
        return {"Project": projects, "Employees": employees}
    if k == 3058:
        return {"Friends": [(1, 2), (1, 3), (2, 3), (3, 4)] + [(4, 10 + j) for j in range(i)]}
    if k == 3059:
        return {
            "Emails": [(1, "a@x.com"), (2, "b@x.com"), (3, "c@y.org")]
            + [(5 + j, f"p{j}@z.com") for j in range(i)]
        }
    if k == 3060:
        times = [
            (1, 0, 1, "Viewer"),
            (1, 13, 14, "Viewer"),
            (2, 0, 1, "Viewer"),
            (2, 2, 3, "Streamer"),
            (3, 0, 1, "Streamer"),
            (3, 14, 15, "Streamer"),
        ]
        times.extend((5 + j, 4, 5, "Viewer") for j in range(i))
        return {
            "Sessions": [(u, stamp(a), stamp(b), n, kind) for n, (u, a, b, kind) in enumerate(times, 1)]
        }
    if k == 3061:
        return {"Heights": list(enumerate([4, 0, 2, 0, 4, 1] + [r.randrange(6) for _ in range(i)], 1))}
    if k in (3087, 3103):
        texts = (
            ["#a news", "#b news", "#c news", "#d news", "#a again"]
            if k == 3087
            else ["#a #b", "#b #c", "#a #d", "#c #d"]
        )
        texts += [f"news #tag{j % 5}" for j in range(i)]
        return {"Tweets": [(j, j, day(j % 28), txt) for j, txt in enumerate(texts, 1)]}
    if k == 3089:
        return {
            "Posts": [
                (n + 1, u, day(d))
                for n, (u, d) in enumerate(
                    [
                        (1, 0),
                        (1, 0),
                        (1, 6),
                        (1, 7),
                        (1, 14),
                        (1, 21),
                        (2, 0),
                        (2, 7),
                        (2, 14),
                        (2, 21),
                        (2, 28),
                    ]
                    + [(3, j % 6) for j in range(i)]
                )
            ]
        }
    if k == 3118:
        return {
            "Users": [(1, "Premium"), (2, "VIP"), (3, "Standard")]
            + [(5 + j, "Premium") for j in range(i)],
            "Purchases": [(1, "2023-11-03", 10), (3, "2023-11-03", 90), (2, "2023-11-10", 3)]
            + [(5 + j, "2023-11-24", j + 2) for j in range(i)],
        }
    if k == 3124:
        return {
            "Contacts": [(j, f"P{j:02}", "Z") for j in range(1, 5 + i)],
            "Calls": [
                (j, kind, 40 + 5 * j + (kind == "incoming"))
                for j in range(1, 5 + i)
                for kind in ("incoming", "outgoing")
            ],
        }
    if k == 3126:
        return {
            "Servers": [
                (j, stamp(a), state)
                for j in range(1, i + 3)
                for a, state in [(0, "start"), (13, "stop"), (24, "start"), (35, "stop")]
            ]
        }
    if k == 3140:
        return {"Cinema": list(enumerate([1, 1, 1, 0, 1, 1, 1, 0, 1, 0] + [j % 2 for j in range(i)], 1))}
    if k == 3150:
        texts = ["a" * 140, "a" * 141, "@a @b @c", "@a @b @c @d", "#a #b #c", "#a #b #c #d", "ok"]
        return {"Tweets": list(enumerate(texts + [f"@u{j} ok" for j in range(i)], 1))}
    if k == 3156:
        return {
            "Tasks": [
                (1, 1, stamp(0), stamp(3)),
                (2, 1, stamp(2), stamp(4)),
                (3, 1, stamp(4), stamp(5)),
                (4, 2, stamp(1), stamp(1.5)),
            ]
            + [(10 + j, 3, stamp(2 * j), stamp(2 * j + 1)) for j in range(i)]
        }
    if k == 3166:
        return {
            "ParkingTransactions": [
                (1, 1, stamp(0), stamp(2), 10),
                (2, 1, stamp(3), stamp(4), 8),
                (2, 1, stamp(6), stamp(8), 6),
            ]
            + [(3, 10 + j, stamp(0), stamp(j + 1), 4 + j) for j in range(i)]
        }
    if k == 3172:
        return {
            "emails": [(n, n, day(0)) for n in range(1, 4 + i)],
            "texts": [
                (1, 1, "Verified", day(1)),
                (2, 2, "Verified", day(0)),
                (3, 3, "Not Verified", day(1)),
            ]
            + [(5 + j, 4 + j, "Verified", day(2)) for j in range(i)],
        }
    if k in (3182, 3188):
        students = [(n, f"S{n}", "CS") for n in range(1, 4 + i)]
        courses = [
            (1, "Math", 3, "CS"),
            (2, "Data", 3, "CS"),
            (3, "Lab", 2, "CS"),
            (4, "Arts", 2, "Arts"),
        ]
        if k == 3182:
            records = [(1, c, "Fall", "A") for c in (1, 2, 3)] + [
                (2, 1, "Fall", "A"),
                (3, 2, "Fall", "B"),
            ]
        else:
            courses = [(*c, "yes" if c[0] == 1 else "no") for c in courses]
            records = [
                (u, c, "Fall", "A" if c == 1 else "B", 3.0) for u in (1, 2) for c in (1, 2, 3)
            ] + [(2, 4, "Fall", "F", 0.0), (3, 1, "Fall", "A", 4.0)]
            records.extend([(3, 2, "Fall", "A", 4.0), (3, 2, "Spring", "B", 3.0)])
            records.extend(
                [(4, 1, "Fall", "A", 4.0), (4, 2, "Fall", "C", 3.0), (4, 3, "Fall", "A", 4.0)]
            )
        return {"students": students, "courses": courses, "enrollments": records}
    if k == 3198:
        return {
            "cities": [("CA", "Oak"), ("CA", "Ash"), ("NY", "Pine")]
            + [("TX", f"City{j:02}") for j in range(i)]
        }
    if k == 3204:
        return {"user_permissions": [(1, 6), (2, 3)] + [(j + 3, 2 | (1 << (j % 5))) for j in range(i)]}
    if k == 3214:
        return {
            "user_transactions": [
                (1, 1, 50, "2020-01-01"),
                (2, 1, 50, "2020-02-01"),
                (3, 1, 120, "2021-01-01"),
                (4, 1, 300, "2023-01-01"),
            ]
            + [(5 + j, 2, 30 + j, day(j)) for j in range(i)]
        }
    if k == 3220:
        return {"transactions": [(j + 1, j + 2, day(j % 3)) for j in range(3 + i)]}
    if k == 3230:
        products = [(1, "A", 10), (2, "B", 20), (3, "C", 5)]
        return {
            "Products": products,
            "Transactions": [(1, 1, 1, day(0), 10), (2, 1, 2, day(1), 20), (3, 2, 3, day(0), 5)]
            + [(5 + j, 3, 1 + j % 3, day(j), 15 + j) for j in range(i)],
        }
    if k == 3236:
        return {
            "Employees": [(1, "CEO", None, 500)]
            + [(j, f"E{j}", max(1, j // 2), 200 + 10 * j) for j in range(2, 4 + i)]
        }
    if k in (3246, 3252):
        return {
            "TeamStats": [(j, f"T{j:02}", 10, j % 4, j % 3, 10 - j % 4 - j % 3) for j in range(1, 7 + i)]
        }
    return t
