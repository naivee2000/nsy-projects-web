from .database_solutions_01 import Solution

FRIDAY = """dates=Purchases.purchase_date
fridays=Purchases.loc[dates.dt.strftime('%Y-%m').eq('2023-11') & dates.dt.weekday.eq(4)].groupby('purchase_date').amount_spend.sum()
"""
SOLUTIONS = {
    2480: Solution(
        "Joins",
        "",
        """m=Elements.loc[Elements.type.eq('Metal'),['symbol']].rename(columns={'symbol':'metal'})
n=Elements.loc[Elements.type.eq('Nonmetal'),['symbol']].rename(columns={'symbol':'nonmetal'})
return m.merge(n,how='cross')""",
        [
            ("b.type = 'Nonmetal'", "b.type != 'Metal'", "type.eq('Nonmetal')", "type.ne('Metal')"),
            ("a.type = 'Metal'", "a.type != 'Nonmetal'", "type.eq('Metal')", "type.ne('Nonmetal')"),
        ],
    ),
    2494: Solution(
        "Window functions",
        "",
        """rows=[]
for hall,g in HallEvents.sort_values('start_day').groupby('hall_id'):
    windows=[]
    for a,b in g[['start_day','end_day']].itertuples(index=False,name=None):
        if windows and a<=windows[-1][1]:
            windows[-1]=(windows[-1][0],max(windows[-1][1],b))
        else: windows.append((a,b))
    rows.extend((hall,a,b) for a,b in windows)
return pd.DataFrame(rows,columns=['hall_id','start_day','end_day'])""",
        [
            ("start_day <=", "start_day <", "a<=windows", "a<windows"),
            (
                "MAX(end_day) OVER ( PARTITION BY hall_id ORDER BY start_day ) AS cur_max_end_day",
                "end_day AS cur_max_end_day",
                "max(windows[-1][1],b)",
                "b",
            ),
        ],
    ),
    2504: Solution(
        "Strings",
        "",
        "return Person.assign(name=Person.name+'('+Person.profession.str[0]+')')[['person_id','name']].sort_values('person_id',ascending=False)",
        [
            ("person_id DESC", "person_id ASC", "ascending=False", "ascending=True"),
            ("SUBSTRING(profession, 1, 1)", "profession", "profession.str[0]", "profession"),
        ],
        True,
    ),
    2668: Solution(
        "Aggregation",
        "SELECT emp_id,firstname,lastname,CAST(MAX(CAST(salary AS UNSIGNED)) AS CHAR) AS salary,department_id FROM Salary GROUP BY emp_id,firstname,lastname,department_id ORDER BY emp_id",
        "return Salary.sort_values('salary',key=pd.to_numeric,ascending=False).drop_duplicates('emp_id').sort_values('emp_id')",
        [
            ("MAX(CAST", "MIN(CAST", "ascending=False", "ascending=True"),
            (
                "ORDER BY emp_id",
                "ORDER BY emp_id DESC",
                "sort_values('emp_id')",
                "sort_values('emp_id',ascending=False)",
            ),
        ],
        True,
    ),
    2669: Solution(
        "Aggregation",
        "",
        "return Spotify.groupby('artist').size().reset_index(name='occurrences').sort_values(['occurrences','artist'],ascending=[False,True])",
        [
            (
                "COUNT(1)",
                "COUNT(DISTINCT track_name)",
                "Spotify.groupby",
                "Spotify.drop_duplicates(['artist','track_name']).groupby",
            ),
            (
                "occurrences DESC, artist",
                "occurrences DESC, artist DESC",
                "[False,True]",
                "[False,False]",
            ),
        ],
        True,
    ),
    2686: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
pct=Delivery.order_date.eq(Delivery.customer_pref_delivery_date).groupby(Delivery.order_date).mean()*100
return pct.map(lambda x:float(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))).reset_index(name='immediate_percentage')""",
        [
            ("100 * SUM", "1 * SUM", "mean()*100", "mean()*1"),
            (
                "customer_pref_delivery_date = order_date",
                "customer_pref_delivery_date <> order_date",
                "order_date.eq",
                "order_date.ne",
            ),
        ],
        True,
    ),
    2687: Solution(
        "Dates",
        "",
        "return Bikes.groupby('bike_number').end_time.max().reset_index().sort_values('end_time',ascending=False)",
        [
            ("MAX(end_time)", "MIN(end_time)", "end_time.max()", "end_time.min()"),
            ("end_time DESC", "end_time ASC", "ascending=False", "ascending=True"),
        ],
        ["end_time"],
    ),
    2688: Solution(
        "Dates",
        "",
        """a=Users.sort_values(['user_id','created_at'])
