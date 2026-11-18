from .database_solutions_01 import Solution

WORDS_SQL = """WITH RECURSIVE words AS (
SELECT u.content_id,u.content_text,j.n,j.word FROM user_content u
JOIN JSON_TABLE(CONCAT('[',REPLACE(JSON_QUOTE(u.content_text),' ','","'),']'),'$[*]' COLUMNS(n FOR ORDINALITY,word VARCHAR(512) PATH '$')) j
), parts AS (SELECT w.*,0 i,CAST('' AS CHAR(512)) converted FROM words w UNION ALL
SELECT content_id,content_text,n,word,i+1,CONCAT(converted,CASE WHEN KEEP_WORD THEN SUBSTRING(word,i+1,1)
WHEN i=0 OR (HYPHENS AND SUBSTRING(word,i,1)='-') THEN UPPER(SUBSTRING(word,i+1,1))
ELSE LOWER(SUBSTRING(word,i+1,1)) END) FROM parts WHERE i<CHAR_LENGTH(word))
SELECT content_id,content_text AS original_text,GROUP_CONCAT(converted ORDER BY n SEPARATOR ' ') AS converted_text
FROM parts WHERE i=CHAR_LENGTH(word) GROUP BY content_id,content_text"""
WORDS_PD = """import re
def convert(w):
    if not w: return w
    if KEEP: return w
    if HYPHENS: return '-'.join(part.capitalize() for part in w.split('-'))
    return w.capitalize()
a=user_content.rename(columns={'content_text':'original_text'}).copy()
return a.assign(converted_text=a.original_text.map(lambda s:' '.join(convert(w) for w in s.split(' '))))"""
PAIR_PD = """from collections import Counter
from itertools import combinations
a=ProductPurchases.merge(ProductInfo,on='product_id')
counts=Counter()
for u,g in a.groupby('user_id'):
    counts.update(combinations(sorted(set(g[FIELD])),2))
"""
SOLUTIONS = {
    3262: Solution(
        "Joins",
        "",
        """from itertools import combinations
rows=[]
for u,g in EmployeeShifts.groupby('employee_id'):
    count=sum(max(a.start_time,b.start_time)<min(a.end_time,b.end_time) for a,b in combinations(g.itertuples(),2))
    if count: rows.append((u,count))
return pd.DataFrame(rows,columns=['employee_id','overlapping_shifts'])""",
        [
            (
                "t1.end_time > t2.start_time",
                "t1.end_time >= t2.start_time",
                "b.start_time)<min",
                "b.start_time)<=min",
            ),
            (
                "COUNT(*) AS overlapping_shifts",
                "COUNT(DISTINCT t1.start_time) AS overlapping_shifts",
                "sum(max(a.start_time,b.start_time)<min(a.end_time,b.end_time) for a,b in combinations(g.itertuples(),2))",
                "len({min(a.start_time,b.start_time) for a,b in combinations(g.itertuples(),2) if max(a.start_time,b.start_time)<min(a.end_time,b.end_time)})",
            ),
        ],
        True,
    ),
    3268: Solution(
        "Window functions",
        "",
        """from itertools import combinations
rows=[]
for u,g in EmployeeShifts.groupby('employee_id'):
    peak=max(((g.start_time<=s)&(g.end_time>s)).sum() for s in g.start_time)
    overlap=sum(max(0,(min(a.end_time,b.end_time)-max(a.start_time,b.start_time)).total_seconds()/60) for a,b in combinations(g.itertuples(),2))
    rows.append((u,peak,overlap))
return pd.DataFrame(rows,columns=['employee_id','max_overlapping_shifts','total_overlap_duration'])""",
        [
            ("MAX(concurrent_count)", "MIN(concurrent_count)", "peak=max(", "peak=min("),
            ("TIMESTAMPDIFF(MINUTE", "TIMESTAMPDIFF(HOUR", "total_seconds()/60", "total_seconds()/3600"),
        ],
        True,
    ),
    3278: Solution(
        "Joins",
        "",
        """rows=[]
for project,req in Projects.groupby('project_id'):
    scores=[]
    for u,g in Candidates.groupby('candidate_id'):
        m=req.merge(g,on='skill')
        if len(m)==len(req):
            score=100+10*(m.proficiency>m.importance).sum()-5*(m.proficiency<m.importance).sum()
            scores.append((-score,u))
    if scores:
        neg,u=min(scores)
        rows.append((project,u,-neg))
return pd.DataFrame(rows,columns=['project_id','candidate_id','score'])""",
        [
            ("THEN 10", "THEN 5", "100+10*", "100+5*"),
            (
                "score DESC, candidate_id",
                "score DESC, candidate_id DESC",
                "neg,u=min(scores)",
                "neg,u=min(scores,key=lambda x:(x[0],-x[1]))",
            ),
        ],
        True,
    ),
    3293: Solution(
        "Joins",
        "",
        """a=Products.merge(Discounts,on='category',how='left')
a['final_price']=a.price*(100-a.discount.fillna(0))/100
return a[['product_id','final_price','category']].sort_values('product_id')""",
        [
            ("LEFT JOIN", "JOIN", "how='left'", "how='inner'"),
            ("100 - IFNULL", "100 + IFNULL", "100-a.discount", "100+a.discount"),
        ],
        True,
    ),
    3308: Solution(
        "Ranking",
        "",
        """a=Trips.merge(Vehicles,on='vehicle_id').merge(Drivers,on='driver_id')
g=a.groupby(['fuel_type','driver_id']).agg(rating=('rating','mean'),distance=('distance','sum'),accidents=('accidents','first')).reset_index()
g['rating']=g.rating.round(2)
g=g.sort_values(['fuel_type','rating','distance','accidents'],ascending=[True,False,False,True])
return g.drop_duplicates('fuel_type')[['fuel_type','driver_id','rating','distance']]""",
        [
            (
                "distance DESC, accidents",
                "distance ASC, accidents",
                "[True,False,False,True]",
                "[True,False,True,True]",
            ),
            (
                "rating DESC, distance",
                "rating ASC, distance",
                "[True,False,False,True]",
                "[True,True,False,True]",
            ),
        ],
        True,
    ),
    3322: Solution(
        "Ranking",
        "",
        """a=SeasonStats.assign(points=3*SeasonStats.wins+SeasonStats.draws,goal_difference=SeasonStats.goals_for-SeasonStats.goals_against)
a=a.sort_values(['season_id','points','goal_difference','team_name'],ascending=[True,False,False,True])
return a.assign(position=a.groupby('season_id').cumcount()+1)[['season_id','team_id','team_name','points','goal_difference','position']]""",
        [
            ("wins * 3", "wins * 2", "3*SeasonStats.wins", "2*SeasonStats.wins"),
            (
                "goals_for - goals_against",
                "goals_against - goals_for",
                "SeasonStats.goals_for-SeasonStats.goals_against",
                "SeasonStats.goals_against-SeasonStats.goals_for",
            ),
        ],
        True,
    ),
    3328: Solution(
        "Strings",
        "",
        """rows=[]
for state,g in cities.groupby('state'):
    count=g.city.str[0].eq(state[0]).sum()
    if len(g)>=3 and count>0: rows.append((state,', '.join(sorted(g.city,key=lambda c:(c.replace(' ','').casefold(),c))),count))
return pd.DataFrame(rows,columns=['state','cities','matching_letter_count']).sort_values(['matching_letter_count','state'],ascending=[False,True])""",
        [
            ("COUNT(city) >= 3", "COUNT(city) > 3", "len(g)>=3", "len(g)>3"),
            ("matching_letter_count > 0", "matching_letter_count >= 0", "count>0", "count>=0"),
        ],
        True,
    ),
    3338: Solution(
        "Ranking",
        "",
        """rank=employees.groupby('dept').salary.rank(method='dense',ascending=False)
return employees.loc[rank.eq(2),['emp_id','dept']].sort_values('emp_id')""",
        [
            ("DENSE_RANK()", "RANK()", "method='dense'", "method='min'"),
            ("rk = 2", "rk = 1", "rank.eq(2)", "rank.eq(1)"),
        ],
        True,
    ),
    3358: Solution(
        "Filtering",
        "",
        "return books.loc[books.rating.isna(),['book_id','title','author','published_year']].sort_values('book_id')",
        [
            ("rating IS NULL", "rating IS NOT NULL", "rating.isna()", "rating.notna()"),
            (
                "ORDER BY 1",
                "ORDER BY 1 DESC",
                "sort_values('book_id')",
                "sort_values('book_id',ascending=False)",
            ),
        ],
        True,
    ),
    3368: Solution(
        "Strings",
        WORDS_SQL.replace("KEEP_WORD", "FALSE").replace("HYPHENS", "FALSE"),
        WORDS_PD.replace("KEEP", "False").replace("HYPHENS", "False"),
        [
            (
                "LOWER(SUBSTRING(word,i+1,1))",
                "SUBSTRING(word,i+1,1)",
                "return w.capitalize()",
                "return w[:1].upper()+w[1:]",
            ),
            ("SEPARATOR ' '", "SEPARATOR ''", "' '.join(convert(w)", "''.join(convert(w)"),
        ],
    ),
    3374: Solution(
        "Strings",
        WORDS_SQL.replace("KEEP_WORD", "NOT REGEXP_LIKE(word,'^[A-Za-z]','c')").replace(
            "HYPHENS", "REGEXP_LIKE(word,'^[A-Za-z]+(-[A-Za-z]+)+$','c')"
        ),
        WORDS_PD.replace("KEEP", "not re.match(r'[A-Za-z]',w)").replace(
            "HYPHENS", "re.fullmatch(r'[A-Za-z]+(-[A-Za-z]+)+',w)"
        ),
        [
            (
                "REGEXP_LIKE(word,'^[A-Za-z]+(-[A-Za-z]+)+$','c')",
                "FALSE",
                "if re.fullmatch(r'[A-Za-z]+(-[A-Za-z]+)+',w)",
                "if False",
            ),
            (
                "NOT REGEXP_LIKE(word,'^[A-Za-z]','c')",
                "FALSE",
                "if not re.match(r'[A-Za-z]',w)",
                "if False",
            ),
        ],
    ),
    3384: Solution(
        "Aggregation",
        "",
        """teams=Teams.set_index('player_id').team_name
a=Passes.assign(team_name=Passes.pass_from.map(teams),to=Passes.pass_to.map(teams),half_number=Passes.time_stamp.le('45:00').map({True:1,False:2}))
return a.assign(dominance=a.team_name.eq(a.to).map({True:1,False:-1})).groupby(['team_name','half_number']).dominance.sum().reset_index()""",
        [
            ("time_stamp <=", "time_stamp <", "time_stamp.le", "time_stamp.lt"),
            ("1, -1", "1, 0", "False:-1", "False:0"),
        ],
        True,
    ),
    3390: Solution(
        "Window functions",
        "",
        """teams=Teams.set_index('player_id').team_name
a=Passes.sort_values('time_stamp').copy()
a['team']=a.pass_from.map(teams)
a['ok']=a.team.eq(a.pass_to.map(teams))
rows=[]
for u,g in a.groupby('team'):
    streak=peak=0
    for ok in g.ok:
        streak=streak+1 if ok else 0
        peak=max(peak,streak)
    if peak: rows.append((u,peak))
return pd.DataFrame(rows,columns=['team_name','longest_streak']).sort_values('team_name')""",
        [
            ("MAX(streak_length)", "SUM(streak_length)", "peak=max(peak,streak)", "peak+=int(ok)"),
            (
                "ORDER BY 1",
                "ORDER BY 1 DESC",
                "sort_values('team_name')",
                "sort_values('team_name',ascending=False)",
            ),
        ],
        True,
    ),
    3401: Solution(
        "Hierarchy",
        """WITH RECURSIVE walk AS (SELECT giver_id start_id,receiver_id curr,1 n,gift_value value_sum FROM SecretSanta
UNION ALL SELECT w.start_id,s.receiver_id,w.n+1,w.value_sum+s.gift_value FROM walk w JOIN SecretSanta s ON w.curr=s.giver_id WHERE w.curr<>w.start_id AND s.giver_id>w.start_id),
cycles AS (SELECT DISTINCT n chain_length,value_sum total_gift_value FROM walk WHERE curr=start_id)
SELECT ROW_NUMBER() OVER(ORDER BY chain_length DESC,total_gift_value DESC) chain_id,chain_length,total_gift_value FROM cycles ORDER BY chain_id""",
        """edge={a:(b,v) for a,b,v in SecretSanta.itertuples(index=False,name=None)}
seen=set()
cycles=[]
for start in edge:
    if start in seen: continue
    u=start
    total=n=0
    while u not in seen:
        seen.add(u)
        u,v=edge[u]
        total+=v
        n+=1
    if u==start: cycles.append((n,total))
return pd.DataFrame([(j,n,v) for j,(n,v) in enumerate(sorted(set(cycles),reverse=True),1)],columns=['chain_id','chain_length','total_gift_value'])""",
        [
            (
                "SELECT DISTINCT n chain_length",
                "SELECT n chain_length",
                "sorted(set(cycles),reverse=True)",
                "sorted(cycles,reverse=True)",
            ),
            (
                "ORDER BY chain_length DESC,total_gift_value DESC",
                "ORDER BY chain_length ASC,total_gift_value ASC",
                "sorted(set(cycles),reverse=True)",
                "sorted(set(cycles))",
            ),
        ],
        True,
    ),
    3415: Solution(
        "Strings",
        "",
        "return Products.loc[Products.name.str.contains(r'(?<![0-9])[0-9]{3}(?![0-9])'),['product_id','name']].sort_values('product_id')",
        [
            ("(^|[^0-9])[0-9]{3}([^0-9]|$)", "[0-9]{3}", "(?<![0-9])[0-9]{3}(?![0-9])", "[0-9]{3}"),
            ("[0-9]{3}", "[0-9]{2}", "[0-9]{3}", "[0-9]{2}"),
        ],
        True,
    ),
    3421: Solution(
        "Window functions",
        "",
        """a=Scores.sort_values('exam_date')
g=a.groupby(['student_id','subject']).score.agg(first_score='first',latest_score='last').reset_index()
return g.loc[g.latest_score.gt(g.first_score)].sort_values(['student_id','subject'])""",
        [
            (
                "latest_score > first_score",
                "latest_score >= first_score",
                "latest_score.gt",
                "latest_score.ge",
            ),
            (
                "l.score AS latest_score",
                "(SELECT MAX(z.score) FROM Scores z WHERE z.student_id=l.student_id AND z.subject=l.subject) AS latest_score",
                "latest_score='last'",
                "latest_score='max'",
            ),
        ],
        True,
    ),
    3436: Solution(
        "Strings",
        "SELECT user_id,email FROM Users WHERE REGEXP_LIKE(email,'^[A-Za-z0-9_]+@[A-Za-z]+[.]com$','c') ORDER BY user_id",
        "return Users.loc[Users.email.str.fullmatch(r'[A-Za-z0-9_]+@[A-Za-z]+[.]com'),['user_id','email']].sort_values('user_id')",
        [
            ("@[A-Za-z]+", "@[A-Za-z0-9]+", "@[A-Za-z]+", "@[A-Za-z0-9]+"),
            ("A-Za-z0-9_", "A-Za-z0-9_.", "A-Za-z0-9_", "A-Za-z0-9_."),
        ],
        True,
    ),
    3451: Solution(
        "Strings",
        """SELECT ip,COUNT(*) invalid_count FROM logs WHERE NOT REGEXP_LIKE(ip,'^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?|0)[.]){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?|0)$') GROUP BY ip ORDER BY invalid_count DESC,ip DESC""",
        """def invalid(value):
    parts=value.split('.')
    return len(parts)!=4 or any(not p.isascii() or not p.isdigit() or int(p)>255 or (len(p)>1 and p[0]=='0') for p in parts)
n=logs.loc[logs.ip.map(invalid)].groupby('ip').size().reset_index(name='invalid_count')
return n.sort_values(['invalid_count','ip'],ascending=False)""",
        [
            ("[1-9][0-9]?|0", "[0-9]{1,3}", "int(p)>255 or (len(p)>1 and p[0]=='0')", "False"),
            ("ip DESC", "ip ASC", "ascending=False", "ascending=[False,True]"),
        ],
        True,
    ),
    3465: Solution(
        "Strings",
        "SELECT product_id,product_name,description FROM products WHERE REGEXP_LIKE(description,'SN[0-9]{4}-[0-9]{4}([^0-9]|$)','c') ORDER BY product_id",
        "return products.loc[products.description.str.contains(r'SN[0-9]{4}-[0-9]{4}(?![0-9])')].sort_values('product_id')",
        [("([^0-9]|$)", "", "(?![0-9])", ""), (",'c')", ",'i')", "r'SN", "r'(?i)SN")],
        True,
    ),
    3475: Solution(
        "Strings",
        "",
        """s=Samples.dna_sequence
return Samples.assign(has_start=s.str.startswith('ATG').astype(int),has_stop=s.str.endswith(('TAA','TAG','TGA')).astype(int),
    has_atat=s.str.contains('ATAT').astype(int),has_ggg=s.str.contains('GGG').astype(int)).sort_values('sample_id')""",
        [
            ("'ATG%'", "'%ATG%'", "str.startswith", "str.contains"),
            ("'GGG+'", "'GG+'", "contains('GGG')", "contains('GG')"),
        ],
        True,
    ),
    3497: Solution(
        "Aggregation",
        "",
        """a=UserActivity.groupby(['user_id','activity_type']).activity_duration.mean().unstack()
out=a.reindex(columns=['free_trial','paid']).dropna().round(2)
return out.set_axis(['trial_avg_duration','paid_avg_duration'],axis=1).reset_index().sort_values('user_id')""",
        [
            ("F JOIN P", "F LEFT JOIN P", ".dropna()", ".fillna(0)"),
            (
                "SUM(activity_duration) / COUNT(1)",
                "MAX(activity_duration)",
                "activity_duration.mean()",
                "activity_duration.max()",
            ),
        ],
        True,
    ),
    3521: Solution(
        "Joins",
        """SELECT a.product_id product1_id,b.product_id product2_id,p.category product1_category,q.category product2_category,COUNT(DISTINCT a.user_id) customer_count
FROM ProductPurchases a JOIN ProductPurchases b ON a.user_id=b.user_id AND a.product_id<b.product_id JOIN ProductInfo p ON p.product_id=a.product_id JOIN ProductInfo q ON q.product_id=b.product_id
GROUP BY a.product_id,b.product_id,p.category,q.category HAVING customer_count>=3 ORDER BY customer_count DESC,product1_id,product2_id""",
        PAIR_PD.replace("FIELD", "'product_id'")
        + """cats=ProductInfo.set_index('product_id').category
rows=[(a,b,cats[a],cats[b],n) for (a,b),n in counts.items() if n>=3]
return pd.DataFrame(rows,columns=['product1_id','product2_id','product1_category','product2_category','customer_count']).sort_values(['customer_count','product1_id','product2_id'],ascending=[False,True,True])""",
        [(">=3", ">3", "n>=3", "n>3"), (">=3", ">=2", "n>=3", "n>=2")],
        True,
    ),
    3554: Solution(
        "Joins",
        "",
        PAIR_PD.replace("FIELD", "'category'")
        + """rows=[(a,b,n) for (a,b),n in counts.items() if n>=3]
return pd.DataFrame(rows,columns=['category1','category2','customer_count']).sort_values(['customer_count','category1','category2'],ascending=[False,True,True])""",
        [(">= 3", "> 3", "n>=3", "n>3"), (">= 3", ">= 2", "n>=3", "n>=2")],
        True,
    ),
}
