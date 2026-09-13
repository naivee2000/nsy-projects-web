"""Replacement slot completing batch 91 after one candidate quarantine."""
from collections import Counter
from .import_batch_055 import entry

def sorting_oracle(args):
 remaining=list(args[0]);answer='';ascending=True
 while remaining:
  choices=sorted(set(remaining),reverse=not ascending)
  for char in choices:answer+=char;remaining.remove(char)
  ascending=not ascending
 return answer
def random_text(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,60)))]
REFERENCE='''def increasing_decreasing_string(s):
 from collections import Counter
 counts=Counter(s);answer=[]
 while len(answer)<len(s):
  for char in sorted(counts):
   if counts[char]:answer.append(char);counts[char]-=1
  for char in sorted(counts,reverse=True):
   if counts[char]:answer.append(char);counts[char]-=1
 return ''.join(answer)
'''
BATCH={1370:entry('increasing_decreasing_string',[('s','str')],'str',['sorting','hash-maps'],
 ['s contains lowercase English letters.','Each ascending and descending pass uses at most one copy of each remaining character.'],
 [(['aaaabbbbcccc'],'Alternating distinct-character passes produce abccba twice.'),(['rat'],'The ascending pass consumes a,r,t, so the result is art.')],
 [[s] for s in ['a','aa','ab','ba','abc','cba','aabb','abbccc','leetcode','spo','ggggggg','abcdefedcba','zzzyx','banana']],REFERENCE,
 [REFERENCE.replace('sorted(counts,reverse=True)','sorted(counts)'),REFERENCE.replace('if counts[char]:answer.append(char);counts[char]-=1','while counts[char]:answer.append(char);counts[char]-=1')],
 ['Runs both passes ascending rather than reversing direction.','Consumes every copy during the first visit instead of one per pass.'],sorting_oracle,random_text,
 ['Character counts avoid repeatedly sorting every occurrence.','On an ascending pass visit keys smallest to largest and consume one available copy; then visit largest to smallest.','Repeat the two passes until output length equals input length.','Each pass follows the required next-greater or next-smaller choice exactly.'],
 'O(n+alphabet*n)','O(alphabet)',3)}