d=a.groupby('user_id').created_at.diff().dt.days
return a.loc[d.le(7),['user_id']].drop_duplicates()""",
        [("<= 7", "< 7", "d.le(7)", "d.lt(7)"), ("<= 7", "<= 8", "d.le(7)", "d.le(8)")],
    ),
    2701: Solution(
        "Window functions",
        "",
        """a=Transactions.sort_values(['customer_id','transaction_date']).copy()
g=a.groupby('customer_id')
continuation=g.transaction_date.diff().dt.days.eq(1) & g.amount.diff().gt(0).fillna(False)
a['grp']=(~continuation).cumsum()
runs=a.groupby(['customer_id','grp']).transaction_date.agg(['min','max','size']).reset_index()
return runs.loc[runs['size'].ge(3),['customer_id','min','max']].rename(columns={'min':'consecutive_start','max':'consecutive_end'}).sort_values('customer_id')""",
        [
            ("t1.amount > t2.amount", "t1.amount >= t2.amount", "diff().gt(0)", "diff().ge(0)"),
            (">= 3", "> 3", "ge(3)", "gt(3)"),
        ],
        ["customer_id"],
    ),
    2720: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
people=pd.concat([Friends.user1,Friends.user2])
n=people.value_counts()
pct=n.map(lambda v:float((100*Decimal(int(v))/len(n)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)))
return pct.rename_axis('user1').reset_index(name='percentage_popularity').sort_values('user1')""",
        [
            ("* 100", "* 1", "100*Decimal", "1*Decimal"),
            (
                "ORDER BY 1",
                "ORDER BY 1 DESC",
                "sort_values('user1')",
                "sort_values('user1',ascending=False)",
            ),
        ],
        True,
    ),
    2738: Solution(
        "Strings",
        "",
        """return pd.DataFrame({'word':['bull','bear'],'count':[Files.content.str.contains(' '+w+' ',regex=False).sum() for w in ['bull','bear']]})""",
        [
            ("LIKE '% bull %'", "LIKE '%bull%'", "' '+w+' '", "w"),
            ("LIKE '% bear %'", "LIKE '% bear%'", "' '+w+' '", "(' '+w if w=='bear' else ' '+w+' ')"),
        ],
    ),
    2752: Solution(
        "Window functions",
        """WITH d AS (SELECT DISTINCT customer_id,transaction_date FROM Transactions), r AS
(SELECT customer_id,DATE_SUB(transaction_date,INTERVAL ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY transaction_date) DAY) grp FROM d),
g AS (SELECT customer_id,COUNT(*) n FROM r GROUP BY customer_id,grp)
SELECT DISTINCT customer_id FROM g WHERE n=(SELECT MAX(n) FROM g) ORDER BY customer_id""",
        """a=Transactions[['customer_id','transaction_date']].drop_duplicates().sort_values(['customer_id','transaction_date']).copy()
a['grp']=a.transaction_date-pd.to_timedelta(a.groupby('customer_id').cumcount(),unit='D')
n=a.groupby(['customer_id','grp']).size()
return n[n.eq(n.max())].reset_index()[['customer_id']].drop_duplicates().sort_values('customer_id')""",
        [
            ("SELECT MAX(n)", "SELECT MIN(n)", "n.max()", "n.min()"),
            (
                "ORDER BY customer_id",
                "ORDER BY customer_id DESC",
                "sort_values('customer_id')",
                "sort_values('customer_id',ascending=False)",
            ),
        ],
        True,
    ),
    2783: Solution(
        "Joins",
        "",
        """a=Flights.assign(n=Flights.flight_id.map(Passengers.flight_id.value_counts()).fillna(0))
a['booked_cnt']=a[['n','capacity']].min(axis=1)
a['waitlist_cnt']=(a.n-a.capacity).clip(lower=0)
return a[['flight_id','booked_cnt','waitlist_cnt']].sort_values('flight_id')""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "a=Flights.assign",
                "Flights=Flights.loc[Flights.flight_id.isin(Passengers.flight_id)].copy()\na=Flights.assign",
            ),
            (
                "LEAST(COUNT(passenger_id), capacity)",
                "COUNT(passenger_id)",
                "a[['n','capacity']].min(axis=1)",
                "a.n",
            ),
        ],
        True,
    ),
    2793: Solution(
        "Ranking",
        "",
        """p=Passengers.merge(Flights,on='flight_id').sort_values('booking_time')
rank=p.groupby('flight_id').cumcount()+1
return p[['passenger_id']].assign(Status=rank.le(p.capacity).map({True:'Confirmed',False:'Waitlist'})).sort_values('passenger_id')""",
        [
            ("<= capacity", "< capacity", "rank.le", "rank.lt"),
            (
                "ORDER BY booking_time",
                "ORDER BY booking_time DESC",
                "sort_values('booking_time')",
                "sort_values('booking_time',ascending=False)",
            ),
        ],
        True,
    ),
    2820: Solution(
        "Aggregation",
        "",
        """from fractions import Fraction
a=Votes.dropna(subset=['candidate']).copy()
a['v']=a.groupby('voter').candidate.transform('size').map(lambda n:Fraction(1,int(n)))
totals=a.groupby('candidate').v.sum()
return totals[totals.eq(totals.max())].index.to_frame(index=False).sort_values('candidate')""",
        [
            (
                "1 / (COUNT(candidate) OVER (PARTITION BY voter))",
                "1",
                "Fraction(1,int(n))",
                "Fraction(1,1)",
            ),
            ("RANK()", "ROW_NUMBER()", "sort_values('candidate')", "sort_values('candidate').head(1)"),
        ],
        True,
    ),
    2837: Solution(
        "Joins",
        "",
        """n=Rides.groupby('user_id').distance.sum()
a=Users.copy()
a['traveled distance']=a.user_id.map(n).fillna(0)
return a.sort_values('user_id')""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "a=Users.copy()",
                "a=Users.loc[Users.user_id.isin(Rides.user_id)].copy()",
            ),
            ("SUM(distance)", "MAX(distance)", ".distance.sum()", ".distance.max()"),
        ],
        True,
    ),
    2853: Solution(
        "Aggregation",
        "",
        """n=Salaries.groupby('department').salary.max()
return pd.DataFrame({'salary_difference':[abs(n['Engineering']-n['Marketing'])]})""",
        [
            ("MAX(salary)", "MIN(salary)", ".salary.max()", ".salary.min()"),
            ("MAX(s) - MIN(s)", "MIN(s) - MAX(s)", "[abs(", "[-abs("),
        ],
    ),
    2854: Solution(
        "Window functions",
        "",
        """a=Steps.sort_values(['user_id','steps_date']).copy()
g=a.groupby('user_id')
a['rolling_average']=g.steps_count.transform(lambda s:s.rolling(3).mean()).round(2)
ok=(a.steps_date-g.steps_date.shift(2)).dt.days.eq(2)
return a.loc[ok,['user_id','steps_date','rolling_average']]""",
        [
            ("ROWS 2 PRECEDING", "ROWS 1 PRECEDING", "rolling(3)", "rolling(2)"),
            (" = 2 AS st", " >= 2 AS st", "days.eq(2)", "days.ge(2)"),
        ],
        True,
    ),
    2893: Solution(
        "Aggregation",
        "",
        """groups=(Orders.minute+5)//6
return Orders.order_count.groupby(groups).sum().rename_axis('interval_no').reset_index(name='total_orders')""",
        [
            ("minute + 5", "minute + 6", "minute+5", "minute+6"),
            ("SUM(order_count)", "COUNT(*)", "groupby(groups).sum()", "groupby(groups).size()"),
        ],
        True,
    ),
    2922: Solution(
        "Aggregation",
        "",
        """a=Orders.merge(Items,on='item_id').merge(Users,on='seller_id')
n=a.loc[a.item_brand.ne(a.favorite_brand)].groupby('seller_id').item_id.nunique()
return n[n.eq(n.max())].reset_index(name='num_items').sort_values('seller_id')""",
        [
            ("COUNT(DISTINCT item_id)", "COUNT(item_id)", "item_id.nunique()", "item_id.size()"),
            (
                "item_brand != favorite_brand",
                "item_brand = favorite_brand",
                "item_brand.ne",
                "item_brand.eq",
            ),
        ],
        True,
    ),
    2978: Solution(
        "Joins",
        """SELECT l.X AS x,l.Y AS y FROM Coordinates l JOIN Coordinates r ON l.X=r.Y AND l.Y=r.X WHERE l.X<=l.Y GROUP BY l.X,l.Y HAVING l.X<l.Y OR COUNT(*)>1 ORDER BY l.X,l.Y""",
        """from collections import Counter
counts=Counter(Coordinates.itertuples(index=False,name=None))
return pd.DataFrame(sorted((x,y) for (x,y),v in counts.items() if (y,x) in counts and (x<y or x==y and v>=2)),columns=['x','y'])""",
        [
            ("COUNT(*)>1", "COUNT(*)>=1", "v>=2", "v>=1"),
            ("l.X<l.Y OR COUNT(*)>1", "l.X<l.Y", " or x==y and v>=2", ""),
        ],
        True,
    ),
    2984: Solution(
        "Ranking",
        "",
        """a=Calls.assign(hour=Calls.call_time.dt.hour)
n=a.groupby(['city','hour']).size().reset_index(name='number_of_calls')
top=n.number_of_calls.eq(n.groupby('city').number_of_calls.transform('max'))
return n.loc[top].rename(columns={'hour':'peak_calling_hour'}).sort_values(['peak_calling_hour','city'],ascending=[False,False])""",
        [
            ("RANK()", "ROW_NUMBER()", "n.loc[top]", "n.loc[top].drop_duplicates('city')"),
            ("ORDER BY 2 DESC, 1 DESC", "ORDER BY 2 ASC, 1 DESC", "[False,False]", "[True,False]"),
        ],
        True,
    ),
    2985: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
