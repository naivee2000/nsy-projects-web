"""Second reviewed group of workbook batch 117."""
from collections import Counter, deque
from itertools import combinations, permutations

from .import_batch_055 import entry


def almost_o(a):
    first, second = a
    return all(abs(first.count(char) - second.count(char)) <= 3 for char in "abcdefghijklmnopqrstuvwxyz")


def beauty_o(a):
    items, queries = a
    return [max((beauty for price, beauty in items if price <= query), default=0) for query in queries]


def tasks_o(a):
    tasks, workers, pills, strength = a
    for count in range(min(len(tasks), len(workers)), -1, -1):
        for chosen_tasks in combinations(tasks, count):
            for chosen_workers in combinations(workers, count):
                for assignment in permutations(chosen_workers):
                    needed = sum(worker < task <= worker + strength for task, worker in zip(chosen_tasks, assignment))
                    if needed <= pills and all(task <= worker + strength for task, worker in zip(chosen_tasks, assignment)):
                        return count
    return 0


def tickets_o(a):
    tickets, k = a
    queue = deque((index, count) for index, count in enumerate(tickets))
    elapsed = 0
    while queue:
        index, count = queue.popleft()
        elapsed += 1
        count -= 1
        if count == 0 and index == k:
            return elapsed
        if count:
            queue.append((index, count))


def groups_o(a):
    values = a[0]
    answer = []
    start = 0
    requested = 1
    while start < len(values):
        group = values[start:start + requested]
        answer.extend(reversed(group) if len(group) % 2 == 0 else group)
        start += len(group)
        requested += 1
    return answer


def ralmost(r):
    n = r.randint(1, 30)
    return ["".join(r.choice("abcde") for _ in range(n)), "".join(r.choice("abcde") for _ in range(n))]


def rbeauty(r):
    return [[[r.randint(1, 20), r.randint(1, 30)] for _ in range(r.randint(1, 9))], [r.randint(1, 20) for _ in range(r.randint(1, 9))]]


def rtasks(r):
    n, m = r.randint(1, 6), r.randint(1, 6)
    return [[r.randint(1, 10) for _ in range(n)], [r.randint(0, 10) for _ in range(m)], r.randint(0, min(n, m)), r.randint(0, 5)]


def rtickets(r):
    values = [r.randint(1, 8) for _ in range(r.randint(1, 15))]
    return [values, r.randrange(len(values))]


def rgroups(r):
    return [[r.randint(-20, 20) for _ in range(r.randint(0, 30))]]


ALMOST = '''\
def almost_equivalent_strings(word1,word2):
    from collections import Counter
    difference=Counter(word1)
    difference.subtract(word2)
    return all(abs(value)<=3 for value in difference.values())
'''

BEAUTY = '''\
def maximum_beauty_for_queries(items,queries):
    items=sorted(items);ordered=sorted((query,index) for index,query in enumerate(queries))
    answer=[0]*len(queries);item_index=0;best=0
    for query,index in ordered:
        while item_index<len(items) and items[item_index][0]<=query:
            best=max(best,items[item_index][1]);item_index+=1
        answer[index]=best
    return answer
'''

TASKS = '''\
def maximum_assignable_tasks(tasks,workers,pills,strength):
    from collections import deque
    tasks=sorted(tasks);workers=sorted(workers)
    def possible(count):
        available=deque();task_index=0;remaining=pills
        for worker in workers[len(workers)-count:]:
            while task_index<count and tasks[task_index]<=worker+strength:
                available.append(tasks[task_index]);task_index+=1
            if not available:return False
            if available[0]<=worker:available.popleft()
            elif remaining:
                remaining-=1;available.pop()
            else:return False
        return True
    low,high=0,min(len(tasks),len(workers))
    while low<high:
        middle=(low+high+1)//2
        if possible(middle):low=middle
        else:high=middle-1
    return low
'''

TICKETS = '''\
def time_to_buy_tickets(tickets,k):
    target=tickets[k]
    return sum(min(count,target if index<=k else target-1) for index,count in enumerate(tickets))
'''

GROUPS = '''\
def reverse_even_length_groups(head):
    dummy=ListNode(0,head);before=dummy;requested=1
    while before.next:
        tail=before
        actual=0
        while actual<requested and tail.next:
            tail=tail.next;actual+=1
        after=tail.next
        if actual%2==0:
            previous=after;node=before.next
            for _ in range(actual):
                following=node.next;node.next=previous;previous=node;node=following
            old_first=before.next;before.next=previous;before=old_first
        else:
            before=tail
        requested+=1
    return dummy.next
'''


