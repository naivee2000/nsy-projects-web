"""Reference submissions and two query-specific misunderstandings in each language."""

from dataclasses import dataclass


@dataclass
class Solution:
    topic: str
    sql: str
    pandas: str
    mistakes: list
    ordered: object = False


SOLUTIONS = {
    180: Solution(
        "Window functions",
        """WITH runs AS (SELECT num,LAG(num) OVER (ORDER BY id) prev,LEAD(num) OVER (ORDER BY id) nxt FROM Logs)
SELECT DISTINCT num AS ConsecutiveNums FROM runs WHERE num=prev AND num=nxt""",
        """s = Logs.sort_values('id').num
mask = s.eq(s.shift()) & s.eq(s.shift(-1))
return s[mask].drop_duplicates().to_frame('ConsecutiveNums')""",
        [
            ("num=prev AND num=nxt", "num=prev", " & s.eq(s.shift(-1))", ""),
            ("DISTINCT num AS", "num AS", ".drop_duplicates()", ""),
        ],
    ),
    184: Solution(
        "Joins",
        """SELECT d.name AS Department,e.name AS Employee,e.salary AS Salary FROM Employee e JOIN Department d ON d.id=e.departmentId
WHERE e.salary=(SELECT MAX(z.salary) FROM Employee z WHERE z.departmentId=e.departmentId)""",
        """best = Employee.groupby('departmentId').salary.transform('max')
rows = Employee.loc[Employee.salary.eq(best)].merge(Department, left_on='departmentId', right_on='id', suffixes=('_e','_d'))
return rows[['name_d','name_e','salary']].set_axis(['Department','Employee','Salary'],axis=1)""",
        [
            (
                " WHERE z.departmentId=e.departmentId",
                "",
                "Employee.groupby('departmentId').salary.transform('max')",
                "Employee.salary.max()",
            ),
            ("MAX(z.salary)", "MIN(z.salary)", "transform('max')", "transform('min')"),
        ],
    ),
    262: Solution(
        "Joins",
        """SELECT request_at AS Day, ROUND(AVG(status <> 'completed'),2) AS `Cancellation Rate` FROM Trips t
JOIN Users c ON c.users_id=t.client_id JOIN Users d ON d.users_id=t.driver_id
WHERE c.banned='No' AND d.banned='No' AND request_at BETWEEN '2013-10-01' AND '2013-10-03' GROUP BY request_at""",
        """valid = Users.loc[Users.banned.eq('No'),'users_id']
t = Trips.loc[Trips.client_id.isin(valid) & Trips.driver_id.isin(valid) & Trips.request_at.between('2013-10-01','2013-10-03')].copy()
t['Cancellation Rate'] = t.status.ne('completed')
return t.groupby('request_at')['Cancellation Rate'].mean().round(2).rename_axis('Day').reset_index()""",
        [
            ("d.banned='No' AND ", "", " & Trips.driver_id.isin(valid)", ""),
            ("c.banned='No' AND ", "", "Trips.client_id.isin(valid) & ", ""),
        ],
    ),
    511: Solution(
        "Aggregation",
        "SELECT player_id,MIN(event_date) AS first_login FROM Activity GROUP BY player_id",
        "return Activity.groupby('player_id').event_date.min().rename('first_login').reset_index()",
        [
            ("MIN(", "MAX(", ".min()", ".max()"),
            (
                " GROUP BY player_id",
                " GROUP BY player_id, device_id",
                "groupby('player_id')",
                "groupby(['player_id','device_id'])",
            ),
        ],
    ),
    512: Solution(
        "Window functions",
        """WITH r AS (SELECT a.*, ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY event_date) pos FROM Activity a)
SELECT player_id,device_id FROM r WHERE pos=1""",
        "return Activity.sort_values('event_date').drop_duplicates('player_id')[['player_id','device_id']]",
        [
            (
                "ORDER BY event_date",
                "ORDER BY event_date DESC",
                "sort_values('event_date')",
                "sort_values('event_date',ascending=False)",
            ),
            ("PARTITION BY player_id ", "", "drop_duplicates('player_id')", "head(1)"),
        ],
    ),
    534: Solution(
        "Window functions",
        "SELECT player_id,event_date,SUM(games_played) OVER (PARTITION BY player_id ORDER BY event_date) AS games_played_so_far FROM Activity",
        """rows = Activity.sort_values(['player_id','event_date']).copy()
rows['games_played_so_far'] = rows.groupby('player_id').games_played.cumsum()
return rows[['player_id','event_date','games_played_so_far']]""",
        [
            (" ORDER BY event_date", "", "games_played.cumsum()", "games_played.transform('sum')"),
            (
                "ORDER BY event_date",
                "ORDER BY event_date DESC",
                "'event_date']).copy()",
                "'event_date'],ascending=[True,False]).copy()",
            ),
        ],
    ),
    550: Solution(
        "Dates",
        """WITH firsts AS (SELECT player_id,MIN(event_date) d FROM Activity GROUP BY player_id)
SELECT ROUND(AVG(EXISTS(SELECT 1 FROM Activity a WHERE a.player_id=f.player_id AND a.event_date=DATE_ADD(f.d,INTERVAL 1 DAY))),2) AS fraction FROM firsts f""",
        """first = Activity.groupby('player_id').event_date.transform('min')
returned = Activity.loc[Activity.event_date.eq(first + pd.Timedelta(days=1)),'player_id'].nunique()
return pd.DataFrame({'fraction':[round(returned / Activity.player_id.nunique(),2)]})""",
        [
            ("INTERVAL 1 DAY", "INTERVAL 2 DAY", "days=1", "days=2"),
            (
                "a.player_id=f.player_id AND ",
                "",
                "Activity.event_date.eq(first + pd.Timedelta(days=1))",
                "Activity.event_date.isin(first + pd.Timedelta(days=1))",
            ),
        ],
    ),
    569: Solution(
        "Ranking",
        """WITH r AS (SELECT e.*,ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary,id) pos,
COUNT(*) OVER (PARTITION BY company) n FROM Employee e)
SELECT id,company,salary FROM r WHERE pos IN (FLOOR((n+1)/2), FLOOR((n+2)/2))""",
        """s = Employee.sort_values(['company','salary','id'])
pos = s.groupby('company').cumcount() + 1
n = s.groupby('company').id.transform('size')
return s.loc[(pos.eq((n+1)//2)) | (pos.eq((n+2)//2)), ['id','company','salary']]""",
        [
            (
                "ORDER BY salary,id",
                "ORDER BY salary,id DESC",
                "sort_values(['company','salary','id'])",
                "sort_values(['company','salary','id'],ascending=[True,True,False])",
            ),
            ("FLOOR((n+2)/2)", "FLOOR((n+1)/2)", " | (pos.eq((n+2)//2))", ""),
        ],
    ),
    570: Solution(
        "Aggregation",
        "SELECT name FROM Employee WHERE id IN (SELECT managerId FROM Employee GROUP BY managerId HAVING COUNT(*)>=5)",
        """counts = Employee.managerId.value_counts()
return Employee.loc[Employee.id.isin(counts[counts >= 5].index),['name']]""",
        [(">=5", ">5", ">= 5", "> 5"), (">=5", "=5", ">= 5", "== 5")],
    ),
    571: Solution(
        "Aggregation",
        """WITH r AS (SELECT num,frequency,SUM(frequency) OVER (ORDER BY num) hi,SUM(frequency) OVER () n FROM Numbers)
SELECT ROUND(AVG(num),1) AS median FROM r WHERE hi>=FLOOR((n+1)/2) AND hi-frequency<FLOOR((n+2)/2)""",
        "return pd.DataFrame({'median':[Numbers.num.repeat(Numbers.frequency).median()]})",
        [
            (
                "SUM(frequency) OVER",
                "SUM(1) OVER",
                "Numbers.num.repeat(Numbers.frequency)",
                "Numbers.num",
            ),
            (
                "hi-frequency<FLOOR((n+2)/2)",
                "hi-frequency<FLOOR((n+1)/2)",
                "Numbers.num.repeat(Numbers.frequency).median()",
                "sorted(Numbers.num.repeat(Numbers.frequency))[(int(Numbers.frequency.sum())-1)//2]",
            ),
        ],
    ),
    574: Solution(
        "Aggregation",
        "SELECT c.name FROM Candidate c JOIN Vote v ON c.id=v.candidateId GROUP BY c.id,c.name ORDER BY COUNT(*) DESC LIMIT 1",
        """counts = Vote.candidateId.value_counts()
return Candidate.loc[Candidate.id.eq(counts.idxmax()), ['name']]""",
        [
            ("COUNT(*) DESC", "COUNT(*) ASC", "idxmax()", "idxmin()"),
            ("COUNT(*) DESC", "c.id ASC", "counts.idxmax()", "counts.index.min()"),
        ],
    ),
    577: Solution(
        "Joins",
        "SELECT e.name,b.bonus FROM Employee e LEFT JOIN Bonus b ON e.empId=b.empId WHERE b.bonus IS NULL OR b.bonus<1000",
        """rows = Employee.merge(Bonus, how='left', on='empId')
return rows.loc[rows.bonus.isna() | rows.bonus.lt(1000),['name','bonus']]""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            ("bonus<1000", "bonus<=1000", ".lt(1000)", ".le(1000)"),
        ],
    ),
    578: Solution(
        "Aggregation",
        """SELECT question_id AS survey_log FROM SurveyLog GROUP BY question_id ORDER BY SUM(action='answer')/NULLIF(SUM(action='show'),0) DESC,question_id ASC LIMIT 1""",
        """a = SurveyLog.assign(answers=SurveyLog.action.eq('answer'),shows=SurveyLog.action.eq('show')).groupby('question_id')[['answers','shows']].sum().reset_index()
a['rate'] = a.answers / a.shows
return a.sort_values(['rate','question_id'],ascending=[False,True]).head(1)[['question_id']].rename(columns={'question_id':'survey_log'})""",
        [
            ("/NULLIF(SUM(action='show'),0)", "", "a.answers / a.shows", "a.answers"),
            ("question_id ASC", "question_id DESC", "[False,True]", "[False,False]"),
        ],
    ),
    579: Solution(
        "Window functions",
        """WITH r AS (SELECT id,month,SUM(salary) OVER (PARTITION BY id ORDER BY month RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS Salary,
MAX(month) OVER (PARTITION BY id) last_month FROM Employee) SELECT id,month,Salary FROM r WHERE month<last_month ORDER BY id,month DESC""",
        """parts = []
for ident,g in Employee.groupby('id'):
    data = g.set_index('month').salary
    for month in sorted(data.index, reverse=True)[1:]:
        total = data.loc[(data.index >= month-2) & (data.index <= month)].sum()
        parts.append((ident,month,total))
return pd.DataFrame(parts,columns=['id','month','Salary'])""",
        [
            ("2 PRECEDING", "1 PRECEDING", "month-2", "month-1"),
            ("month<last_month", "month<=last_month", "reverse=True)[1:]", "reverse=True)"),
        ],
        True,
    ),
    580: Solution(
        "Joins",
        "SELECT d.dept_name,COUNT(s.student_id) AS student_number FROM Department d LEFT JOIN Student s USING(dept_id) GROUP BY d.dept_id,d.dept_name ORDER BY student_number DESC,dept_name",
        """a = Department.merge(Student.groupby('dept_id').size().rename('student_number'), how='left',on='dept_id').fillna({'student_number':0})
return a[['dept_name','student_number']].sort_values(['student_number','dept_name'],ascending=[False,True])""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            ("student_number DESC", "student_number ASC", "[False,True]", "[True,True]"),
        ],
        True,
    ),
    585: Solution(
        "Window functions",
        """WITH r AS (SELECT i.*,COUNT(*) OVER(PARTITION BY tiv_2015) n,COUNT(*) OVER(PARTITION BY lat,lon) loc FROM Insurance i)
SELECT ROUND(SUM(tiv_2016),2) AS tiv_2016 FROM r WHERE n>1 AND loc=1""",
        """eligible = Insurance.tiv_2015.duplicated(keep=False) & ~Insurance.duplicated(['lat','lon'],keep=False)
return pd.DataFrame({'tiv_2016':[Insurance.loc[eligible,'tiv_2016'].sum(min_count=1)]})""",
        [
            ("n>1 AND loc=1", "n>1", " & ~Insurance.duplicated(['lat','lon'],keep=False)", ""),
            ("n>1 AND loc=1", "loc=1", "Insurance.tiv_2015.duplicated(keep=False) & ", ""),
        ],
    ),
    586: Solution(
        "Aggregation",
        "SELECT customer_number FROM Orders GROUP BY customer_number ORDER BY COUNT(*) DESC LIMIT 1",
        """c = Orders.customer_number.value_counts()
return pd.DataFrame({'customer_number':[c.idxmax()]})""",
        [
            ("COUNT(*) DESC", "COUNT(*) ASC", "idxmax()", "idxmin()"),
            ("COUNT(*) DESC", "customer_number ASC", "c.idxmax()", "c.index.min()"),
        ],
    ),
    596: Solution(
        "Aggregation",
        "SELECT class FROM Courses GROUP BY class HAVING COUNT(DISTINCT student)>=5",
        """n = Courses.groupby('class').student.nunique()
return n[n >= 5].index.to_frame(index=False)""",
        [(">=5", ">5", ">= 5", "> 5"), (">=5", "=5", ">= 5", "== 5")],
    ),
    597: Solution(
        "Aggregation",
        """SELECT ROUND(COALESCE((SELECT COUNT(DISTINCT requester_id,accepter_id) FROM RequestAccepted) /
NULLIF((SELECT COUNT(DISTINCT sender_id,send_to_id) FROM FriendRequest),0),0),2) AS accept_rate""",
        """den = len(FriendRequest.drop_duplicates(['sender_id','send_to_id']))
num = len(RequestAccepted.drop_duplicates(['requester_id','accepter_id']))
return pd.DataFrame({'accept_rate':[round(num/den,2) if den else 0]})""",
        [
            (
                "COUNT(DISTINCT requester_id,accepter_id)",
                "COUNT(*)",
                "len(RequestAccepted.drop_duplicates(['requester_id','accepter_id']))",
                "len(RequestAccepted)",
            ),
            (
                "COUNT(DISTINCT sender_id,send_to_id)",
                "COUNT(*)",
                "len(FriendRequest.drop_duplicates(['sender_id','send_to_id']))",
                "len(FriendRequest)",
            ),
        ],
    ),
    601: Solution(
        "Window functions",
        """WITH tagged AS (SELECT s.*,id-ROW_NUMBER() OVER(ORDER BY id) grp FROM Stadium s WHERE people>=100),
r AS (SELECT tagged.*, COUNT(*) OVER(PARTITION BY grp) n FROM tagged)
SELECT id,visit_date,people FROM r WHERE n>=3 ORDER BY visit_date""",
        """s = Stadium.loc[Stadium.people.ge(100)].sort_values('id').copy()
groups = s.id.astype(int) - pd.RangeIndex(len(s))
return s.loc[s.groupby(groups).id.transform('size').ge(3)].sort_values('visit_date')""",
        [("people>=100", "people>100", ".ge(100)", ".gt(100)"), ("n>=3", "n>=2", ".ge(3)", ".ge(2)")],
        True,
    ),
    602: Solution(
        "Aggregation",
        """WITH persons AS (SELECT requester_id id FROM RequestAccepted UNION ALL SELECT accepter_id FROM RequestAccepted)
SELECT id,COUNT(*) num FROM persons GROUP BY id ORDER BY num DESC LIMIT 1""",
        """counts = pd.concat([RequestAccepted.requester_id,RequestAccepted.accepter_id]).value_counts()
return pd.DataFrame({'id':[counts.idxmax()],'num':[counts.max()]})""",
        [
            (
                " UNION ALL SELECT accepter_id FROM RequestAccepted",
                "",
                "pd.concat([RequestAccepted.requester_id,RequestAccepted.accepter_id])",
                "RequestAccepted.requester_id",
            ),
            (
                "SELECT requester_id id FROM RequestAccepted UNION ALL SELECT accepter_id",
                "SELECT accepter_id id",
                "pd.concat([RequestAccepted.requester_id,RequestAccepted.accepter_id])",
                "RequestAccepted.accepter_id",
            ),
        ],
    ),
    603: Solution(
        "Joins",
        """SELECT a.seat_id FROM Cinema a WHERE a.free=1 AND EXISTS(SELECT 1 FROM Cinema b WHERE b.free=1 AND ABS(a.seat_id-b.seat_id)=1) ORDER BY a.seat_id""",
        """seats = Cinema.loc[Cinema.free.eq(1),'seat_id']
return seats[(seats-1).isin(seats) | (seats+1).isin(seats)].sort_values().to_frame()""",
        [
            ("ABS(a.seat_id-b.seat_id)", "(a.seat_id-b.seat_id)", " | (seats+1).isin(seats)", ""),
            (
                "AND EXISTS(SELECT 1 FROM Cinema b WHERE b.free=1 AND ABS(a.seat_id-b.seat_id)=1)",
                "",
                "[(seats-1).isin(seats) | (seats+1).isin(seats)]",
                "",
            ),
        ],
        True,
    ),
    607: Solution(
        "Joins",
        """SELECT s.name FROM SalesPerson s WHERE NOT EXISTS(SELECT 1 FROM Orders o JOIN Company c ON c.com_id=o.com_id WHERE o.sales_id=s.sales_id AND c.name='RED')""",
        """red = Company.loc[Company.name.eq('RED'),'com_id']
sellers = Orders.loc[Orders.com_id.isin(red),'sales_id']
return SalesPerson.loc[~SalesPerson.sales_id.isin(sellers),['name']]""",
        [
            ("NOT EXISTS", "EXISTS", "~SalesPerson.sales_id", "SalesPerson.sales_id"),
            (
                "AND c.name='RED'",
                "",
                "Orders.loc[Orders.com_id.isin(red),'sales_id']",
                "Orders.sales_id",
            ),
        ],
    ),
    608: Solution(
        "Hierarchy",
        """SELECT t.id,CASE WHEN t.p_id IS NULL THEN 'Root' WHEN EXISTS(SELECT 1 FROM Tree c WHERE c.p_id=t.id) THEN 'Inner' ELSE 'Leaf' END AS type FROM Tree t""",
        """result = Tree[['id']].copy()
result['type'] = ['Root' if pd.isna(p) else 'Inner' if i in set(Tree.p_id.dropna()) else 'Leaf' for i,p in Tree[['id','p_id']].itertuples(index=False,name=None)]
return result""",
        [
            ("THEN 'Root'", "THEN 'Inner'", "'Root' if", "'Inner' if"),
            ("THEN 'Inner'", "THEN 'Leaf'", "else 'Inner' if", "else 'Leaf' if"),
        ],
    ),
    610: Solution(
        "Filtering",
        "SELECT x,y,z,IF(x+y>z AND y+z>x AND x+z>y,'Yes','No') AS triangle FROM Triangle",
        """t = Triangle.copy()
ok = (t.x+t.y > t.z) & (t.y+t.z > t.x) & (t.x+t.z > t.y)
return t.assign(triangle=ok.map({True:'Yes',False:'No'}))""",
        [
            ("x+y>z", "x+y>=z", "t.x+t.y > t.z", "t.x+t.y >= t.z"),
            (" AND x+z>y", "", " & (t.x+t.z > t.y)", ""),
        ],
    ),
    612: Solution(
        "Aggregation",
        """SELECT ROUND(MIN(SQRT(POW(a.x-b.x,2)+POW(a.y-b.y,2))),2) AS shortest FROM Point2D a CROSS JOIN Point2D b WHERE a.x<>b.x OR a.y<>b.y""",
        """from itertools import combinations
from math import hypot
points = list(Point2D[['x','y']].itertuples(index=False,name=None))
return pd.DataFrame({'shortest':[round(min(hypot(x-u,y-v) for (x,y),(u,v) in combinations(points,2)),2)]})""",
        [
            (
                "a.x<>b.x OR a.y<>b.y",
                "a.x<>b.x AND a.y<>b.y",
                "in combinations(points,2)",
                "in combinations(points,2) if x!=u and y!=v",
            ),
            (
                "SQRT(POW(a.x-b.x,2)+POW(a.y-b.y,2))",
                "(ABS(a.x-b.x)+ABS(a.y-b.y))",
                "hypot(x-u,y-v)",
                "(abs(x-u)+abs(y-v))",
            ),
        ],
    ),
    613: Solution(
        "Aggregation",
        "SELECT MIN(ABS(a.x-b.x)) AS shortest FROM Point a JOIN Point b ON a.x<>b.x",
        """diff = Point.x.sort_values().diff().dropna()
return pd.DataFrame({'shortest':[diff.min()]})""",
        [
            ("MIN(ABS", "MAX(ABS", "diff.min()", "Point.x.max()-Point.x.min()"),
            ("a.x<>b.x", "a.x=b.x", "diff.min()", "(Point.x-Point.x).min()"),
        ],
    ),
    614: Solution(
        "Joins",
        """SELECT a.followee AS follower,COUNT(DISTINCT a.follower) AS num FROM Follow a WHERE EXISTS(SELECT 1 FROM Follow b WHERE b.follower=a.followee) GROUP BY a.followee ORDER BY follower""",
        """f = Follow.loc[Follow.followee.isin(Follow.follower)]
return f.groupby('followee').follower.nunique().rename('num').rename_axis('follower').reset_index()""",
        [
            (
                " WHERE EXISTS(SELECT 1 FROM Follow b WHERE b.follower=a.followee)",
                "",
                "Follow.loc[Follow.followee.isin(Follow.follower)]",
                "Follow",
            ),
            (
                "COUNT(DISTINCT a.follower)",
                "COUNT(DISTINCT a.followee)",
                "follower.nunique()",
                "followee.nunique()",
            ),
        ],
        True,
    ),
    615: Solution(
        "Aggregation",
        """WITH d AS (SELECT DATE_FORMAT(s.pay_date,'%Y-%m') pay_month,e.department_id,AVG(s.amount) avg_d
FROM Salary s JOIN Employee e USING(employee_id) GROUP BY pay_month,e.department_id),
c AS (SELECT DATE_FORMAT(pay_date,'%Y-%m') pay_month,AVG(amount) avg_c FROM Salary GROUP BY pay_month)
SELECT d.pay_month,d.department_id,CASE WHEN avg_d>avg_c THEN 'higher' WHEN avg_d<avg_c THEN 'lower' ELSE 'same' END comparison FROM d JOIN c USING(pay_month)""",
        """a = Salary.merge(Employee,on='employee_id').assign(pay_month=lambda x: x.pay_date.dt.strftime('%Y-%m'))
d = a.groupby(['pay_month','department_id']).amount.mean().rename('dept').reset_index()
d['overall'] = d.pay_month.map(a.groupby('pay_month').amount.mean())
d['comparison'] = ['higher' if x>y else 'lower' if x<y else 'same' for x,y in zip(d.dept,d.overall)]
return d[['pay_month','department_id','comparison']]""",
        [
            ("avg_d>avg_c", "avg_d>=avg_c", "if x>y", "if x>=y"),
            (
                "AVG(s.amount)",
                "SUM(s.amount)",
                "amount.mean().rename('dept')",
                "amount.sum().rename('dept')",
            ),
        ],
    ),
    618: Solution(
        "Reshaping",
        """WITH r AS (SELECT name,continent,ROW_NUMBER() OVER(PARTITION BY continent ORDER BY name) pos FROM Student)
SELECT MAX(IF(continent='America',name,NULL)) AS America,MAX(IF(continent='Asia',name,NULL)) AS Asia,MAX(IF(continent='Europe',name,NULL)) AS Europe FROM r GROUP BY pos ORDER BY pos""",
        """cols = {c:Student.loc[Student.continent.eq(c),'name'].sort_values().reset_index(drop=True) for c in ['America','Asia','Europe']}
return pd.DataFrame(cols)""",
        [
            ("ORDER BY name", "ORDER BY name DESC", "sort_values()", "sort_values(ascending=False)"),
            (
                "FROM r GROUP BY pos ORDER BY pos",
                "FROM r GROUP BY pos HAVING COUNT(DISTINCT continent)=3 ORDER BY pos",
                "pd.DataFrame(cols)",
                "pd.DataFrame(cols).dropna()",
            ),
        ],
        True,
    ),
    619: Solution(
        "Aggregation",
        "SELECT MAX(num) AS num FROM (SELECT num FROM MyNumbers GROUP BY num HAVING COUNT(*)=1) singles",
        """single = MyNumbers.loc[~MyNumbers.num.duplicated(keep=False),'num']
return pd.DataFrame({'num':[single.max()]})""",
        [
            (
                "COUNT(*)=1",
                "COUNT(*)>0",
                "~MyNumbers.num.duplicated(keep=False)",
                "MyNumbers.num.notna()",
            ),
            ("MAX(num)", "MIN(num)", "single.max()", "single.min()"),
        ],
    ),
    626: Solution(
        "Joins",
        "SELECT s.id,COALESCE(n.student,s.student) AS student FROM Seat s LEFT JOIN Seat n ON n.id=s.id+IF(MOD(s.id,2)=1,1,-1) ORDER BY s.id",
        """s = Seat.sort_values('id').copy()
lookup = s.set_index('id').student
partner = s.id.where(s.id.mod(2).eq(0),s.id+2)-1
s['student'] = partner.map(lookup).fillna(s.student)
return s""",
        [
            ("LEFT JOIN", "JOIN", ".fillna(s.student)", ".dropna()"),
            ("=1,1,-1", "=1,-1,1", "+2)-1", "-2)+1"),
        ],
        True,
    ),
}
