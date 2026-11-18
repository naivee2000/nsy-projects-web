from .database_solutions_01 import Solution

SOLUTIONS = {
    3657: Solution(
        "Aggregation",
        "",
        """a=customer_transactions.assign(refunded=customer_transactions.transaction_type.eq('refund'))
g=a.groupby('customer_id').agg(total=('transaction_id','size'),refunds=('refunded','sum'),first=('transaction_date','min'),last=('transaction_date','max'))
ok=(g.total-g.refunds).ge(3) & (g.refunds/g.total).lt(.2) & (g['last']-g['first']).dt.days.ge(30)
return g[ok].index.to_frame(index=False).sort_values('customer_id')""",
        [("< 0.2", "<= 0.2", ".lt(.2)", ".le(.2)"), (">= 30", "> 30", ".ge(30)", ".gt(30)")],
        True,
    ),
    3673: Solution(
        "Aggregation",
        """SELECT session_id,user_id,TIMESTAMPDIFF(MINUTE,MIN(event_timestamp),MAX(event_timestamp)) session_duration_minutes,
SUM(event_type='scroll') scroll_count FROM app_events GROUP BY session_id,user_id
HAVING TIMESTAMPDIFF(SECOND,MIN(event_timestamp),MAX(event_timestamp))>1800 AND scroll_count>=5
AND SUM(event_type='click')*5<scroll_count AND SUM(event_type='purchase')=0 ORDER BY scroll_count DESC,session_id""",
        """rows=[]
for (sid,u),g in app_events.groupby(['session_id','user_id']):
    secs=(g.event_timestamp.max()-g.event_timestamp.min()).total_seconds()
    n=g.event_type.eq('scroll').sum()
    if secs>1800 and n>=5 and 5*g.event_type.eq('click').sum()<n and not g.event_type.eq('purchase').any():
        rows.append((sid,u,int(secs//60),n))
return pd.DataFrame(rows,columns=['session_id','user_id','session_duration_minutes','scroll_count']).sort_values(['scroll_count','session_id'],ascending=[False,True])""",
        [
            ("))>1800", "))>=1800", "secs>1800", "secs>=1800"),
            ("*5<scroll_count", "*5<=scroll_count", "sum()<n", "sum()<=n"),
        ],
        True,
    ),
    3705: Solution(
        "Dates",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
rows=[]
for u,g in restaurant_orders.groupby('customer_id'):
    n=len(g)
    ts=g.order_timestamp.dt.strftime('%H:%M:%S')
    peak=(ts.between('11:00:00','14:00:00') | ts.between('18:00:00','21:00:00')).sum()
    rates=g.order_rating.dropna()
    if n>=3 and 5*peak>=3*n and len(rates)*2>=n and rates.mean()>=4:
        pct=int((Decimal(int(peak))*100/n).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        avg=float((sum(Decimal(str(x)) for x in rates)/len(rates)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
        rows.append((u,n,pct,avg))
return pd.DataFrame(rows,columns=['customer_id','total_orders','peak_hour_percentage','average_rating']).sort_values(['average_rating','customer_id'],ascending=False)""",
        [
            (">= 3 * COUNT(1)", "> 3 * COUNT(1)", "5*peak>=3*n", "5*peak>3*n"),
            ("average_rating >= 4.0", "average_rating > 4.0", "rates.mean()>=4", "rates.mean()>4"),
        ],
        True,
    ),
    3716: Solution(
        "Window functions",
        "",
        """rows=[]
for u,g in subscription_events.sort_values(['event_date','event_id']).groupby('user_id'):
    end=g.iloc[-1]
    high=g.monthly_amount.max()
    days=(end.event_date-g.event_date.iloc[0]).days
    if end.event_type!='cancel' and g.event_type.eq('downgrade').any() and end.monthly_amount<high/2 and days>=60:
        rows.append((u,end.plan_name,end.monthly_amount,high,days))
return pd.DataFrame(rows,columns=['user_id','current_plan','current_monthly_amount','max_historical_amount','days_as_subscriber']).sort_values(['days_as_subscriber','user_id'],ascending=[False,True])""",
        [
            ("< 0.5 *", "<= 0.5 *", "monthly_amount<high", "monthly_amount<=high"),
            (">= 60", "> 60", "days>=60", "days>60"),
        ],
        True,
    ),
    3764: Solution(
        "Window functions",
        "",
        """from collections import Counter
counts=Counter()
for u,g in course_completions.sort_values('completion_date').groupby('user_id'):
    if len(g)>=5 and g.course_rating.mean()>=4:
        courses=g.course_name.tolist()
        counts.update(zip(courses,courses[1:]))
rows=[(a,b,n) for (a,b),n in counts.items()]
return pd.DataFrame(rows,columns=['first_course','second_course','transition_count']).sort_values(['transition_count','first_course','second_course'],ascending=[False,True,True])""",
        [
            ("COUNT(1) >= 5", "COUNT(1) > 5", "len(g)>=5", "len(g)>5"),
            ("AVG(course_rating) >= 4", "AVG(course_rating) > 4", "mean()>=4", "mean()>4"),
        ],
        True,
    ),
    3793: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
rows=[]
for u,g in prompts.groupby('user_id'):
    n=len(g)
    mean=Decimal(int(g.tokens.sum()))/n
    if n>=3 and int(g.tokens.max())>mean:
        rows.append((u,n,float(mean.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))))
return pd.DataFrame(rows,columns=['user_id','prompt_count','avg_tokens']).sort_values(['avg_tokens','user_id'],ascending=[False,True])""",
        [
            ("prompt_count >= 3", "prompt_count > 3", "n>=3", "n>3"),
            ("MAX(tokens) > AVG", "MAX(tokens) >= AVG", "max())>mean", "max())>=mean"),
        ],
        True,
    ),
    3808: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
rows=[]
for u,g in reactions.groupby('user_id'):
    counts=g.reaction.value_counts()
    if g.content_id.nunique()>=5 and 5*counts.iloc[0]>=3*len(g):
        ratio=(Decimal(int(counts.iloc[0]))/len(g)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        rows.append((u,counts.index[0],float(ratio)))
return pd.DataFrame(rows,columns=['user_id','dominant_reaction','reaction_ratio']).sort_values(['reaction_ratio','user_id'],ascending=[False,True])""",
        [
            (">= 3 * SUM", "> 3 * SUM", "counts.iloc[0]>=3", "counts.iloc[0]>3"),
            ("SUM(cnt) >= 5", "SUM(cnt) >= 4", "nunique()>=5", "nunique()>=4"),
        ],
        True,
    ),
    3832: Solution(
        "Window functions",
        """WITH days AS (SELECT user_id,action_date,MIN(action) action FROM activity GROUP BY user_id,action_date HAVING COUNT(*)=1),
runs AS (SELECT days.*,DATE_SUB(action_date,INTERVAL ROW_NUMBER() OVER(PARTITION BY user_id,action ORDER BY action_date) DAY) grp FROM days),
streaks AS (SELECT user_id,action,COUNT(*) streak_length,MIN(action_date) start_date,MAX(action_date) end_date FROM runs GROUP BY user_id,action,grp HAVING COUNT(*)>=5),
w AS (SELECT streaks.*,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY streak_length DESC,action ASC,start_date DESC) pos FROM streaks)
SELECT user_id,action,streak_length,start_date,end_date FROM w WHERE pos=1 ORDER BY streak_length DESC,user_id""",
        """a=activity.loc[~activity.duplicated(['user_id','action_date'],keep=False)].sort_values('action_date').copy()
a['grp']=a.action_date-pd.to_timedelta(a.groupby(['user_id','action']).cumcount(),unit='D')
g=a.groupby(['user_id','action','grp']).action_date.agg(streak_length='size',start_date='min',end_date='max').reset_index().drop(columns='grp')
ranked=g.loc[g.streak_length.ge(5)].sort_values(['streak_length','action','start_date'],ascending=[False,True,False])
return ranked.drop_duplicates('user_id').sort_values(['streak_length','user_id'],ascending=[False,True])""",
        [
            ("start_date DESC) pos", "start_date ASC) pos", "[False,True,False]", "[False,True,True]"),
            (
                "action ASC,start_date",
                "action DESC,start_date",
                "[False,True,False]",
                "[False,False,False]",
            ),
        ],
        True,
    ),
}
