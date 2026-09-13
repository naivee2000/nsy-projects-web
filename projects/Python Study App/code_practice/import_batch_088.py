"""Reviewed deterministic string, arithmetic, array, and graph imports."""
from collections import Counter, deque
from .import_batch_055 import entry


def palindrome_oracle(args):
    text = args[0]
    best = text[0]
    for left in range(len(text)):
        for right in range(left + len(best), len(text)):
            piece = text[left:right + 1]
            if piece == piece[::-1] and len(piece) > len(best):
                best = piece
    return best


def power_oracle(args):
    base, exponent = args
    return base ** exponent


def fraction_oracle(args):
    numerator, denominator = args
    if numerator == 0:
        return "0"
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    numerator, denominator = abs(numerator), abs(denominator)
    whole, remainder = divmod(numerator, denominator)
    if remainder == 0:
        return sign + str(whole)
    digits, first_position = [], {}
    while remainder and remainder not in first_position:
        first_position[remainder] = len(digits)
        digit, remainder = divmod(remainder * 10, denominator)
        digits.append(str(digit))
    if remainder:
        start = first_position[remainder]
        decimal = "".join(digits[:start]) + "(" + "".join(digits[start:]) + ")"
    else:
        decimal = "".join(digits)
    return sign + str(whole) + "." + decimal


def sorted_pair_oracle(args):
    numbers, target = args
    for left in range(len(numbers)):
        for right in range(left + 1, len(numbers)):
            if numbers[left] + numbers[right] == target:
                return [left + 1, right + 1]


def courses_oracle(args):
    count, prerequisites = args
    graph = [[] for _ in range(count)]
    for course, requirement in prerequisites:
        graph[requirement].append(course)
    state = [0] * count
    def cyclic(node):
        if state[node] == 1:
            return True
        if state[node] == 2:
            return False
        state[node] = 1
        if any(cyclic(other) for other in graph[node]):
            return True
        state[node] = 2
        return False
    return not any(cyclic(node) for node in range(count) if state[node] == 0)


def ransom_oracle(args):
    note, magazine = args
    remaining = list(magazine)
    for char in note:
        if char not in remaining:
            return False
        remaining.remove(char)
    return True


def difference_oracle(args):
    source, changed = args
    remaining = list(changed)
    for char in source:
        remaining.remove(char)
    return remaining[0]


def rotation_oracle(args):
    nums = args[0]
    return max(sum(index * nums[(index - shift) % len(nums)] for index in range(len(nums)))
               for shift in range(len(nums)))


def digit_oracle(args):
    position = args[0]
    def through(number):
        total, start, width = 0, 1, 1
        while start * 10 <= number:
            total += 9 * start * width
            start *= 10
            width += 1
        return total + (number - start + 1) * width
    low, high = 1, position
    while low < high:
        middle = (low + high) // 2
        if through(middle) >= position:
            high = middle
        else:
            low = middle + 1
    before = through(low - 1) if low > 1 else 0
    return int(str(low)[position - before - 1])


def constructible_palindrome_oracle(args):
    counts = Counter(args[0])
    pairs = sum(value // 2 for value in counts.values())
    return pairs * 2 + int(any(value % 2 for value in counts.values()))


def random_palindrome(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 18)))]


def random_power(rng):
    exponent = rng.randint(-24, 24)
    base = rng.choice([-3.0, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.25, 2.0, 3.0])
    return [base, exponent]


def random_fraction(rng):
    denominator = rng.choice([value for value in range(-40, 41) if value])
    return [rng.randint(-200, 200), denominator]


def random_sorted_pair(rng):
    while True:
        numbers = sorted(rng.randint(-30, 30) for _ in range(rng.randint(2, 14)))
        left, right = sorted(rng.sample(range(len(numbers)), 2))
        target = numbers[left] + numbers[right]
        matches = [(i, j) for i in range(len(numbers)) for j in range(i + 1, len(numbers))
                   if numbers[i] + numbers[j] == target]
        if len(matches) == 1:
            return [numbers, target]


def random_courses(rng):
    count = rng.randint(1, 10)
    edges = [[course, requirement] for course in range(count) for requirement in range(count)
             if course != requirement and rng.random() < .12]
    return [count, edges]


def random_ransom(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(0, 18))),
            ''.join(rng.choice('abcd') for _ in range(rng.randint(0, 24)))]


