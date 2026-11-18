"""Database catalog and independently computed fixtures for the verified local batches."""
from __future__ import annotations

import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1] / "database_catalog"
INVENTORY = {item["id"]: item for item in json.loads((ROOT / "inventory.json").read_text())}
CREDITS = {"Easy": 1, "Medium": 2, "Hard": 3}


def table(columns, rows):
    return {"columns": list(columns), "rows": list(rows)}


def fixture(tables, columns, rows, **parameters):
    return {"tables": tables, "expected": table(columns, rows), "parameters": parameters}


def sample_set(seed, factory):
    random = Random(seed)
    cases = [factory(random, i) for i in range(16)]
    assert len({json.dumps(c, sort_keys=True) for c in cases}) == len(cases)
    return cases


def join_case(rng, i):
    people = [(1, "Li", "Ada"), (2, "Kim", "Ben")]
    addresses = [(8, 2, "Austin", "TX")]
    if i:
        people += [(j, rng.choice(["Li", "Kim"]), f"Name{rng.randrange(20)}")
                   for j in range(3, 4 + i % 4)]
        addresses = [(j + 8, rng.randrange(1, len(people) + 3), rng.choice(["Paris", None]), "TX")
                     for j in range(i)]
    rows = [(first, last, city, state) for key, last, first in people
            for city, state in ([(city, state) for _, person, city, state in addresses if key == person]
                                or [(None, None)])]
    return fixture({"Person": people, "Address": addresses}, ("firstName", "lastName", "city", "state"), rows)


def salary_case(rng, i, parameter=False):
    salaries = [100, 300, 300, 200] if i == 0 else [300, 300] if i == 1 else [
        rng.randrange(1, 12) * 10 for _ in range(i - 2)
    ]
    n = (i % 5) + 1 if parameter else 2
    unique = sorted(set(salaries), reverse=True)
    name = f"getNthHighestSalary({n})" if parameter else "SecondHighestSalary"
    return fixture({"Employee": list(enumerate(salaries, 1))}, (name,),
                   [(unique[n - 1] if len(unique) >= n else None,)], **({"n": n} if parameter else {}))


def rank_case(rng, i):
    scores = [4.0, 5.0, 4.0, 2.0] if i == 0 else [float(rng.randrange(1, 20)) / 2 for _ in range(i)]
    distinct = sorted(set(scores), reverse=True)
    return fixture({"Scores": list(enumerate(scores, 1))}, ("score", "rank"),
                   [(score, distinct.index(score) + 1) for score in sorted(scores, reverse=True)])


def email_case(rng, i, mutate=False):
    size = i + 3
    entries = [(f"user{rng.randrange(max(2, i // 2))}@example.test") for _ in range(size)]
    people = list(reversed(list(enumerate(entries, 1))))
    if mutate:
        return fixture({"Person": people}, ("id", "email"),
                       [(idx, email) for idx, email in people if idx == entries.index(email) + 1])
    return fixture({"Person": people}, ("Email",), [(e,) for e in sorted(set(entries)) if entries.count(e) > 1])


def products_case(rng, i):
    products = [(j, rng.choice(["Y", "N"]), rng.choice(["Y", "N"])) for j in range(i + 4)]
    return fixture({"Products": products}, ("product_id",), [(j,) for j, low, rec in products if low == rec == "Y"])


def big_case(rng, i):
    world = [(f"C{j}", "Region", rng.choice([2999999, 3000000, 1]),
              rng.choice([24999999, 25000000, 0]), 7) for j in range(i + 3)]
    return fixture({"World": world}, ("name", "population", "area"),
                   [(name, pop, area) for name, _, area, pop, _ in world if pop >= 25000000 or area >= 3000000])


def pivot_case(rng, i):
    products = [(j, store, rng.randrange(1, 99)) for j in range(1, 3 + i % 4)
                for store in ["Ax", "By", "Cz", "Dw"][:2 + i % 3] if rng.randrange(3)]
    stores = sorted({store for _, store, _ in products})
    product_ids = sorted({j for j, _, _ in products})
    prices = {(j, store): price for j, store, price in products}
    return fixture({"Products": products}, ("product_id", *stores),
                   [(j, *(prices.get((j, store)) for store in stores)) for j in product_ids])


