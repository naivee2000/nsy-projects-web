from __future__ import annotations

from datetime import date, timedelta


# Unscheduled full-day NYSE closures are deliberately explicit. The recurring
# holiday rules below cannot derive these dates, and treating them as missing
# provider observations would either reject valid history or silently shorten a
# comparison. This covers the app's supported modern-history window.
SPECIAL_CLOSURES = {
    date(2001, 9, 11),
    date(2001, 9, 12),
    date(2001, 9, 13),
    date(2001, 9, 14),
    date(2004, 6, 11),
    date(2007, 1, 2),
    date(2012, 10, 29),
    date(2012, 10, 30),
    date(2018, 12, 5),
    date(2025, 1, 9),
}


def _observed(day: date) -> date:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def _nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> date:
    current = date(year, month, 1)
    current += timedelta(days=(weekday - current.weekday()) % 7)
    return current + timedelta(weeks=occurrence - 1)


def _last_weekday(year: int, month: int, weekday: int) -> date:
    current = date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1)
    return current - timedelta(days=(current.weekday() - weekday) % 7)


def _easter(year: int) -> date:
    """Gregorian Easter date, used for the NYSE Good Friday closure."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    line = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * line) // 451
    month = (h + line - 7 * m + 114) // 31
    day = (h + line - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def us_market_holidays(year: int) -> set[date]:
    holidays = {
        _observed(date(year, 1, 1)),
        _nth_weekday(year, 1, 0, 3),
        _nth_weekday(year, 2, 0, 3),
        _easter(year) - timedelta(days=2),
        _last_weekday(year, 5, 0),
        _observed(date(year, 7, 4)),
        _nth_weekday(year, 9, 0, 1),
        _nth_weekday(year, 11, 3, 4),
        _observed(date(year, 12, 25)),
    }
    if year >= 2022:
        holidays.add(_observed(date(year, 6, 19)))
    return holidays


def is_us_trading_day(day: date) -> bool:
    if day.weekday() >= 5:
        return False
    holidays: set[date] = set()
    for year in {day.year - 1, day.year, day.year + 1}:
        holidays.update(us_market_holidays(year))
    return day not in holidays and day not in SPECIAL_CLOSURES


def trading_dates(start: date, end: date) -> list[date]:
    dates: list[date] = []
    current = start
    while current <= end:
        if is_us_trading_day(current):
            dates.append(current)
        current += timedelta(days=1)
    return dates