def random_difference(rng):
    source = ''.join(rng.choice('abcdxyz') for _ in range(rng.randint(0, 20)))
    changed = list(source + rng.choice('abcdxyz'))
    rng.shuffle(changed)
    return [source, ''.join(changed)]


def random_rotation(rng):
    return [[rng.randint(-20, 20) for _ in range(rng.randint(1, 14))]]


def random_digit(rng):
    return [rng.randint(1, 2_000_000_000)]


def random_constructible(rng):
    return [''.join(rng.choice('aAbBcC012') for _ in range(rng.randint(1, 60)))]


PALINDROME = '''def longest_palindromic_substring(s):
 best_left=best_right=0
 def expand(left,right):
  while left>=0 and right<len(s) and s[left]==s[right]:left-=1;right+=1
  return left+1,right-1
 for center in range(len(s)):
  for left,right in (expand(center,center),expand(center,center+1)):
   if right-left>best_right-best_left:best_left,best_right=left,right
 return s[best_left:best_right+1]
'''

POWER = '''def fast_power(x, n):
 exponent=abs(n);answer=1.0;factor=x
 while exponent:
  if exponent&1:answer*=factor
  factor*=factor;exponent//=2
 return answer if n>=0 else 1.0/answer
'''

FRACTION = '''def fraction_to_recurring_decimal(numerator, denominator):
 if numerator==0:return "0"
 answer='-' if (numerator<0)!=(denominator<0) else ''
 numerator,denominator=abs(numerator),abs(denominator)
 whole,remainder=divmod(numerator,denominator);answer+=str(whole)
 if not remainder:return answer
 answer+='.';seen={};digits=[]
 while remainder and remainder not in seen:
  seen[remainder]=len(digits);digit,remainder=divmod(remainder*10,denominator);digits.append(str(digit))
 if remainder:
  at=seen[remainder];answer+=''.join(digits[:at])+'('+''.join(digits[at:])+')'
 else:answer+=''.join(digits)
 return answer
'''

PAIR = '''def two_sum_sorted_indices(numbers, target):
 left,right=0,len(numbers)-1
 while left<right:
  total=numbers[left]+numbers[right]
  if total==target:return [left+1,right+1]
  if total<target:left+=1
  else:right-=1
'''

COURSES = '''def can_finish_courses(num_courses, prerequisites):
 graph=[[] for _ in range(num_courses)];indegree=[0]*num_courses
 for course,requirement in prerequisites:graph[requirement].append(course);indegree[course]+=1
 queue=__import__('collections').deque(i for i,value in enumerate(indegree) if value==0);taken=0
 while queue:
  node=queue.popleft();taken+=1
  for other in graph[node]:
   indegree[other]-=1
   if indegree[other]==0:queue.append(other)
 return taken==num_courses
'''

RANSOM = '''def can_construct_note(ransom_note, magazine):
 from collections import Counter
 need=Counter(ransom_note);available=Counter(magazine)
 return all(available[char]>=amount for char,amount in need.items())
'''

DIFFERENCE = '''def added_character(s, t):
 value=0
 for char in s+t:value^=ord(char)
 return chr(value)
'''

ROTATION = '''def maximum_rotation_function(nums):
 total=sum(nums);current=sum(index*value for index,value in enumerate(nums));best=current;n=len(nums)
 for shift in range(1,n):
  current=current+total-n*nums[-shift];best=max(best,current)
 return best
'''

DIGIT = '''def nth_sequence_digit(n):
 width=1;count=9;start=1
 while n>width*count:
  n-=width*count;width+=1;count*=10;start*=10
 number=start+(n-1)//width
 return int(str(number)[(n-1)%width])
'''

PAL_LENGTH = '''def longest_constructible_palindrome(s):
 from collections import Counter
 length=0;odd=False
 for count in Counter(s).values():
  length+=(count//2)*2;odd|=bool(count%2)
 return length+int(odd)
'''