def exercise(topic, schema, cases, sql, pandas, wrong, *, runner="query", ordered=False, advice=""):
    return {"topic": topic, "schema": schema, "cases": cases, "sql": sql, "pandas": pandas,
            "runner": runner, "ordered": ordered, "wrong": wrong, "advice": advice}


EMAIL_SCHEMA = {"Person": [("id", "INT PRIMARY KEY"), ("email", "VARCHAR(128)")]}
SALARY_SCHEMA = {"Employee": [("id", "INT PRIMARY KEY"), ("salary", "INT")]}
CATALOG = {
    175: exercise("Joins",
        {"Person": [("personId", "INT PRIMARY KEY"), ("lastName", "VARCHAR(64)"), ("firstName", "VARCHAR(64)")],
         "Address": [("addressId", "INT PRIMARY KEY"), ("personId", "INT"), ("city", "VARCHAR(64)"), ("state", "VARCHAR(64)")]},
        sample_set(175, join_case),
        "SELECT firstName,lastName,city,state FROM Person LEFT JOIN Address USING(personId);",
        "return Person.merge(Address, how='left', on='personId')[['firstName','lastName','city','state']]",
        ["SELECT firstName,lastName,city,state FROM Person JOIN Address USING(personId)",
         "SELECT DISTINCT firstName,lastName,city,state FROM Person JOIN Address USING(personId)"]),
    176: exercise("Aggregation", SALARY_SCHEMA, sample_set(176, salary_case),
        "SELECT (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1) AS SecondHighestSalary;",
        "values = Employee.salary.drop_duplicates().sort_values(ascending=False).tolist()\nreturn pd.DataFrame({'SecondHighestSalary': [values[1] if len(values) > 1 else None]})",
        ["SELECT MAX(salary) AS SecondHighestSalary FROM Employee",
         "SELECT (SELECT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1) AS SecondHighestSalary"]),
    177: exercise("Aggregation", SALARY_SCHEMA, sample_set(177, lambda r, i: salary_case(r, i, True)),
        """DELIMITER //
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT READS SQL DATA
BEGIN
  DECLARE off_idx INT DEFAULT N - 1;
  RETURN (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET off_idx);
END//
DELIMITER ;
""",
        "values = Employee.salary.drop_duplicates().sort_values(ascending=False).tolist()\nreturn pd.DataFrame({f'getNthHighestSalary({n})': [values[n-1] if len(values) >= n else None]})",
        ["CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT READS SQL DATA RETURN (SELECT MAX(salary) FROM Employee);",
         "CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT READS SQL DATA RETURN NULL;"],
        runner="function", advice="Define getNthHighestSalary(N INT). The judge calls it with each test's n."),
    178: exercise("Ranking", {"Scores": [("id", "INT PRIMARY KEY"), ("score", "DECIMAL(8,2)")]},
        sample_set(178, rank_case),
        "SELECT score,DENSE_RANK() OVER (ORDER BY score DESC) AS `rank` FROM Scores ORDER BY score DESC;",
        "result = Scores[['score']].sort_values('score', ascending=False).copy()\nresult['rank'] = result.score.rank(method='dense', ascending=False).astype(int)\nreturn result",
        ["SELECT score,RANK() OVER (ORDER BY score DESC) AS `rank` FROM Scores ORDER BY score DESC",
         "SELECT score,DENSE_RANK() OVER (ORDER BY score DESC) AS `rank` FROM Scores ORDER BY score ASC"],
        ordered=True),
    182: exercise("Aggregation", EMAIL_SCHEMA, sample_set(182, email_case),
        "SELECT email AS Email FROM Person GROUP BY email HAVING COUNT(*) > 1;",
        "return Person.loc[Person.email.duplicated(keep=False), ['email']].drop_duplicates().rename(columns={'email':'Email'})",
        ["SELECT DISTINCT email AS Email FROM Person",
         "SELECT email AS Email FROM Person WHERE id > 1"]),
    196: exercise("Mutations", EMAIL_SCHEMA, sample_set(196, lambda r, i: email_case(r, i, True)),
        "DELETE a FROM Person a JOIN Person b ON a.email=b.email AND a.id>b.id;",
        "Person.sort_values('id', inplace=True)\nPerson.drop_duplicates('email', inplace=True)",
        ["DELETE FROM Person WHERE id > 1;", "DELETE a FROM Person a JOIN Person b ON a.email=b.email AND a.id<b.id;"],
        runner="mutation", advice="Update Person in place. The judge inspects that table after your code finishes."),
    595: exercise("Filtering",
        {"World": [("name", "VARCHAR(64) PRIMARY KEY"), ("continent", "VARCHAR(64)"), ("area", "INT"),
                   ("population", "INT"), ("gdp", "BIGINT")]}, sample_set(595, big_case),
        "SELECT name,population,area FROM World WHERE area>=3000000 OR population>=25000000;",
        "return World.loc[(World.area >= 3000000) | (World.population >= 25000000), ['name','population','area']]",
        ["SELECT name,population,area FROM World WHERE area>=3000000 AND population>=25000000",
         "SELECT name,population,area FROM World WHERE area>3000000 OR population>25000000"]),
    1757: exercise("Filtering",
        {"Products": [("product_id", "INT PRIMARY KEY"), ("low_fats", "CHAR(1)"), ("recyclable", "CHAR(1)")]},
        sample_set(1757, products_case),
        "SELECT product_id FROM Products WHERE low_fats='Y' AND recyclable='Y';",
        "return Products.loc[(Products.low_fats == 'Y') & (Products.recyclable == 'Y'), ['product_id']]",
        ["SELECT product_id FROM Products WHERE low_fats='Y' OR recyclable='Y'",
         "SELECT product_id FROM Products WHERE recyclable='Y'"]),
    2252: exercise("Reshaping",
        {"Products": [("product_id", "INT"), ("store", "VARCHAR(100)"), ("price", "INT")]}, sample_set(2252, pivot_case),
        """DELIMITER //
CREATE PROCEDURE PivotProducts()
BEGIN
  SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(store=', QUOTE(store), ',price,NULL)) AS `',
    REPLACE(store, '`', '``'), '`') ORDER BY store SEPARATOR ',') INTO @cols FROM Products;
  SET @stmt = CONCAT('SELECT product_id,', @cols, ' FROM Products GROUP BY product_id');
  PREPARE pivot FROM @stmt;
  EXECUTE pivot;
  DEALLOCATE PREPARE pivot;
END//
DELIMITER ;
""",
        "return Products.pivot(index='product_id', columns='store', values='price').sort_index(axis=1).reset_index()",
        ["CREATE PROCEDURE PivotProducts() SELECT DISTINCT product_id FROM Products;",
         "CREATE PROCEDURE PivotProducts() SELECT product_id, MAX(price) AS Ax FROM Products GROUP BY product_id;"],
        runner="procedure", advice="Define the procedure PivotProducts(). Store names determine the output columns."),
}


