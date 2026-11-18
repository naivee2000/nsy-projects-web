"""Executable contracts with in-place results, variable schemas, parameters and window boundaries."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .database_exercise import exercise, fixture, sample_set


def department_case(rng, index):
    departments = [(1, "Research"), (2, "Sales"), (3, "Support")]
    wages = [100, 100, 90, 80, 70]
    employees = [(i, f"R{i}", salary, 1) for i, salary in enumerate(wages, 1)]
    employees += [(10, "Sue", 20, 2), (11, "Joe", 10, 2)]
    if index == 1:
        employees = []
    elif index > 1:
        employees += [(20 + i, f"New{i}", rng.choice([30, 50, 85, 100]), rng.randint(1, 3)) for i in range(index)]
    rows = []
    for key, name in departments:
        group = [row for row in employees if row[3] == key]
        for _, employee, salary, _ in group:
            if len({other[2] for other in group if other[2] > salary}) < 3:
                rows.append((name, employee, salary))
    return fixture({"Employee": employees, "Department": departments}, ["Department", "Employee", "Salary"], rows)


DEPARTMENT_SQL = """WITH ranked AS (
  SELECT e.*, DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS position_in_dept
  FROM Employee e
)
SELECT d.name AS Department, r.name AS Employee, r.salary AS Salary
FROM ranked r JOIN Department d ON r.departmentId = d.id WHERE position_in_dept <= 3"""
DEPARTMENT_PD = """top = Employee.groupby('departmentId').salary.rank(method='dense', ascending=False)
joined = Employee.loc[top <= 3].merge(Department, left_on='departmentId', right_on='id', suffixes=('_emp','_dept'))
return joined[['name_dept','name_emp','salary']].set_axis(['Department','Employee','Salary'], axis=1)"""


def swap_case(rng, index):
    rows = [(i, f"Person{i}", ("m" if i % 3 else "f"), rng.randint(100, 300)) for i in range(1, index + 4)]
    if index == 1:
        rows = [(5, "Kay", "f", 120)]
    return fixture({"Salary": rows}, ["id", "name", "sex", "salary"],
                   [(i, name, "m" if sex == "f" else "f", salary) for i, name, sex, salary in rows])


def restaurant_case(rng, index):
    start = date(2024, 2, 24) + timedelta(days=index)
    n = [7, 3, 8, 12][index % 4]
    rows = []
    for offset in range(n):
        for customer in range(1, 2 + (offset + index) % 3):
            rows.append((customer, f"C{customer}", (start + timedelta(days=offset)).isoformat(),
                         rng.randint(1, 100)))
    expected = []
    for offset in range(6, n):
        end = start + timedelta(days=offset)
        amount = sum(value for _, _, day, value in rows if end - timedelta(days=6) <= date.fromisoformat(day) <= end)
        avg = (Decimal(amount) / 7).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected.append((end.isoformat(), amount, float(avg)))
    rng.shuffle(rows)
    return fixture({"Customer": rows}, ["visited_on", "amount", "average_amount"], expected)


RESTAURANT_SQL = """WITH daily AS (SELECT visited_on, SUM(amount) AS total FROM Customer GROUP BY visited_on),
windows AS (SELECT visited_on, SUM(total) OVER w AS amount, COUNT(*) OVER w AS days
  FROM daily WINDOW w AS (ORDER BY visited_on ROWS BETWEEN 6 PRECEDING AND CURRENT ROW))
