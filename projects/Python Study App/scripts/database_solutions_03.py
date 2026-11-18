from .database_solutions_01 import Solution

SOLUTIONS = {
    1211: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
a=Queries.assign(q=Queries.rating/Queries.position,bad=Queries.rating.lt(3)*100)
g=a.groupby('query_name').agg(quality=('q','mean'),poor_query_percentage=('bad','mean'))
return g.map(lambda x:float(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))).reset_index()""",
        [
            ("rating < 3", "rating <= 3", "rating.lt(3)", "rating.le(3)"),
            ("rating / position", "rating", "Queries.rating/Queries.position", "Queries.rating"),
        ],
    ),
    1212: Solution(
        "Aggregation",
        "",
        """points = dict.fromkeys(Teams.team_id,0)
for m in Matches.itertuples():
    points[m.host_team] += 3 if m.host_goals>m.guest_goals else int(m.host_goals==m.guest_goals)
    points[m.guest_team] += 3 if m.guest_goals>m.host_goals else int(m.guest_goals==m.host_goals)
return Teams.assign(num_points=Teams.team_id.map(points)).sort_values(['num_points','team_id'],ascending=[False,True])""",
        [
            ("THEN 1 ELSE 0", "THEN 0 ELSE 0", "int(m.host_goals==m.guest_goals)", "0"),
            ("THEN 3", "THEN 2", "+= 3 if", "+= 2 if"),
        ],
        True,
    ),
    1225: Solution(
        "Dates",
        "",
        """all_days = pd.concat([Failed.fail_date.rename('day').to_frame().assign(state='failed'),Succeeded.success_date.rename('day').to_frame().assign(state='succeeded')]).sort_values('day')
days = all_days.loc[all_days.day.dt.year.eq(2019)]
runs = (days.state.ne(days.state.shift()) | days.day.diff().ne(pd.Timedelta(days=1))).cumsum()
return days.groupby(runs).agg(period_state=('state','first'),start_date=('day','min'),end_date=('day','max')).reset_index(drop=True)""",
        [
            (
                "YEAR(fail_date) = 2019",
                "YEAR(fail_date) <= 2019",
                "all_days.day.dt.year.eq(2019)",
                "(all_days.day.dt.year.eq(2019) | all_days.state.eq('failed'))",
            ),
            (
                "ORDER BY 2",
                "ORDER BY 2 DESC",
                "reset_index(drop=True)",
                "reset_index(drop=True).iloc[::-1]",
            ),
        ],
        True,
    ),
    1241: Solution(
        "Joins",
        "",
        """posts = Submissions.loc[Submissions.parent_id.isna(), 'sub_id'].drop_duplicates()
