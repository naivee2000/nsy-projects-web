"""Checkpoint replacement for one twice-quarantined batch-80 candidate."""
from .import_batch_055 import entry

def grumpy_oracle(a):
 customers,grumpy,minutes=a;base=sum(c for c,g in zip(customers,grumpy) if not g)
 return base+max(sum(customers[i] for i in range(start,start+minutes) if grumpy[i]) for start in range(len(customers)-minutes+1))

def random_grumpy(r):
 n=r.randint(1,18);return [[r.randint(0,30) for _ in range(n)],[r.randrange(2) for _ in range(n)],r.randint(1,n)]

GRUMPY='''def maximum_satisfied_customers(customers, grumpy, minutes):
 baseline=sum(c for c,g in zip(customers,grumpy) if g==0);extra=sum(customers[i] for i in range(minutes) if grumpy[i]);best=extra
 for right in range(minutes,len(customers)):
  if grumpy[right]:extra+=customers[right]
  if grumpy[right-minutes]:extra-=customers[right-minutes]
  best=max(best,extra)
 return baseline+best
'''

BATCH={1052:entry('maximum_satisfied_customers',[('customers','list[int]'),('grumpy','list[int]'),('minutes','int')],'int',['sliding-window','arrays'],['customers and grumpy have equal nonzero length; grumpy values are binary.','Use the technique for one consecutive window of exactly minutes.'],[([[1,0,1,2,1,1,7,5],[0,1,0,1,0,1,0,1],3],'Normally satisfied customers total ten; the best window recovers six more.'),([[1],[0],1],'The only customer is already satisfied, so the answer is one.')],[[c,g,m] for c,g,m in [([1],[1],1),([0],[1],1),([1,2],[0,0],1),([1,2],[1,1],1),([1,2],[1,1],2),([5,1,5],[1,0,1],1),([5,1,5],[1,0,1],2),([1,2,3,4],[0,1,1,0],2),([10,0,10],[1,1,1],2),([2,3,4],[0,1,0],3),([1,1,1,1],[1,0,1,0],1),([9,1,2,8],[1,0,0,1],2),([3,8,2,6,4],[1,1,0,1,0],2),([0,5,0,5],[1,1,1,1],3)]],GRUMPY,[GRUMPY.replace('if grumpy[right]:extra+=customers[right]','if not grumpy[right]:extra+=customers[right]'),GRUMPY.replace('best=max(best,extra)','best=min(best,extra)')],['Adds already satisfied customers when the window enters instead of newly recoverable ones.','Keeps the least useful technique window instead of the best.'],grumpy_oracle,random_grumpy,['Customers from non-grumpy minutes form an unavoidable satisfied baseline.','The technique adds only customers in grumpy minutes inside its window.','Slide a fixed-size window over recoverable counts and retain its maximum, then add the baseline.','Every allowed use is one such window, and baseline customers never depend on its position.'],'O(n)','O(1)',5)}
