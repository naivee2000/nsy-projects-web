from datetime import date, datetime, timedelta


def inputs(k, i, r, seed):
    def day(j):
        return (date(2024, 1, 1) + timedelta(days=j)).isoformat()

    if k == 3657:
        rows = []
        for u, types, length in [
            (1, ["purchase"] * 3, 30),
            (2, ["purchase"] * 4 + ["refund"], 40),
            (3, ["purchase"] * 3, 29),
            (4, ["purchase"] * 5 + ["refund"], 40 + i),
        ]:
            rows.extend(
                (10 * u + j, u, day(length if j == len(types) - 1 else j), 20 + j, v)
                for j, v in enumerate(types)
            )
        return {"customer_transactions": rows}
    if k == 3673:
        rows = []
        for u, n, d, click, buy in [
            (1, 5, 31, 0, 0),
            (2, 5, 30, 0, 0),
            (3, 5, 40, 1, 0),
            (4, 6, 42, 0, 1),
            (5, 5 + i, 35 + i, 0, 0),
        ]:
            events = (
                ["app_open"] + ["scroll"] * n + ["click"] * click + ["purchase"] * buy + ["app_close"]
            )
            for j, v in enumerate(events):
                timestamp = (
                    datetime(2024, 1, 1) + timedelta(minutes=d if j == len(events) - 1 else j)
                ).isoformat(sep=" ")
                rows.append((len(rows) + 1, u, timestamp, v, f"S{u}", None))
        return {"app_events": rows}
    if k == 3705:
        rows = []
        for u, times, ratings in [
            (1, [11, 12, 18, 9, 10], [5, 4, 4, None, None]),
            (2, [11, 12, 14, 9, 10], [5, None, None, None, None]),
            (3, [11, 19, 21], [4, 4, 4]),
            (4, [11] * i, [5] * i),
        ]:
            for j, (h, v) in enumerate(zip(times, ratings)):
                rows.append((len(rows) + 1, u, day(j) + f" {h:02}:00:00", 20, "card", v))
        return {"restaurant_orders": rows}
    if k == 3716:
        rows = []
        for u, low, n in [(1, 15, 60), (2, 20, 65), (3, 10, 59), (4, 9, 60 + i)]:
            for d, v, plan, amount in [(0, "start", "premium", 40), (n, "downgrade", "basic", low)]:
                rows.append((len(rows) + 1, u, day(d), v, plan, amount))
        return {"subscription_events": rows}
    if k == 3764:
        rows = []
        for u, n, grade in [(1, 5, 4), (2, 4, 5), (3, 6, 3), (4, 5 + i, 5)]:
            for j in range(n):
                rows.append((u, j + 1, f"Course{j + 1}", day(j), grade))
        return {"course_completions": rows}
    if k == 3793:
        return {
            "prompts": [
                (u, f"Q{j}", v)
                for u, vals in [
                    (1, [10, 20, 30]),
                    (2, [9, 9, 9]),
                    (3, [2, 8]),
                    (4, list(range(2, 4 + i))),
                ]
                for j, v in enumerate(vals)
            ]
        }
    if k == 3808:
        return {
            "reactions": [
                (u, j, v)
                for u, seq in [
                    (1, ["like"] * 3 + ["love"] * 2),
                    (2, ["like"] * 2 + ["love", "wow", "sad"]),
                    (3, ["like"] * 4),
                    (4, ["love"] * (4 + i) + ["like"]),
                ]
                for j, v in enumerate(seq, 1)
            ]
        }
    if k == 3832:
        rows = []
        for start, action, length in [(0, "view", 5), (7, "click", 5), (14, "click", 5)]:
            rows.extend((1, day(start + j), action) for j in range(length))
        rows.extend((2, day(j), "login") for j in range(5 + i))
        rows.extend((3, day(j), "view") for j in range(5))
        rows.append((3, day(2), "click"))
        return {"activity": rows}
    raise KeyError(k)