def manager_case(rng, i):
    employees = [(1, "Lead", 80, None), (2, "Higher", 81, 1), (3, "Equal", 80, 1)] + [
        (num, f"E{num}", rng.randrange(60, 100), rng.randrange(1, num)) for num in range(4, i + 4)]
    salary_by_id = {ident: salary for ident, _, salary, _ in employees}
    return fixture({"Employee": employees}, ("Employee",),
                   [(name,) for _, name, salary, manager in employees
                    if manager in salary_by_id and salary > salary_by_id[manager]])


def no_order_case(rng, i):
    customers = [(j, f"C{j}") for j in range(1, i + 4)]
    orders = [(1, 2), (2, 2)] + [(j + 3, rng.randrange(1, len(customers) + 1)) for j in range(i)]
    buyers = {buyer for _, buyer in orders}
    return fixture({"Customers": customers, "Orders": orders}, ("Customers",),
                   [(name,) for ident, name in customers if ident not in buyers])


def weather_case(rng, i):
    from datetime import date, timedelta

    start = date(2024, 2, 25)
    days = [(0, 8), (2, 18), (3, 20), (4, 20)] + [(j, rng.randrange(-5, 28)) for j in range(6, 6 + i)]
    temps = dict(days)
    keys = rng.sample(range(101, 301), len(days))
    weather = [(ident, (start + timedelta(days=day)).isoformat(), temperature)
               for ident, (day, temperature) in zip(keys, days)]
    return fixture({"Weather": weather}, ("id",),
                   [(ident,) for ident, (day, temp) in zip(keys, days)
                    if day - 1 in temps and temp > temps[day - 1]])


