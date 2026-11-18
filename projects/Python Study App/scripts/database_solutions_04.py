from .database_solutions_01 import Solution

HOPPER = """from decimal import Decimal, ROUND_HALF_UP
months = range(1,13)
joined = Rides.merge(AcceptedRides,on='ride_id')
year = joined.loc[joined.requested_at.dt.year.eq(2020)].copy()
year['month'] = year.requested_at.dt.month
active = [int((Drivers.join_date < pd.Timestamp(2020,m,1)+pd.offsets.MonthBegin(1)).sum()) for m in months]
"""
SOLUTIONS = {
    1468: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
top=Salaries.groupby('company_id').salary.transform('max')
a=Salaries.copy()
a['salary']=[int((Decimal(int(s))*Decimal('1' if m<1000 else '.76' if m<=10000 else '.51')).quantize(Decimal('1'),rounding=ROUND_HALF_UP)) for s,m in zip(a.salary,top)]
return a""",
        [
            ("top < 1000", "top <= 1000", "m<1000", "m<=1000"),
            ("top <= 10000", "top < 10000", "m<=10000", "m<10000"),
        ],
    ),
    1479: Solution(
        "Reshaping",
        "",
        """from calendar import day_name
a=Orders.merge(Items,on='item_id').assign(weekday=lambda x:x.order_date.dt.day_name())
g=a.pivot_table(index='item_category',columns='weekday',values='quantity',aggfunc='sum',fill_value=0)
return g.reindex(index=sorted(Items.item_category.unique()),columns=list(day_name),fill_value=0).rename_axis('Category').reset_index()""",
        [
            (
                "RIGHT JOIN",
                "JOIN",
                "sorted(Items.item_category.unique())",
                "sorted(a.item_category.unique())",
            ),
            ("quantity, 0", "1, 0", "aggfunc='sum'", "aggfunc='count'"),
        ],
        True,
    ),
    1484: Solution(
        "Aggregation",
        "SELECT sell_date,COUNT(DISTINCT product) AS num_sold,GROUP_CONCAT(DISTINCT product ORDER BY product) AS products FROM Activities GROUP BY sell_date ORDER BY sell_date",
        """return Activities.groupby('sell_date').product.agg(num_sold='nunique',products=lambda s:','.join(sorted(set(s)))).reset_index()""",
        [
            ("COUNT(DISTINCT product)", "COUNT(product)", "num_sold='nunique'", "num_sold='size'"),
            (
                "GROUP_CONCAT(DISTINCT product ORDER",
                "GROUP_CONCAT(product ORDER",
                "sorted(set(s))",
                "sorted(s)",
            ),
        ],
        True,
    ),
    1495: Solution(
        "Joins",
        "",
        """a=TVProgram.assign(content_id=TVProgram.content_id.astype(str)).merge(Content.assign(content_id=Content.content_id.astype(str)),on='content_id')
return a.loc[a.program_date.dt.strftime('%Y%m').eq('202006') & a.Kids_content.eq('Y') & a.content_type.eq('Movies'),['title']].drop_duplicates()""",
        [
            ("SELECT DISTINCT", "SELECT", ".drop_duplicates()", ""),
            ("AND kids_content = 'Y' ", "", " & a.Kids_content.eq('Y')", ""),
        ],
    ),
    1501: Solution(
        "Aggregation",
        """SELECT c.name AS country FROM Country c JOIN Person p ON LEFT(p.phone_number,3)=c.country_code
JOIN Calls a ON p.id IN (caller_id, callee_id) GROUP BY c.name
HAVING SUM(a.duration)*(SELECT COUNT(*) FROM Calls) > COUNT(*)*(SELECT SUM(duration) FROM Calls)""",
        """country=Country.set_index('country_code').name
names=Person.set_index('id').phone_number.str.slice(0,3).map(country)
a=pd.concat([Calls.caller_id,Calls.callee_id],ignore_index=True).map(names)
lengths=pd.concat([Calls.duration,Calls.duration],ignore_index=True)
avg=lengths.groupby(a).mean()
return avg[avg.gt(Calls.duration.mean())].index.to_frame(index=False,name='country')""",
        [
            (
                "id IN (caller_id, callee_id)",
                "id = caller_id",
                "[Calls.caller_id,Calls.callee_id]",
                "[Calls.caller_id,Calls.caller_id]",
            ),
            (" > COUNT(*)", " < COUNT(*)", "avg.gt(", "avg.lt("),
        ],
    ),
    1511: Solution(
        "Aggregation",
        "",
        """a=Orders.merge(Product,on='product_id')
a=a.loc[a.order_date.dt.year.eq(2020)].assign(month=lambda x:x.order_date.dt.month,total=lambda x:x.quantity*x.price)
g=a.pivot_table(index='customer_id',columns='month',values='total',aggfunc='sum',fill_value=0).reindex(columns=[6,7],fill_value=0)
ids=g[g.ge(100).all(axis=1)].index
return Customers.loc[Customers.customer_id.isin(ids),['customer_id','name']]""",
        [
            (">= 100", "> 100", "g.ge(100)", "g.gt(100)"),
            (" AND SUM(IF(MONTH", " OR SUM(IF(MONTH", ".all(axis=1)", ".any(axis=1)"),
        ],
    ),
    1517: Solution(
        "Strings",
        r"SELECT * FROM Users WHERE REGEXP_LIKE(mail,'^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$','c')",
        r"""pattern=r'[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com'
return Users.loc[Users.mail.str.fullmatch(pattern,na=False)]""",
        [
            ("@leetcode[.]com", "@leetcode.com", "@leetcode[.]com", "@leetcode.com"),
            (
                "[A-Za-z][A-Za-z0-9",
                "[A-Za-z0-9][A-Za-z0-9",
                "[A-Za-z][A-Za-z0-9",
                "[A-Za-z0-9][A-Za-z0-9",
            ),
        ],
    ),
    1527: Solution(
        "Strings",
        "",
        "return Patients.loc[Patients.conditions.str.contains(r'(?:^| )DIAB1',regex=True,na=False)]",
        [
            (
                "conditions LIKE 'DIAB1%' OR conditions LIKE '% DIAB1%'",
                "conditions LIKE '%DIAB1%'",
                "(?:^| )DIAB1",
                "DIAB1",
            ),
            (" OR conditions LIKE '% DIAB1%'", "", "(?:^| )DIAB1", "^DIAB1"),
        ],
    ),
    1532: Solution(
        "Ranking",
        "",
        """a=Orders.sort_values('order_date',ascending=False).groupby('customer_id').head(3).merge(Customers,on='customer_id').rename(columns={'name':'customer_name'})
return a[['customer_name','customer_id','order_id','order_date']].sort_values(['customer_name','customer_id','order_date'],ascending=[True,True,False])""",
        [
            ("rk <= 3", "rk < 3", "head(3)", "head(2)"),
            (
                "ORDER BY order_date DESC",
                "ORDER BY order_date ASC",
                "sort_values('order_date',ascending=False)",
                "sort_values('order_date')",
            ),
        ],
        True,
    ),
    1543: Solution(
        "Strings",
        "",
        """a=Sales.assign(product_name=Sales.product_name.str.strip().str.lower(),sale_date=Sales.sale_date.dt.strftime('%Y-%m'))
return a.groupby(['product_name','sale_date']).size().reset_index(name='total')""",
        [
            ("TRIM(product_name)", "product_name", ".str.strip()", ""),
            ("'%Y-%m'", "'%m'", "'%Y-%m'", "'%m'"),
        ],
        True,
    ),
    1549: Solution(
        "Ranking",
        "",
        """latest=Orders.groupby('product_id').order_date.transform('max')
a=Orders.loc[Orders.order_date.eq(latest)].merge(Products,on='product_id')
return a[['product_name','product_id','order_id','order_date']].sort_values(['product_name','product_id','order_id'])""",
        [
            (
                "RANK()",
                "ROW_NUMBER()",
                "Orders.loc[Orders.order_date.eq(latest)]",
                "Orders.loc[Orders.order_date.eq(latest)].drop_duplicates('product_id')",
            ),
            ("order_date DESC", "order_date ASC", "transform('max')", "transform('min')"),
        ],
        True,
    ),
    1555: Solution(
        "Aggregation",
        "",
        """paid=Transactions.groupby('paid_by').amount.sum()
received=Transactions.groupby('paid_to').amount.sum()
u=Users.copy()
u['credit']=u.credit+u.user_id.map(received).fillna(0)-u.user_id.map(paid).fillna(0)
return u.assign(credit_limit_breached=u.credit.lt(0).map({True:'Yes',False:'No'}))""",
        [
            ("SUM(t.credit) < 0", "SUM(t.credit) <= 0", "credit.lt(0)", "credit.le(0)"),
            ("-amount AS credit", "amount AS credit", "-u.user_id.map(paid)", "+u.user_id.map(paid)"),
        ],
    ),
    1565: Solution(
        "Dates",
        "",
        """a=Orders.loc[Orders.invoice.gt(20)].assign(month=lambda x:x.order_date.dt.strftime('%Y-%m'))
return a.groupby('month').agg(order_count=('order_id','size'),customer_count=('customer_id','nunique')).reset_index()""",
        [
            ("invoice > 20", "invoice >= 20", "invoice.gt(20)", "invoice.ge(20)"),
            (
                "COUNT(DISTINCT customer_id)",
                "COUNT(customer_id)",
                "'customer_id','nunique'",
                "'customer_id','size'",
            ),
        ],
    ),
    1571: Solution(
        "Aggregation",
        "",
        """a=Warehouse.merge(Products,on='product_id')
volume=a.Width*a.Length*a.Height*a.units
return volume.groupby(a.name).sum().rename_axis('warehouse_name').reset_index(name='volume')""",
        [(" * units", "", "*a.units", ""), (" * height", "", "*a.Height", "")],
    ),
    1581: Solution(
        "Joins",
        "",
        """v=Visits.loc[~Visits.visit_id.isin(Transactions.visit_id)]
return v.groupby('customer_id').size().reset_index(name='count_no_trans')""",
        [
            ("NOT IN", "IN", "~Visits.visit_id", "Visits.visit_id"),
            (
                "COUNT(1)",
                "COUNT(DISTINCT customer_id)",
                ".size().reset_index",
                ".customer_id.nunique().reset_index",
            ),
        ],
    ),
    1587: Solution(
        "Aggregation",
        "",
        """g=Transactions.groupby('account').amount.sum().rename('balance')
a=Users.merge(g,on='account')
return a.loc[a.balance.gt(10000),['name','balance']]""",
        [
            ("balance > 10000", "balance >= 10000", "balance.gt", "balance.ge"),
            (
                "SUM(amount)",
                "SUM(ABS(amount))",
                "Transactions.groupby",
                "Transactions.assign(amount=Transactions.amount.abs()).groupby",
            ),
        ],
    ),
    1596: Solution(
        "Ranking",
        "",
        """n=Orders.groupby(['customer_id','product_id']).size().rename('n').reset_index()
w=n.loc[n.n.eq(n.groupby('customer_id').n.transform('max'))]
return w.merge(Products,on='product_id')[['customer_id','product_id','product_name']]""",
        [
            (
                "RANK()",
                "ROW_NUMBER()",
                "return w.merge",
                "return w.drop_duplicates('customer_id').merge",
            ),
            ("COUNT(1) DESC", "COUNT(1) ASC", "transform('max')", "transform('min')"),
        ],
    ),
    1607: Solution(
        "Joins",
        "",
        """ids=Orders.loc[Orders.sale_date.dt.year.eq(2020),'seller_id']
return Seller.loc[~Seller.seller_id.isin(ids),['seller_name']].sort_values('seller_name')""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "~Seller.seller_id.isin(ids)",
                "~Seller.seller_id.isin(ids) & Seller.seller_id.isin(Orders.seller_id)",
            ),
            ("= 2020", "= 2019", "eq(2020)", "eq(2019)"),
        ],
        True,
    ),
    1613: Solution(
        "Filtering",
        "",
        """ids=set(Customers.customer_id)
return pd.DataFrame({'ids':[k for k in range(1,max(ids)+1) if k not in ids]})""",
        [
            ("SELECT 1 AS n", "SELECT 2 AS n", "range(1,", "range(2,"),
            ("MAX(customer_id)", "MAX(customer_id)-1", "max(ids)+1", "max(ids)-1"),
        ],
        True,
    ),
    1623: Solution(
        "Joins",
        "",
        """from itertools import product
rows=[]
for a,b,c in product(SchoolA.itertuples(),SchoolB.itertuples(),SchoolC.itertuples()):
    if len({a.student_id,b.student_id,c.student_id})==3 and len({a.student_name,b.student_name,c.student_name})==3:
        rows.append((a.student_name,b.student_name,c.student_name))
return pd.DataFrame(rows,columns=['member_A','member_B','member_C'])""",
        [
            (
                "a.student_name != b.student_name AND ",
                "",
                "len({a.student_name,b.student_name,c.student_name})==3",
                "a.student_name!=c.student_name and b.student_name!=c.student_name",
            ),
            (
                "a.student_id != b.student_id AND ",
                "",
                "len({a.student_id,b.student_id,c.student_id})==3",
                "a.student_id!=c.student_id and b.student_id!=c.student_id",
            ),
        ],
    ),
    1633: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