v=Decimal(int((Orders.item_count*Orders.order_occurrences).sum()))/int(Orders.order_occurrences.sum())
return pd.DataFrame({'average_items_per_order':[float(v.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))]})""",
        [
            (
                "SUM(item_count * order_occurrences) / SUM(order_occurrences)",
                "AVG(item_count)",
                "Decimal(int((Orders.item_count*Orders.order_occurrences).sum()))/int(Orders.order_occurrences.sum())",
                "Decimal(str(Orders.item_count.mean()))",
            ),
            ("SUM(order_occurrences)", "COUNT(*)", "int(Orders.order_occurrences.sum())", "len(Orders)"),
        ],
    ),
    2986: Solution(
        "Window functions",
        "",
        """a=Transactions.sort_values('transaction_date').copy()
g=a.groupby('user_id')
ok=g.cumcount().eq(2) & a.spend.gt(g.spend.shift()) & a.spend.gt(g.spend.shift(2))
return a.loc[ok,['user_id','spend','transaction_date']].rename(columns={'spend':'third_transaction_spend','transaction_date':'third_transaction_date'}).sort_values('user_id')""",
        [
            ("spend >", "spend >=", "spend.gt", "spend.ge"),
            ("rk = 3", "rk >= 3", "cumcount().eq(2)", "cumcount().ge(2)"),
        ],
        True,
    ),
    2987: Solution(
        "Aggregation",
        "",
        """n=Listings.groupby('city').price.mean()
