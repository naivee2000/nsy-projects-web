"""Third slice of workbook batch 126."""

from collections import Counter
from itertools import permutations

from .import_batch_055 import entry


def visible_line(values):
    answer = [0] * len(values)
    for left in range(len(values)):
        tallest = -1
        for right in range(left + 1, len(values)):
            if tallest < min(values[left], values[right]):
                answer[left] += 1
            tallest = max(tallest, values[right])
    return answer


def people_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0]); answer = [visible_line(row) for row in grid]
    for column in range(columns):
        seen = visible_line([grid[row][column] for row in range(rows)])
        for row in range(rows): answer[row][column] += seen[row]
    return answer


def random_people(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    values = rng.sample(range(1, 100), rows * columns)
    return [[values[row * columns:(row + 1) * columns] for row in range(rows)]]


def digit_count_oracle(args):
    text = args[0]
    return all(text.count(str(index)) == int(value) for index, value in enumerate(text))


def random_digit_count(rng):
    return ["".join(str(rng.randrange(10)) for _ in range(rng.randint(1, 10)))]


def sender_oracle(args):
    messages, senders = args; totals = {}
    for message, sender in zip(messages, senders): totals[sender] = totals.get(sender, 0) + len(message.split())
    return max(totals, key=lambda sender: (totals[sender], sender))


def random_sender(rng):
    names = rng.sample(['Alice','Bob','Carol','dave','Eve','zoe'], rng.randint(1, 6))
    senders = [rng.choice(names) for _ in range(rng.randint(1, 15))]
    messages = [' '.join('x' for _ in range(rng.randint(1, 8))) for _ in senders]
    return [messages, senders]


def importance_oracle(args):
    n, roads = args; best = 0
    for labels in permutations(range(1, n + 1)):
        best = max(best, sum(labels[left] + labels[right] for left, right in roads))
    return best


def random_importance(rng):
    n = rng.randint(2, 8)
    roads = [[left,right] for left in range(n) for right in range(left + 1,n) if rng.randrange(3) == 0]
    return [n, roads]


def copies_oracle(args):
    source, target = args; available = Counter(source); needed = Counter(target)
    count = 0
    while all(available[char] >= amount for char, amount in needed.items()):
        for char, amount in needed.items(): available[char] -= amount
        count += 1
    return count


def random_copies(rng):
    return ["".join(rng.choice('abcde') for _ in range(rng.randint(1,40))),
            "".join(rng.choice('abcde') for _ in range(rng.randint(1,8)))]


PEOPLE = '''\
def visible_people_right_and_below(heights):
    rows,columns=len(heights),len(heights[0]);answer=[[0]*columns for _ in range(rows)]
    def scan(values):
        counts=[0]*len(values);stack=[]
        for index in range(len(values)-1,-1,-1):
            while stack and values[index]>stack[-1]:stack.pop();counts[index]+=1
            if stack:counts[index]+=1
            stack.append(values[index])
        return counts
    for row in range(rows):answer[row]=scan(heights[row])
    for column in range(columns):
        counts=scan([heights[row][column] for row in range(rows)])
        for row in range(rows):answer[row][column]+=counts[row]
    return answer
'''

DIGITS = '''\
def digit_frequency_matches_value(num):
    from collections import Counter
    counts=Counter(num)
    return all(counts[str(index)]==int(value) for index,value in enumerate(num))
'''

SENDER = '''\
def sender_with_most_words(messages,senders):
    totals={}
    for message,sender in zip(messages,senders):totals[sender]=totals.get(sender,0)+len(message.split())
    return max(totals,key=lambda sender:(totals[sender],sender))
'''

IMPORTANCE = '''\
def maximum_road_importance(n,roads):
    degree=[0]*n
    for left,right in roads:degree[left]+=1;degree[right]+=1
    return sum(value*weight for value,weight in zip(range(1,n+1),sorted(degree)))
'''

COPIES = '''\
def maximum_target_copies(s,target):
    from collections import Counter
    available=Counter(s);needed=Counter(target)
    return min(available[char]//count for char,count in needed.items())
'''


BATCH = {
    2282: entry('visible_people_right_and_below',[('heights','list[list[int]]')],'list[list[int]]',['matrices','monotonic stacks'],['All heights are distinct positive integers.','A person sees rightward and downward until and including the first person at least as tall; shorter people popped before that are also visible.','Return for every cell the total visible people in those two directions.'],[([[[3,1,4,2,5]]],'The five rightward counts are 2,1,2,1,0.'),([[[5],[3],[4],[2]]],'Downward visibility counts are 2,1,1,0.')],[[g] for g in [[[1]],[[1,2]],[[2,1]],[[3,1,4,2,5]],[[5],[3],[4],[2]],[[1,2],[3,4]],[[4,3],[2,1]],[[5,1,4],[2,6,3]],[[9,1,8,2],[3,7,4,6]],[[1,3,2]],[[10],[1],[9]],[[8,4,2],[7,3,1]],[[2,9,1],[8,3,7],[4,6,5]],[[6,1,5,2,4,3]]]],PEOPLE,[PEOPLE.replace('if stack:counts[index]+=1',''),PEOPLE.replace('>stack[-1]','<stack[-1]')],['Fails to count the first blocking person at least as tall.','Pops taller people instead of shorter ones and corrupts visibility order.'],people_oracle,random_people,['A decreasing stack summarizes which people remain visible in one scan direction.','Scanning from the far end, each shorter popped height is visible, and the remaining stack top is the one blocking visible person.','Run that scan on each row and each column, adding the two counts.','Popped people have no taller obstruction before the current person, while only the nearest surviving taller person can be seen beyond them.'],'O(rows*columns)','O(max(rows,columns))',7),
    2283: entry('digit_frequency_matches_value',[('num','str')],'bool',['strings','counting'],['For every index i in num, interpret num[i] as the required count of digit str(i).','Counts refer to the whole string; indices with required zero must also be checked.','Return true only when every indexed requirement matches exactly.'],[(['1210'],'Digit zero occurs once, one occurs twice, two occurs once, and three occurs zero times.'),(['030'],'The required zero count is zero, but digit zero occurs twice, so return false.')],[[x] for x in ['0','1','1210','030','2020','21200','3211000','1000','2000','101','22','1234','0000','42101000']],DIGITS,[DIGITS.replace('==int(value)','>=int(value)'),DIGITS.replace('enumerate(num)','enumerate(num[1:],1)')],['Allows a digit to occur more often than its declared count.','Skips validation of the required count for digit zero.'],digit_count_oracle,random_digit_count,['Count every digit character in the full string.','For each position and stored digit, compare the frequency of str(index) with int(value).','Return all(counts[str(i)] == int(num[i]) for every index i).','The conjunction checks every equality in the definition, including explicit zero counts.'],'O(n)','O(n)',3),
    2284: entry('sender_with_most_words',[('messages','list[str]'),('senders','list[str]')],'str',['arrays','hash maps','strings'],['messages[i] was sent by senders[i], and words are separated by single spaces.','Sum word counts across all messages from each sender.','Choose the lexicographically largest sender name when total counts tie.'],[([['Hello userTwooo','Hi userThree','Wonderful day Alice','Nice day userThree'],['Alice','userTwo','userThree','Alice']],'Alice has five total words, more than either other sender.'),([['How is leetcode for everyone','Leetcode is useful for practice'],['Bob','Charlie']],'Both senders have five words, so lexicographically larger Charlie wins.')],[[m,s] for m,s in [(['x'],['A']),(['a b','c'],['A','A']),(['Hello userTwooo','Hi userThree','Wonderful day Alice','Nice day userThree'],['Alice','userTwo','userThree','Alice']),(['How is leetcode for everyone','Leetcode is useful for practice'],['Bob','Charlie']),(['one','two'],['a','b']),(['one two three','x'],['a','b']),(['x','a b'],['Z','a']),(['a b','c d'],['same','same']),(['one','two three','four'],['A','B','A']),(['x y','z'],['zoe','Zoe']),(['a','b','c'],['u','v','w']),(['a b c','d e','f'],['x','y','y']),(['hello world'],['Alice']),(['a b','c d','e f'],['Bob','Alice','Bob'])]],SENDER,[SENDER.replace('(totals[sender],sender)','totals[sender]'),SENDER.replace('len(message.split())','1')],['Ignores the lexicographically largest tie-break and keeps an arbitrary maximum insertion order.','Counts messages instead of words within messages.'],sender_oracle,random_sender,['Aggregate word totals in a dictionary keyed by sender.','Python tuple ordering can rank first by total and then by sender name.','Return max(totals, key=lambda sender: (totals[sender], sender)).','Aggregation computes each sender’s exact total, and the tuple key implements both primary and tie-break rules.'],'O(total message characters)','O(senders)',5),
    2285: entry('maximum_road_importance',[('n','int'),('roads','list[list[int]]')],'int',['graphs','greedy','sorting'],['Assign each city a distinct integer value from one through n.','Each road contributes the values of both endpoints, so a city’s label is counted once per incident road.','Return the maximum possible total road importance.'],[([5,[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]],'Assigning larger values to higher-degree cities produces total importance forty-three.'),([3,[]],'With no roads every assignment has total importance zero.')],[[n,r] for n,r in [(1,[]),(2,[[0,1]]),(3,[]),(5,[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]),(3,[[0,1],[1,2]]),(4,[[0,1],[0,2],[0,3]]),(4,[[0,1],[1,2],[2,3],[3,0]]),(5,[[0,1],[2,3]]),(6,[[0,1],[0,2],[0,3],[4,5]]),(3,[[0,1],[0,2],[1,2]]),(5,[[0,4],[1,4],[2,4],[3,4]]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]]),(4,[[0,1]]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]])]],IMPORTANCE,[IMPORTANCE.replace('sorted(degree)','sorted(degree,reverse=True)'),IMPORTANCE.replace('range(1,n+1)','range(n)')],['Pairs the largest labels with the smallest degrees.','Assigns values zero through n-1 instead of the required one through n.'],importance_oracle,random_importance,['Rewrite total road importance as the sum of label[city]*degree[city].','By the rearrangement inequality, pair the largest labels with the largest degrees.','Sort degrees ascending and take their dot product with values one through n.','Any inversion pairing a larger label with a smaller degree can be swapped without decreasing the total, yielding the sorted optimum.'],'O(n+roads+n log n)','O(n)',6),
    2287: entry('maximum_target_copies',[('s','str'),('target','str')],'int',['strings','counting','hash maps'],['Characters of s may be rearranged and each occurrence may be used at most once.','Each target copy consumes its full character multiset, including repeated target letters.','Return the greatest number of complete copies.'],[(['ilovecodingonleetcode','code'],'The source has enough of every required letter for two complete copies of code.'),(['abbaccaddaeea','aaaaa'],'Only one group of five a characters is available.')],[[s,t] for s,t in [('a','a'),('a','b'),('ilovecodingonleetcode','code'),('abbaccaddaeea','aaaaa'),('abcabc','abc'),('aaaa','aa'),('xyz','xyzz'),('leetcode','leet'),('mississippi','issi'),('ababab','ab'),('hello','ll'),('programming','gram'),('abc','abcd'),('zzzzzy','zy')]],COPIES,[COPIES.replace('//count',''),COPIES.replace('min(','max(',1)],['Ignores repeated letters needed by each target copy.','Uses the most abundant required ratio instead of the limiting least abundant character.'],copies_oracle,random_copies,['Count available source characters and required target characters.','For each distinct target character, integer-divide available count by required count.','Return the minimum of those per-character copy limits.','Every copy must satisfy every character requirement, so the smallest ratio is necessary; using that many copies is also sufficient.'],'O(len(s)+len(target))','O(alphabet)',3),
}
