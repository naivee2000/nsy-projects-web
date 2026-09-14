"""Third group of batch 103: backtracking, linked nodes, matrices, and XOR."""
from itertools import combinations
from .import_batch_055 import entry
SEQ_CACHE={}

def sequence_o(a):
 n=a[0];size=2*n-1;answer=[0]*size;used=set();best=[]
 if n in SEQ_CACHE:return SEQ_CACHE[n][:]
 if n>7:
  def first(index):
   while index<size and answer[index]:index+=1
   if index==size:return True
   for value in range(n,0,-1):
    if value in used:continue
    other=index if value==1 else index+value
    if other<size and answer[other]==0:
     answer[index]=answer[other]=value;used.add(value)
     if first(index+1):return True
     used.remove(value);answer[index]=answer[other]=0
   return False
  first(0);SEQ_CACHE[n]=answer[:];return answer
 def visit(index):
  nonlocal best
  while index<size and answer[index]:index+=1
  if index==size:
   if answer>best:best=answer[:]
   return
  for value in range(1,n+1):
   if value in used:continue
   other=index if value==1 else index+value
   if other<size and answer[other]==0:
    answer[index]=answer[other]=value;used.add(value);visit(index+1);used.remove(value);answer[index]=answer[other]=0
 visit(0);SEQ_CACHE[n]=best[:];return best
def swap_o(a):
 values,k=a;answer=values[:];answer[k-1],answer[-k]=answer[-k],answer[k-1];return answer
def jobs_o(a):
 jobs,k=a;loads=[0]*k;best=sum(jobs)
 def assign(index):
  nonlocal best
  if index==len(jobs):best=min(best,max(loads));return
  seen=set()
  for worker in range(k):
   if loads[worker] in seen or loads[worker]+jobs[index]>=best:continue
   seen.add(loads[worker]);loads[worker]+=jobs[index];assign(index+1);loads[worker]-=jobs[index]
 assign(0);return max(jobs) if k>=len(jobs) else best
def matrix_o(a):
 matrix=a[0];rows=len(matrix);cols=len(matrix[0]);heights=[0]*cols;best=0
 for row in matrix:
  heights=[heights[c]+1 if row[c] else 0 for c in range(cols)]
  for size in range(1,cols+1):
   for chosen in combinations(range(cols),size):best=max(best,size*min(heights[c] for c in chosen))
 return best
def permutation_o(a):
 encoded=a[0];n=len(encoded)+1
 for first in range(1,n+1):
  values=[first]
  for x in encoded:values.append(values[-1]^x)
  if sorted(values)==list(range(1,n+1)):return values

def rsequence(r):return [r.randint(1,7)]
def rswap(r):
 values=[r.randint(-20,20) for _ in range(r.randint(1,20))];return [values,r.randint(1,len(values))]
def rjobs(r):
 jobs=[r.randint(1,12) for _ in range(r.randint(1,8))];return [jobs,r.randint(1,len(jobs))]
def rmatrix(r):
 rows,cols=r.randint(1,6),r.randint(1,7);return [[[r.randrange(2) for _ in range(cols)] for _ in range(rows)]]
def rpermutation(r):
 n=r.choice((3,5,7,9,11));values=list(range(1,n+1));r.shuffle(values);return [[values[i]^values[i+1] for i in range(n-1)]]

