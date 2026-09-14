"""Fourth slice of workbook batch 125."""

from collections import Counter

from .import_batch_055 import entry


def texts_oracle(args):
    text = args[0]
    maximum = {'7': 4, '9': 4}
    def decode(index):
        if index == len(text):
            return 1
        answer = 0
        for end in range(index, min(len(text), index + maximum.get(text[index], 3))):
            if text[end] != text[index]:
                break
            answer += decode(end + 1)
        return answer
    return decode(0) % 1_000_000_007


def random_texts(rng):
    return ["".join(rng.choice("23456789") for _ in range(rng.randint(1, 18)))]


def parentheses_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    def walk(row, column, balance):
        balance += 1 if grid[row][column] == '(' else -1
        if balance < 0:
            return False
        if (row, column) == (rows - 1, columns - 1):
            return balance == 0
        return ((row + 1 < rows and walk(row + 1, column, balance)) or
                (column + 1 < columns and walk(row, column + 1, balance)))
    return walk(0, 0, 0)


def random_parentheses(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[ [rng.choice('()') for _ in range(columns)] for _ in range(rows) ]]


def keypress_oracle(args):
    frequencies = sorted(Counter(args[0]).values(), reverse=True)
    best = 0
    for index, count in enumerate(frequencies):
        best += count * (1 + index // 9)
    return best


def random_keypress(rng):
    return ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(1, 60)))]


def beauty_oracle(args):
    number, size = args
    text = str(number)
    answer = 0
    for index in range(len(text) - size + 1):
        value = int(text[index:index + size])
        answer += value != 0 and number % value == 0
    return answer


def random_beauty(rng):
    number = rng.randint(1, 99999999)
    return [number, rng.randint(1, len(str(number)))]


def split_oracle(args):
    nums = args[0]
    return sum(sum(nums[:index]) >= sum(nums[index:]) for index in range(1, len(nums)))


def random_split(rng):
    return [[rng.randint(-30, 30) for _ in range(rng.randint(2, 30))]]


TEXTS = '''\
def count_possible_phone_texts(pressed_keys):
    modulo=1000000007;dp=[0]*(len(pressed_keys)+1);dp[0]=1
    for end in range(1,len(pressed_keys)+1):
        limit=4 if pressed_keys[end-1] in '79' else 3
        for length in range(1,min(limit,end)+1):
            if pressed_keys[end-length:end]==pressed_keys[end-1]*length:dp[end]=(dp[end]+dp[end-length])%modulo
            else:break
    return dp[-1]
'''

PARENTHESES = '''\
def has_valid_parentheses_grid_path(grid):
    rows,columns=len(grid),len(grid[0]);length=rows+columns-1
    if length%2 or grid[0][0]==')' or grid[-1][-1]=='(':return False
    states=[[set() for _ in range(columns)] for _ in range(rows)];states[0][0].add(1)
    for row in range(rows):
        for column in range(columns):
            if row==0 and column==0:continue
            change=1 if grid[row][column]=='(' else -1
            previous=set()
            if row:previous|=states[row-1][column]
            if column:previous|=states[row][column-1]
            remaining=(rows-1-row)+(columns-1-column)
            states[row][column]={balance+change for balance in previous if 0<=balance+change<=remaining}
    return 0 in states[-1][-1]
'''

KEYPRESSES = '''\
def minimum_keypad_presses(s):
    from collections import Counter
    frequencies=sorted(Counter(s).values(),reverse=True)
    return sum(count*(index//9+1) for index,count in enumerate(frequencies))
'''

BEAUTY = '''\
def number_k_beauty(num,k):
    text=str(num);answer=0
    for index in range(len(text)-k+1):
        value=int(text[index:index+k])
        if value and num%value==0:answer+=1
    return answer
'''

SPLITS = '''\
def count_dominant_prefix_splits(nums):
    total=sum(nums);prefix=0;answer=0
    for value in nums[:-1]:
        prefix+=value
        answer+=prefix>=total-prefix
    return answer
'''