E = entry
BATCH = {
5:E('longest_palindromic_substring',[('s','str')],'str',['strings','two-pointers'],['1 <= len(s) <= 1000.','When several longest palindromes exist, return the leftmost one.'],[(['babad'],'Both bab and aba have length three; the leftmost answer is bab.'),(['cbbd'],'The even-length center between the two b characters yields bb.')],[[s] for s in ['a','aa','ab','aba','abba','abcda','aaaa','bananas','racecarx','xyzzy','abacdfgdcaba','noonabbad','tattarrattat','cabacddc']],PALINDROME,[PALINDROME.replace('expand(center,center+1)','expand(center+1,center+1)'),PALINDROME.replace('right-left>best_right-best_left','right-left>=best_right-best_left')],['Never expands around the gap between equal characters, missing even palindromes.','Overwrites equal-length answers and returns the rightmost tie.'],palindrome_oracle,random_palindrome,['A palindrome grows symmetrically from either one character or a gap.','Expand around every odd and even center while the two characters match.','Keep a candidate only when it is strictly longer, preserving the leftmost tie.','Every palindrome has exactly one such center, so one expansion discovers every candidate.'],'O(n²)','O(1)',5),
50:E('fast_power',[('x','float'),('n','int')],'float',['math','divide-and-conquer','binary'],['-100 < x < 100; -2^31 <= n <= 2^31-1.','If n is negative, x is nonzero; answers remain finite.'],[([2.0,10],'Repeated squaring computes 2^10 as 1024.'),([2.0,-2],'A negative exponent returns the reciprocal, 0.25.')],[[x,n] for x,n in [(1.0,0),(-1.0,7),(-1.0,8),(0.0,5),(2.0,1),(2.0,3),(2.0,-1),(-2.0,5),(-2.0,-4),(0.5,3),(1.5,4),(10.0,-3),(1.0001,1000),(-0.5,9)]],POWER,[POWER.replace('return answer if n>=0 else 1.0/answer','return answer'),POWER.replace('if exponent&1:answer*=factor','if exponent&1:pass')],['Forgets to take the reciprocal for negative exponents.','Squares the factor but never multiplies selected binary powers into the answer.'],power_oracle,random_power,['Use the binary digits of the exponent.','Square the current factor each round and multiply it in when the low exponent bit is one.','Work with abs(n), then take the reciprocal exactly once for a negative exponent.','Each round accounts for one binary place, reducing the exponent by half.'],'O(log |n|)','O(1)',5),
166:E('fraction_to_recurring_decimal',[('numerator','int'),('denominator','int')],'str',['hash-maps','math','simulation'],['Inputs are signed 32-bit integers and denominator is nonzero.','Enclose only the repeating decimal suffix in parentheses.'],[([1,2],'One half terminates as 0.5.'),([4,333],'The remainder cycle repeats 012, producing 0.(012).')],[[a,b] for a,b in [(0,3),(1,1),(2,1),(1,3),(2,3),(1,6),(1,7),(-1,2),(1,-2),(-1,-2),(22,7),(50,8),(7,12),(10,6)]],FRACTION,[FRACTION.replace("seen[remainder]=len(digits)","seen[remainder]=0"),FRACTION.replace("answer='-' if (numerator<0)!=(denominator<0) else ''","answer='' ")],['Records every cycle as beginning immediately after the decimal point.','Drops the negative sign for fractions with exactly one negative operand.'],fraction_oracle,random_fraction,['Long division is determined entirely by the current remainder.','Map each remainder to the digit position where it first appeared.','On remainder zero the decimal terminates; on a repeated remainder wrap the corresponding suffix in parentheses.','A repeated state must generate the same future digits, and no earlier digits belong to that cycle.'],'O(period length)','O(period length)',5),
167:E('two_sum_sorted_indices',[('numbers','list[int]'),('target','int')],'list[int]',['two-pointers','arrays'],['numbers is sorted nondecreasing and contains 2..30000 integers.','Exactly one distinct pair reaches target; return one-based indices using O(1) extra space.'],[([[2,7,11,15],9],'The first two values sum to nine, so return one-based indices 1 and 2.'),([[2,3,4],6],'The endpoints two and four form the unique pair.')],[[a,t] for a,t in [([-3,-1,2,5],1),([-5,-2,0,8],3),([1,2],3),([1,2,3,9],11),([0,1,4,6],10),([-10,-4,-1,7,12],2),([1,3,5,7,9],12),([2,2,3],4),([-2,0,3],1),([4,5,10,20],25),([-9,-3,2,11],8),([1,4,8,12,20],21),([-6,-5,-2,10],4),([3,6,8,14],20)]],PAIR,[PAIR.replace('return [left+1,right+1]','return [left,right]'),PAIR.replace('if total<target:left+=1','if total<target:right-=1')],['Returns zero-based indices instead of the required one-based positions.','Moves the upper pointer inward when the current sum is too small.'],sorted_pair_oracle,random_sorted_pair,['The smallest and largest remaining values bound every unexamined pair.','Start pointers at both ends of the sorted array.','If the sum is low, advance left; if high, retreat right; return the one-based positions on equality.','The discarded endpoint cannot participate in a solution after the comparison.'],'O(n)','O(1)',5),
207:E('can_finish_courses',[('num_courses','int'),('prerequisites','list[list[int]]')],'bool',['graphs','topological-sort','breadth-first-search'],['1 <= num_courses <= 2000; prerequisite pairs are distinct.','[a,b] means b must be completed before a.'],[([2,[[1,0]]],'Course zero unlocks course one, so both can be completed.'),([2,[[1,0],[0,1]]],'The two courses depend on each other and form a cycle.')],[[n,e] for n,e in [(1,[]),(2,[]),(3,[[1,0],[2,1]]),(3,[[1,0],[2,1],[0,2]]),(4,[[1,0],[2,0],[3,1],[3,2]]),(4,[[1,0],[2,1],[1,2]]),(5,[[1,0],[2,0],[3,1],[4,3]]),(5,[[1,0],[2,1],[0,2]]),(3,[[2,0],[2,1]]),(6,[[1,0],[2,1],[3,2],[4,3],[5,4]]),(6,[[1,0],[2,1],[0,2],[4,3]]),(4,[[0,1]]),(3,[[1,0],[2,0],[1,2]]),(7,[[1,0],[2,0],[3,1],[3,2],[5,4],[6,5]])]],COURSES,['''def can_finish_courses(num_courses, prerequisites):
 indegree=[0]*num_courses
 for course,requirement in prerequisites:indegree[course]+=1
 return any(value==0 for value in indegree)
''','''def can_finish_courses(num_courses, prerequisites):
 return len(prerequisites)<num_courses
'''],['Treats the existence of an initial zero-indegree course as proof that every component is acyclic.','Uses edge count as a cycle test, although acyclic graphs may have at least as many edges as vertices.'],courses_oracle,random_courses,['A course becomes available only after all incoming prerequisite edges are removed.','Track indegrees and begin with every zero-indegree course.','Repeatedly take one available course, decrement its outgoing neighbors, and enqueue newly unlocked courses.','All courses are processed exactly when the dependency graph has no directed cycle.'],'O(courses+prerequisites)','O(courses+prerequisites)',5),
383:E('can_construct_note',[('ransom_note','str'),('magazine','str')],'bool',['hash-maps','strings'],['Both strings contain lowercase English letters.','Each magazine character occurrence may be used once.'],[(['a','b'],'The magazine has no a, so the note cannot be formed.'),(['aa','aab'],'Two available a characters cover both required copies.')],[[a,b] for a,b in [('', ''),('', 'abc'),('a','a'),('aa','a'),('ab','ba'),('abc','ab'),('abc','cbad'),('zzz','zzzz'),('aab','aba'),('abcd','dcba'),('hello','oleh'),('hello','oellh'),('xxy','xyx'),('cab','aabbcc')]],RANSOM,['''def can_construct_note(ransom_note, magazine):
 return set(ransom_note)<=set(magazine)
''','''def can_construct_note(ransom_note, magazine):
 return len(ransom_note)<=len(magazine)
'''],['Checks only character presence and ignores required multiplicities.','Checks only total length and ignores which letters are available.'],ransom_oracle,random_ransom,['Count how many copies of each character are required and available.','Compare the two frequency maps.','Every required count must be no greater than its magazine count.','Counts enforce both character identity and one-use-per-occurrence.'],'O(n+m)','O(alphabet)',3),
389:E('added_character',[('s','str'),('t','str')],'str',['bit-manipulation','strings'],['t is a shuffle of s plus exactly one lowercase letter.','Return that added character, including when it duplicates an existing one.'],[(['abcd','abcde'],'XOR cancels a,b,c,d across both strings, leaving e.'),(['','y'],'With an empty source, y is the added character.')],[[a,b] for a,b in [('a','aa'),('ab','baa'),('xyz','zyxx'),('hello','olehlx'),('zz','zzz'),('abc','dcab'),('mnop','pmonq'),('aaa','baaa'),('kitten','tkitena'),('q','zq'),('race','ecrad'),('binary','ryanibb'),('same','mseak'),('longer','grolenr')]],DIFFERENCE,['''def added_character(s, t):
 for char in t:
  if char not in s:return char
 return t[0]
''','''def added_character(s, t):
 return t[-1]
'''],['A membership check cannot identify which repeated occurrence is extra.','Assumes the added character remains last after t is shuffled.'],difference_oracle,random_difference,['Equal character occurrences cancel between the two strings.','XOR the code point of every character in both strings.','Convert the one remaining code point back to a character.','XOR is commutative and x XOR x is zero, so shuffle order is irrelevant.'],'O(n)','O(1)',3),
396:E('maximum_rotation_function',[('nums','list[int]')],'int',['arrays','dynamic-programming','math'],['1 <= len(nums) <= 100000; values are signed integers.','For each right rotation k, score sum(i * rotated[i]); return the maximum.'],[([[4,3,2,6]],'Rotation scores are 25,16,23,26, so the maximum is 26.'),([[100]],'The sole value always has index zero, so the score is zero.')],[[x] for x in [[1],[1,2],[2,1],[0,0],[-1,-2,-3],[1,2,3],[3,2,1],[4,3,2,6],[10,-10,10],[-5,0,5],[2,2,2,2],[1,-2,3,-4],[9,1,8,2,7],[1000,-1000]]],ROTATION,[ROTATION.replace('current=current+total-n*nums[-shift]','current=current-total+n*nums[-shift]'),ROTATION.replace('best=max(best,current)','best=min(best,current)')],['Uses the left-rotation recurrence while iterating right rotations.','Keeps the minimum rotation score rather than the maximum.'],rotation_oracle,random_rotation,['Adjacent rotation scores differ by the array total and one wrapped value.','Compute F(0) and the total sum once.','For right rotation k, F(k)=F(k-1)+total-n*nums[n-k]; retain the maximum.','All nonwrapped values gain one index while the wrapped value loses n-1, yielding the recurrence.'],'O(n)','O(1)',5),
400:E('nth_sequence_digit',[('n','int')],'int',['math','binary-search'],['1 <= n <= 2^31-1.','Positions are one-based in the sequence 123456789101112... .'],[([3],'The third sequence digit is 3.'),([11],'Positions ten and eleven are the digits 1 and 0 of number 10.')],[[n] for n in [1,2,9,10,12,15,20,100,189,190,191,1000,10000,2147483647]],DIGIT,[DIGIT.replace('number=start+(n-1)//width','number=start+n//width'),DIGIT.replace('(n-1)%width','n%width')],['Advances to the next number when n lands on a block boundary.','Uses a zero-based digit offset on a one-based remaining position.'],digit_oracle,random_digit,['Numbers with the same decimal width form a contiguous digit block.','Subtract complete 1-digit, 2-digit, and wider blocks until n lies inside one.','Use (n-1)//width to locate the number and (n-1)%width to select its digit.','Subtracting whole blocks preserves the one-based position within the remaining width group.'],'O(log n)','O(1)',5),
409:E('longest_constructible_palindrome',[('s','str')],'int',['hash-maps','greedy','strings'],['1 <= len(s) <= 2000; uppercase and lowercase are distinct.','Characters may be reordered; return the greatest possible palindrome length.'],[(['abccccdd'],'Three character pairs plus one center create a palindrome of length seven.'),(['Aa'],'Case-sensitive characters differ, so only one can be used.')],[[s] for s in ['a','aa','ab','abc','aabb','aaab','aaaa','AaAa','cccddd','bananas','1122334','abccccdd','zzzyyyxxx','aAaaBBb']],PAL_LENGTH,['''def longest_constructible_palindrome(s):
 from collections import Counter
 return sum(count for count in Counter(s).values() if count%2==0)
''','''def longest_constructible_palindrome(s):
 from collections import Counter
 return sum((count//2)*2 for count in Counter(s).values())+sum(count%2 for count in Counter(s).values())
'''],['Discards the usable even portion of every odd frequency.','Places every odd leftover in the center although a palindrome has only one center.'],constructible_palindrome_oracle,random_constructible,['Every mirrored pair consumes two equal characters.','Take the largest even portion of each frequency.','After counting all pairs, add one center if any odd count exists.','All pairs can coexist symmetrically, while at most one unpaired character can occupy the center.'],'O(n)','O(alphabet)',3),
}

BATCH[50]['comparator']='float'