def referee_case(rng, i):
    people = [(j, f"Customer{j}", None if j < 3 else rng.choice([None, 1, 2])) for j in range(1, i + 5)]
    people[2] = (3, "Filtered", 2)
    people[3] = (4, "Referred", 1)
    return fixture({"Customer": people}, ("name",), [(name,) for _, name, ref in people if ref != 2])


def cinema_case(rng, i):
    ratings = rng.sample(range(1, 100), i + 4)
    movies = [(j, f"Movie{j}", "boring" if j % 3 == 0 else "fun", number / 10)
              for j, number in enumerate(ratings, 1)]
    return fixture({"Cinema": movies}, ("id", "movie", "description", "rating"),
                   sorted((movie for movie in movies if movie[0] % 2 and movie[2] != "boring"),
                          key=lambda movie: -movie[3]))


def cooperation_case(rng, i):
    pairs = [(1, 1)] * 3 + [(2, 1)] * 2 + [(2, 2)] + [
        (rng.randrange(1, 5), rng.randrange(1, 5)) for _ in range(i)]
    return fixture({"ActorDirector": [(a, d, j) for j, (a, d) in enumerate(pairs, 1)]},
                   ("actor_id", "director_id"), [pair for pair in set(pairs) if pairs.count(pair) >= 3])


def tweet_case(rng, i):
    tweets = [(1, "a" * 15), (2, "b" * 16)] + [
        (j, ("hi ! " * rng.randrange(1, 6)).strip()) for j in range(3, i + 3)]
    return fixture({"Tweets": tweets}, ("tweet_id",), [(ident,) for ident, message in tweets if len(message) > 15])


def follower_case(rng, i):
    pairs = [(9, 3), (4, 9), (4, 1)] + rng.sample(
        [(u, f) for u in range(10, 16) for f in range(1, 8)], i)
    return fixture({"Followers": pairs}, ("user_id", "followers_count"),
                   [(u, sum(user == u for user, _ in pairs)) for u in sorted({u for u, _ in pairs})])


def primary_department_case(rng, i):
    employees = [(1, 2, "N"), (2, 1, "N"), (2, 3, "Y")]
    for employee in range(3, i + 3):
        departments = rng.sample(range(1, 8), rng.randrange(1, 4))
        primary = departments[-1] if len(departments) > 1 else None
        employees.extend((employee, d, "Y" if d == primary else "N") for d in departments)
    return fixture({"Employee": employees}, ("employee_id", "department_id"),
                   [(e, d) for e, d, flag in employees if flag == "Y" or sum(emp == e for emp, _, _ in employees) == 1])


def bonus_case(rng, i):
    employees = [(1, "Mike", 80), (2, "Alex", 100), (3, "Ben", 90)] + [
        (j, rng.choice(["Ming", "Ada", "Zoe"]), rng.randrange(60, 120)) for j in range(4, i + 4)]
    rng.shuffle(employees)
    return fixture({"Employees": employees}, ("employee_id", "bonus"),
                   [(k, salary if k % 2 and not name.startswith("M") else 0) for k, name, salary in sorted(employees)])