SELECT visited_on, amount, ROUND(amount/7,2) AS average_amount FROM windows WHERE days=7 ORDER BY visited_on"""
RESTAURANT_PD = """daily = Customer.groupby('visited_on').amount.sum().sort_index()
result = daily.rolling(7).sum().dropna().rename('amount').reset_index()
result['average_amount'] = result.amount.div(7).round(2)
return result"""


def discount_case(rng, index, count):
    start = date(2024, 2, 21) + timedelta(days=index)
    end = start + timedelta(days=2 + index % 3)
    threshold = 40 + index
    midnight = datetime.combine(start, time())
    last = datetime.combine(end, time())
    records = [(1, midnight, threshold), (1, midnight + timedelta(hours=1), threshold + 1),
               (2, last, threshold), (3, last + timedelta(seconds=1), threshold + 9),
               (4, midnight - timedelta(seconds=1), threshold + 1),
               (5, midnight, threshold - 1), (5, last, threshold - 1)]
    if index == 1:
        records = []
    for i in range(max(0, index-2)):
        records.append((6+i, midnight+timedelta(hours=rng.randint(-6, 99)), rng.randint(1, 99)))
    qualify = sorted({user for user, stamp, amt in records if midnight <= stamp <= last and amt >= threshold})
    return fixture({"Purchases": [(u, t.isoformat(sep=" "), a) for u,t,a in records]},
                   ["user_cnt"] if count else ["user_id"], [(len(qualify),)] if count else [(u,) for u in qualify],
                   startDate=start.isoformat(), endDate=end.isoformat(), minAmount=threshold)


def discount_exercise(count):
    select = "COUNT(DISTINCT user_id)" if count else "DISTINCT user_id"
    query = f"SELECT {select} FROM Purchases WHERE time_stamp BETWEEN startDate AND endDate AND amount >= minAmount"
    args = "getUserIDs(startDate DATE, endDate DATE, minAmount INT)"
    definition = ("CREATE FUNCTION " + args + " RETURNS INT READS SQL DATA\nRETURN (" + query + ")"
                  if count else "CREATE PROCEDURE " + args + "\n" + query + " ORDER BY user_id")
    pandas = """eligible = Purchases.loc[Purchases.time_stamp.between(pd.Timestamp(startDate), pd.Timestamp(endDate)) & Purchases.amount.ge(minAmount)]
""" + ("return pd.DataFrame({'user_cnt': [eligible.user_id.nunique()]})" if count else
       "return eligible[['user_id']].drop_duplicates().sort_values('user_id')")
    return exercise("Filtering", {"Purchases": [("user_id", "INT"), ("time_stamp", "DATETIME"), ("amount", "INT")]},
        sample_set(2205 if count else 2230, lambda r,i: discount_case(r,i,count)), definition, pandas,
        [definition.replace(">= minAmount", "> minAmount"), definition.replace("AND endDate AND", "AND DATE_ADD(endDate, INTERVAL 1 DAY) AND")],
        runner="function" if count else "procedure", routine="getUserIDs", scalar_column="user_cnt" if count else None,
        ordered=not count, mysql_starter=(f"CREATE FUNCTION {args} RETURNS INT READS SQL DATA\nRETURN (\n    -- Write your query here.\n);"
            if count else f"CREATE PROCEDURE {args}\n-- Write your query here.\n;"),
        wrong_pandas=[pandas.replace(".ge(minAmount)", ".gt(minAmount)"),
                      pandas.replace("pd.Timestamp(endDate)", "(pd.Timestamp(endDate) + pd.Timedelta(days=1))")],
        advice="Both dates denote midnight. A purchase later on endDate falls outside the closed interval.")


def unpivot_case(rng, index):
    stores = (["East", "West"] if index == 0 else ["Solo"] if index == 1 else
              [f"Shop_{index}_{j}" for j in range(30 if index == 15 else 1 + index % 5)])
    rows = [(i, *(None if (i+j+index) % 3 == 0 else rng.randrange(0, 12) for j in range(len(stores))))
            for i in range(1, 4 + index % 3)]
    if index == 1:
        rows = [(1, None), (2, 0)]
    schema = {"Products": [("product_id", "INT PRIMARY KEY")] + [(k, "INT") for k in stores]}
    expected = [(r[0], store, value) for r in rows for store, value in zip(stores, r[1:]) if value is not None]
    case = fixture({"Products": rows}, ["product_id", "store", "price"], expected)
    return {**case, "schema": schema}


UNPIVOT_SQL = """DELIMITER //
CREATE PROCEDURE UnpivotProducts()
BEGIN
  SET SESSION group_concat_max_len=131072;
  SELECT GROUP_CONCAT(CONCAT('SELECT product_id,', QUOTE(column_name), ' AS store, `',
    REPLACE(column_name, '`', '``'), '` AS price FROM Products WHERE `',
    REPLACE(column_name, '`', '``'), '` IS NOT NULL') SEPARATOR ' UNION ALL ')
    INTO @query FROM information_schema.columns
    WHERE table_schema=DATABASE() AND table_name='Products' AND column_name <> 'product_id';
  PREPARE stmt FROM @query;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END//
