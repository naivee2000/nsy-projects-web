from .database_solutions_01 import Solution

BUS_SQL = """WITH RECURSIVE waiting AS (
 SELECT b.bus_id,b.capacity,ROW_NUMBER() OVER(ORDER BY b.arrival_time) n,
 (SELECT COUNT(*) FROM Passengers p WHERE p.arrival_time<=b.arrival_time) people FROM Buses b
), boarding AS (
 SELECT n,bus_id,LEAST(capacity,people) boarded,LEAST(capacity,people) handled FROM waiting WHERE n=1
 UNION ALL SELECT w.n,w.bus_id,LEAST(w.capacity,w.people-b.handled),b.handled+LEAST(w.capacity,w.people-b.handled)
 FROM waiting w JOIN boarding b ON w.n=b.n+1
) SELECT bus_id,boarded AS passengers_cnt FROM boarding ORDER BY bus_id"""
BUS_PD = """handled=0
rows=[]
for b in Buses.sort_values('arrival_time').itertuples():
    waiting=int(Passengers.arrival_time.le(b.arrival_time).sum())-handled
    boarded=min(b.capacity,waiting)
    rows.append((b.bus_id,boarded))
    handled+=boarded
return pd.DataFrame(rows,columns=['bus_id','passengers_cnt']).sort_values('bus_id')"""
SOLUTIONS = {
    2026: Solution(
        "Filtering",
        "",
        "return Problems.loc[Problems.likes.lt(.6*(Problems.likes+Problems.dislikes)),['problem_id']].sort_values('problem_id')",
        [
            ("< 0.6", "<= 0.6", "likes.lt", "likes.le"),
            (
                "(likes + dislikes)",
                "dislikes",
                ".6*(Problems.likes+Problems.dislikes)",
                ".6*Problems.dislikes",
            ),
        ],
        True,
    ),
    2041: Solution(
        "Joins",
        "",
        """scores=Rounds.groupby('interview_id').score.sum()
return Candidates.loc[Candidates.years_of_exp.ge(2) & Candidates.interview_id.map(scores).gt(15),['candidate_id']]""",
        [(">= 2", "> 2", "exp.ge", "exp.gt"), ("> 15", ">= 15", "scores).gt", "scores).ge")],
    ),
    2051: Solution(
        "Joins",
        "",
        """p=Visits.assign(bought=Visits.visit_id.isin(Purchases.visit_id)).groupby('member_id').bought.mean()
cats=Members.member_id.map(p).map(lambda v:'Bronze' if pd.isna(v) else 'Diamond' if v>=.8 else 'Gold' if v>=.5 else 'Silver')
return Members.assign(category=cats)""",
        [(">= 80", "> 80", "v>=.8", "v>.8"), (">= 50", "> 50", "v>=.5", "v>.5")],
    ),
    2066: Solution(
        "Window functions",
        "",
        """a=Transactions.sort_values(['account_id','day'])
net=a.amount.where(a.type.eq('Deposit'),-a.amount)
return a[['account_id','day']].assign(balance=net.groupby(a.account_id).cumsum())""",
        [
            ("amount, -amount", "amount, amount", "-a.amount", "a.amount"),
            (
                "PARTITION BY account_id ORDER BY day",
                "PARTITION BY account_id",
                "cumsum()",
                "transform('sum')",
            ),
        ],
        True,
    ),
    2072: Solution(
        "Aggregation",
        "",
        """a=NewYork.score.ge(90).sum()
b=California.score.ge(90).sum()
return pd.DataFrame({'winner':['New York University' if a>b else 'California University' if b>a else 'No Winner']})""",
        [
            (">= 90", "> 90", ".ge(90)", ".gt(90)"),
            ("n1.cnt > n2.cnt", "n1.cnt >= n2.cnt", "if a>b", "if a>=b"),
        ],
    ),
    2082: Solution(
        "Aggregation",
        "",
        "return pd.DataFrame({'rich_count':[Store.loc[Store.amount.gt(500),'customer_id'].nunique()]})",
        [
            ("COUNT(DISTINCT customer_id)", "COUNT(customer_id)", ".nunique()", ".size"),
            ("> 500", ">= 500", "amount.gt", "amount.ge"),
        ],
    ),
    2084: Solution(
        "Filtering",
        "",
        """preferred=Orders.loc[Orders.order_type.eq(0),'customer_id']
return Orders.loc[Orders.order_type.eq(0) | ~Orders.customer_id.isin(preferred)]""",
        [
            (
                " OR NOT EXISTS (SELECT 1 FROM T AS t WHERE t.customer_id = o.customer_id)",
                "",
                " | ~Orders.customer_id.isin(preferred)",
                "",
            ),
            ("OR NOT EXISTS", "OR EXISTS", "~Orders.customer_id", "Orders.customer_id"),
        ],
    ),
    2112: Solution(
        "Aggregation",
        """WITH traffic AS (SELECT departure_airport id,flights_count n FROM Flights UNION ALL SELECT arrival_airport,flights_count FROM Flights),
totals AS (SELECT id,SUM(n) n FROM traffic GROUP BY id) SELECT id AS airport_id FROM totals WHERE n=(SELECT MAX(n) FROM totals)""",
        """start=Flights.groupby('departure_airport').flights_count.sum()
end=Flights.groupby('arrival_airport').flights_count.sum()
n=start.add(end,fill_value=0)
return n[n.eq(n.max())].index.to_frame(index=False,name='airport_id')""",
        [
            (
                "UNION ALL",
                "UNION",
                "start.add(end,fill_value=0)",
                "Flights[['departure_airport','flights_count']].set_axis(['id','n'],axis=1).pipe(lambda a:pd.concat([a,Flights[['arrival_airport','flights_count']].set_axis(a.columns,axis=1)])).drop_duplicates().groupby('id').n.sum()",
            ),
            ("MAX(n)", "MIN(n)", "n.max()", "n.min()"),
        ],
    ),
    2118: Solution(
        "Strings",
        "",
        """terms=[]
for power,factor in Terms.sort_values('power',ascending=False).itertuples(index=False,name=None):
    suffix='' if power==0 else 'X' if power==1 else 'X^'+str(power)
    terms.append(f'{factor:+d}'+suffix)
return pd.DataFrame({'equation':[''.join(terms)+'=0']})""",
        [
            ("power DESC", "power ASC", "ascending=False", "ascending=True"),
            ("'X' )", "'X^1' )", "else 'X' if", "else 'X^1' if"),
        ],
    ),
    2142: Solution(
        "Window functions",
        "",
        """n=Buses.sort_values('arrival_time').copy()
n['passengers_cnt']=[int(Passengers.arrival_time.le(t).sum()) for t in n.arrival_time]
n['passengers_cnt']=n.passengers_cnt.diff().fillna(n.passengers_cnt)
return n[['bus_id','passengers_cnt']].sort_values('bus_id')""",
        [
            (
                "p.arrival_time <= b.arrival_time",
                "p.arrival_time < b.arrival_time",
                "arrival_time.le(t)",
                "arrival_time.lt(t)",
            ),
            (
                "- LAG(COUNT(passenger_id), 1, 0) OVER ( ORDER BY b.arrival_time )",
                "",
                "n.passengers_cnt.diff().fillna(n.passengers_cnt)",
                "n.passengers_cnt",
            ),
        ],
        True,
    ),
    2153: Solution(
        "Window functions",
        BUS_SQL,
        BUS_PD,
        [
            (
                "p.arrival_time<=b.arrival_time",
                "p.arrival_time<b.arrival_time",
                "arrival_time.le(b.arrival_time)",
                "arrival_time.lt(b.arrival_time)",
            ),
            ("w.people-b.handled", "w.people", "-handled", ""),
        ],
        True,
    ),
    2159: Solution(
        "Ranking",
        """WITH a AS (SELECT first_col,ROW_NUMBER() OVER (ORDER BY first_col) n FROM Data),b AS (SELECT second_col,ROW_NUMBER() OVER (ORDER BY second_col DESC) n FROM Data)
SELECT first_col,second_col FROM a JOIN b USING(n) ORDER BY n""",
        "return pd.DataFrame({'first_col':sorted(Data.first_col),'second_col':sorted(Data.second_col,reverse=True)})",
        [
            ("second_col DESC", "second_col ASC", "Data.second_col,reverse=True", "Data.second_col"),
            (
                "ORDER BY first_col)",
                "ORDER BY first_col DESC)",
                "sorted(Data.first_col)",
                "sorted(Data.first_col,reverse=True)",
            ),
        ],
        True,
    ),
    2173: Solution(
        "Window functions",
        """WITH games AS (SELECT m.*,SUM(result<>'Win') OVER(PARTITION BY player_id ORDER BY match_day) grp FROM Matches m), runs AS (SELECT player_id,grp,SUM(result='Win') n FROM games GROUP BY player_id,grp)
SELECT player_id,MAX(n) longest_streak FROM runs GROUP BY player_id""",
        """rows=[]
for u,g in Matches.sort_values('match_day').groupby('player_id'):
    longest=streak=0
    for value in g.result:
        streak=streak+1 if value=='Win' else 0
        longest=max(longest,streak)
    rows.append((u,longest))
return pd.DataFrame(rows,columns=['player_id','longest_streak'])""",
        [
            (
                "SUM(result<>'Win')",
                "SUM(result='Lose')",
                "else 0\n",
                "else streak if value=='Draw' else 0\n",
            ),
            (
                "MAX(n) longest_streak",
                "SUM(n) longest_streak",
                "longest=max(longest,streak)",
                "longest+=int(value=='Win')",
            ),
        ],
    ),
    2175: Solution(
        "Ranking",
        "",
        """a=TeamPoints.merge(PointsChange.groupby('team_id').points_change.sum(),on='team_id',how='left').fillna({'points_change':0})
old=a.sort_values(['points','name'],ascending=[False,True]).team_id.tolist()
new=a.assign(points=a.points+a.points_change).sort_values(['points','name'],ascending=[False,True]).team_id.tolist()
return a[['team_id','name']].assign(rank_diff=[old.index(u)-new.index(u) for u in a.team_id])""",
        [
            ("points + delta", "points - delta", "a.points+a.points_change", "a.points-a.points_change"),
            (
                "points DESC, name",
                "points DESC, name DESC",
                "['points','name'],ascending=[False,True]",
                "['points','name'],ascending=[False,False]",
            ),
        ],
    ),
    2199: Solution(
        "Strings",
        """SELECT p.post_id,COALESCE(GROUP_CONCAT(DISTINCT k.topic_id ORDER BY k.topic_id),'Ambiguous!') AS topic FROM Posts p
LEFT JOIN Keywords k ON LOCATE(CONCAT(' ',LOWER(k.word),' '),CONCAT(' ',LOWER(p.content),' '))>0 GROUP BY p.post_id""",
        """rows=[]
for post,text in Posts.itertuples(index=False,name=None):
    words=set(text.lower().split())
    topics=sorted({topic for topic,word in Keywords.itertuples(index=False,name=None) if word.lower() in words})
    rows.append((post,','.join(map(str,topics)) if topics else 'Ambiguous!'))
return pd.DataFrame(rows,columns=['post_id','topic'])""",
        [
            (
                "LOCATE(CONCAT(' ',LOWER(k.word),' '),CONCAT(' ',LOWER(p.content),' '))",
                "LOCATE(LOWER(k.word),LOWER(p.content))",
                "word.lower() in words",
                "word.lower() in text.lower()",
            ),
            ("LEFT JOIN", "JOIN", "rows.append((post,", "if topics: rows.append((post,"),
        ],
    ),
    2228: Solution(
        "Dates",
        "",
        """a=Purchases.sort_values(['user_id','purchase_date'])
d=a.groupby('user_id').purchase_date.diff().dt.days
return a.loc[d.le(7),['user_id']].drop_duplicates().sort_values('user_id')""",
        [("d <= 7", "d < 7", "d.le(7)", "d.lt(7)"), ("d <= 7", "d <= 8", "d.le(7)", "d.le(8)")],
        True,
    ),
    2238: Solution(
        "Joins",
        "",
        """ids=Rides[['driver_id']].drop_duplicates()
n=Rides.passenger_id.value_counts()
return ids.assign(cnt=ids.driver_id.map(n).fillna(0))""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "return ids.assign",
                "return ids.loc[ids.driver_id.isin(n.index)].assign",
            ),
            (
                "COUNT(passenger_id)",
                "COUNT(DISTINCT passenger_id)",
                "map(n).fillna(0)",
                "isin(n.index).astype(int)",
            ),
        ],
    ),
    2292: Solution(
        "Dates",
        "",
        """n=Orders.groupby(['product_id',Orders.purchase_date.dt.year]).size()
pairs=set(n[n.ge(3)].index)
return pd.DataFrame({'product_id':sorted({p for p,y in pairs if (p,y+1) in pairs})})""",
        [(">= 3", "> 3", "n.ge(3)", "n.gt(3)"), ("p2.y - 1", "p2.y - 2", "p,y+1", "p,y+2")],
    ),
    2298: Solution(
        "Dates",
        "",
        """weekend=Tasks.submit_date.dt.weekday.isin([5,6])
return pd.DataFrame({'weekend_cnt':[weekend.sum()],'working_cnt':[(~weekend).sum()]})""",
        [("(5, 6)", "(6)", "[5,6]", "[6]"), ("(5, 6)", "(4, 5)", "[5,6]", "[4,5]")],
    ),
    2308: Solution(
        "Ranking",
        "",
        """a=Genders.sort_values('user_id').copy()
a['i']=a.groupby('gender').cumcount()
a['j']=a.gender.map({'female':0,'other':1,'male':2})
return a.sort_values(['i','j'])[['user_id','gender']]""",
        [
            (
                "THEN 0 WHEN gender = 'other' THEN 1",
                "THEN 1 WHEN gender = 'other' THEN 0",
                "'female':0,'other':1",
                "'female':1,'other':0",
            ),
            (
                "ORDER BY user_id",
                "ORDER BY user_id DESC",
                "sort_values('user_id')",
                "sort_values('user_id',ascending=False)",
            ),
        ],
        True,
    ),
    2314: Solution(
        "Ranking",
        "",
        "return Weather.sort_values(['city_id','degree','day'],ascending=[True,False,True]).drop_duplicates('city_id')",
        [
            ("degree DESC, day", "degree DESC, day DESC", "[True,False,True]", "[True,False,False]"),
            ("degree DESC", "degree ASC", "[True,False,True]", "[True,True,True]"),
        ],
        True,
    ),
    2324: Solution(
        "Ranking",
        "",
        """a=Sales.merge(Product,on='product_id')
s=(a.quantity*a.price).groupby([a.user_id,a.product_id]).sum().reset_index(name='total')
return s.loc[s.total.eq(s.groupby('user_id').total.transform('max')),['user_id','product_id']]""",
        [
            (
                "RANK()",
                "ROW_NUMBER()",
                "['user_id','product_id']]",
                "['user_id','product_id']].drop_duplicates('user_id')",
            ),
            ("quantity * price", "quantity", "a.quantity*a.price", "a.quantity"),
        ],
    ),
    2329: Solution(
        "Aggregation",
        "",
        """a=Sales.merge(Product,on='product_id')
s=(a.quantity*a.price).groupby(a.user_id).sum().reset_index(name='spending')
return s.sort_values(['spending','user_id'],ascending=[False,True])""",
        [
            ("quantity * price", "price", "a.quantity*a.price", "a.price"),
            ("2 DESC, 1", "2 DESC, 1 DESC", "[False,True]", "[False,False]"),
        ],
        True,
    ),
    2339: Solution(
        "Joins",
        "",
        """from itertools import permutations
return pd.DataFrame(list(permutations(Teams.team_name,2)),columns=['home_team','away_team'])""",
        [
            (
                "t1.team_name != t2.team_name",
                "t1.team_name < t2.team_name",
                "list(permutations(Teams.team_name,2))",
                "[(a,b) for a,b in permutations(Teams.team_name,2) if a<b]",
            ),
            (
                "t1.team_name != t2.team_name",
                "1=1",
                "list(permutations(Teams.team_name,2))",
                "[(a,b) for a in Teams.team_name for b in Teams.team_name]",
            ),
        ],
    ),
    2346: Solution(
        "Ranking",
        "",
        """g=Students.groupby('department_id').mark
above=g.rank(method='min',ascending=False)-1
n=g.transform('size')
a=Students[['student_id','department_id']].copy()
return a.assign(percentage=(100*above/(n-1).where(n.gt(1))).fillna(0).round(2))""",
        [
            ("RANK()", "DENSE_RANK()", "method='min'", "method='dense'"),
            ("mark DESC", "mark ASC", "ascending=False", "ascending=True"),
        ],
    ),
    2356: Solution(
        "Aggregation",
        "",
        "return Teacher.groupby('teacher_id').subject_id.nunique().reset_index(name='cnt')",
        [
            (
                "COUNT(DISTINCT subject_id)",
                "COUNT(subject_id)",
                "subject_id.nunique()",
                "subject_id.size()",
            ),
            ("DISTINCT subject_id", "DISTINCT dept_id", "subject_id.nunique()", "dept_id.nunique()"),
        ],
    ),
    2362: Solution(
        "Ranking",
        "",
        """a=Purchases.merge(Products,on='product_id').copy()
a['price']=a.quantity*a.price
n=a.groupby('invoice_id').price.sum().sort_index()
return a.loc[a.invoice_id.eq(n.idxmax()),['product_id','quantity','price']]""",
        [
            (
                "ORDER BY 2 DESC, 1",
                "ORDER BY 2 DESC, 1 DESC",
                "sort_index()",
                "sort_index(ascending=False)",
            ),
            (
                "(quantity * price) AS price",
                "price AS price",
                "'quantity','price']]",
                "'quantity','price']].assign(price=lambda x:x.price/x.quantity)",
            ),
        ],
    ),
    2372: Solution(
        "Joins",
        "",
        """a=Customer.merge(Sales,on='customer_id')
s=a.groupby('salesperson_id').price.sum()
return Salesperson.assign(total=Salesperson.salesperson_id.map(s).fillna(0))""",
        [
            (
                "LEFT JOIN Customer",
                "JOIN Customer",
                "Salesperson.assign",
                "Salesperson.loc[Salesperson.salesperson_id.isin(Customer.salesperson_id)].assign",
            ),
            ("SUM(price)", "MAX(price)", ".price.sum()", ".price.max()"),
        ],
    ),
    2377: Solution(
        "Ranking",
        "",
        "return Olympic.sort_values(['gold_medals','silver_medals','bronze_medals','country'],ascending=[False,False,False,True])",
        [
            (
                "2 DESC, 3 DESC",
                "3 DESC, 2 DESC",
                "'gold_medals','silver_medals'",
                "'silver_medals','gold_medals'",
            ),
            ("4 DESC, 1", "4 DESC, 1 DESC", "False,True]", "False,False]"),
        ],
        True,
    ),
    2388: Solution(
        "Window functions",
        """WITH tagged AS (SELECT c.*,SUM(drink IS NOT NULL) OVER(ORDER BY input_position) grp FROM CoffeeShop c)
SELECT id,MAX(drink) OVER(PARTITION BY grp) AS drink FROM tagged ORDER BY input_position""",
        """a=CoffeeShop.sort_values('input_position')
return a[['id']].assign(drink=a.drink.ffill())""",
        [
            (
                "OVER(ORDER BY input_position)",
                "OVER(ORDER BY id)",
                "a.drink.ffill()",
                "CoffeeShop.sort_values('id').drink.ffill().reindex(a.index)",
            ),
            ("SUM(drink IS NOT NULL)", "SUM(drink IS NULL)", "a.drink.ffill()", "a.drink.bfill()"),
        ],
        True,
    ),
    2394: Solution(
        "Dates",
        "",
        """import math
mins=((Logs.out_time-Logs.in_time).dt.total_seconds()/60).map(math.ceil)
total=mins.groupby(Logs.employee_id).sum()
return Employees.loc[Employees.employee_id.map(total).fillna(0).lt(Employees.needed_hours*60),['employee_id']]""",
        [
            ("ceiling(", "floor(", ".ceil)", ".floor)"),
            ("< needed_hours", "<= needed_hours", ".lt(Employees", ".le(Employees"),
        ],
    ),
    2474: Solution(
        "Window functions",
        "",
        """n=Orders.groupby(['customer_id',Orders.order_date.dt.year]).price.sum()
ids=[]
for u,g in n.groupby(level=0):
    s=g.droplevel(0)
    complete=s.reindex(range(s.index.min(),s.index.max()+1),fill_value=0)
    if complete.diff().dropna().gt(0).all(): ids.append(u)
return pd.DataFrame({'customer_id':ids})""",
        [
            ("RANK()", "ROW_NUMBER()", "dropna().gt(0)", "dropna().ge(0)"),
            (
                "YEAR(order_date) - RANK()",
                "DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY YEAR(order_date)) - RANK()",
                "s.reindex(range(s.index.min(),s.index.max()+1),fill_value=0)",
                "s",
            ),
        ],
    ),
}