CATALOG.update({
    181: exercise("Joins",
        {"Employee": [("id", "INT PRIMARY KEY"), ("name", "VARCHAR(64)"), ("salary", "INT"), ("managerId", "INT")]},
        sample_set(181, manager_case),
        "SELECT e.name AS Employee FROM Employee e JOIN Employee m ON e.managerId=m.id WHERE e.salary>m.salary",
        "joined = Employee.merge(Employee, left_on='managerId', right_on='id', suffixes=('_e','_m'))\nreturn joined.loc[joined.salary_e > joined.salary_m, ['name_e']].rename(columns={'name_e':'Employee'})",
        ["SELECT e.name AS Employee FROM Employee e JOIN Employee m ON e.managerId=m.id WHERE e.salary>=m.salary",
         "SELECT name AS Employee FROM Employee WHERE managerId IS NOT NULL"]),
    183: exercise("Joins",
        {"Customers": [("id", "INT PRIMARY KEY"), ("name", "VARCHAR(64)")],
         "Orders": [("id", "INT PRIMARY KEY"), ("customerId", "INT")]},
        sample_set(183, no_order_case),
        "SELECT name AS Customers FROM Customers c WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.customerId=c.id)",
        "return Customers.loc[~Customers.id.isin(Orders.customerId), ['name']].rename(columns={'name':'Customers'})",
        ["SELECT name AS Customers FROM Customers WHERE id IN (SELECT customerId FROM Orders)",
         "SELECT name AS Customers FROM Customers WHERE id NOT IN (SELECT id FROM Orders)"]),
    197: exercise("Dates", {"Weather": [("id", "INT PRIMARY KEY"), ("recordDate", "DATE"), ("temperature", "INT")]},
        sample_set(197, weather_case),
        "SELECT a.id FROM Weather a JOIN Weather b ON DATEDIFF(a.recordDate,b.recordDate)=1 WHERE a.temperature>b.temperature",
        "prior = Weather.assign(next_day=Weather.recordDate + pd.Timedelta(days=1))\njoined = Weather.merge(prior, left_on='recordDate', right_on='next_day', suffixes=('', '_prior'))\nreturn joined.loc[joined.temperature > joined.temperature_prior, ['id']]",
        ["SELECT a.id FROM Weather a JOIN Weather b ON DATEDIFF(a.recordDate,b.recordDate)=1 WHERE a.temperature>=b.temperature",
         "SELECT id FROM (SELECT id,temperature,LAG(temperature) OVER(ORDER BY recordDate) AS prior FROM Weather) t WHERE temperature>prior"]),
    584: exercise("Filtering",
        {"Customer": [("id", "INT PRIMARY KEY"), ("name", "VARCHAR(64)"), ("referee_id", "INT")]},
        sample_set(584, referee_case),
        "SELECT name FROM Customer WHERE referee_id<>2 OR referee_id IS NULL",
        "return Customer.loc[Customer.referee_id.ne(2).fillna(True), ['name']]",
        ["SELECT name FROM Customer WHERE referee_id<>2", "SELECT name FROM Customer WHERE referee_id IS NULL"]),
    620: exercise("Filtering",
        {"Cinema": [("id", "INT PRIMARY KEY"), ("movie", "VARCHAR(64)"), ("description", "VARCHAR(64)"),
                    ("rating", "DECIMAL(4,2)")]},
        sample_set(620, cinema_case),
        "SELECT id,movie,description,rating FROM Cinema WHERE MOD(id,2)=1 AND description<>'boring' ORDER BY rating DESC",
        "return Cinema.loc[Cinema.id.mod(2).eq(1) & Cinema.description.ne('boring')].sort_values('rating', ascending=False)",
        ["SELECT * FROM Cinema WHERE MOD(id,2)=1 ORDER BY rating DESC",
         "SELECT * FROM Cinema WHERE MOD(id,2)=1 AND description<>'boring' ORDER BY rating ASC"],
        ordered=True),
    1050: exercise("Aggregation",
        {"ActorDirector": [("actor_id", "INT"), ("director_id", "INT"), ("timestamp", "INT PRIMARY KEY")]},
        sample_set(1050, cooperation_case),
        "SELECT actor_id,director_id FROM ActorDirector GROUP BY actor_id,director_id HAVING COUNT(*)>=3",
        "counts = ActorDirector.groupby(['actor_id','director_id']).size().reset_index(name='count')\nreturn counts.loc[counts['count'] >= 3, ['actor_id','director_id']]",
        ["SELECT actor_id,director_id FROM ActorDirector GROUP BY actor_id,director_id HAVING COUNT(*)>3",
         "SELECT actor_id,director_id FROM ActorDirector GROUP BY actor_id,director_id HAVING COUNT(*)>=2"]),
    1683: exercise("Filtering",
        {"Tweets": [("tweet_id", "INT PRIMARY KEY"), ("content", "VARCHAR(128)")]},
        sample_set(1683, tweet_case),
        "SELECT tweet_id FROM Tweets WHERE CHAR_LENGTH(content)>15",
        "return Tweets.loc[Tweets.content.str.len() > 15, ['tweet_id']]",
        ["SELECT tweet_id FROM Tweets WHERE CHAR_LENGTH(content)>=15",
         "SELECT tweet_id FROM Tweets WHERE CHAR_LENGTH(content)<15"]),
    1729: exercise("Aggregation", {"Followers": [("user_id", "INT"), ("follower_id", "INT")]},
        sample_set(1729, follower_case),
        "SELECT user_id, COUNT(*) AS followers_count FROM Followers GROUP BY user_id ORDER BY user_id",
        "return Followers.groupby('user_id', sort=True).size().reset_index(name='followers_count')",
        ["SELECT user_id, COUNT(*) AS followers_count FROM Followers GROUP BY user_id ORDER BY user_id DESC",
         "SELECT follower_id AS user_id, COUNT(*) AS followers_count FROM Followers GROUP BY follower_id ORDER BY follower_id"],
        ordered=True),
    1789: exercise("Aggregation",
        {"Employee": [("employee_id", "INT"), ("department_id", "INT"), ("primary_flag", "CHAR(1)")]},
        sample_set(1789, primary_department_case),
        "SELECT employee_id,department_id FROM Employee WHERE primary_flag='Y' OR employee_id IN (SELECT employee_id FROM Employee GROUP BY employee_id HAVING COUNT(*)=1)",
        "count = Employee.groupby('employee_id').department_id.transform('size')\nreturn Employee.loc[count.eq(1) | Employee.primary_flag.eq('Y'), ['employee_id','department_id']]",
        ["SELECT employee_id,department_id FROM Employee WHERE primary_flag='Y'",
         "SELECT employee_id,department_id FROM Employee WHERE primary_flag='N'"]),
    1873: exercise("Filtering",
        {"Employees": [("employee_id", "INT PRIMARY KEY"), ("name", "VARCHAR(64)"), ("salary", "INT")]},
        sample_set(1873, bonus_case),
        "SELECT employee_id, CASE WHEN MOD(employee_id,2)=1 AND name NOT LIKE 'M%' THEN salary ELSE 0 END AS bonus FROM Employees ORDER BY employee_id",
        "result = Employees.sort_values('employee_id').copy()\nresult['bonus'] = result.salary.where(result.employee_id.mod(2).eq(1) & ~result.name.str.startswith('M'), 0)\nreturn result[['employee_id','bonus']]",
        ["SELECT employee_id, IF(MOD(employee_id,2)=1,salary,0) AS bonus FROM Employees ORDER BY employee_id",
         "SELECT employee_id, IF(name NOT LIKE 'M%',salary,0) AS bonus FROM Employees ORDER BY employee_id"],
        ordered=True),
})


# Ranking has its own Medium skill and follows written aggregation practice.
PREREQUISITES = {"Ranking": "Aggregation", "Reshaping": "Aggregation"}


def pandas_starter(problem, *, reference=False):
    params = [*problem["schema"], *problem["cases"][0]["parameters"]]
    lines = problem["pandas"].splitlines() if reference else ["# Write your solution here.", "raise NotImplementedError"]
    return "import pandas as pd\n\ndef solve(" + ", ".join(params) + "):\n" + "\n".join("    " + line for line in lines) + "\n"


def summary(item, passed=()):
    problem = CATALOG.get(item["id"])
    return {**{k: item[k] for k in ("id", "title", "difficulty", "premium", "url")},
            "prompt": next((line.removeprefix("Task:").strip() for line in item["summary"].splitlines()
                            if line.startswith("Task:")), ""),
            "topic": problem["topic"] if problem else None, "runnable": problem is not None,
            "passedLanguages": list(passed)}


def public_case(problem, case):
    return {**case, "tables": {key: table([c[0] for c in problem["schema"][key]], rows)
                              for key, rows in case["tables"].items()}}
