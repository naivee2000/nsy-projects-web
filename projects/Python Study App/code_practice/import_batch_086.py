"""Two independently reviewed scalar/counting imports."""
from collections import Counter
from datetime import date
from .import_batch_055 import entry

def weekday_oracle(a):return date(a[2],a[1],a[0]).strftime('%A')
def balloon_oracle(a):
 c=Counter(a[0]);return min(c['b'],c['a'],c['l']//2,c['o']//2,c['n'])
def random_date(r):
 y=r.randint(1971,2100);m=r.randint(1,12)
 while True:
  d=r.randint(1,31)
  try:date(y,m,d);return [d,m,y]
  except ValueError:pass
def random_text(r):return [''.join(r.choice('balloonxyz') for _ in range(r.randint(1,80)))]
WEEK='''def weekday_name(day, month, year):
 names=['Friday','Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday'];days=0
 for y in range(1971,year):days+=366 if y%400==0 or y%4==0 and y%100!=0 else 365
 lengths=[31,28+(year%400==0 or year%4==0 and year%100!=0),31,30,31,30,31,31,30,31,30,31]
 days+=sum(lengths[:month-1])+day-1
 return names[days%7]
'''
BALLOON='''def maximum_balloon_copies(text):
 from collections import Counter
 counts=Counter(text)
 return min(counts['b'],counts['a'],counts['l']//2,counts['o']//2,counts['n'])
'''
E=entry
BATCH={
1185:E('weekday_name',[('day','int'),('month','int'),('year','int')],'str',['math','dates'],['The date is valid and lies from 1971 through 2100.','Return the full English weekday name.'],[([31,8,2019],'August 31, 2019 was Saturday.'),([18,7,1999],'July 18, 1999 was Sunday.')],[[d,m,y] for d,m,y in [(1,1,1971),(2,1,1971),(31,12,1971),(29,2,1972),(1,3,1972),(1,1,2000),(29,2,2000),(1,3,2001),(1,3,2004),(31,12,2020),(1,1,2021),(29,2,2096),(31,12,2100),(4,7,2026)]],WEEK,[WEEK.replace("'Friday'","'Thursday'"),WEEK.replace('day-1','day')],['Anchors January 1, 1971 to the wrong weekday.','Counts the current date with an off-by-one day.'],weekday_oracle,random_date,['Use a known weekday anchor for January 1, 1971.','Add complete intervening years with Gregorian leap rules.','Add completed months and day-1, then take the total modulo seven.','Every elapsed calendar day advances the weekday index exactly once.'],'O(year-1971)','O(1)',3),
1189:E('maximum_balloon_copies',[('text','str')],'int',['hash-maps','counting'],['Each character occurrence may be used once.','The word balloon needs two l characters and two o characters.'],[(['nlaebolko'],'The letters can form balloon once.'),(['loonbalxballpoon'],'The available counts form balloon twice.')],[[s] for s in ['b','balloon','balloonballoon','balon','bbaalloooonn','leetcode','loonbalxballpoon','nlaebolko','balloo','balloonx','bbbbbaaaaalllllllllloooooooooonnnnn','abc','oollnoba','balloonballoo']],BALLOON,[BALLOON.replace("counts['l']//2","counts['l']"),BALLOON.replace("counts['n']","counts['n']//2")],['Forgets that each copy consumes two l characters.','Incorrectly requires two n characters per copy.'],balloon_oracle,random_text,['Count every character in the text.','A copy consumes one b, one a, two l, two o, and one n.','Divide the l and o counts by two and take the minimum requirement capacity.','The scarcest required character capacity exactly limits the number of disjoint copies.'],'O(n)','O(1)',3),
}