DELIMITER ;"""
UNPIVOT_PD = """long = Products.melt(id_vars='product_id', var_name='store', value_name='price')
return long.dropna(subset=['price'])"""


def fraud_case(rng, index):
    size = [21, 22, 1, 2, 20, 41, 42][index % 7]
    rows = [(i+1, "East", round(1-i/100, 2)) for i in range(size)]
    if index == 1:
        rows[2] = (3, "East", rows[1][2])
    rows += [(101+j, "West", rng.choice([.91, .91, .80, .64])) for j in range(index+1)]
    rng.shuffle(rows)
    result = []
    for claim, state, score in rows:
        local = [x[2] for x in rows if x[1] == state]
        above = sum(s > score for s in local)
        if len(local) == 1 or 20*above < len(local)-1:
            result.append((claim, state, score))
    result.sort(key=lambda row: (row[1], -row[2], row[0]))
    return fixture({"Fraud": rows}, ["policy_id","state","fraud_score"], result)


FRAUD_SQL = """WITH ranked AS (SELECT f.*, PERCENT_RANK() OVER (PARTITION BY state ORDER BY fraud_score DESC) AS p FROM Fraud f)
SELECT policy_id,state,fraud_score FROM ranked WHERE p < 0.05 ORDER BY state, fraud_score DESC, policy_id"""
FRAUD_PD = """groups = Fraud.groupby('state').fraud_score
above = groups.rank(ascending=False, method='min') - 1
size = groups.transform('size')
return Fraud.loc[(size == 1) | (20*above < size-1)].sort_values(['state','fraud_score','policy_id'], ascending=[True,False,True])"""


def hierarchy_case(rng, index):
    size = 5 if index == 0 else index
    rows = [(i, f"Emp{i:02}", None if i == 1 else max(1, (i-1)//2) if index == 0 else rng.randrange(1,i),
             rng.randrange(1,10)*100, "Research") for i in range(1, size+1)]
    parent = {r[0]: r[2] for r in rows}
    sizes = dict.fromkeys(parent, 0)
    budgets = {r[0]: r[3] for r in rows}
    levels = {}
    for ident, _, manager, pay, _ in rows:
        level = 1
        while manager is not None:
            level += 1
            sizes[manager] += 1
            budgets[manager] += pay
            manager = parent[manager]
        levels[ident] = level
    expected = [(i, name, levels[i], sizes[i], budgets[i]) for i,name,*_ in rows]
    expected.sort(key=lambda r:(r[2],-r[4],r[1]))
    rng.shuffle(rows)
    return fixture({"Employees":rows}, ["employee_id","employee_name","level","team_size","budget"], expected)


HIERARCHY_SQL = """WITH RECURSIVE paths AS (
  SELECT employee_id AS ancestor, employee_id AS child, 1 AS depth FROM Employees
  UNION ALL SELECT paths.ancestor, e.employee_id, paths.depth+1 FROM paths JOIN Employees e ON e.manager_id=paths.child
), levels AS (SELECT child, MAX(depth) AS lvl FROM paths GROUP BY child)
SELECT e.employee_id,e.employee_name,l.lvl AS level,COUNT(*)-1 AS team_size,SUM(c.salary) AS budget
FROM Employees e JOIN paths p ON p.ancestor=e.employee_id JOIN Employees c ON c.employee_id=p.child
JOIN levels l ON l.child=e.employee_id GROUP BY e.employee_id,e.employee_name,l.lvl
ORDER BY level,budget DESC,employee_name"""
HIERARCHY_PD = """children = Employees.groupby('manager_id').employee_id.agg(list).to_dict()
salaries = Employees.set_index('employee_id').salary
levels = {}
sizes = {}
budgets = {}
def visit(node, level):
    levels[node] = level
    counts = [visit(child, level+1) for child in children.get(node, [])]
    sizes[node] = sum(size + 1 for size, _ in counts)
    budgets[node] = int(salaries[node]) + sum(value for _, value in counts)
    return sizes[node], budgets[node]
for root in Employees.loc[Employees.manager_id.isna(), 'employee_id']:
    visit(root, 1)
result = Employees[['employee_id','employee_name']].copy()
for name, mapping in [('level',levels), ('team_size',sizes), ('budget',budgets)]:
    result[name] = result.employee_id.map(mapping)
