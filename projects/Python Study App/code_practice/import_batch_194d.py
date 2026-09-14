"""Odd/even GCD, frequency filtering, least digits, absolute sorting, and race order."""
from collections import Counter
from math import gcd
from .import_batch_055 import entry

def gcd_oracle(a):return gcd(sum(range(1,2*a[0],2)),sum(range(2,2*a[0]+1,2)))
def random_gcd(r):return [r.randint(1,1000)]
def filter_oracle(a):
    s,k=a;c=Counter(s);return ''.join(ch for ch in s if c[ch]<k)
def random_filter(r):return [''.join(r.choice('abcdef') for _ in range(r.randint(1,60))),r.randint(1,12)]
def least_oracle(a):
    c=Counter(str(a[0]));return min(map(int,c),key=lambda d:(c[str(d)],d))
def random_least(r):return [r.randint(0,10**12)]
def absolute_oracle(a):return sorted(a[0],key=abs)
def random_absolute(r):return [[r.randint(-100,100) for _ in range(r.randint(1,40))]]
def race_oracle(a):return [x for x in a[0] if x in set(a[1])]
def random_race(r):
    n=r.randint(1,30);order=list(range(1,n+1));r.shuffle(order);friends=sorted(r.sample(order,r.randint(1,n)));return [order,friends]

GCD='''def gcd_of_first_odd_even_sums(n):
    return n
'''
FILTER='''def filter_characters_below_frequency(s,k):
    from collections import Counter
    counts=Counter(s)
    return ''.join(char for char in s if counts[char]<k)
'''
LEAST='''def least_frequent_digit(n):
    from collections import Counter
    counts=Counter(str(n))
    return min((int(char) for char in counts),key=lambda digit:(counts[str(digit)],digit))
'''
ABSOLUTE='''def sort_by_absolute_value(nums):
    return sorted(nums,key=abs)
'''
RACE='''def restore_friend_finishing_order(order,friends):
    selected=set(friends)
    return [person for person in order if person in selected]
'''

BATCH={
3658:entry('gcd_of_first_odd_even_sums',[('n','int')],'int',['math','number theory'],['Sum the first n positive odd numbers and the first n positive even numbers.','Return the greatest common divisor of those two sums.','n is positive.'],[([4],'The sums are sixteen and twenty, whose greatest common divisor is four.'),([1],'The sums one and two have gcd one.')],[[n] for n in [2,3,5,6,7,8,9,10,12,25,50,99,100,1000]],GCD,[GCD.replace('return n','return n*n'),GCD.replace('return n','return 2*n')],['Returns the odd-number sum instead of the gcd.','Returns the even sum factor two-n.'],gcd_oracle,random_gcd,['The first n odd numbers sum to n squared.','The first n even numbers sum to n(n+1).','Their gcd is n*gcd(n,n+1).','Consecutive integers are coprime, leaving n.'],'O(1)','O(1)',3),
3662:entry('filter_characters_below_frequency',[('s','str'),('k','int')],'str',['strings','hash maps'],['Count every lowercase character in s.','Keep exactly the occurrences whose character appears fewer than k times overall.','Preserve their original order.'],[(['aadbbcccca',3],'Only d and the two b occurrences have total frequencies below three, giving dbb.'),(['aaa',3],'a occurs exactly k times, so every occurrence is removed.')],[[s,k] for s,k in [('a',1),('a',2),('aaa',3),('aadbbcccca',3),('abc',2),('aabb',2),('aabb',3),('mississippi',3),('leetcode',2),('zzzyx',3),('ababac',4),('qqqww',2),('xyxyzz',3),('hello',5)]],FILTER,[FILTER.replace('<k','<=k'),FILTER.replace('counts[char]','s.count(s[0])')],['Keeps characters occurring exactly k times.','Uses the first character frequency for every position.'],filter_oracle,random_filter,['Build a global character frequency table.','Scan the original string in order.','Append a character only when its total count is strictly below k.','Joining retained occurrences preserves their source order.'],'O(n)','O(n)',3),
3663:entry('least_frequent_digit',[('n','int')],'int',['math','digits','hash maps'],['Count digits that actually appear in n.','Return the digit with the smallest frequency.','Break equal-frequency ties by the smaller digit.'],[([1553322],'Digit one appears once while two, three, and five appear twice, so return one.'),([9009],'Digits zero and nine tie twice; zero is smaller.')],[[n] for n in [0,1,11,12,9009,1553322,123456789,99910,101010,4444332,765567,100000,987789,222333444]],LEAST,[LEAST.replace(',digit)',',-digit)'),LEAST.replace('min(','max(',1)],['Breaks ties toward the larger digit.','Chooses the most frequent digit.'],least_oracle,random_least,['Count only decimal digits present in n.','Rank each by frequency first and numeric digit second.','The minimum tuple selects least frequency and then smallest digit.','Return the digit component as an integer.'],'O(digits)','O(1)',3),
3667:entry('sort_by_absolute_value',[('nums','list[int]')],'list[int]',['arrays','sorting'],['Rearrange nums by nondecreasing absolute value.','Python’s stable ordering preserves source order when absolute values tie.','Return the sorted array.'],[([[3,-1,-4,1,5]],'Absolute values order the result as [-1,1,3,-4,5].'),([[-2,2,-1,1]],'The tied signs retain their original order within each absolute value.')],[[x] for x in [[0],[1,-1],[3,-1,-4,1,5],[-2,2,-1,1],[5,4,3],[ -5,-1,-3],[0,-2,2],[10,-10,1],[2,-3,1],[7,0,-7],[4,-2,-4,2],[100,-1,50],[3,3,-3],[9,-8,7,-6]]],ABSOLUTE,[ABSOLUTE.replace('key=abs',''),ABSOLUTE.replace('key=abs','key=lambda x:-abs(x)')],['Sorts by signed numeric value.','Sorts by decreasing absolute value.'],absolute_oracle,random_absolute,['Use absolute value as the sorting key.','Nondecreasing key order gives the required arrangement.','A stable sort keeps original relative order on equal keys.','Return the newly ordered values.'],'O(n log n)','O(n)',3),
3668:entry('restore_friend_finishing_order',[('order','list[int]'),('friends','list[int]')],'list[int]',['arrays','sets','filtering'],['order is a permutation describing all race finishers.','friends lists selected racer IDs, but not their finishing order.','Return only friend IDs in the order they appear in the race result.'],[([[3,1,2,5,4],[1,3,4]],'Filtering the finish order keeps 3, then 1, then 4.'),([[1,2,3],[2]],'The only friend finishes second, so return [2].')],[[o,f] for o,f in [([1],[1]),([1,2],[1]),([1,2],[2]),([2,1],[1,2]),([3,1,2,5,4],[1,3,4]),([1,2,3],[2]),([4,3,2,1],[1,4]),([2,4,1,3],[1,2,3,4]),([5,1,4,2,3],[2,5]),([1,3,5,2,4],[3,4]),([6,5,4,3,2,1],[2,3,6]),([2,1,3],[1,3]),([7,1,2,3,4,5,6],[6,7]),([3,2,1,4],[1,2])]],RACE,[RACE.replace('order if person in selected','friends if person in selected'),RACE.replace('if person in selected','if person not in selected')],['Returns friends in their ID-list order rather than finish order.','Returns nonfriends instead of friends.'],race_oracle,random_race,['Place friend IDs in a membership set.','Scan the complete finishing order.','Append each finisher who belongs to the friend set.','Filtering this way preserves exactly the race order.'],'O(n+friends)','O(friends)',3),
}