comments = Submissions.groupby('parent_id').sub_id.nunique()
return pd.DataFrame({'post_id':posts,'number_of_comments':posts.map(comments).fillna(0)}).sort_values('post_id')""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                ".sort_values('post_id')",
                ".loc[lambda t:t.number_of_comments.gt(0)].sort_values('post_id')",
            ),
            ("SELECT DISTINCT s1.sub_id", "SELECT s1.sub_id", "sub_id.nunique()", "sub_id.size()"),
        ],
        True,
    ),
    1251: Solution(
        "Joins",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
s=UnitsSold.merge(Prices,on='product_id')
s=s.loc[s.purchase_date.between(s.start_date,s.end_date)].copy()
g=s.assign(total=s.price*s.units).groupby('product_id')[['total','units']].sum()
av=(g.total/g.units).map(lambda v:float(Decimal(str(v)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)))
a=Prices[['product_id']].drop_duplicates().copy()
return a.assign(average_price=a.product_id.map(av).fillna(0))""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                ".assign(average_price=a.product_id.map(av).fillna(0))",
                ".assign(average_price=a.product_id.map(av)).dropna()",
            ),
            (
                "SUM(price * units) / SUM(units)",
                "AVG(price)",
                "(g.total/g.units)",
                "s.groupby('product_id').price.mean()",
            ),
        ],
    ),
    1264: Solution(
        "Joins",
        "",
        """friends = set(Friendship.loc[Friendship.user1_id.eq(1),'user2_id']) | set(Friendship.loc[Friendship.user2_id.eq(1),'user1_id'])
pages = Likes.loc[Likes.user_id.isin(friends),'page_id']
mine = Likes.loc[Likes.user_id.eq(1),'page_id']
return pages[~pages.isin(mine)].drop_duplicates().to_frame('recommended_page')""",
        [
            (
                "WHERE user2_id = 1 UNION",
                "WHERE 0 UNION",
                " | set(Friendship.loc[Friendship.user2_id.eq(1),'user1_id'])",
                "",
            ),
            (
                "WHERE page_id NOT IN (SELECT page_id FROM Likes WHERE user_id = 1)",
                "",
                "[~pages.isin(mine)]",
                "",
            ),
        ],
    ),
    1270: Solution(
        "Hierarchy",
        "",
        """boss=dict(Employees[['employee_id','manager_id']].itertuples(index=False,name=None))
def reports(k):
    for step in range(3):
        k=boss[k]
        if k==1: return True
    return False
return Employees.loc[Employees.employee_id.ne(1) & Employees.employee_id.map(reports),['employee_id']]""",
        [
            ("e3.manager_id = 1", "e1.manager_id = 1", "range(3)", "range(1)"),
            ("e1.employee_id != 1 AND ", "", "Employees.employee_id.ne(1) & ", ""),
        ],
    ),
    1280: Solution(
        "Joins",
        "",
        """all_pairs=Students.merge(Subjects,how='cross')
counts=Examinations.groupby(['student_id','subject_name']).size().rename('attended_exams')
return all_pairs.merge(counts,how='left',on=['student_id','subject_name']).fillna({'attended_exams':0}).sort_values(['student_id','subject_name'])""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            (
                "COUNT(e.student_id)",
                "COUNT(DISTINCT e.student_id)",
                "Examinations.groupby",
                "Examinations.drop_duplicates().groupby",
            ),
        ],
        True,
    ),
    1285: Solution(
        "Window functions",
        "",
        """v=Logs.log_id.sort_values().reset_index(drop=True)
return v.groupby(v.diff().ne(1).fillna(True).cumsum()).agg(start_id='min',end_id='max').reset_index(drop=True)""",
        [
            ("= 1, 0, 1", "<= 2, 0, 1", "diff().ne(1)", "diff().gt(2)"),
            ("MAX(log_id) AS end_id", "MIN(log_id) AS end_id", "end_id='max'", "end_id='min'"),
        ],
    ),
    1294: Solution(
        "Dates",
        "",
        """w=Weather.loc[Weather.day.dt.strftime('%Y-%m').eq('2019-11')].merge(Countries,on='country_id')
avg=w.groupby('country_name').weather_state.mean()
return avg.map(lambda n:'Cold' if n<=15 else 'Hot' if n>=25 else 'Warm').rename('weather_type').reset_index()""",
        [("<= 15", "< 15", "n<=15", "n<15"), (">= 25", "> 25", "n>=25", "n>25")],
    ),
    1303: Solution(
        "Aggregation",
        "",
        "return Employee[['employee_id']].assign(team_size=Employee.groupby('team_id').employee_id.transform('size'))",
        [
            (
                "COUNT(1) AS team_size",
                "COUNT(1)-1 AS team_size",
                "transform('size')",
                "transform('size')-1",
            ),
            (
                "COUNT(1) AS team_size",
                "COUNT(DISTINCT team_id) AS team_size",
                "employee_id.transform('size')",
                "team_id.transform('nunique')",
            ),
        ],
    ),
    1308: Solution(
        "Window functions",
        "SELECT gender,day,SUM(score_points) OVER (PARTITION BY gender ORDER BY day) AS total FROM Scores ORDER BY gender,day",
        """s=Scores.sort_values(['gender','day'])
return s[['gender','day']].assign(total=s.groupby('gender').score_points.cumsum())""",
        [
            (
                "PARTITION BY gender ORDER BY day",
                "PARTITION BY gender",
                "score_points.cumsum()",
                "score_points.transform('sum')",
            ),
            (
                "ORDER BY day)",
                "ORDER BY day DESC)",
                "sort_values(['gender','day'])",
                "sort_values(['gender','day'],ascending=[True,False])",
            ),
        ],
        True,
    ),
    1322: Solution(
        "Aggregation",
        "",
        """a=Ads.assign(c=Ads.action.eq('Clicked'),v=Ads.action.isin(['Clicked','Viewed'])).groupby('ad_id')[['c','v']].sum()
a['ctr']=(100*a.c/a.v.where(a.v.ne(0))).fillna(0).round(2)
return a[['ctr']].reset_index().sort_values(['ctr','ad_id'],ascending=[False,True])""",
        [
            (
                "SUM(action IN ('Clicked', 'Viewed'))",
                "COUNT(*)",
                "Ads.action.isin(['Clicked','Viewed'])",
                "Ads.action.notna()",
            ),
            ("* 100", "* 1", "100*a.c", "1*a.c"),
        ],
        True,
    ),
    1327: Solution(
        "Dates",
        "",
        """o=Orders.loc[Orders.order_date.dt.strftime('%Y-%m').eq('2020-02')]
units=o.groupby('product_id').unit.sum().rename('unit')
return Products.merge(units,on='product_id').loc[lambda s:s.unit.ge(100),['product_name','unit']]""",
        [
            ("unit >= 100", "unit > 100", "unit.ge(100)", "unit.gt(100)"),
            ("SUM(unit) AS unit", "MAX(unit) AS unit", "unit.sum()", "unit.max()"),
        ],
    ),
    1336: Solution(
        "Aggregation",
        "",
        """tx=Transactions.groupby(['user_id','transaction_date']).size()
v=[int(tx.get((u,d),0)) for u,d in Visits[['user_id','visit_date']].itertuples(index=False,name=None)]
return pd.DataFrame([(n,v.count(n)) for n in range(max(v,default=0)+1)],columns=['transactions_count','visits_count'])""",
        [
            (
                "SELECT 0 AS n",
                "SELECT 1 AS n",
                "range(max(v,default=0)+1)",
                "range(1,max(v,default=0)+1)",
            ),
            (
                "FROM S AS s LEFT JOIN",
                "FROM S AS s JOIN",
                "for n in range(max(v,default=0)+1)",
                "for n in sorted(set(v))",
            ),
        ],
        True,
    ),
    1341: Solution(
        "Ranking",
        "",
        """cnt=MovieRating.groupby('user_id').size().rename('n')
user=Users.merge(cnt,on='user_id').sort_values(['n','name'],ascending=[False,True]).name.iloc[0]
r=MovieRating.loc[MovieRating.created_at.dt.strftime('%Y-%m').eq('2020-02')].groupby('movie_id').rating.mean().rename('avg')
title=Movies.merge(r,on='movie_id').sort_values(['avg','title'],ascending=[False,True]).title.iloc[0]
return pd.DataFrame({'results':[user,title]})""",
        [
            (
                "COUNT(1) DESC, name",
                "COUNT(1) DESC, name DESC",
                "['n','name'],ascending=[False,True]",
                "['n','name'],ascending=[False,False]",
            ),
            (
                "AVG(rating) DESC",
                "AVG(rating) ASC",
                "['avg','title'],ascending=[False,True]",
                "['avg','title'],ascending=[True,True]",
            ),
        ],
        True,
    ),
    1350: Solution(
        "Filtering",
        "",
        "return Students.loc[~Students.department_id.isin(Departments.id),['id','name']]",
        [
            ("NOT IN", "IN", "~Students.department_id", "Students.department_id"),
            ("WHERE department_id", "WHERE id", "Students.department_id.isin", "Students.id.isin"),
        ],
    ),
    1355: Solution(
        "Aggregation",
        "",
        """n=Friends.activity.value_counts()
return n[n.gt(n.min()) & n.lt(n.max())].index.to_frame(index=False)""",
        [
            ("cnt > (SELECT MIN", "cnt >= (SELECT MIN", "n.gt(n.min())", "n.ge(n.min())"),
            ("cnt < (SELECT MAX", "cnt <= (SELECT MAX", "n.lt(n.max())", "n.le(n.max())"),
        ],
    ),
    1364: Solution(
        "Joins",
        "",
        """c=Contacts.assign(trusted=Contacts.contact_email.isin(Customers.email))
counts=c.groupby('user_id').agg(contacts_cnt=('contact_email','size'),trusted_contacts_cnt=('trusted','sum'))
a=Invoices.merge(Customers,left_on='user_id',right_on='customer_id').merge(counts,how='left',on='user_id').fillna({'contacts_cnt':0,'trusted_contacts_cnt':0})
return a[['invoice_id','customer_name','price','contacts_cnt','trusted_contacts_cnt']].sort_values('invoice_id')""",
        [
            ("LEFT JOIN Contacts", "JOIN Contacts", "how='left'", "how='inner'"),
            (
                "COUNT(t4.email)",
                "COUNT(t3.contact_email)",
                "trusted_contacts_cnt=('trusted','sum')",
                "trusted_contacts_cnt=('trusted','size')",
            ),
        ],
        True,
    ),
    1369: Solution(
        "Ranking",
        """WITH r AS (SELECT a.*,ROW_NUMBER() OVER(PARTITION BY username ORDER BY startDate DESC) n,COUNT(*) OVER(PARTITION BY username) cnt FROM UserActivity a)
SELECT username,activity,startDate,endDate FROM r WHERE n=2 OR cnt=1""",
        """a=UserActivity.sort_values('startDate',ascending=False)
pos=a.groupby('username').cumcount()+1
return a.loc[pos.eq(2) | a.groupby('username').activity.transform('size').eq(1)]""",
        [
            (" OR cnt=1", "", " | a.groupby('username').activity.transform('size').eq(1)", ""),
            ("WHERE n=2", "WHERE n=1", "pos.eq(2)", "pos.eq(1)"),
        ],
    ),
    1378: Solution(
        "Joins",
        "",
        "return Employees.merge(EmployeeUNI,on='id',how='left')[['unique_id','name']]",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            (
                "SELECT unique_id",
                "SELECT IFNULL(unique_id,0) AS unique_id",
                "[['unique_id','name']]",
                "[['unique_id','name']].fillna({'unique_id':0})",
            ),
        ],
    ),
    1384: Solution(
        "Dates",
        "",
        """names=Product.set_index('product_id').product_name
rows=[]
for s in Sales.itertuples():
    for y in range(s.period_start.year,s.period_end.year+1):
        first=max(s.period_start,pd.Timestamp(y,1,1))
        last=min(s.period_end,pd.Timestamp(y,12,31))
        rows.append((s.product_id,names[s.product_id],str(y),s.average_daily_sales*((last-first).days+1)))
return pd.DataFrame(rows,columns=['product_id','product_name','report_year','total_amount']).sort_values(['product_id','report_year'])""",
        [
            (" ) + 1", " ) + 0", "(last-first).days+1", "(last-first).days"),
            (
                "DAYOFYEAR(s.period_start)",
                "1",
                "max(s.period_start,pd.Timestamp(y,1,1))",
                "pd.Timestamp(y,1,1)",
            ),
        ],
        True,
    ),
    1393: Solution(
        "Aggregation",
        "",
        """p=Stocks.price.where(Stocks.operation.eq('Sell'),-Stocks.price)
return p.groupby(Stocks.stock_name).sum().rename('capital_gain_loss').reset_index()""",
        [
            ("-price, price", "price, price", "-Stocks.price", "Stocks.price"),
            ("-price, price", "0, price", "-Stocks.price", "0"),
        ],
    ),
    1398: Solution(
        "Filtering",
        "",
        """groups=Orders.groupby('customer_id').product_name.agg(set)
ok=groups.map(lambda p:'A' in p and 'B' in p and 'C' not in p)
return Customers.loc[Customers.customer_id.isin(ok[ok].index)].sort_values('customer_id')""",
        [
            (" AND SUM(product_name = 'C') = 0", "", " and 'C' not in p", ""),
            (" AND SUM(product_name = 'B') > 0", "", " and 'B' in p", ""),
        ],
        True,
    ),
    1407: Solution(
        "Joins",
        "",
        """d=Rides.groupby('user_id').distance.sum()
a=Users.assign(travelled_distance=Users.id.map(d).fillna(0))
return a[['name','travelled_distance']].sort_values(['travelled_distance','name'],ascending=[False,True])""",
        [
            ("LEFT JOIN", "JOIN", "a[['name'", "a.loc[a.id.isin(Rides.user_id),['name'"),
            ("ORDER BY 2 DESC, 1", "ORDER BY 2 DESC, 1 DESC", "[False,True]", "[False,False]"),
        ],
        True,
    ),
    1412: Solution(
        "Ranking",
        "",
        """groups=Exam.groupby('exam_id').score
outlier=Exam.score.eq(groups.transform('min')) | Exam.score.eq(groups.transform('max'))
ok=Student.student_id.isin(Exam.student_id) & ~Student.student_id.isin(Exam.loc[outlier,'student_id'])
return Student.loc[ok].sort_values('student_id')""",
        [
            (" AND SUM(rk2 = 1) = 0", "", " | Exam.score.eq(groups.transform('max'))", ""),
            ("SUM(rk1 = 1) = 0 AND ", "", "Exam.score.eq(groups.transform('min')) | ", ""),
        ],
        True,
    ),
    1421: Solution(
        "Joins",
        "",
        "return Queries.merge(NPV,on=['id','year'],how='left').fillna({'npv':0})",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            ("IFNULL(npv, 0)", "npv", ".fillna({'npv':0})", ""),
        ],
    ),
    1435: Solution(
        "Aggregation",
        "",
        """bins=['[0-5>','[5-10>','[10-15>','15 or more']
groups=pd.cut(Sessions.duration,[-1,300,600,900,float('inf')],right=False,labels=bins)
return groups.value_counts(sort=False).rename_axis('bin').reset_index(name='total')""",
        [
            ("duration < 300", "duration <= 300", "right=False", "right=True"),
            ("900 <= duration", "900 < duration", "600,900,float", "600,901,float"),
        ],
    ),
    1440: Solution(
        "Joins",
        "",
        """v=Variables.set_index('name').value
a=Expressions.copy()
l=a.left_operand.map(v)
r=a.right_operand.map(v)
result=(a.operator.eq('=') & l.eq(r)) | (a.operator.eq('>') & l.gt(r)) | (a.operator.eq('<') & l.lt(r))
return a.assign(value=result.map({True:'true',False:'false'}))""",
        [
            ("v1.value > v2.value", "v1.value >= v2.value", "l.gt(r)", "l.ge(r)"),
            ("v1.value < v2.value", "v1.value > v2.value", "l.lt(r)", "l.gt(r)"),
        ],
    ),
    1445: Solution(
        "Aggregation",
        "",
        """net=Sales.sold_num.where(Sales.fruit.eq('apples'),-Sales.sold_num)
return net.groupby(Sales.sale_date).sum().rename('diff').reset_index().sort_values('sale_date')""",
        [
            ("sold_num, -sold_num", "sold_num, sold_num", "-Sales.sold_num", "Sales.sold_num"),
            ("fruit = 'apples'", "fruit = 'oranges'", "eq('apples')", "eq('oranges')"),
        ],
        True,
    ),
    1454: Solution(
        "Dates",
        "",
        """a=Logins.drop_duplicates().sort_values(['id','login_date']).copy()
a['grp']=a.login_date-pd.to_timedelta(a.groupby('id').cumcount(),unit='D')
runs=a.groupby(['id','grp']).size()
ids=runs[runs.ge(5)].index.get_level_values('id')
return Accounts.loc[Accounts.id.isin(ids)].sort_values('id')""",
        [(">= 5", "> 5", "runs.ge(5)", "runs.gt(5)"), (">= 5", ">= 4", "runs.ge(5)", "runs.ge(4)")],
        True,
    ),
    1459: Solution(
        "Joins",
        "",
        """from itertools import combinations
rows=[]
for a,b in combinations(Points.sort_values('id').itertuples(),2):
    area=abs((a.x_value-b.x_value)*(a.y_value-b.y_value))
    if area: rows.append((a.id,b.id,area))
return pd.DataFrame(rows,columns=['p1','p2','area']).sort_values(['area','p1','p2'],ascending=[False,True,True])""",
        [
            (
                "WHERE p1.x_value != p2.x_value AND p1.y_value != p2.y_value",
                "",
                "if area:",
                "if area>=0:",
            ),
            ("area DESC", "area ASC", "[False,True,True]", "[True,True,True]"),
        ],
        True,
    ),
}