BATCH = {
    2266: entry('count_possible_phone_texts',[('pressed_keys','str')],'int',['strings','dynamic programming'],['Digits two through six and eight have three letters; seven and nine have four.','A letter is encoded by one through that digit’s maximum consecutive equal presses.','Count all complete partitions of the received string and return the result modulo 1,000,000,007.'],[(['22233'],'The run 222 has four partitions and 33 has two, producing eight possible messages.'),(['7777'],'The four equal presses can be partitioned in eight valid ways when group size is at most four.')],[[x] for x in ['2','22','222','2222','7','7777','77777','22233','234','9999','99999','888222','7777333','222222','239992','5556666']],TEXTS,[TEXTS.replace("in '79'","in '7'"),TEXTS.replace('dp[end-length]','dp[end-1]')],['Treats digit nine as having only three mapped letters.','Every transition reuses only the immediately preceding state instead of the state before its chosen group.'],texts_oracle,random_texts,['This is a partition-counting dynamic program over prefixes.','For each ending position, try equal-digit groups of lengths one through three or four.','Add dp[end-length] for each valid equal group, applying the modulus.','Every decoded message has one unique final press group, so the transitions partition all messages without overlap.'],'O(n)','O(n)',6),
    2267: entry('has_valid_parentheses_grid_path',[('grid','list[list[str]]')],'bool',['matrices','dynamic programming','parentheses'],['Start at the top-left, finish at the bottom-right, and move only down or right.','The visited characters must form a balanced-parentheses string: no prefix has negative balance and final balance is zero.','Return whether at least one valid path exists.'],[([[['(','(','('],[')','(',')'],['(','(',')'],['(','(',')']]],'A down-and-right route exists whose running balance never becomes negative and ends at zero.'),([[[')',')'],['(','(']]],'Every path begins with a closing parenthesis, so none can be valid.')],[[g] for g in [[['(',')']],[['(',')'],['(',')']],[['(',')'],[')',')']],[['(',')','('],['(',')',')']],[['(','(','('],[')','(',')'],['(','(',')'],['(','(',')']],[[')',')'],['(','(']],[['(']],[[')']],[['(','('],[')',')']],[['(','(',')'],[')',')',')']],[['(','('],['(',')'],[')',')']],[['(',')',')'],['(','(',')']],[['(','(','('],[')',')',')'],['(','(',')']],[['(','(',')',')']]]],PARENTHESES,[PARENTHESES.replace('balance+change for balance in previous if 0<=balance+change','balance+change for balance in previous if -1<=balance+change'),PARENTHESES.replace('length%2','length%2==0')],['Allows a path prefix balance of negative one.','Rejects even-length paths and accepts the impossible odd path-length parity.'],parentheses_oracle,random_parentheses,['A path state needs its cell and current open-parenthesis balance.','Propagate all feasible balances from the upper and left cells, discarding negative balances and balances too large to close in remaining steps.','Initialize balance one at the opening start and accept when zero reaches the destination.','Every down/right path is represented by successive state transitions, and balance filtering is exactly the validity condition.'],'O(m*n*(m+n))','O(m*n*(m+n))',8),
    2268: entry('minimum_keypad_presses',[('s','str')],'int',['strings','greedy','counting'],['Nine buttons each provide a one-press, two-press, and three-press letter slot.','Every lowercase letter is assigned exactly once, but only characters occurring in s contribute cost.','Minimize total keypresses across all occurrences of s.'],[(['apple'],'Assigning its four used letters to one-press slots makes all five characters cost one press.'),(['abcdefghijkl'],'Nine letters cost one press and three cost two, totaling fifteen.')],[[x] for x in ['a','apple','abcdefghijkl','abcdefghi','abcdefghij','abcdefghijklmnopqrstuvwxyz','aaaa','aabbcc','thequickbrownfox','zzzzzy','abcabcabc','leetcode','mississippi','programming']],KEYPRESSES,[KEYPRESSES.replace('index//9+1','index//8+1'),KEYPRESSES.replace('reverse=True','reverse=False')],['Uses only eight slots per press level instead of nine.','Assigns the most frequent letters to the most expensive slots.'],keypress_oracle,random_keypress,['Letter identities do not matter after their frequencies are known.','Assign larger frequencies to cheaper slots: nine cost-one slots, then nine cost-two slots, then eight cost-three slots.','Sort frequencies descending and sum frequency*(index//9+1).','Swapping a more frequent letter out of a costlier slot never increases cost, proving the sorted greedy assignment.'],'O(n+alphabet log alphabet)','O(alphabet)',6),
    2269: entry('number_k_beauty',[('num','int'),('k','int')],'int',['strings','sliding windows','math'],['Inspect every contiguous length-k substring of the decimal representation, including ones with leading zeros.','Convert each substring to an integer; zero is not a divisor.','Count windows whose nonzero value divides num evenly.'],[([240,2],'The windows 24 and 40 both divide 240, so the k-beauty is two.'),([430043,2],'The windows 43 at both ends divide the number; 30,00, and 04 do not.')],[[n,k] for n,k in [(240,2),(430043,2),(1,1),(10,1),(100,2),(120,1),(999,2),(555,1),(10101,2),(9876,3),(1001,2),(2222,2),(314159,1),(808080,2)]],BEAUTY,[BEAUTY.replace('if value and','if '),BEAUTY.replace('len(text)-k+1','len(text)-k')],['Attempts modulo by a zero-valued window and fails instead of skipping it.','Omits the final length-k window.'],beauty_oracle,random_beauty,['A fixed-size scan directly enumerates all candidate divisor substrings.','Parse each window; test nonzero before taking num modulo the value.','Loop index zero through len(text)-k inclusive and increment on value and num%value==0.','Every possible length-k substring appears at exactly one start index, so the count includes precisely the valid divisors.'],'O(d*k)','O(k)',3),
    2270: entry('count_dominant_prefix_splits',[('nums','list[int]')],'int',['arrays','prefix sums'],['Split only after indices zero through n-2 so both sides are nonempty.','A split is valid when the left sum is greater than or equal to the right sum.','Values may be negative.'],[([[10,4,-8,7]],'Splits after indices zero and one satisfy left sum at least right sum, giving two.'),([[2,3,1,0]],'All three possible splits satisfy the inequality.')],[[x] for x in [[1,1],[1,2],[2,1],[10,4,-8,7],[2,3,1,0],[-1,-1],[-1,1],[1,-1],[0,0,0],[5,-2,-3],[1,2,3,4],[-5,-1,-2],[10,-20,30,-40],[3,3,3,3]]],SPLITS,[SPLITS.replace('nums[:-1]','nums'),SPLITS.replace('>=','>')],['Allows a split after the final element and counts an empty right side.','Requires strict inequality and omits equal-sum splits.'],split_oracle,random_split,['Maintain the total sum and a running left prefix.','At each legal split, right equals total-prefix, so compare without a second scan.','Iterate nums[:-1], update prefix, and count prefix>=total-prefix.','The loop covers every and only legal split index, and the algebra gives its exact two side sums.'],'O(n)','O(1)',5),
}

BATCH[2267]['boundaries'].append([[list('())(()')]])
BATCH[2269]['wrong'][0] = '''\
def number_k_beauty(num,k):
    text=str(num);answer=0
    for index in range(len(text)-k+1):
        value=int(text[index:index+k])
        if value==0 or num%value==0:answer+=1
    return answer
'''
BATCH[2269]['wrong_reasons'][0] = 'Counts a zero-valued window as a divisor even though zero is explicitly excluded.'