a=Register.groupby('contest_id').size().map(lambda n:float((Decimal(int(n))*100/len(Users)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))).reset_index(name='percentage')
return a.sort_values(['percentage','contest_id'],ascending=[False,True])""",
        [
            (" * 100", " * 1", "*100/", "*1/"),
            ("2 DESC, 1", "2 DESC, 1 DESC", "[False,True]", "[False,False]"),
        ],
        True,
    ),
    1635: Solution(
        "Dates",
        "",
        HOPPER
        + """counts=year.groupby('month').size()
return pd.DataFrame({'month':months,'active_drivers':active,'accepted_rides':[int(counts.get(m,0)) for m in months]})""",
        [
            ("month < 12", "month < 11", "range(1,13)", "range(1,12)"),
            (
                "YEAR(requested_at) = 2020",
                "YEAR(requested_at) = 2019",
                "dt.year.eq(2020)",
                "dt.year.eq(2019)",
            ),
        ],
        True,
    ),
    1645: Solution(
        "Dates",
        "",
        HOPPER
        + """counts=year.groupby('month').driver_id.nunique()
pct=[float((Decimal(int(counts.get(m,0)))*100/n).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)) if n else 0 for m,n in zip(months,active)]
return pd.DataFrame({'month':months,'working_percentage':pct})""",
        [("* 100", "* 1", "*100/n", "*1/n"), ("month < 12", "month < 11", "range(1,13)", "range(1,12)")],
        True,
    ),
    1651: Solution(
        "Window functions",
        "",
        HOPPER
        + """totals=year.groupby('month')[['ride_distance','ride_duration']].sum().reindex(months,fill_value=0)
