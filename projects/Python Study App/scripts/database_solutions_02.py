"""Native Pandas answers and paired misconception tests for the sales/activity batch."""

from .database_solutions_01 import Solution

SOLUTIONS = {
    1045: Solution(
        "Joins",
        "",
        """counts = Customer.groupby('customer_id').product_key.nunique()
return counts[counts.eq(len(Product))].index.to_frame(index=False)""",
        [
            ("COUNT(DISTINCT product_key)", "COUNT(*)", "product_key.nunique()", "product_key.size()"),
            ("= (SELECT", "< (SELECT", "counts.eq", "counts.lt"),
        ],
    ),
    1068: Solution(
        "Joins",
        "",
        "return Sales.merge(Product, on='product_id')[['product_name','year','price']]",
        [
            (
                "SELECT product_name",
                "SELECT DISTINCT product_name",
                "'price']]",
                "'price']].drop_duplicates()",
            ),
            (
                "year, price",
                "year, price*quantity AS price",
                "Sales.merge",
                "Sales.assign(price=Sales.price*Sales.quantity).merge",
            ),
        ],
    ),
    1069: Solution(
        "Aggregation",
        "",
        "return Sales.groupby('product_id').quantity.sum().rename('total_quantity').reset_index()",
        [
            ("SUM(quantity)", "COUNT(quantity)", ".quantity.sum()", ".quantity.size()"),
            ("SUM(quantity)", "MAX(quantity)", ".quantity.sum()", ".quantity.max()"),
        ],
    ),
    1070: Solution(
        "Window functions",
        "",
        """first = Sales.groupby('product_id').year.transform('min')
return Sales.loc[Sales.year.eq(first),['product_id','year','quantity','price']].rename(columns={'year':'first_year'})""",
        [
            ("MIN(year)", "MAX(year)", "transform('min')", "transform('max')"),
            (
                "SELECT product_id, year AS",
                "SELECT DISTINCT product_id, year AS",
                ".rename(columns=",
                ".drop_duplicates().rename(columns=",
            ),
        ],
    ),
    1075: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
return Project.merge(Employee,on='employee_id').groupby('project_id').experience_years.mean().map(lambda x: float(Decimal(str(x)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))).rename('average_years').reset_index()""",
        [
            ("AVG(experience_years)", "MAX(experience_years)", "years.mean()", "years.max()"),
            ("AVG(experience_years)", "SUM(experience_years)", "years.mean()", "years.sum()"),
        ],
    ),
    1076: Solution(
        "Ranking",
        "",
        """counts = Project.groupby('project_id').employee_id.size()
return counts[counts.eq(counts.max())].index.to_frame(index=False)""",
        [
            (">= ALL", "<= ALL", "counts.max()", "counts.min()"),
            (
                "GROUP BY project_id )",
                "GROUP BY project_id ) LIMIT 1",
                "index.to_frame(index=False)",
                "index.to_frame(index=False).head(1)",
            ),
        ],
    ),
    1077: Solution(
        "Ranking",
        "",
        """p = Project.merge(Employee,on='employee_id')
rank = p.groupby('project_id').experience_years.rank(method='min',ascending=False)
return p.loc[rank.eq(1),['project_id','employee_id']]""",
        [
            ("RANK()", "ROW_NUMBER()", "method='min'", "method='first'"),
            ("experience_years DESC", "experience_years ASC", "ascending=False", "ascending=True"),
        ],
    ),
    1082: Solution(
        "Aggregation",
        "",
        """totals = Sales.groupby('seller_id').price.sum()
return totals[totals.eq(totals.max())].index.to_frame(index=False)""",
        [
            ("SUM(price)", "COUNT(*)", "price.sum()", "price.size()"),
            (">= ALL", "<= ALL", "totals.max()", "totals.min()"),
        ],
    ),
    1083: Solution(
        "Joins",
        "",
        """s = Sales.merge(Product,on='product_id')
s8 = s.loc[s.product_name.eq('S8'),'buyer_id']
iphone = s.loc[s.product_name.eq('iPhone'),'buyer_id']
return s8[~s8.isin(iphone)].drop_duplicates().to_frame()""",
        [
            (" AND SUM(product_name = 'iPhone') = 0", "", "[~s8.isin(iphone)]", ""),
            (
                "SUM(product_name = 'iPhone') = 0",
                "SUM(product_name = 'iPhone') > 0",
                "~s8.isin",
                "s8.isin",
            ),
        ],
    ),
    1084: Solution(
        "Dates",
        "",
        """ok = Sales.sale_date.between('2019-01-01','2019-03-31').groupby(Sales.product_id).all()
return Product.loc[Product.product_id.isin(ok[ok].index),['product_id','product_name']]""",
        [
            ("COUNT(1) = SUM", "0 < SUM", ").all()", ").any()"),
            ("2019-03-31", "2019-03-30", "2019-03-31", "2019-03-30"),
        ],
    ),
    1097: Solution(
        "Dates",
        "",
        """installs = Activity.groupby('player_id').event_date.min().rename('install_dt').reset_index()
visits = set(Activity[['player_id','event_date']].itertuples(index=False,name=None))
installs['retained'] = [(p,d+pd.Timedelta(days=1)) in visits for p,d in installs.itertuples(index=False,name=None)]
return installs.groupby('install_dt').agg(installs=('player_id','size'),Day1_retention=('retained','mean')).round(2).reset_index()""",
        [
            ("install_dt) = 1", "install_dt) = 2", "days=1", "days=2"),
            ("MIN(event_date)", "MAX(event_date)", "event_date.min()", "event_date.max()"),
        ],
    ),
    1098: Solution(
        "Joins",
        """SELECT b.book_id,b.name FROM Books b LEFT JOIN Orders o ON o.book_id=b.book_id AND o.dispatch_date BETWEEN '2018-06-23' AND '2019-06-23'
WHERE available_from <= '2019-05-23' GROUP BY b.book_id,b.name HAVING COALESCE(SUM(o.quantity),0) < 10""",
        """sold = Orders.loc[Orders.dispatch_date.ge('2018-06-23')].groupby('book_id').quantity.sum()
a = Books.assign(sold=Books.book_id.map(sold).fillna(0))
return a.loc[a.available_from.le('2019-05-23') & a.sold.lt(10),['book_id','name']]""",
        [
            (" < 10", " <= 10", "sold.lt(10)", "sold.le(10)"),
            ("available_from <=", "available_from <", "available_from.le", "available_from.lt"),
        ],
    ),
    1107: Solution(
        "Dates",
        "",
        """first = Traffic.loc[Traffic.activity.eq('login')].groupby('user_id').activity_date.min()
days = first[first.between('2019-04-01','2019-06-30')]
return days.value_counts().rename_axis('login_date').reset_index(name='user_count')""",
        [
            ("<= 90", "< 90", "2019-04-01", "2019-04-02"),
            ("MIN(activity_date)", "MAX(activity_date)", "activity_date.min()", "activity_date.max()"),
        ],
    ),
    1112: Solution(
        "Ranking",
        "",
        "return Enrollments.sort_values(['student_id','grade','course_id'],ascending=[True,False,True]).drop_duplicates('student_id')",
        [
            (
                "grade DESC, course_id",
                "grade DESC, course_id DESC",
                "[True,False,True]",
                "[True,False,False]",
            ),
            ("grade DESC", "grade ASC", "[True,False,True]", "[True,True,True]"),
        ],
        True,
    ),
    1113: Solution(
        "Aggregation",
        "",
        """a = Actions.loc[Actions.action_date.eq('2019-07-04') & Actions.action.eq('report')]
return a.groupby('extra').post_id.nunique().rename('report_count').rename_axis('report_reason').reset_index()""",
        [
            ("COUNT(DISTINCT post_id)", "COUNT(post_id)", ".post_id.nunique()", ".post_id.size()"),
            ("action_date = '2019-07-04' AND ", "", "Actions.action_date.eq('2019-07-04') & ", ""),
        ],
    ),
    1126: Solution(
        "Aggregation",
        """SELECT business_id FROM (SELECT e.*,AVG(occurrences) OVER (PARTITION BY event_type) a FROM Events e) r WHERE occurrences>a GROUP BY business_id HAVING COUNT(*)>=2""",
        """avg = Events.groupby('event_type').occurrences.transform('mean')
counts = Events.loc[Events.occurrences.gt(avg)].groupby('business_id').size()
return counts[counts.ge(2)].index.to_frame(index=False)""",
        [
            ("occurrences>a", "occurrences>=a", ".gt(avg)", ".ge(avg)"),
            ("COUNT(*)>=2", "COUNT(*)>=1", "counts.ge(2)", "counts.ge(1)"),
        ],
    ),
    1127: Solution(
        "Aggregation",
        "",
        """g = Spending.groupby(['spend_date','user_id'])
users = g.agg(amount=('amount','sum'), label=('platform',lambda s: 'both' if s.nunique()>1 else s.iloc[0])).reset_index()
totals = users.groupby(['spend_date','label']).agg(total_amount=('amount','sum'),total_users=('user_id','size'))
idx = pd.MultiIndex.from_product([Spending.spend_date.unique(),['desktop','mobile','both']], names=['spend_date','platform'])
return totals.reindex(idx,fill_value=0).reset_index()""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                ".reindex(idx,fill_value=0)",
                ".rename_axis(['spend_date','platform'])",
            ),
            ("SUM(amount)", "MAX(amount)", "amount=('amount','sum')", "amount=('amount','max')"),
        ],
    ),
    1132: Solution(
        "Aggregation",
        "",
        """from decimal import Decimal, ROUND_HALF_UP
a = Actions.loc[Actions.extra.eq('spam'),['action_date','post_id']].drop_duplicates()
a['removed'] = a.post_id.isin(Removals.post_id)
percent = 100*a.groupby('action_date').removed.mean().mean()
return pd.DataFrame({'average_daily_percent':[float(Decimal(str(percent)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))]})""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "a['removed'] =",
                "a = a.loc[a.post_id.isin(Removals.post_id)].copy()\na['removed'] =",
            ),
            (" * 100", " * 1", "100*a.groupby", "1*a.groupby"),
        ],
    ),
    1141: Solution(
        "Dates",
        "",
        """a = Activity.loc[Activity.activity_date.between('2019-06-28','2019-07-27')]
return a.groupby('activity_date').user_id.nunique().rename('active_users').rename_axis('day').reset_index()""",
        [
            ("COUNT(DISTINCT user_id)", "COUNT(user_id)", ".user_id.nunique()", ".user_id.size()"),
            ("< 30", "<= 30", "2019-06-28", "2019-06-27"),
        ],
    ),
    1142: Solution(
        "Dates",
        "",
        """a = Activity.loc[Activity.activity_date.between('2019-06-28','2019-07-27')]
v = a.groupby('user_id').session_id.nunique()
return pd.DataFrame({'average_sessions_per_user':[round(v.mean(),2) if len(v) else 0]})""",
        [
            (
                "COUNT(DISTINCT session_id)",
                "COUNT(session_id)",
                ".session_id.nunique()",
                ".session_id.size()",
            ),
            ("< 30", "<= 30", "2019-06-28", "2019-06-27"),
        ],
    ),
    1148: Solution(
        "Filtering",
        "",
        "return Views.loc[Views.author_id.eq(Views.viewer_id),['author_id']].drop_duplicates().sort_values('author_id').rename(columns={'author_id':'id'})",
        [
            ("SELECT DISTINCT", "SELECT", ".drop_duplicates()", ""),
            ("author_id = viewer_id", "author_id <> viewer_id", "author_id.eq", "author_id.ne"),
        ],
        True,
    ),
    1149: Solution(
        "Aggregation",
        "",
        """n = Views.groupby(['viewer_id','view_date']).article_id.nunique()
return n[n.gt(1)].reset_index()[['viewer_id']].drop_duplicates().sort_values('viewer_id').rename(columns={'viewer_id':'id'})""",
        [
            (
                "COUNT(DISTINCT article_id)",
                "COUNT(article_id)",
                "article_id.nunique()",
                "article_id.size()",
            ),
            (
                "GROUP BY viewer_id, view_date",
                "GROUP BY viewer_id",
                "['viewer_id','view_date']",
                "['viewer_id']",
            ),
        ],
        True,
    ),
    1158: Solution(
        "Joins",
        "",
        """o = Orders.loc[Orders.order_date.dt.year.eq(2019)].groupby('buyer_id').size()
a = Users.rename(columns={'user_id':'buyer_id'}).copy()
a['orders_in_2019'] = a.buyer_id.map(o).fillna(0)
return a[['buyer_id','join_date','orders_in_2019']]""",
        [
            (
                "LEFT JOIN",
                "JOIN",
                "return a[['buyer_id'",
                "return a.loc[a.orders_in_2019.gt(0),['buyer_id'",
            ),
            ("= 2019", "= 2018", "eq(2019)", "eq(2018)"),
        ],
    ),
    1159: Solution(
        "Ranking",
        "",
        """o = Orders.sort_values('order_date')
second = o.loc[o.groupby('seller_id').cumcount().eq(1)].merge(Items,on='item_id').set_index('seller_id').item_brand
a = Users.rename(columns={'user_id':'seller_id'}).copy()
a['2nd_item_fav_brand'] = a.favorite_brand.eq(a.seller_id.map(second)).map({True:'yes',False:'no'})
return a[['seller_id','2nd_item_fav_brand']]""",
        [
            ("rk = 2", "rk = 1", "cumcount().eq(1)", "cumcount().eq(0)"),
            (
                "ORDER BY order_date",
                "ORDER BY order_date DESC",
                "sort_values('order_date')",
                "sort_values('order_date',ascending=False)",
            ),
        ],
    ),
    1164: Solution(
        "Dates",
        "",
        """latest = Products.loc[Products.change_date.le('2019-08-16')].sort_values('change_date').drop_duplicates('product_id',keep='last').set_index('product_id').new_price
a = Products[['product_id']].drop_duplicates().copy()
return a.assign(price=a.product_id.map(latest).fillna(10))""",
        [
            ("change_date <=", "change_date <", "change_date.le", "change_date.lt"),
            ("IFNULL(price, 10)", "IFNULL(price, 0)", "fillna(10)", "fillna(0)"),
        ],
    ),
    1173: Solution(
        "Aggregation",
        "",
        "return pd.DataFrame({'immediate_percentage':[round(100*Delivery.order_date.eq(Delivery.customer_pref_delivery_date).mean(),2)]})",
        [
            ("* 100", "* 1", "100*Delivery", "1*Delivery"),
            (
                "order_date = customer_pref_delivery_date",
                "order_date <> customer_pref_delivery_date",
                "order_date.eq",
                "order_date.ne",
            ),
        ],
    ),
    1174: Solution(
        "Aggregation",
        "",
        """first = Delivery.sort_values('order_date').drop_duplicates('customer_id', keep='first')
return pd.DataFrame({'immediate_percentage':[round(100*first.order_date.eq(first.customer_pref_delivery_date).mean(),2)]})""",
        [
            ("MIN(order_date)", "MAX(order_date)", "keep='first'", "keep='last'"),
            ("* 100", "* 1", "100*first", "1*first"),
        ],
    ),
    1179: Solution(
        "Reshaping",
        "",
        """from calendar import month_abbr
months = list(month_abbr)[1:]
wide = Department.pivot(index='id',columns='month',values='revenue').reindex(columns=months)
return wide.add_suffix('_Revenue').reset_index()""",
        [
            (
                "THEN revenue END",
                "THEN revenue ELSE 0 END",
                "wide.add_suffix",
                "wide.fillna(0).add_suffix",
            ),
            ("WHEN 'Jan'", "WHEN 'Dec'", "wide.add_suffix", "wide.assign(Jan=wide.Dec).add_suffix"),
        ],
    ),
    1193: Solution(
        "Aggregation",
        "",
        """a = Transactions.assign(month=Transactions.trans_date.dt.strftime('%Y-%m'), approved=Transactions.state.eq('approved'))
a['approved_amount'] = a.amount.where(a.approved,0)
return a.groupby(['month','country'],dropna=False).agg(trans_count=('id','size'),approved_count=('approved','sum'),trans_total_amount=('amount','sum'),approved_total_amount=('approved_amount','sum')).reset_index()""",
        [
            (
                "COUNT(1) AS trans_count",
                "SUM(state='approved') AS trans_count",
                "trans_count=('id','size')",
                "trans_count=('approved','sum')",
            ),
            (
                "SUM(IF(state = 'approved', amount, 0))",
                "SUM(amount)",
                "approved_total_amount=('approved_amount','sum')",
                "approved_total_amount=('amount','sum')",
            ),
        ],
    ),
    1194: Solution(
        "Ranking",
        """WITH scores AS (SELECT first_player player_id,first_score score FROM Matches UNION ALL SELECT second_player,second_score FROM Matches),
totals AS (SELECT p.group_id,p.player_id,COALESCE(SUM(s.score),0) points FROM Players p LEFT JOIN scores s USING(player_id) GROUP BY p.group_id,p.player_id),
r AS (SELECT totals.*,ROW_NUMBER() OVER (PARTITION BY group_id ORDER BY points DESC,player_id ASC) pos FROM totals) SELECT group_id,player_id FROM r WHERE pos=1""",
        """a = Matches.groupby('first_player').first_score.sum()
b = Matches.groupby('second_player').second_score.sum()
players = Players.assign(points=Players.player_id.map(a.add(b,fill_value=0)).fillna(0))
return players.sort_values(['points','player_id'],ascending=[False,True]).drop_duplicates('group_id')[['group_id','player_id']]""",
        [
            ("player_id ASC", "player_id DESC", "[False,True]", "[False,False]"),
            ("points DESC", "points ASC", "[False,True]", "[True,True]"),
        ],
    ),
    1204: Solution(
        "Window functions",
        "",
        """q = Queue.sort_values('turn')
return q.loc[q.weight.cumsum().le(1000),['person_name']].tail(1)""",
        [
            ("<= 1000", "< 1000", ".le(1000)", ".lt(1000)"),
            ("ORDER BY a.turn DESC", "ORDER BY a.turn ASC", ".tail(1)", ".head(1)"),
        ],
    ),
    1205: Solution(
        "Aggregation",
        "",
        """approved = Transactions.loc[Transactions.state.eq('approved'),['country','trans_date','amount']].assign(ac=1,charge=0,cb=0)
charge = Chargebacks.merge(Transactions[['id','country','amount','trans_date']].rename(columns={'trans_date':'purchase_date'}),left_on='trans_id',right_on='id')
charge = charge.assign(ac=0,charge=charge.amount,cb=1,amount=0)
a = pd.concat([approved,charge])
a['month'] = a.trans_date.dt.strftime('%Y-%m')
return a.groupby(['month','country'],dropna=False).agg(approved_count=('ac','sum'),approved_amount=('amount','sum'),chargeback_count=('cb','sum'),chargeback_amount=('charge','sum')).reset_index()""",
        [
            (
                "c.trans_date FROM",
                "t.trans_date FROM",
                "charge.assign(ac=0",
                "charge.assign(trans_date=charge.purchase_date,ac=0",
            ),
            (
                "SUM(state = 'chargeback') AS chargeback_count",
                "SUM(state = 'approved') AS chargeback_count",
                "chargeback_count=('cb','sum')",
                "chargeback_count=('ac','sum')",
            ),
        ],
    ),
}