def L(*items):
    return list(items)


BATCH = {
    2068: entry('almost_equivalent_strings',[('word1','str'),('word2','str')],'bool',['hash maps','strings','counting'],['Both strings have equal length and contain lowercase English letters.','They are almost equivalent exactly when every letter-frequency difference is at most three in absolute value.','Return a Boolean result.'],[(['aaaa','bccb'],'The frequency difference for a is four, so the pair is not almost equivalent.'),(['abcdeef','abaaacc'],'Every letter differs in frequency by at most three, including a at exactly three.')],[[x,y] for x,y in [('a','b'),('abc','abc'),('aaaa','bbbb'),('aaab','bbba'),('cccddabba','babababab'),('zzzzx','yyyyx'),('abcd','dcba'),('aaaaa','aaaab'),('abcabc','aabbcc'),('qqqq','qqqq'),('aabbccdd','aaaabbbb'),('eeeeffff','eeeefggg'),('xyzxyz','xyzzxy'),('mmmmnn','nnmmmm')]],ALMOST,[ALMOST.replace('<=3','<3'),ALMOST.replace('<=3','<=4')],['Rejects a valid pair whose frequency difference is exactly three.','Allows a frequency difference of four instead of the stated maximum three.'],almost_o,ralmost,L('Only per-letter totals matter; character positions do not.','Subtract the second string frequency map from the first and inspect every resulting count.','Return all(abs(delta)<=3 for delta in differences).','The stored delta is exactly count1-count2 for each present letter, while absent letters have delta zero.'),'O(n)','O(1)',3),
    2070: entry('maximum_beauty_for_queries',[('items','list[list[int]]'),('queries','list[int]')],'list[int]',['arrays','sorting','offline queries'],['Each item is [positive price, positive beauty], and both inputs are nonempty.','For each query return the greatest beauty among items priced at most that query, or zero when none qualify.','Answers must remain in the original query order.'],[([[[1,2],[3,2],[2,4],[5,6],[3,5]],[1,2,3,4,5,6]],'As the allowed price rises, the best available beauties are 2,4,5,5,6,6.'),([[[10,100]],[5,10]],'No item fits price five, while the item fits price ten.')],[[items,q] for items,q in [([[2,7]],[1]),([[2,7]],[2]),([[2,7]],[3]),([[1,5],[1,9]],[1]),([[5,1],[2,10]],[2,4,5]),([[3,8],[8,2],[6,9]],[9,1,6]),([[1,1],[2,2],[3,3]],[3,2,1]),([[4,20],[2,5],[4,10]],[4]),([[100,1]],[99,100,101]),([[1,100],[10,1]],[1,9,10]),([[7,7],[3,4]],[2,3,7]),([[5,5],[6,6]],[5,5]),([[2,3],[9,20],[4,8]],[0,4,8]),([[1,2],[2,4],[3,1]],[2])]],BEAUTY,[BEAUTY.replace('<=query','<query'),BEAUTY.replace('answer[index]=best','answer[item_index%len(answer)]=best')],['Uses a strict lower threshold and misses items priced exactly at a query.','Writes results by scan position instead of restoring each query’s original index.'],beauty_o,rbeauty,L('Sort items and queries so one forward scan can reuse all earlier eligible items.','Maintain the maximum beauty among item prices no greater than the current sorted query.','Sort (query,original_index); advance items while price<=query; store the running maximum at original_index.','The running maximum contains exactly the eligible prefix, and restoring indices preserves requested output order.'),'O((items+queries) log(items+queries))','O(queries)',5),
    2071: entry('maximum_assignable_tasks',[('tasks','list[int]'),('workers','list[int]'),('pills','int'),('strength','int')],'int',['binary search','greedy','monotonic queue'],['Each task and worker may be used at most once; a worker completes a task when its strength meets the requirement.','At most pills workers may each receive one strength boost.','Return the largest number of tasks that can be assigned.'],[([[3,2,1],[0,3,3],1,1],'All three tasks can be assigned by boosting the zero-strength worker for task one.'),([[5,4],[0,0,0],1,5],'Only one worker can be boosted, so only one task is completed.')],[[t,w,p,s] for t,w,p,s in [([1],[1],0,0),([2],[1],0,1),([2],[1],1,1),([1,2],[1],1,2),([1],[1,2],0,0),([10,15,30],[0,10,10,10,10],3,10),([5,9,8,5,9],[1,6,4,2,6],1,5),([1,1,1],[0,0,0],2,1),([4,4],[3,3],1,1),([7,8],[1,2],2,5),([2,3,4],[2,3,4],0,0),([6,6,6],[1,5,5],2,1),([3,10],[3,4],1,6),([9,9],[4,9],1,5)]],TASKS,[TASKS.replace('workers[len(workers)-count:]','workers[:count]'),TASKS.replace('remaining-=1;available.pop()','remaining-=1;available.popleft()')],['Uses the weakest workers for the feasibility check instead of the strongest available workers.','When using a pill, assigns the easiest eligible task instead of reserving it for a weaker worker.'],tasks_o,rtasks,L('Whether x tasks can be completed is monotone, so binary-search x.','For a candidate x, use the x easiest tasks and x strongest workers; feed each worker all newly reachable tasks into a deque.','Without a pill take the easiest task the worker can do; otherwise spend a pill on the hardest reachable task.','This exchange strategy preserves easy tasks for weaker workers and uses every pill where it unlocks the most demanding available task.'),'O((tasks+workers) log(tasks+workers))','O(min(tasks,workers))',8),
    2073: entry('time_to_buy_tickets',[('tickets','list[int]'),('k','int')],'int',['arrays','queue','simulation'],['tickets is nonempty with positive counts and k is a valid zero-based position.','Each second the front person buys one ticket; unfinished people rejoin the back.','Return the seconds elapsed when person k buys their last ticket.'],[([[2,3,2],2],'Each person buys twice before person two finishes, taking six seconds.'),([[5,1,1,1],0],'The three people behind the target buy at most four tickets each, so the target finishes after eight seconds.')],[[v,k] for v,k in [([1],0),([2],0),([1,1],0),([1,1],1),([2,1],0),([2,1],1),([1,2],1),([3,3,3],1),([5,1,1,1],3),([1,5,1],1),([4,2,3],0),([4,2,3],1),([4,2,3],2),([10,1,10],2)]],TICKETS,[TICKETS.replace('index<=k','index<k'),TICKETS.replace('target-1','target')],['Gives the target person one too few turns.','Lets people behind the target buy once after the target has already finished.'],tickets_o,rtickets,L('Count each person’s purchases before the target finishes instead of simulating the queue.','People at or before k buy at most tickets[k]; people after k buy at most tickets[k]-1.','Sum min(tickets[i],target) for i<=k and min(tickets[i],target-1) afterward.','Those caps exactly describe the complete queue rounds and the partial final round ending at k.'),'O(n)','O(1)',3),
    2074: entry('reverse_even_length_groups',[('head','ListNode | None')],'ListNode | None',['linked lists','in-place reversal'],['Partition nodes consecutively into requested sizes one, two, three, and so on; the final group may be shorter.','Reverse a group exactly when its actual node count is even.','Return the resulting linked-list head using constant auxiliary pointer space.'],[([[5,2,6,3,9,1,7,3,8,4]],'Groups have actual sizes 1,2,3,4; reversing groups two and four gives [5,6,2,3,9,1,4,8,3,7].'),([[1,1,0,6]],'The final group has one node, so only the second group is reversed.')],[[x] for x in [[],[1],[1,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[1,2,3,4,5,6],[1,2,3,4,5,6,7],[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9,10,11],[9,8,7,6,5,4,3,2,1],[0,0,0,0,0,0],[2,-1,4,-3,6,-5,8]]],GROUPS,[GROUPS.replace('actual%2==0','actual%2==1'),GROUPS.replace('if actual%2==0','if requested%2==0')],['Reverses odd-sized groups rather than even-sized groups.','Uses the requested group size, failing when the shortened final group has different parity.'],groups_o,rgroups,L('First measure each actual group; the shortened final group’s parity is what matters.','Keep a pointer before the group, find its tail and length, and reverse exactly that many links when the length is even.','Reverse with after-group as the initial previous pointer, reconnect before.next, then advance before to the old first node.','The reconnection preserves the rest of the list, and each node is visited by one measurement plus at most one reversal.'),'O(n)','O(1)',5),
}

BATCH[2074]['params'][0]=('head','ListNode | None','listnode')
BATCH[2074]['adapter']='listnode'
