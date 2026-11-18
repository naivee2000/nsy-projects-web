"""Native Pandas references for the most recent Database problems."""

from .database_solutions_01 import Solution

SOLUTIONS = {
    3564: Solution(
        "Aggregation",
        "",
        """a=sales.merge(products,on='product_id')
a['season']=a.sale_date.dt.month.map(lambda m:['Winter','Spring','Summer','Fall'][(m%12)//3])
a['revenue']=a.quantity*a.price
g=a.groupby(['season','category']).agg(total_quantity=('quantity','sum'),total_revenue=('revenue','sum')).reset_index()
return g.sort_values(['season','total_quantity','total_revenue','category'],ascending=[True,False,False,True]).drop_duplicates('season')""",
        [
            (
                "total_revenue DESC",
                "total_revenue ASC",
                "[True,False,False,True]",
                "[True,False,True,True]",
            ),
            ("SUM(quantity * price)", "SUM(price)", "a.quantity*a.price", "a.price"),
        ],
        True,
    ),
    3570: Solution(
        "Joins",
        "",
        """n=borrowing_records.loc[borrowing_records.return_date.isna()].groupby('book_id').size().rename('current_borrowers')
a=library_books.merge(n,on='book_id')
return a.loc[a.current_borrowers.eq(a.total_copies)].drop(columns='total_copies').sort_values(['current_borrowers','title'],ascending=[False,True])""",
        [
            (
                "WHERE return_date IS NULL",
                "",
                "borrowing_records.loc[borrowing_records.return_date.isna()]",
                "borrowing_records",
            ),
            (
                "current_borrowers = total_copies",
                "current_borrowers <= total_copies",
                "current_borrowers.eq",
                "current_borrowers.le",
            ),
        ],
        True,
    ),
    3580: Solution(
        "Window functions",
        "",
        """names=employees.set_index('employee_id').name
rows=[]
for u,g in performance_reviews.sort_values('review_date').groupby('employee_id'):
    scores=g.rating.tolist()[-3:]
    if len(scores)==3 and scores[0]<scores[1]<scores[2]:
        rows.append((u,names[u],scores[2]-scores[0]))
return pd.DataFrame(rows,columns=['employee_id','name','improvement_score']).sort_values(['improvement_score','name'],ascending=[False,True])""",
        [
            (
                "MIN(delta) > 0",
                "MIN(delta) >= 0",
                "scores[0]<scores[1]<scores[2]",
                "scores[0]<=scores[1]<=scores[2]",
            ),
            ("review_date DESC", "review_date ASC", "tolist()[-3:]", "tolist()[:3][::-1]"),
        ],
        True,
    ),
    3586: Solution(
        "Dates",
        "",
        """rows=[]
for u,g in covid_tests.groupby('patient_id'):
    pos=g.loc[g.result.eq('Positive'),'test_date'].min()
    neg=g.loc[g.result.eq('Negative') & g.test_date.gt(pos),'test_date'].min()
    if pd.notna(neg): rows.append((u,(neg-pos).days))
n=pd.DataFrame(rows,columns=['patient_id','recovery_time'])
return patients.merge(n,on='patient_id').sort_values(['recovery_time','patient_name'])""",
        [
            (
                "MIN(test_date) AS first_positive_date",
                "MAX(test_date) AS first_positive_date",
                "eq('Positive'),'test_date'].min()",
                "eq('Positive'),'test_date'].max()",
            ),
            (
                "MIN(t.test_date) AS first_negative_date",
                "MAX(t.test_date) AS first_negative_date",
                "gt(pos),'test_date'].min()",
                "gt(pos),'test_date'].max()",
            ),
        ],
        True,
    ),
    3601: Solution(
        "Aggregation",
        "",
        """a=trips.assign(half=trips.trip_date.dt.month.le(6).map({True:1,False:2}),eff=trips.distance_km/trips.fuel_consumed)
g=a.groupby(['driver_id','half']).eff.mean().unstack().reindex(columns=[1,2]).dropna()
g=g.loc[g[2].gt(g[1])].copy()
g['efficiency_improvement']=g[2]-g[1]
return drivers.merge(g.rename(columns={1:'first_half_avg',2:'second_half_avg'}).round(2),on='driver_id').sort_values(['efficiency_improvement','driver_name'],ascending=[False,True])""",
        [
            (
                "AVG(distance_km / fuel_consumed)",
                "SUM(distance_km) / SUM(fuel_consumed)",
                "a.groupby(['driver_id','half']).eff.mean()",
                "(a.groupby(['driver_id','half']).distance_km.sum()/a.groupby(['driver_id','half']).fuel_consumed.sum())",
            ),
            ("t1.half_avg < t2.half_avg", "t1.half_avg > t2.half_avg", "g[2].gt(g[1])", "g[2].lt(g[1])"),
        ],
        True,
    ),
    3611: Solution(
        "Dates",
        "",
        """week=meetings.meeting_date.dt.to_period('W-SUN')
total=meetings.groupby([meetings.employee_id,week]).duration_hours.sum()
heavy=total[total.gt(20)].groupby(level=0).size().rename('meeting_heavy_weeks')
return employees.merge(heavy[heavy.ge(2)],on='employee_id').sort_values(['meeting_heavy_weeks','employee_name'],ascending=[False,True])""",
        [
            ("hours > 20", "hours >= 20", "total.gt(20)", "total.ge(20)"),
            ("meeting_heavy_weeks >= 2", "meeting_heavy_weeks >= 1", "heavy.ge(2)", "heavy.ge(1)"),
        ],
        True,
    ),
    3617: Solution(
        "Window functions",
        "",
        """rows=[]
for u,g in study_sessions.sort_values(['session_date','session_id']).groupby('student_id'):
    subjects=g.subject.tolist()
    size=len(set(subjects))
    if size<3 or len(subjects)<2*size or len(subjects)%size: continue
    if g.session_date.diff().dt.days.gt(2).any(): continue
    if all(v==subjects[j%size] for j,v in enumerate(subjects)): rows.append((u,size,g.hours_studied.sum()))
data=pd.DataFrame(rows,columns=['student_id','cycle_length','total_study_hours'])
return students.merge(data,on='student_id').sort_values(['cycle_length','total_study_hours'],ascending=False)""",
        [
            ("cycle_length >= 3", "cycle_length >= 2", "size<3", "size<2"),
            ("date_diff > 2", "date_diff > 10", "days.gt(2)", "days.gt(10)"),
        ],
        ["cycle_length", "total_study_hours"],
    ),
    3626: Solution(
        "Ranking",
        "",
        """rows=[]
for u,g in inventory.groupby('store_id'):
    if len(g)<3: continue
    hi=g.sort_values(['price','quantity'],ascending=False).iloc[0]
    lo=g.sort_values(['price','quantity'],ascending=[True,False]).iloc[0]
    if hi.quantity < lo.quantity: rows.append((u,hi.product_name,lo.product_name,round(lo.quantity/hi.quantity,2)))
data=pd.DataFrame(rows,columns=['store_id','most_exp_product','cheapest_product','imbalance_ratio'])
return stores.merge(data,on='store_id').sort_values(['imbalance_ratio','store_name'],ascending=[False,True])""",
        [
            ("cnt >= 3", "cnt >= 2", "len(g)<3", "len(g)<2"),
            (
                "p1.quantity < p2.quantity",
                "p1.quantity > p2.quantity",
                "hi.quantity < lo.quantity",
                "hi.quantity > lo.quantity",
            ),
        ],
        True,
    ),
    3642: Solution(
        "Aggregation",
        "",
        """rows=[]
for b,g in reading_sessions.groupby('book_id'):
    s=g.session_rating
    extreme=(s.le(2)|s.ge(4)).sum()
    if len(s)>=5 and s.max()>=4 and s.min()<=2 and extreme*5>=3*len(s):
        rows.append((b,s.max()-s.min(),round(extreme/len(s),2)))
a=pd.DataFrame(rows,columns=['book_id','rating_spread','polarization_score'])
return books.merge(a,on='book_id').sort_values(['polarization_score','title'],ascending=False)""",
        [
            (" >= 3 * COUNT(1)", " > 3 * COUNT(1)", "extreme*5>=3*len(s)", "extreme*5>3*len(s)"),
            (
                "MAX(session_rating) - MIN(session_rating)",
                "MAX(session_rating) + MIN(session_rating)",
                "s.max()-s.min()",
                "s.max()+s.min()",
            ),
        ],
        True,
    ),
}
