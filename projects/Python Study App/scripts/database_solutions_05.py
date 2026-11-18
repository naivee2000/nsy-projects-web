from .database_solutions_01 import Solution

MUSIC = """songs=Listens.drop_duplicates().groupby(['day','user_id']).song_id.agg(set)
from itertools import combinations
pairs=set()
for _,group in songs.groupby(level='day'):
    for (a,sa),(b,sb) in combinations(group.droplevel('day').items(),2):
        if len(sa & sb)>=3: pairs.add(tuple(sorted((a,b))))
friends={tuple(sorted(row)) for row in Friendship.itertuples(index=False,name=None)}
"""
HIRE_SQL = """WITH seniors AS (SELECT employee_id,salary,SUM(salary) OVER(ORDER BY salary,employee_id ROWS UNBOUNDED PRECEDING) cost FROM Candidates WHERE experience='Senior'),
jun AS (SELECT employee_id,SUM(salary) OVER(ORDER BY salary,employee_id ROWS UNBOUNDED PRECEDING) cost FROM Candidates WHERE experience='Junior'),
picked AS (SELECT employee_id,'Senior' experience FROM seniors WHERE cost<=70000 UNION ALL
SELECT employee_id,'Junior' experience FROM jun WHERE cost<=70000-(SELECT COALESCE(SUM(salary),0) FROM seniors WHERE cost<=70000)) """
HIRE_PD = """remaining=70000
hired=[]
for label in ['Senior','Junior']:
    g=Candidates.loc[Candidates.experience.eq(label)].sort_values(['salary','employee_id'])
    chosen=g.loc[g.salary.cumsum().le(remaining)]
    hired.extend((e,label) for e in chosen.employee_id)
    remaining-=int(chosen.salary.sum())
"""
SOLUTIONS = {
    1741: Solution(
        "Aggregation",
        "",
        """a=Employees.assign(total_time=Employees.out_time-Employees.in_time).rename(columns={'event_day':'day'})
return a.groupby(['day','emp_id']).total_time.sum().reset_index()""",
        [
            (
                "SUM(out_time - in_time)",
                "MAX(out_time - in_time)",
                "total_time.sum()",
                "total_time.max()",
            ),
            (
                "out_time - in_time",
                "out_time - in_time + 1",
                "out_time-Employees.in_time",
                "out_time-Employees.in_time+1",
            ),
        ],
    ),
    1747: Solution(
        "Joins",
        "",
        """pairs=LogInfo.merge(LogInfo,on='account_id',suffixes=('_a','_b'))
return pairs.loc[pairs.ip_address_a.ne(pairs.ip_address_b) & pairs.login_a.between(pairs.login_b,pairs.logout_b),['account_id']].drop_duplicates()""",
        [
            (
                "a.login BETWEEN b.login AND b.logout",
                "a.login >= b.login AND a.login < b.logout",
                "pairs.login_b,pairs.logout_b)",
                "pairs.login_b,pairs.logout_b,inclusive='left')",
            ),
            (
                "a.ip_address != b.ip_address",
                "a.login != b.login",
                "pairs.ip_address_a.ne(pairs.ip_address_b)",
                "pairs.login_a.ne(pairs.login_b)",
            ),
        ],
    ),
    1767: Solution(
        "Joins",
        """WITH RECURSIVE todo AS (SELECT task_id,subtasks_count subtask_id FROM Tasks UNION ALL SELECT task_id,subtask_id-1 FROM todo WHERE subtask_id>1)
SELECT t.task_id,t.subtask_id FROM todo t WHERE NOT EXISTS(SELECT 1 FROM Executed e WHERE e.task_id=t.task_id AND e.subtask_id=t.subtask_id)""",
        """done=set(Executed.itertuples(index=False,name=None))
left=[(t.task_id,s) for t in Tasks.itertuples() for s in range(1,t.subtasks_count+1) if (t.task_id,s) not in done]
return pd.DataFrame(left,columns=['task_id','subtask_id'])""",
        [
            ("WHERE subtask_id>1", "WHERE subtask_id>2", "range(1,t.subtasks", "range(2,t.subtasks"),
            (
                "e.task_id=t.task_id AND ",
                "",
                "(t.task_id,s) not in done",
                "s not in {p[1] for p in done}",
            ),
        ],
    ),
    1777: Solution(
        "Reshaping",
        "",
        """cols=['store1','store2','store3']
return Products.pivot(index='product_id',columns='store',values='price').reindex(columns=cols).reset_index()""",
        [
            ("price, NULL", "price, 0", ".reset_index()", ".fillna(0).reset_index()"),
            (
                "IF(store = 'store1'",
                "IF(store = 'store2'",
                ".reset_index()",
                ".assign(store1=lambda d:d.store2).reset_index()",
            ),
        ],
    ),
    1783: Solution(
        "Aggregation",
        "",
        """m=Championships.drop(columns='year').melt(value_name='player_id').groupby('player_id').size().rename('grand_slams_count')
return Players.merge(m,on='player_id')""",
        [
            (
                "UNION ALL",
                "UNION",
                "groupby('player_id').size()",
                "drop_duplicates('player_id').groupby('player_id').size()",
            ),
            (
                "COUNT(1) AS grand_slams_count",
                "COUNT(DISTINCT player_id) AS grand_slams_count",
                ".size().rename",
                ".player_id.nunique().rename",
            ),
        ],
    ),
    1795: Solution(
        "Reshaping",
        "",
        """m=Products.melt(id_vars='product_id',var_name='store',value_name='price')
return m.dropna(subset=['price'])""",
        [
            (
                "WHERE store1 IS NOT NULL",
                "WHERE 1=1",
                "m.dropna(subset=['price'])",
                "m.loc[m.price.notna() | m.store.eq('store1')]",
            ),
            (
                "store1 IS NOT NULL",
                "store1 > 0",
                "m.dropna(subset=['price'])",
                "m.loc[m.price.notna() & ~(m.store.eq('store1') & m.price.eq(0))]",
            ),
        ],
    ),
    1809: Solution(
        "Joins",
        "",
        """p=Playback.merge(Ads,on='customer_id')
seen=p.loc[p.timestamp.between(p.start_time,p.end_time),'session_id']
return Playback.loc[~Playback.session_id.isin(seen),['session_id']]""",
        [
            (
                "BETWEEN p.start_time AND p.end_time",
                "> p.start_time AND a.timestamp < p.end_time",
                "p.start_time,p.end_time)",
                "p.start_time,p.end_time,inclusive='neither')",
            ),
            ("NOT IN", "IN", "~Playback.session_id", "Playback.session_id"),
        ],
    ),
    1811: Solution(
        "Window functions",
        "",
        """medals=Contests.melt(id_vars='contest_id',value_name='user_id')
gold=Contests.gold_medal.value_counts()
qualified=set(gold[gold.ge(3)].index)
for u,g in medals.groupby('user_id'):
    ids=set(g.contest_id)
    if any({n,n+1,n+2} <= ids for n in ids): qualified.add(u)
return Users.loc[Users.user_id.isin(qualified),['name','mail']]""",
        [
            ("COUNT(1) >= 3", "COUNT(1) >= 4", "{n,n+1,n+2}", "{n,n+1,n+2,n+3}"),
            (
                "WHERE type = 1",
                "WHERE type <> 1",
                "Contests.gold_medal.value_counts()",
                "medals.loc[medals.variable.ne('gold_medal'),'user_id'].value_counts()",
            ),
        ],
    ),
    1821: Solution(
        "Filtering",
        "",
        "return Customers.loc[Customers.year.eq(2021) & Customers.revenue.gt(0),['customer_id']]",
        [
            ("revenue > 0", "revenue >= 0", "revenue.gt", "revenue.ge"),
            ("year = '2021' AND ", "", "Customers.year.eq(2021) & ", ""),
        ],
    ),
    1831: Solution(
        "Ranking",
        "",
        """best=Transactions.groupby(Transactions.day.dt.date).amount.transform('max')
return Transactions.loc[Transactions.amount.eq(best),['transaction_id']].sort_values('transaction_id')""",
        [
            (
                "RANK()",
                "ROW_NUMBER()",
                "Transactions.loc[Transactions.amount.eq(best),['transaction_id']]",
                "Transactions.loc[Transactions.amount.eq(best)].drop_duplicates(subset=['amount'])[['transaction_id']]",
            ),
            ("amount DESC", "amount ASC", "transform('max')", "transform('min')"),
        ],
        True,
    ),
    1841: Solution(
        "Aggregation",
        "",
        """home=Matches[['home_team_id','home_team_goals','away_team_goals']].set_axis(['team_id','gf','ga'],axis=1)
away=Matches[['away_team_id','away_team_goals','home_team_goals']].set_axis(home.columns,axis=1)
a=pd.concat([home,away],ignore_index=True)
a['points']=3*a.gf.gt(a.ga).astype(int)+a.gf.eq(a.ga).astype(int)
g=a.groupby('team_id').agg(matches_played=('gf','size'),points=('points','sum'),goal_for=('gf','sum'),goal_against=('ga','sum'))
g['goal_diff']=g.goal_for-g.goal_against
return Teams.merge(g,on='team_id').drop(columns='team_id').sort_values(['points','goal_diff','team_name'],ascending=[False,False,True])""",
        [
            ("THEN 3", "THEN 2", "3*a.gf", "2*a.gf"),
            ("ELSE 1 END", "ELSE 0 END", "+a.gf.eq(a.ga).astype(int)", "+0"),
        ],
        True,
    ),
    1843: Solution(
        "Dates",
        "",
        """t=Transactions.loc[Transactions.type.eq('Creditor')].copy()
t['month']=t.day.dt.year*12+t.day.dt.month
s=t.groupby(['account_id','month']).amount.sum().reset_index().merge(Accounts,on='account_id')
hi=s.loc[s.amount.gt(s.max_income)]
ids=[u for u,g in hi.groupby('account_id') if any(m+1 in set(g.month) for m in g.month)]
return pd.DataFrame({'account_id':ids})""",
        [
            ("> max_income", ">= max_income", "amount.gt", "amount.ge"),
            (
                "WHERE type = 'Creditor'",
                "",
                "Transactions.loc[Transactions.type.eq('Creditor')]",
                "Transactions",
            ),
        ],
    ),
    1853: Solution(
        "Dates",
        "",
        "return Days.assign(day=Days.day.dt.strftime('%A, %B ')+Days.day.dt.day.astype(str)+Days.day.dt.strftime(', %Y'))",
        [
            ("%e", "%d", "dt.day.astype(str)", "dt.strftime('%d')"),
            ("%M", "%b", "'%A, %B '", "'%A, %b '"),
        ],
    ),
    1867: Solution(
        "Aggregation",
        "",
        """g=OrdersDetails.groupby('order_id').quantity.agg(['max','mean'])
return g[g['max'].gt(g['mean'].max())].index.to_frame(index=False)""",
        [
            ("max_quantity >", "max_quantity >=", ".gt(g['mean']", ".ge(g['mean']"),
            ("MAX(avg_quantity)", "MIN(avg_quantity)", "g['mean'].max()", "g['mean'].min()"),
        ],
    ),
    1875: Solution(
        "Ranking",
        "",
        """a=Employees.loc[Employees.salary.duplicated(keep=False)].copy()
a['team_id']=a.salary.rank(method='dense').astype(int)
return a.sort_values(['team_id','employee_id'])""",
        [
            (
                "ORDER BY salary)",
                "ORDER BY salary DESC)",
                "method='dense'",
                "method='dense',ascending=False",
            ),
            (
                "HAVING COUNT(1) > 1",
                "HAVING COUNT(1) >= 1",
                "Employees.loc[Employees.salary.duplicated(keep=False)]",
                "Employees",
            ),
        ],
        True,
    ),
    1890: Solution(
        "Dates",
        "",
        """a=Logins.loc[Logins.time_stamp.dt.year.eq(2020)]
return a.groupby('user_id').time_stamp.max().reset_index(name='last_stamp')""",
        [
            ("MAX(time_stamp)", "MIN(time_stamp)", ".time_stamp.max()", ".time_stamp.min()"),
            ("= 2020", "= 2019", "eq(2020)", "eq(2019)"),
        ],
    ),
    1892: Solution(
        "Joins",
        """WITH f AS (SELECT user1_id u,user2_id friend FROM Friendship UNION ALL SELECT user2_id,user1_id FROM Friendship)
SELECT f.u AS user_id,l.page_id,COUNT(DISTINCT f.friend) AS friends_likes FROM f JOIN Likes l ON l.user_id=f.friend
WHERE NOT EXISTS(SELECT 1 FROM Likes m WHERE m.user_id=f.u AND m.page_id=l.page_id) GROUP BY f.u,l.page_id""",
        """from collections import Counter
owned=set(Likes.itertuples(index=False,name=None))
edges=list(Friendship.itertuples(index=False,name=None))
votes=Counter((u,p) for a,b in edges for u,f in [(a,b),(b,a)] for v,p in owned if f==v and (u,p) not in owned)
return pd.DataFrame([(u,p,c) for (u,p),c in votes.items()],columns=['user_id','page_id','friends_likes'])""",
        [
            (" UNION ALL SELECT user2_id,user1_id FROM Friendship", "", "[(a,b),(b,a)]", "[(a,b)]"),
            ("m.user_id=f.u AND m.page_id=l.page_id", "1=0", " and (u,p) not in owned", ""),
        ],
    ),
    1907: Solution(
        "Aggregation",
        "",
        """v=Accounts.income
return pd.DataFrame({'category':['Low Salary','Average Salary','High Salary'],'accounts_count':[v.lt(20000).sum(),v.between(20000,50000).sum(),v.gt(50000).sum()]})""",
        [
            ("income < 20000", "income <= 20000", "lt(20000)", "le(20000)"),
            ("income > 50000", "income >= 50000", "gt(50000)", "ge(50000)"),
        ],
    ),
    1917: Solution(
        "Joins",
        "",
        MUSIC
        + """return pd.DataFrame([(u,f) for a,b in pairs-friends for u,f in [(a,b),(b,a)]],columns=['user_id','recommended_id'])""",
        [
            (">= 3", "> 3", "sa & sb)>=3", "sa & sb)>3"),
            ("l1.user_id != l2.user_id", "l1.user_id < l2.user_id", "[(a,b),(b,a)]", "[(a,b)]"),
        ],
    ),
    1919: Solution(
        "Joins",
        "",
        MUSIC + """return pd.DataFrame(sorted(pairs & friends),columns=['user1_id','user2_id'])""",
        [(">= 3", "> 3", "sa & sb)>=3", "sa & sb)>3"), (">= 3", ">= 2", "sa & sb)>=3", "sa & sb)>=2")],
    ),
    1934: Solution(
        "Aggregation",
        "",
        """rates=Confirmations.action.eq('confirmed').groupby(Confirmations.user_id).mean().round(2)
return Signups[['user_id']].assign(confirmation_rate=Signups.user_id.map(rates).fillna(0))""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "Signups[['user_id']].assign",
                "Signups.loc[Signups.user_id.isin(Confirmations.user_id),['user_id']].assign",
            ),
            ("action = 'confirmed'", "action = 'timeout'", "eq('confirmed')", "eq('timeout')"),
        ],
    ),
    1939: Solution(
        "Dates",
        "",
        """s=Confirmations.sort_values(['user_id','time_stamp'])
gap=s.groupby('user_id').time_stamp.diff()
return s.loc[gap.le(pd.Timedelta(hours=24)),['user_id']].drop_duplicates()""",
        [("<= 24", "< 24", "gap.le", "gap.lt"), ("<= 24", "<= 48", "hours=24", "hours=48")],
    ),
    1949: Solution(
        "Joins",
        "",
        """from collections import defaultdict
friends=defaultdict(set)
for a,b in Friendship.itertuples(index=False,name=None):
    friends[a].add(b)
    friends[b].add(a)
rows=[(a,b,len(friends[a]&friends[b])) for a,b in Friendship.itertuples(index=False,name=None) if len(friends[a]&friends[b])>=3]
return pd.DataFrame(rows,columns=['user1_id','user2_id','common_friend'])""",
        [(">= 3", "> 3", ">=3", ">3"), (">= 3", ">= 2", ">=3", ">=2")],
    ),
    1951: Solution(
        "Joins",
        "",
        """from itertools import combinations
followers=Relations.groupby('user_id').follower_id.agg(set)
pairs=[(u,v,len(a&b)) for (u,a),(v,b) in combinations(followers.items(),2)]
best=max(n for _,_,n in pairs)
return pd.DataFrame([(u,v) for u,v,n in pairs if n==best],columns=['user1_id','user2_id'])""",
        [
            (
                "RANK()",
                "ROW_NUMBER()",
                "[(u,v) for u,v,n in pairs if n==best]",
                "[(u,v) for u,v,n in pairs if n==best][:1]",
            ),
            (
                "COUNT(1) DESC",
                "COUNT(1) ASC",
                "max(n for _,_,n in pairs)",
                "min(n for _,_,n in pairs if n)",
            ),
        ],
    ),
    1965: Solution(
        "Joins",
        "",
        """a=set(Employees.employee_id)
b=set(Salaries.employee_id)
return pd.DataFrame({'employee_id':sorted(a ^ b)})""",
        [
            (
                " UNION SELECT employee_id FROM Salaries WHERE employee_id NOT IN (SELECT employee_id FROM Employees)",
                "",
                "a ^ b",
                "a - b",
            ),
            (
                "SELECT employee_id FROM Employees WHERE employee_id NOT IN (SELECT employee_id FROM Salaries) UNION ",
                "",
                "a ^ b",
                "b - a",
            ),
        ],
        True,
    ),
    1972: Solution(
        "Window functions",
        "",
        """a=Calls[['caller_id','recipient_id','call_time']].copy()
b=a.rename(columns={'caller_id':'recipient_id','recipient_id':'caller_id'})
both=pd.concat([a,b]).sort_values('call_time')
v=both.groupby(['caller_id',both.call_time.dt.date]).recipient_id.agg(['first','last'])
return v[v['first'].eq(v['last'])].reset_index()[['caller_id']].drop_duplicates().rename(columns={'caller_id':'user_id'})""",
        [
            (
                " UNION ALL SELECT recipient_id, caller_id, call_time FROM Calls",
                "",
                "pd.concat([a,b])",
                "a",
            ),
            ("first = last", "first <> last", "['first'].eq", "['first'].ne"),
        ],
    ),
    1978: Solution(
        "Joins",
        "",
        """ok=Employees.salary.lt(30000) & Employees.manager_id.notna() & ~Employees.manager_id.isin(Employees.employee_id)
return Employees.loc[ok,['employee_id']].sort_values('employee_id')""",
        [
            ("salary < 30000", "salary <= 30000", "salary.lt", "salary.le"),
            (" AND e1.manager_id IS NOT NULL", "", " & Employees.manager_id.notna()", ""),
        ],
        True,
    ),
    1988: Solution(
        "Joins",
        "",
        """a=Schools[['school_id']].copy()
a['score']=[Exam.loc[Exam.student_count.le(cap),'score'].min() for cap in Schools.capacity]
return a.fillna({'score':-1})""",
        [
            (
                "capacity >= e.student_count",
                "capacity > e.student_count",
                "student_count.le",
                "student_count.lt",
            ),
            ("MIN(IFNULL", "MAX(IFNULL", "'score'].min()", "'score'].max()"),
        ],
    ),
    1990: Solution(
        "Reshaping",
        "",
        """idx=pd.MultiIndex.from_product([['Android','IOS','Web'],['Reading','Sports','Programming']],names=['platform','experiment_name'])
return Experiments.groupby(['platform','experiment_name']).size().reindex(idx,fill_value=0).reset_index(name='num_experiments')""",
        [
            ("LEFT JOIN", "JOIN", ".reindex(idx,fill_value=0)", ""),
            ("COUNT(experiment_id)", "COUNT(*)", "fill_value=0", "fill_value=1"),
        ],
    ),
    2004: Solution(
        "Window functions",
        HIRE_SQL
        + """SELECT labels.experience,COUNT(p.employee_id) accepted_candidates FROM
(SELECT 'Senior' experience UNION ALL SELECT 'Junior') labels LEFT JOIN picked p USING(experience) GROUP BY labels.experience""",
        HIRE_PD
        + """return pd.DataFrame({'experience':['Senior','Junior'],'accepted_candidates':[sum(t==label for _,t in hired) for label in ['Senior','Junior']]})""",
        [
            ("cost<=70000", "cost<70000", "cumsum().le", "cumsum().lt"),
            ("70000-(SELECT", "70000-0*(SELECT", "remaining-=int", "remaining-=0*int"),
        ],
    ),
    2010: Solution(
        "Window functions",
        HIRE_SQL + "SELECT employee_id FROM picked",
        HIRE_PD + """return pd.DataFrame({'employee_id':[e for e,_ in hired]})""",
        [
            ("cost<=70000", "cost<70000", "cumsum().le", "cumsum().lt"),
            ("70000-(SELECT", "70000-0*(SELECT", "remaining-=int", "remaining-=0*int"),
        ],
    ),
    2020: Solution(
        "Joins",
        """SELECT COUNT(DISTINCT s.account_id) AS accounts_count FROM Subscriptions s WHERE s.start_date<='2021-12-31' AND s.end_date>='2021-01-01'
AND NOT EXISTS (SELECT 1 FROM Streams t WHERE t.account_id=s.account_id AND YEAR(t.stream_date)=2021)""",
        """t=Subscriptions.loc[Subscriptions.start_date.le('2021-12-31') & Subscriptions.end_date.ge('2021-01-01')]
played=Streams.loc[Streams.stream_date.dt.year.eq(2021),'account_id']
return pd.DataFrame({'accounts_count':[t.loc[~t.account_id.isin(played),'account_id'].nunique()]})""",
        [
            (
                "YEAR(t.stream_date)=2021",
                "YEAR(t.stream_date)<=2021",
                "dt.year.eq(2021)",
                "dt.year.le(2021)",
            ),
            (
                "s.start_date<='2021-12-31'",
                "YEAR(s.start_date)=2021",
                "start_date.le('2021-12-31')",
                "start_date.dt.year.eq(2021)",
            ),
        ],
    ),
}