return n[n.gt(Listings.price.mean())].index.to_frame(index=False).sort_values('city')""",
        [
            ("AVG(price) >", "AVG(price) >=", "n.gt", "n.ge"),
            ("AVG(price) >", "AVG(price) <", "n.gt", "n.lt"),
        ],
        True,
    ),
    2988: Solution(
        "Aggregation",
        "",
        """n=Employees.dep_id.value_counts()
a=Employees.loc[Employees.position.eq('Manager') & Employees.dep_id.isin(n[n.eq(n.max())].index)]
return a[['emp_name','dep_id']].rename(columns={'emp_name':'manager_name'}).sort_values('dep_id')""",
        [
            ("MAX(cnt)", "MIN(cnt)", "n.max()", "n.min()"),
            (
                "ORDER BY 2",
                "ORDER BY 2 LIMIT 1",
                "sort_values('dep_id')",
                "sort_values('dep_id').head(1)",
            ),
        ],
        True,
    ),
    2989: Solution(
        "Aggregation",
        "",
        """scores=Scores[['assignment1','assignment2','assignment3']].sum(axis=1)
return pd.DataFrame({'difference_in_score':[scores.max()-scores.min()]})""",
        [
            (" + assignment3", "", "'assignment2','assignment3'", "'assignment2'"),
            (" - MIN(", " + MIN(", "scores.max()-scores.min()", "scores.max()+scores.min()"),
        ],
    ),
    2990: Solution(
        "Aggregation",
        "",
        """n=Loans.groupby('user_id').loan_type.agg(set)