return result.sort_values(['level','budget','employee_name'], ascending=[True,False,True])"""


def exercises():
    cases = sample_set(2253, unpivot_case)
    return {
        185: exercise("Ranking", {"Employee":[("id","INT PRIMARY KEY"),("name","VARCHAR(60)"),("salary","INT"),("departmentId","INT")],
            "Department":[("id","INT PRIMARY KEY"),("name","VARCHAR(60)")]}, sample_set(185,department_case),
            DEPARTMENT_SQL, DEPARTMENT_PD, [DEPARTMENT_SQL.replace("DENSE_RANK()", "RANK()"), DEPARTMENT_SQL.replace("<= 3","< 3")],
            wrong_pandas=[DEPARTMENT_PD.replace("'dense'","'min'"), DEPARTMENT_PD.replace("<= 3","< 3")]),
        627: exercise("Mutations", {"Salary":[("id","INT PRIMARY KEY"),("name","VARCHAR(64)"),("sex","ENUM('m','f')"),("salary","INT")]},
            sample_set(627,swap_case), "UPDATE Salary SET sex=IF(sex='f','m','f')",
            "Salary['sex'] = Salary.sex.map({'f':'m','m':'f'})",
            ["UPDATE Salary SET sex='f' WHERE sex='m'", "UPDATE Salary SET sex='m' WHERE sex='f'"],
            runner="mutation",result_table="Salary",mysql_starter="-- Update Salary in place using one UPDATE statement.\n",
            wrong_pandas=["Salary.loc[Salary.sex.eq('m'), 'sex'] = 'f'", "Salary.loc[Salary.sex.eq('f'), 'sex'] = 'm'"]),
        1321: exercise("Dates", {"Customer":[("customer_id","INT"),("name","VARCHAR(64)"),("visited_on","DATE"),("amount","INT")]},
            sample_set(1321,restaurant_case), RESTAURANT_SQL, RESTAURANT_PD,
            [RESTAURANT_SQL.replace("6 PRECEDING","5 PRECEDING").replace("days=7","days=6"),
             RESTAURANT_SQL.replace("amount/7","amount/days/7")],
            wrong_pandas=[RESTAURANT_PD.replace("rolling(7)", "rolling(6)"), RESTAURANT_PD.replace(".div(7)", ".div(6)")],
            ordered=True, date_columns=["visited_on"], advice="Sum all visits on the same calendar day first. Return complete seven-day windows and round average_amount to two decimal places."),
        2205:discount_exercise(True), 2230:discount_exercise(False),
        2253:exercise("Reshaping",cases[0]["schema"],cases,UNPIVOT_SQL,UNPIVOT_PD,
            [UNPIVOT_SQL.replace(" IS NOT NULL"," IS NULL"), UNPIVOT_SQL.replace(" IS NOT NULL"," > 0")],
            runner="procedure",routine="UnpivotProducts",mysql_starter="DELIMITER //\nCREATE PROCEDURE UnpivotProducts()\nBEGIN\n    -- Write your query here.\nEND//\nDELIMITER ;",
            wrong_pandas=[UNPIVOT_PD.replace("long.dropna(subset=['price'])","long"), UNPIVOT_PD.replace("long.dropna(subset=['price'])","long.loc[long.price.gt(0)]")],
            advice="The store names and number of store columns can change on every input. Keep zero prices."),
        3055:exercise("Ranking",{"Fraud":[("policy_id","INT PRIMARY KEY"),("state","VARCHAR(50)"),("fraud_score","DECIMAL(8,3)")]},
            sample_set(3055,fraud_case),FRAUD_SQL,FRAUD_PD,[FRAUD_SQL.replace("p < 0.05","p <= 0.05"), FRAUD_SQL.replace("p < 0.05","p = 0")],
            wrong_pandas=[FRAUD_PD.replace("20*above <","20*above <="),FRAUD_PD.replace("20*above < size-1","above == 0")],ordered=True,
            advice="Use a strict cutoff. For 21 distinct scores, only the highest qualifies. For 22, both highest ranks qualify; all claims tied at a qualifying rank count."),
        3482:exercise("Hierarchy",{"Employees":[("employee_id","INT PRIMARY KEY"),("employee_name","VARCHAR(64)"),("manager_id","INT"),
            ("salary","INT"),("department","VARCHAR(64)")]},sample_set(3482,hierarchy_case),HIERARCHY_SQL,HIERARCHY_PD,
            [HIERARCHY_SQL.replace("COUNT(*)-1","COUNT(*)"),HIERARCHY_SQL.replace("SUM(c.salary) AS budget","SUM(c.salary)-e.salary AS budget")],
            wrong_pandas=[HIERARCHY_PD.replace("sizes[node] = sum","sizes[node] = 1 + sum"),HIERARCHY_PD.replace("int(salaries[node]) + sum","sum")],
            ordered=["level","budget","employee_name"])
    }