rows=[(m,*totals.loc[m:m+2].mean().round(2).tolist()) for m in range(1,11)]
return pd.DataFrame(rows,columns=['month','average_ride_distance','average_ride_duration'])""",
        [
            ("AND 2 FOLLOWING", "AND 1 FOLLOWING", "m:m+2", "m:m+1"),
            ("LIMIT 10", "LIMIT 9", "range(1,11)", "range(1,10)"),
        ],
        True,
    ),
    1661: Solution(
        "Aggregation",
        "",
        """p=Activity.pivot(index=['machine_id','process_id'],columns='activity_type',values='timestamp')
return (p.end-p.start).groupby(level='machine_id').mean().round(3).reset_index(name='processing_time')""",
        [
            (" * 2", " * 1", ".mean().round(3)", ".mean().div(2).round(3)"),
            ("THEN -timestamp", "THEN timestamp", "(p.end-p.start)", "(p.end+p.start)"),
        ],
    ),
    1667: Solution(
        "Strings",
        "",
        "return Users.assign(name=Users.name.str.capitalize()).sort_values('user_id')",
        [
            (
                "LOWER(SUBSTRING(name, 2))",
                "SUBSTRING(name, 2)",
                "Users.name.str.capitalize()",
                "Users.name.str[0].str.upper()+Users.name.str[1:]",
            ),
            ("UPPER(LEFT(name, 1))", "LOWER(LEFT(name, 1))", "str.capitalize()", "str.lower()"),
        ],
        True,
    ),
    1677: Solution(
        "Joins",
        "",
        """cols=['rest','paid','canceled','refunded']