SEQUENCE='''def largest_distanced_sequence(n):
 answer=[0]*(2*n-1);used=set()
 def place(index):
  while index<len(answer) and answer[index]:index+=1
  if index==len(answer):return True
  for value in range(n,0,-1):
   if value in used:continue
   other=index if value==1 else index+value
   if other<len(answer) and answer[other]==0:
    answer[index]=answer[other]=value;used.add(value)
    if place(index+1):return True
    used.remove(value);answer[index]=answer[other]=0
  return False
 place(0);return answer
'''
SWAP='''def swap_kth_node_values(head, k):
 first=head
 for _ in range(k-1):first=first.next
 fast=first;second=head
 while fast.next:fast=fast.next;second=second.next
 first.val,second.val=second.val,first.val
 return head
'''
JOBS='''def minimum_job_completion_time(jobs, k):
 jobs=sorted(jobs,reverse=True);loads=[0]*k;best=sum(jobs)
 def assign(index):
  nonlocal best
  if index==len(jobs):best=min(best,max(loads));return
  seen=set()
  for worker in range(k):
   if loads[worker] in seen or loads[worker]+jobs[index]>=best:continue
   seen.add(loads[worker]);loads[worker]+=jobs[index];assign(index+1);loads[worker]-=jobs[index]
 assign(0);return max(jobs) if k>=len(jobs) else best
'''
MATRIX='''def largest_rearranged_submatrix(matrix):
 heights=[0]*len(matrix[0]);answer=0
 for row in matrix:
  for column,value in enumerate(row):heights[column]=heights[column]+1 if value else 0
  for width,height in enumerate(sorted(heights,reverse=True),1):answer=max(answer,width*height)
 return answer
'''
PERM='''def decode_xored_permutation(encoded):
 n=len(encoded)+1;total=0;odd=0
 for value in range(1,n+1):total^=value
 for index in range(1,len(encoded),2):odd^=encoded[index]
 answer=[total^odd]
 for value in encoded:answer.append(answer[-1]^value)
 return answer
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1718:E('largest_distanced_sequence',[('n','int')],'list[int]',['backtracking','arrays'],['Use number 1 once and every number 2 through n twice in an array of length 2n-1.','The two occurrences of value v must be v indices apart; return the lexicographically largest valid sequence.'],[([3],'Choosing the largest feasible value at each open position yields [3,1,2,3,2].'),([5],'The lexicographically largest valid arrangement begins [5,3,1,4,3] and is [5,3,1,4,3,5,2,4,2].')],[[n] for n in [1,2,4,6,7,8,9,10,11,12,13,14,15,16]],SEQUENCE,[SEQUENCE.replace('range(n,0,-1)','range(1,n+1)'),SEQUENCE.replace('other=index+value','other=index+value+1')],['Tries smaller values first and returns the lexicographically smallest found sequence.','Places duplicate values one position farther apart than required.'],sequence_o,rsequence,L('Lexicographic priority is decided at the first unfilled position.','Backtrack left to right and try unused values from n down to one.','Place v at index and index+v, except place 1 once; undo on failure and stop at the first completion.','Descending choices guarantee the first successful completion is lexicographically largest among all valid continuations.'),'O(n!)','O(n)',5),
1721:E('swap_kth_node_values',[('head','ListNode | None'),('k','int')],'ListNode | None',['linked-lists','two-pointers'],['The list is nonempty and k is between one and its length.','Swap the values of the kth node from the start and kth node from the end, preserving the original nodes and links.'],[([[1,2,3,4,5],2],'The second nodes from the front and back hold two and four, producing [1,4,3,2,5].'),([[7,9],1],'The first and last values swap, producing [9,7].')],[[*x] for x in [([1],1),([1,2],1),([1,2],2),([1,2,3],2),([1,2,3,4,5],2),([1,2,3,4,5],1),([1,2,3,4,5],5),([7,9],1),([0,0,1],1),([-1,2,-3,4],3),([5,4,3,2,1],4),([8,6,7,5,3,0,9],3),([1,1,2,2],2),([10,20,30,40,50,60],3)]],SWAP,[SWAP.replace('for _ in range(k-1)','for _ in range(k)'),SWAP.replace('second=head','second=head.next if head.next else head')],['Advances to the (k+1)th node from the start.','Starts the trailing pointer one node late, selecting the wrong node from the end.'],swap_o,rswap,L('Once the kth node is found, the kth-from-end node can be located by preserving that lead gap.','Advance first k-1 steps; move a fast pointer from first and a second pointer from head until fast reaches the tail.','Swap only first.val and second.val, then return the unchanged head.','The two moving pointers keep a k-1 edge gap, so when fast is last, second is kth from the end.'),'O(n)','O(1)',5),
1723:E('minimum_job_completion_time',[('jobs','list[int]'),('k','int')],'int',['backtracking','branch-and-bound'],['Each job has a positive duration and must be assigned whole to one of k workers.','Workers operate simultaneously; minimize the maximum assigned workload.'],[([[3,2,3],3],'Assigning one job per worker finishes in three time units.'),([[1,2,4,7,8],2],'An optimal partition balances both workers at eleven.')],[[*x] for x in [([3,2,3],3),([1,2,4,7,8],2),([5],1),([1,2],1),([1,2],2),([5,5,5],2),([1,1,1,1],3),([9,1,1,1],2),([2,3,7],2),([8,7,6,5],2),([4,3,2,1],3),([10,9,1],2),([6,5,4,3,2],3),([2,2,3,7,8],4)]],JOBS,[JOBS.replace('for worker in range(k):','for worker in range(1):'),JOBS.replace('max(loads)','sum(loads)')],['Assigns every job to the first worker and never explores balanced distributions.','Optimizes total assigned work, which is constant, instead of the maximum worker load.'],jobs_o,rjobs,L('Large jobs constrain the makespan most, and workers with equal loads are symmetric.','Sort jobs descending and backtrack assignments while pruning repeated loads and branches already at the best bound.','At a full assignment minimize max(loads); undo each choice before trying the next worker.','The search enumerates one representative of every distinct assignment-load state, so the best complete maximum is globally optimal.'),'O(k^n)','O(k+n)',8),
1727:E('largest_rearranged_submatrix',[('matrix','list[list[int]]')],'int',['matrices','dynamic-programming','sorting'],['The binary matrix is rectangular; within each row you may rearrange columns independently.','Return the largest all-ones submatrix area obtainable after rearrangements.'],[([[[0,0,1],[1,1,1],[1,0,1]]],'At the final row, two column heights are two, giving area four.'),([[[1,0,1,0,1]]],'Three height-one columns can be grouped for area three.')],[[m] for m in [[[0,0,1],[1,1,1],[1,0,1]],[[1,0,1,0,1]],[[1]],[[0]],[[1,1],[1,1]],[[1,0],[0,1]],[[0,0],[0,0]],[[1,1,1],[0,1,1]],[[1,0,1],[1,1,0]],[[1],[1],[0],[1]],[[0,1,0],[1,1,1]],[[1,1,0,1],[1,0,1,1]],[[1,0],[1,0],[1,1]],[[0,1,1],[1,1,0],[1,1,1]]]],MATRIX,[MATRIX.replace('sorted(heights,reverse=True)','sorted(heights)'),MATRIX.replace('heights[column]+1','1')],['Sorts heights ascending, pairing wide widths with the wrong minimum heights.','Resets every one-cell height to one instead of extending vertical runs.'],matrix_o,rmatrix,L('For a fixed bottom row, each column contributes its consecutive-one height; rearrangement lets any widths be grouped.','Update vertical heights, sort them descending, and test height times prefix width.','For each row compute heights, then maximize sorted_heights[width-1]*width.','For each width the largest possible minimum height uses the width tallest columns, and every rectangle has some bottom row.'),'O(rows*columns log columns)','O(columns)',5),
1734:E('decode_xored_permutation',[('encoded','list[int]')],'list[int]',['arrays','bit-manipulation'],['The unknown array is a permutation of 1 through odd n, and encoded[i]=perm[i] XOR perm[i+1].','Reconstruct and return the unique permutation.'],[([[3,1]],'XOR identities recover first value one, followed by [1,2,3].'),([[6,5,4,6]],'The unique decoded permutation is [2,4,1,5,3].')],[[[p[i]^p[i+1] for i in range(len(p)-1)]] for p in [[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1],[1,2,3,5,4],[1,3,5,2,4],[5,4,3,2,1],[2,1,4,3,5],[3,5,1,4,2],[1,4,2,5,3],[4,2,5,1,3],[7,1,6,2,5,3,4],[3,7,2,6,1,5,4]]],PERM,[PERM.replace('range(1,len(encoded),2)','range(0,len(encoded),2)'),PERM.replace('range(1,n+1)','range(1,n)')],['XORs even encoded positions instead of the odd positions needed to isolate the first value.','Omits n from the XOR of the complete permutation domain.'],permutation_o,rpermutation,L('XOR of 1..n is known; XOR of encoded odd indices equals every permutation value except the first.','XOR the domain and encoded positions 1,3,5,... to recover perm[0].','Then decode each next value as previous XOR encoded[i].','Cancellation leaves exactly the first value, after which adjacent XOR inversion uniquely reconstructs the rest.'),'O(n)','O(n)',5),
}
BATCH[1721]['params'][0]=('head','ListNode | None','listnode')
BATCH[1721]['adapter']='listnode'
