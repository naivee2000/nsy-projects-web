from .database_solutions_01 import Solution

HASH_PD = """from collections import Counter
import re
counts=Counter()
for text in Tweets.loc[Tweets.tweet_date.dt.strftime('%Y-%m').eq('2024-02'),'tweet']:
    counts.update(re.findall(r'#[A-Za-z0-9_]+',text))
rows=sorted(counts.items(),key=lambda x:(x[1],x[0]),reverse=True)[:3]
"""
STAND = """a=TeamStats.assign(points=TeamStats.wins*3+TeamStats.draws)
a['position']=a.points.rank(method='min',ascending=False).astype(int)
"""
SOLUTIONS = {
    3050: Solution(
        "Joins",
        "",
        """from itertools import combinations
rows=[]
for trio in combinations(Toppings.sort_values('topping_name').itertuples(),3):
    rows.append((','.join(x.topping_name for x in trio),round(sum(x.cost for x in trio),2)))
return pd.DataFrame(rows,columns=['pizza','total_cost']).sort_values(['total_cost','pizza'],ascending=[False,True])""",
        [
            ("2 DESC, 1 ASC", "2 ASC, 1 ASC", "[False,True]", "[True,True]"),
            ("2 DESC, 1 ASC", "2 DESC, 1 DESC", "[False,True]", "[False,False]"),
        ],
        True,
    ),
    3051: Solution(
        "Filtering",
        "",
        """s=Candidates.groupby('candidate_id').skill.agg(set)
return s[s.map(lambda v:{'Python','Tableau','PostgreSQL'} <= v)].index.to_frame(index=False).sort_values('candidate_id')""",
        [
            (
                "COUNT(1) = 3",
                "COUNT(1) >= 2",
                "{'Python','Tableau','PostgreSQL'} <= v",
                "len({'Python','Tableau','PostgreSQL'} & v)>=2",
            ),
            ("'Python', 'Tableau', 'PostgreSQL'", "'Python', 'Tableau', 'C++'", "'PostgreSQL'", "'C++'"),
        ],
        True,
    ),
    3052: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal
space=Decimal(500000)
rows=[]
for kind in ['prime_eligible','not_prime']:
    size=Inventory.loc[Inventory.item_type.eq(kind),'square_footage']
    need=sum(Decimal(str(x)) for x in size)
    batches=int(space//need) if need else 0
    rows.append((kind,len(size)*batches))
    space-=need*batches
return pd.DataFrame(rows,columns=['item_type','item_count']).sort_values(['item_count','item_type'],ascending=False)""",
        [
            ("500000 % s", "500000", "space-=need*batches", "space-=0*need*batches"),
            (
                "cnt * FLOOR(500000 / s)",
                "FLOOR(500000 / s)",
                "len(size)*batches",
                "(1 if kind=='prime_eligible' else len(size))*batches",
            ),
        ],
        True,
    ),
    3053: Solution(
        "Filtering",
        "",
        """def kind(sides):
    a,b,c=sorted(sides)
    if a+b<=c: return 'Not A Triangle'
    return {1:'Equilateral',2:'Isosceles',3:'Scalene'}[len({a,b,c})]
return pd.DataFrame({'triangle_type':[kind(row) for row in Triangles.itertuples(index=False,name=None)]})""",
        [
            (" <= ", " < ", "a+b<=c", "a+b<c"),
            ("THEN 'Equilateral'", "THEN 'Isosceles'", "1:'Equilateral'", "1:'Isosceles'"),
        ],
    ),
    3054: Solution(
        "Hierarchy",
        "",
        """parents=set(Tree.P.dropna())
a=Tree[['N']].copy()
a['Type']=['Root' if pd.isna(p) else 'Inner' if n in parents else 'Leaf' for n,p in Tree[['N','P']].itertuples(index=False,name=None)]
return a.sort_values('N')""",
        [
            ("'Root'", "'Leaf'", "'Root' if", "'Leaf' if"),
            ("ORDER BY 1", "ORDER BY 1 DESC", "sort_values('N')", "sort_values('N',ascending=False)"),
        ],
        True,
    ),
    3056: Solution(
        "Aggregation",
        "",
        """a=Activities.merge(Age,on='user_id')
tot=a.groupby('age_bucket').time_spent.sum()
out=pd.DataFrame(index=tot.index)
for label in ['send','open']:
    amt=a.loc[a.activity_type.eq(label)].groupby('age_bucket').time_spent.sum().reindex(tot.index,fill_value=0)
    out[label+'_perc']=(amt*100/tot).round(2)
return out.reset_index()""",
        [
            ("100 * SUM", "1 * SUM", "amt*100", "amt*1"),
            ("time_spent, 0", "1, 0", "time_spent.sum().reindex", "time_spent.size().reindex"),
        ],
    ),
    3057: Solution(
        "Aggregation",
        "",
        """a=Project.merge(Employees,on='employee_id')
avg=a.groupby('team').workload.transform('mean')
return a.loc[a.workload.gt(avg),['employee_id','project_id','name','workload']].set_axis(['employee_id','project_id','employee_name','project_workload'],axis=1).sort_values(['employee_id','project_id'])""",
        [
            ("workload > avg_workload", "workload >= avg_workload", "workload.gt", "workload.ge"),
            ("AVG(workload)", "MAX(workload)", "transform('mean')", "transform('max')"),
        ],
        True,
    ),
    3058: Solution(
        "Joins",
        """WITH f AS (SELECT user_id1 u,user_id2 v FROM Friends UNION ALL SELECT user_id2,user_id1 FROM Friends)
SELECT x.user_id1,x.user_id2 FROM Friends x WHERE NOT EXISTS(SELECT 1 FROM f a JOIN f b ON a.v=b.v WHERE a.u=x.user_id1 AND b.u=x.user_id2) ORDER BY x.user_id1,x.user_id2""",
        """from collections import defaultdict
groups=defaultdict(set)
for a,b in Friends.itertuples(index=False,name=None):
    groups[a].add(b)
    groups[b].add(a)
rows=[(a,b) for a,b in Friends.itertuples(index=False,name=None) if not groups[a]&groups[b]]
return pd.DataFrame(sorted(rows),columns=['user_id1','user_id2'])""",
        [
            ("NOT EXISTS", "EXISTS", "if not groups", "if groups"),
            (" UNION ALL SELECT user_id2,user_id1 FROM Friends", "", "    groups[b].add(a)", "    pass"),
        ],
        True,
    ),
    3059: Solution(
        "Strings",
        "",
        """s=Emails.loc[Emails.email.str.endswith('.com'),'email'].str.rsplit('@',n=1).str[-1]
return s.value_counts().rename_axis('email_domain').reset_index(name='count').sort_values('email_domain')""",
        [
            (
                " WHERE email LIKE '%.com'",
                "",
                "Emails.loc[Emails.email.str.endswith('.com'),'email']",
                "Emails.email",
            ),
            (
                "COUNT(1)",
                "COUNT(DISTINCT SUBSTRING_INDEX(email,'@',-1))",
                "s.value_counts()",
                "s.drop_duplicates().value_counts()",
            ),
        ],
        True,
    ),
    3060: Solution(
        "Window functions",
        "",
        """a=Sessions.sort_values('session_end')
prev=a.groupby(['user_id','session_type']).session_end.shift()
return a.loc[(a.session_start-prev).le(pd.Timedelta(hours=12)),['user_id']].drop_duplicates().sort_values('user_id')""",
        [
            (
                "PARTITION BY user_id, session_type",
                "PARTITION BY user_id",
                "['user_id','session_type']",
                "['user_id']",
            ),
            ("session_start <=", "session_start <", "prev).le", "prev).lt"),
        ],
        True,
    ),
    3061: Solution(
        "Window functions",
        "",
        """h=Heights.sort_values('id').height
level=pd.concat([h.cummax(),h.iloc[::-1].cummax()],axis=1).min(axis=1)
return pd.DataFrame({'total_trapped_water':[(level-h).sum()]})""",
        [
            ("LEAST(l, r)", "GREATEST(l, r)", "min(axis=1)", "max(axis=1)"),
            ("LEAST(l, r) - height", "LEAST(l, r)", "(level-h).sum()", "level.sum()"),
        ],
    ),
    3087: Solution(
        "Strings",
        "",
        HASH_PD + "return pd.DataFrame(rows,columns=['hashtag','hashtag_count'])",
        [
            (
                "2 DESC, 1 DESC",
                "2 DESC, 1 ASC",
                "key=lambda x:(x[1],x[0]),reverse=True",
                "key=lambda x:(-x[1],x[0])",
            ),
            ("LIMIT 3", "LIMIT 2", "[:3]", "[:2]"),
        ],
        True,
    ),
    3089: Solution(
        "Window functions",
        """WITH feb AS (SELECT * FROM Posts WHERE post_date BETWEEN '2024-02-01' AND '2024-02-28'), w AS (
SELECT p.user_id,p.post_id,(SELECT COUNT(*) FROM feb q WHERE q.user_id=p.user_id AND q.post_date BETWEEN p.post_date AND DATE_ADD(p.post_date,INTERVAL 6 DAY)) n FROM feb p)
SELECT user_id,MAX(n) max_7day_posts,COUNT(*)/4 avg_weekly_posts FROM w GROUP BY user_id HAVING max_7day_posts>=2*avg_weekly_posts ORDER BY user_id""",
        """a=Posts.loc[Posts.post_date.between('2024-02-01','2024-02-28')]
rows=[]
for u,g in a.groupby('user_id'):
    peak=max(g.post_date.between(d,d+pd.Timedelta(days=6)).sum() for d in g.post_date.unique())
    avg=len(g)/4
    if peak>=2*avg: rows.append((u,peak,avg))
return pd.DataFrame(rows,columns=['user_id','max_7day_posts','avg_weekly_posts']).sort_values('user_id')""",
        [
            ("INTERVAL 6 DAY", "INTERVAL 7 DAY", "days=6", "days=7"),
            (">=2*", ">2*", "peak>=2*", "peak>2*"),
        ],
        True,
    ),
    3103: Solution(
        "Strings",
        """WITH RECURSIVE tags AS (SELECT tweet_id,tweet,1 idx,REGEXP_SUBSTR(tweet,'#[A-Za-z0-9_]+',1,1) hashtag FROM Tweets
UNION ALL SELECT tweet_id,tweet,idx+1,REGEXP_SUBSTR(tweet,'#[A-Za-z0-9_]+',1,idx+1) FROM tags WHERE hashtag IS NOT NULL)
SELECT hashtag,COUNT(*) AS count FROM tags WHERE hashtag IS NOT NULL GROUP BY hashtag ORDER BY count DESC,hashtag DESC LIMIT 3""",
        HASH_PD + "return pd.DataFrame(rows,columns=['hashtag','count'])",
        [
            (
                "count DESC,hashtag DESC",
                "count DESC,hashtag ASC",
                "key=lambda x:(x[1],x[0]),reverse=True",
                "key=lambda x:(-x[1],x[0])",
            ),
            ("LIMIT 3", "LIMIT 2", "[:3]", "[:2]"),
        ],
        True,
    ),
    3118: Solution(
        "Dates",
        "",
        """a=Purchases.merge(Users,on='user_id')
a=a.loc[a.purchase_date.dt.strftime('%Y-%m').eq('2023-11') & a.purchase_date.dt.weekday.eq(4)].copy()
a['week_of_month']=(a.purchase_date.dt.day+6)//7
idx=pd.MultiIndex.from_product([range(1,5),['Premium','VIP']],names=['week_of_month','membership'])
return a.groupby(['week_of_month','membership']).amount_spend.sum().reindex(idx,fill_value=0).reset_index(name='total_amount')""",
        [
            ("LEFT JOIN", "JOIN", ".reindex(idx,fill_value=0)", ".reindex(idx).dropna()"),
            (
                "DAYOFWEEK(purchase_date) = 6",
                "DAYOFWEEK(purchase_date) = 5",
                "weekday.eq(4)",
                "weekday.eq(3)",
            ),
        ],
        True,
    ),
    3124: Solution(
        "Ranking",
        "",
        """a=Calls.merge(Contacts,left_on='contact_id',right_on='id')
n=a.groupby('type').duration.rank(method='min',ascending=False)
a=a.loc[n.le(3)].sort_values(['type','duration','first_name'],ascending=False).copy()
a['duration_formatted']=a.duration.map(lambda v:f'{v//3600:02d}:{v%3600//60:02d}:{v%60:02d}')
return a[['first_name','type','duration_formatted']]""",
        [
            ("rk <= 3", "rk < 3", "n.le(3)", "n.lt(3)"),
            (
                "duration DESC ) AS rk",
                "duration ASC ) AS rk",
                "method='min',ascending=False",
                "method='min',ascending=True",
            ),
        ],
        True,
    ),
    3126: Solution(
        "Dates",
        """SELECT FLOOR(SUM(IF(session_status='stop',UNIX_TIMESTAMP(status_time),-UNIX_TIMESTAMP(status_time)))/86400) AS total_uptime_days FROM Servers""",
        """seconds=Servers.status_time.map(lambda d:int((d-pd.Timestamp('1970-01-01')).total_seconds()))
net=seconds.where(Servers.session_status.eq('stop'),-seconds)
return pd.DataFrame({'total_uptime_days':[int(net.sum()//86400)]})""",
        [
            ("FLOOR(", "CEIL(", "int(net.sum()//86400)", "int(-(-net.sum()//86400))"),
            ("/86400", "/3600", "//86400", "//3600"),
        ],
    ),
    3140: Solution(
        "Window functions",
        "",
        """s=Cinema.loc[Cinema.free.eq(1),'seat_id'].sort_values().reset_index(drop=True)
g=s.groupby(s-pd.RangeIndex(len(s))).agg(first_seat_id='min',last_seat_id='max',consecutive_seats_len='size')
return g[g.consecutive_seats_len.eq(g.consecutive_seats_len.max())].sort_values('first_seat_id').reset_index(drop=True)""",
        [
            (
                "RANK() OVER (ORDER BY COUNT(1) DESC)",
                "ROW_NUMBER() OVER (ORDER BY COUNT(1) DESC)",
                "sort_values('first_seat_id').reset_index",
                "sort_values('first_seat_id').head(1).reset_index",
            ),
            (
                "COUNT(1) DESC",
                "COUNT(1) ASC",
                "consecutive_seats_len.max()",
                "consecutive_seats_len.min()",
            ),
        ],
        True,
    ),
    3150: Solution(
        "Strings",
        """SELECT tweet_id FROM Tweets WHERE CHAR_LENGTH(content)>140 OR CHAR_LENGTH(content)-CHAR_LENGTH(REPLACE(content,'@',''))>3
OR CHAR_LENGTH(content)-CHAR_LENGTH(REPLACE(content,'#',''))>3 ORDER BY tweet_id""",
        """s=Tweets.content
return Tweets.loc[s.str.len().gt(140) | s.str.count('@').gt(3) | s.str.count('#').gt(3),['tweet_id']].sort_values('tweet_id')""",
        [(">140", ">=140", "gt(140)", "ge(140)"), ("))>3", "))>=3", "gt(3)", "ge(3)")],
        True,
    ),
    3156: Solution(
        "Window functions",
        "",
        """from collections import Counter
rows=[]
for u,g in Tasks.groupby('employee_id'):
    events=Counter(g.start_time)
    events.subtract(g.end_time)
    active=peak=seconds=0
    prev=None
    for time in sorted(events):
        if prev is not None and active: seconds+=(time-prev).total_seconds()
        active+=events[time]
        peak=max(peak,active)
        prev=time
    rows.append((u,int(seconds//3600),peak))
return pd.DataFrame(rows,columns=['employee_id','total_task_hours','max_concurrent_tasks']).sort_values('employee_id')""",
        [
            (
                "MAX(concurrent_count)",
                "MIN(concurrent_count)",
                "peak=max(peak,active)",
                "peak=int(peak or active>0)",
            ),
            ("FLOOR(", "CEIL(", "int(seconds//3600)", "int(-(-seconds//3600))"),
        ],
        True,
    ),
    3166: Solution(
        "Aggregation",
        "",
        """a=ParkingTransactions.assign(sec=(ParkingTransactions.exit_time-ParkingTransactions.entry_time).dt.total_seconds())
rows=[]
for car,g in a.groupby('car_id'):
    best=g.groupby('lot_id').sec.sum().idxmax()
    rows.append((car,round(g.fee_paid.sum(),2),round(g.fee_paid.sum()*3600/g.sec.sum(),2),best))
return pd.DataFrame(rows,columns=['car_id','total_fee_paid','avg_hourly_fee','most_time_lot']).sort_values('car_id')""",
        [
            ("duration DESC", "duration ASC", "sec.sum().idxmax()", "sec.sum().idxmin()"),
            ("total_seconds / 3600", "total_seconds / 60", "sum()*3600", "sum()*60"),
        ],
        True,
    ),
    3172: Solution(
        "Dates",
        "",
        """a=emails.merge(texts,on='email_id')
return a.loc[a.signup_action.eq('Verified') & (a.action_date.dt.normalize()-a.signup_date.dt.normalize()).dt.days.eq(1),['user_id']].sort_values('user_id')""",
        [
            ("= 1 AND", "= 0 AND", "days.eq(1)", "days.eq(0)"),
            (" AND signup_action = 'Verified'", "", "a.signup_action.eq('Verified') & ", ""),
        ],
        True,
    ),
    3182: Solution(
        "Joins",
        "",
        """rows=[]
for u,_,major in students.itertuples(index=False,name=None):
    required=set(courses.loc[courses.major.eq(major),'course_id'])
    passed=set(enrollments.loc[enrollments.student_id.eq(u) & enrollments.grade.eq('A'),'course_id'])
    if required and required <= passed: rows.append(u)
return pd.DataFrame({'student_id':sorted(rows)})""",
        [
            ("grade = 'A'", "grade IN ('A','B')", "grade.eq('A')", "grade.isin(['A','B'])"),
            ("= COUNT(major)", "> 0", "required <= passed", "bool(required & passed)"),
        ],
        True,
    ),
    3188: Solution(
        "Joins",
        """WITH eligible_gpa AS (
  SELECT student_id FROM enrollments GROUP BY student_id HAVING AVG(GPA) >= 2.5
)
SELECT s.student_id FROM students s JOIN eligible_gpa g ON g.student_id=s.student_id
JOIN courses c ON c.major=s.major
LEFT JOIN enrollments e ON e.student_id=s.student_id AND e.course_id=c.course_id
GROUP BY s.student_id
HAVING SUM(CASE WHEN LOWER(c.mandatory)='yes' AND (e.grade IS NULL OR e.grade<>'A') THEN 1 ELSE 0 END)=0
AND SUM(CASE WHEN LOWER(c.mandatory)='no' AND e.grade NOT IN ('A','B') THEN 1 ELSE 0 END)=0
AND COUNT(DISTINCT CASE WHEN LOWER(c.mandatory)='no' AND e.grade IS NOT NULL THEN c.course_id END) >= 2
ORDER BY s.student_id""",
        """rows=[]
for u,_,major in students.itertuples(index=False,name=None):
    e=enrollments.loc[enrollments.student_id.eq(u)]
    major_courses=courses.loc[courses.major.eq(major)]
    mandatory=set(major_courses.loc[major_courses.mandatory.str.lower().eq('yes'),'course_id'])
    electives=set(major_courses.loc[major_courses.mandatory.str.lower().eq('no'),'course_id'])
    required=e.loc[e.course_id.isin(mandatory)]
    options=e.loc[e.course_id.isin(electives)]
    if mandatory == set(required.course_id) and required.grade.eq('A').all() and options.course_id.nunique()>=2 and options.grade.isin(['A','B']).all() and e.GPA.mean()>=2.5:
        rows.append(u)
return pd.DataFrame({'student_id':sorted(rows)})""",
        [
            ("AVG(GPA) >= 2.5", "AVG(GPA) >= 0", "e.GPA.mean()>=2.5", "e.GPA.mean()>=0"),
            ("COUNT(DISTINCT CASE", "COUNT(CASE", "options.course_id.nunique()", "len(options)"),
        ],
        True,
    ),
    3198: Solution(
        "Strings",
        "",
        "return cities.groupby('state').city.agg(lambda x:', '.join(sorted(x))).reset_index(name='cities')",
        [
            (
                "ORDER BY city SEPARATOR",
                "ORDER BY city DESC SEPARATOR",
                "sorted(x)",
                "sorted(x,reverse=True)",
            ),
            ("SEPARATOR ', '", "SEPARATOR ','", "', '.join", "','.join"),
        ],
        True,
    ),
    3204: Solution(
        "Aggregation",
        "",
        """from functools import reduce
from operator import and_,or_
return pd.DataFrame({'common_perms':[reduce(and_,user_permissions.permissions)],'any_perms':[reduce(or_,user_permissions.permissions)]})""",
        [
            ("BIT_AND", "BIT_OR", "reduce(and_", "reduce(or_"),
            ("BIT_OR", "BIT_AND", "reduce(or_", "reduce(and_"),
        ],
    ),
    3214: Solution(
        "Dates",
        "",
        """a=user_transactions.assign(year=user_transactions.transaction_date.dt.year)
s=a.groupby(['year','product_id']).spend.sum().reset_index(name='curr_year_spend')
prev=s.rename(columns={'curr_year_spend':'prev_year_spend'}).copy()
prev['year']+=1
out=s.merge(prev,how='left',on=['year','product_id'])
out['yoy_rate']=((out.curr_year_spend-out.prev_year_spend)*100/out.prev_year_spend).round(2)
return out.sort_values(['product_id','year'])""",
        [("LEFT JOIN", "JOIN", "how='left'", "how='inner'"), ("* 100", "* 1", "*100/", "*1/")],
        True,
    ),
    3220: Solution(
        "Aggregation",
        "",
        """a=transactions.assign(odd_sum=transactions.amount.where(transactions.amount.mod(2).eq(1),0),even_sum=transactions.amount.where(transactions.amount.mod(2).eq(0),0))
return a.groupby('transaction_date')[['odd_sum','even_sum']].sum().reset_index()""",
        [("% 2 = 1", "% 2 = 0", ".eq(1)", ".eq(0)"), ("% 2 = 0", "% 2 = 1", ".eq(0)", ".eq(1)")],
        True,
    ),
    3230: Solution(
        "Aggregation",
        "",
        """a=Transactions.merge(Products,on='product_id')
rows=[]
for u,g in a.groupby('customer_id'):
    c=g.groupby('category').transaction_date.agg(['size','max']).sort_values(['size','max'],ascending=False)
    total=g.amount.sum()
    n=len(g)
    rows.append((u,round(total,2),n,len(c),round(total/n,2),c.index[0],round(n*10+total/100,2)))
return pd.DataFrame(rows,columns=['customer_id','total_amount','transaction_count','unique_categories','avg_transaction_amount','top_category','loyalty_score']).sort_values(['loyalty_score','customer_id'],ascending=[False,True])""",
        [
            (
                "cnt DESC, max_date DESC",
                "cnt DESC, max_date ASC",
                "['size','max'],ascending=False",
                "['size','max'],ascending=[False,True]",
            ),
            ("COUNT(1) * 10", "COUNT(1) * 1", "n*10+", "n*1+"),
        ],
        True,
    ),
    3236: Solution(
        "Hierarchy",
        "",
        """m=Employees.set_index('employee_id')
ceo=m.index[m.manager_id.isna()][0]
rows=[]
for u,g in m.iterrows():
    if u==ceo: continue
    v=u
    level=0
    while not pd.isna(m.at[v,'manager_id']):
        v=m.at[v,'manager_id']
        level+=1
    rows.append((u,g.employee_name,level,g.salary-m.at[ceo,'salary']))
return pd.DataFrame(rows,columns=['subordinate_id','subordinate_name','hierarchy_level','salary_difference']).sort_values(['hierarchy_level','subordinate_id'])""",
        [
            (
                "t.salary - p.salary",
                "p.salary - t.salary",
                "g.salary-m.at[ceo,'salary']",
                "m.at[ceo,'salary']-g.salary",
            ),
            (
                "hierarchy_level != 0",
                "hierarchy_level = 1",
                "rows.append((u,",
                "if level==1: rows.append((u,",
            ),
        ],
        True,
    ),
    3246: Solution(
        "Ranking",
        "",
        STAND
        + "return a[['team_id','team_name','points','position']].sort_values(['points','team_name'],ascending=[False,True])",
        [
            ("RANK()", "DENSE_RANK()", "method='min'", "method='dense'"),
            ("wins * 3", "wins * 2", "wins*3", "wins*2"),
        ],
        True,
    ),
    3252: Solution(
        "Ranking",
        "",
        STAND
        + """from math import ceil
a['tier']=['Tier 1' if p<=ceil(len(a)/3) else 'Tier 2' if p<=ceil(2*len(a)/3) else 'Tier 3' for p in a.position]
return a[['team_name','points','position','tier']].sort_values(['points','team_name'],ascending=[False,True])""",
        [
            ("RANK()", "DENSE_RANK()", "method='min'", "method='dense'"),
            ("CEIL(total_teams / 3.0)", "FLOOR(total_teams / 3.0)", "ceil(len(a)/3)", "(len(a)//3)"),
        ],
        True,
    ),
}