a=Product.merge(Invoice.groupby('product_id')[cols].sum(),how='left',on='product_id')
return a[['name',*cols]].fillna(0).sort_values('name')""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            ("SUM(rest)", "MAX(rest)", "[cols].sum()", "[cols].max()"),
        ],
        True,
    ),
    1693: Solution(
        "Aggregation",
        "",
        "return DailySales.groupby(['date_id','make_name']).agg(unique_leads=('lead_id','nunique'),unique_partners=('partner_id','nunique')).reset_index()",
        [
            ("COUNT(DISTINCT lead_id)", "COUNT(lead_id)", "'lead_id','nunique'", "'lead_id','size'"),
            (
                "COUNT(DISTINCT partner_id)",
                "COUNT(partner_id)",
                "'partner_id','nunique'",
                "'partner_id','size'",
            ),
        ],
    ),
    1699: Solution(
        "Aggregation",
        "",
        """a=Calls.assign(person1=Calls[['from_id','to_id']].min(axis=1),person2=Calls[['from_id','to_id']].max(axis=1))
return a.groupby(['person1','person2']).duration.agg(call_count='size',total_duration='sum').reset_index()""",
        [
            (
                "IF(from_id < to_id, from_id, to_id)",
                "from_id",
                "Calls[['from_id','to_id']].min(axis=1)",
                "Calls.from_id",
            ),
            ("SUM(duration)", "MAX(duration)", "total_duration='sum'", "total_duration='max'"),
        ],
    ),
    1709: Solution(
        "Dates",
        "",
        """a=UserVisits.sort_values(['user_id','visit_date']).copy()
next_day=a.groupby('user_id').visit_date.shift(-1).fillna(pd.Timestamp('2021-01-01'))
return (next_day-a.visit_date).dt.days.groupby(a.user_id).max().reset_index(name='biggest_window')""",
        [
            ("'2021-1-1'", "'2020-12-31'", "2021-01-01", "2020-12-31"),
            ("MAX(diff)", "MIN(diff)", ".max().reset_index", ".min().reset_index"),
        ],
        True,
    ),
    1715: Solution(
        "Joins",
        "",
        """a=Boxes.merge(Chests,on='chest_id',how='left',suffixes=('_box','_chest'))
return pd.DataFrame({k:[(a[k+'_box']+a[k+'_chest'].fillna(0)).sum()] for k in ['apple_count','orange_count']})""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            (" + IFNULL(c.apple_count, 0)", "", "a[k+'_box']+a[k+'_chest'].fillna(0)", "a[k+'_box']"),
        ],
    ),
    1731: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
n=Employees.groupby('reports_to').age.agg(reports_count='size',average_age='mean')
n['average_age']=n.average_age.map(lambda x:int(Decimal(str(x)).quantize(Decimal('1'),rounding=ROUND_HALF_UP)))
a=Employees.merge(n,left_on='employee_id',right_index=True)
return a[['employee_id','name','reports_count','average_age']].sort_values('employee_id')""",
        [
            ("ROUND(AVG(e1.age))", "FLOOR(AVG(e1.age))", "ROUND_HALF_UP)))", "'ROUND_FLOOR')))"),
            (
                "COUNT(1) AS reports_count",
                "COUNT(1)+1 AS reports_count",
                "a[['employee_id'",
                "a.assign(reports_count=a.reports_count+1)[['employee_id'",
            ),
        ],
        True,
    ),
}
