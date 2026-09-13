"""Replacement for the twice-quarantined batch-82 brace candidate."""
from .import_batch_055 import entry

def bookings_oracle(a):
 bookings,n=a;return [sum(seats for first,last,seats in bookings if first<=flight<=last) for flight in range(1,n+1)]
def random_bookings(r):
 n=r.randint(1,15);return [[[first:=r.randint(1,n),r.randint(first,n),r.randint(1,30)] for _ in range(r.randint(1,15))],n]

BOOKINGS='''def flight_booking_totals(bookings, n):
 difference=[0]*(n+1)
 for first,last,seats in bookings:
  difference[first-1]+=seats
  if last<n:difference[last]-=seats
 answer=[];running=0
 for i in range(n):running+=difference[i];answer.append(running)
 return answer
'''
BATCH={1109:entry('flight_booking_totals',[('bookings','list[list[int]]'),('n','int')],'list[int]',['prefix-sums','arrays'],['Flights are labeled 1..n and booking endpoints are inclusive.','Return reserved seats for every flight in label order.'],[([[[1,2,10],[2,3,20],[2,5,25]],5],'Range additions total 10,55,45,25,25 across flights one through five.'),([[[1,2,10],[2,2,15]],2],'The second flight receives both bookings for 25 seats.')],[[b,n] for b,n in [([[1,1,5]],1),([[1,2,5]],2),([[2,2,5]],2),([[1,3,1],[1,3,2]],3),([[1,1,3],[2,2,4],[3,3,5]],3),([[1,2,10],[2,3,20]],3),([[1,5,7]],5),([[2,4,3]],5),([[1,2,1],[3,4,2]],4),([[1,4,5],[2,3,6]],4),([[3,5,10],[1,3,2]],5),([[1,1,9],[1,2,8],[1,3,7]],3),([[2,2,1],[2,2,2]],3),([[1,6,4],[3,3,9],[5,6,2]],6)]],BOOKINGS,[BOOKINGS.replace('difference[first-1]','difference[first]'),BOOKINGS.replace('difference[last]-=seats','difference[last]+=seats')],['Starts each booking one flight too late.','Adds rather than removes seats after the inclusive range ends.'],bookings_oracle,random_bookings,['Inclusive range additions can be represented by two difference-array events.','Add seats at first-1 and subtract at last when that index exists.','Prefix-sum the difference array to recover each flight total.','Each booking contributes from its start event until exactly its end-cancel event.'],'O(n+bookings)','O(n)',5)}