return n[n.map(lambda s:{'Refinance','Mortgage'} <= s)].index.to_frame(index=False).sort_values('user_id')""",
        [
            (
                " AND SUM",
                " OR SUM",
                "{'Refinance','Mortgage'} <= s",
                "bool({'Refinance','Mortgage'} & s)",
            ),
            (
                " AND SUM(loan_type = 'Mortgage') > 0",
                "",
                "{'Refinance','Mortgage'} <= s",
                "'Refinance' in s",
            ),
        ],
        True,
    ),
    2991: Solution(
        "Ranking",
        "",
        """totals=Wineries.groupby(['country','winery']).points.sum().reset_index().sort_values(['country','points','winery'],ascending=[True,False,True])
rows=[]
for c,g in totals.groupby('country'):
    names=[f'{n} ({v})' for n,v in g[['winery','points']].itertuples(index=False,name=None)]
    rows.append((c,names[0],names[1] if len(names)>1 else 'No second winery',names[2] if len(names)>2 else 'No third winery'))
return pd.DataFrame(rows,columns=['country','top_winery','second_winery','third_winery'])""",
        [
            ("SUM(points)", "MAX(points)", "points.sum()", "points.max()"),
            (
                "points DESC, winery",
                "points DESC, winery DESC",
                "[True,False,True]",
                "[True,False,False]",
            ),
        ],
        ["country"],
    ),
    2993: Solution(
        "Dates",
        "",
        FRIDAY
        + """a=fridays.rename('total_amount').reset_index()
return a.assign(week_of_month=(a.purchase_date.dt.day+6)//7)[['week_of_month','purchase_date','total_amount']].sort_values('week_of_month')""",
        [
            (
                "DAYOFWEEK(purchase_date) = 6",
                "DAYOFWEEK(purchase_date) = 5",
                "weekday.eq(4)",
                "weekday.eq(3)",
            ),
            ("SUM(amount_spend)", "MAX(amount_spend)", "amount_spend.sum()", "amount_spend.max()"),
        ],
        True,
    ),
    2994: Solution(
        "Dates",
        "",
        FRIDAY
        + """idx=pd.date_range('2023-11-03','2023-11-30',freq='7D',name='purchase_date')
a=fridays.reindex(idx,fill_value=0).rename('total_amount').reset_index()
return a.assign(week_of_month=(a.purchase_date.dt.day+6)//7)[['week_of_month','purchase_date','total_amount']]""",
        [
            ("LEFT JOIN", "JOIN", "fridays.reindex(idx,fill_value=0)", "fridays"),
            ("SUM(amount_spend)", "MAX(amount_spend)", "amount_spend.sum()", "amount_spend.max()"),
        ],
        True,
    ),
    2995: Solution(
        "Window functions",
        "",
        """first=Sessions.sort_values('session_start').drop_duplicates('user_id').set_index('user_id').session_type
s=Sessions.loc[Sessions.user_id.isin(first[first.eq('Viewer')].index) & Sessions.session_type.eq('Streamer')]
return s.groupby('user_id').size().reset_index(name='sessions_count').sort_values(['sessions_count','user_id'],ascending=[False,False])""",
        [
            (
                "ORDER BY session_start )",
                "ORDER BY session_start DESC )",
                "sort_values('session_start')",
                "sort_values('session_start',ascending=False)",
            ),
            ("ORDER BY 2 DESC, 1 DESC", "ORDER BY 2 DESC, 1 ASC", "[False,False]", "[False,True]"),
        ],
        True,
    ),
}
