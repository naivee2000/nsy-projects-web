"""Square bars, fruit rewards, balanced substrings, swap components, and phone digits."""
from collections import deque
from itertools import combinations

from .import_batch_055 import entry


def square_oracle(args):
    _,_,horizontal,vertical=args
    def longest(values):
        available=set(values);best=1
        for start in values:
            length=0
            while start+length in available:length+=1
            best=max(best,length+1)
        return best
    side=min(longest(horizontal),longest(vertical));return side*side


def random_square(rng):
    n,m=rng.randint(1,12),rng.randint(1,12)
    h=rng.sample(range(2,n+2),rng.randint(1,n));v=rng.sample(range(2,m+2),rng.randint(1,m))
    return [n,m,h,v]


def fruits_oracle(args):
    prices=args[0];size=len(prices);best=sum(prices)
    for mask in range(1<<size):
        bought={index+1 for index in range(size) if mask>>index&1}
        if 1 not in bought:continue
        if all(position in bought or any(source<position<=2*source for source in bought) for position in range(1,size+1)):
            best=min(best,sum(prices[position-1] for position in bought))
    return best


def random_fruits(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,11))]]


PHONE_GROUPS=('ab','cde','fgh','ijk','lmn','opq','rst','uvw','xyz')
PHONE_VALUE={char:index for index,letters in enumerate(PHONE_GROUPS,1) for char in letters}


def beautiful_substrings_oracle(args):
    text,divisor=args;answer=0
    for left,right in combinations(range(len(text)+1),2):
        piece=text[left:right];vowels=sum(char in 'aeiou' for char in piece);consonants=len(piece)-vowels
        answer+=vowels==consonants and vowels*consonants%divisor==0
    return answer


def random_beautiful_substrings(rng):return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,18))),rng.randint(1,12)]


def lexical_oracle(args):
    start=tuple(args[0]);limit=args[1];queue=deque([start]);seen={start};best=start
    while queue:
        state=queue.popleft();best=min(best,state)
        for i in range(len(state)):
            for j in range(i+1,len(state)):
                if abs(state[i]-state[j])<=limit:
                    changed=list(state);changed[i],changed[j]=changed[j],changed[i];following=tuple(changed)
                    if following not in seen:seen.add(following);queue.append(following)
    return list(best)


def random_lexical(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,7))],rng.randint(1,6)]


def divisible_oracle(args):
    text=args[0];answer=0
    for left,right in combinations(range(len(text)+1),2):
        answer+=sum(PHONE_VALUE[char] for char in text[left:right])%(right-left)==0
    return answer


def random_divisible(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,18)))]


SQUARE='''def maximum_square_hole_area(n,m,h_bars,v_bars):
    def span(bars):
        values=sorted(bars);best=current=1
        for index in range(1,len(values)):
            current=current+1 if values[index]==values[index-1]+1 else 1;best=max(best,current)
        return best+1
    side=min(span(h_bars),span(v_bars))
    return side*side
'''


FRUITS='''def minimum_fruit_coins(prices):
    from functools import lru_cache
    size=len(prices)
    @lru_cache(None)
    def buy(position):
        if 2*position>=size:return prices[position-1]
        return prices[position-1]+min(buy(next_position) for next_position in range(position+1,2*position+2))
    return buy(1)
'''


ODD_FRUITS='''def minimum_fruit_coins(prices):
    return sum(prices[::2])
'''


BEAUTIFUL='''def count_balanced_divisible_substrings(s,k):
    vowels=set('aeiou');answer=0
    for left in range(len(s)):
        vowel_count=0
        for right in range(left,len(s)):
            vowel_count+=s[right] in vowels;consonants=right-left+1-vowel_count
            if vowel_count==consonants and vowel_count*consonants%k==0:answer+=1
    return answer
'''


LEXICAL='''def lexicographically_smallest_swappable_array(nums,limit):
    ordered=sorted((value,index) for index,value in enumerate(nums));answer=[0]*len(nums);left=0
    while left<len(nums):
        right=left+1
        while right<len(nums) and ordered[right][0]-ordered[right-1][0]<=limit:right+=1
        indices=sorted(index for _,index in ordered[left:right])
        for index,(value,_) in zip(indices,ordered[left:right]):answer[index]=value
        left=right
    return answer
'''


DIVISIBLE='''def count_phone_divisible_substrings(word):
    groups=('ab','cde','fgh','ijk','lmn','opq','rst','uvw','xyz');values={char:index for index,letters in enumerate(groups,1) for char in letters};answer=0
    for average in range(1,10):
        counts={0:1};balance=0
        for char in word:
            balance+=values[char]-average;answer+=counts.get(balance,0);counts[balance]=counts.get(balance,0)+1
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2943:entry('maximum_square_hole_area',[('n','int'),('m','int'),('h_bars','list[int]'),('v_bars','list[int]')],'int',['sorting','arrays','geometry'],['The grid has n+2 horizontal and m+2 vertical bars; removable interior bar indices are distinct.','Removing r consecutive bars creates a span of r+1 cells in that direction.','Return the maximum square area obtainable by removing listed bars.'],[([2,1,[2,3],[2]],'Two consecutive horizontal removals allow height three, but the vertical span limits the square side to two.'),([1,1,[2],[2]],'Removing one bar in each direction creates a two-by-two square of area four.')],[[n,m,h,v] for n,m,h,v in [(1,1,[2],[2]),(2,2,[2],[2]),(2,2,[2,3],[2,3]),(3,3,[2,4],[2,4]),(3,4,[2,3,4],[3,4]),(5,2,[2,3,5],[2,3]),(2,5,[2,3],[2,4,6]),(6,6,[2,3,4,5],[3,4,5,6]),(4,4,[5,2,3],[4,2]),(10,3,[2,4,6,8],[2,3,4]),(3,10,[2,3,4],[2,4,6,8]),(7,7,[3,4,5],[5,6,7]),(8,5,[2,3,7,8],[2,3,4,5]),(5,8,[2,4,5,6],[3,4,7,8])]],SQUARE,[SQUARE.replace('best+1','best'),SQUARE.replace('min(span(h_bars),span(v_bars))','max(span(h_bars),span(v_bars))')],['Forgets that removing one bar joins two adjacent unit cells.','Uses the larger directional opening even though a square is limited by the smaller side.'],square_oracle,random_square,lesson('A square side is limited by consecutive removable bars in both directions.','Sort each bar list and find its longest consecutive run, then add one for cell span.','Take the smaller horizontal/vertical span and square it.','Only consecutive removed separators merge adjacent unit cells, and a square must fit in both independent directions, proving the minimum-span bound is attainable.'),'O(h log h+v log v)','O(h+v)',5),
2944:entry('minimum_fruit_coins',[('prices','list[int]')],'int',['dynamic programming','recursion','arrays'],['prices is nonempty and prices[i] is the cost of fruit i+1.','Buying fruit i grants any of the next i fruits for free, but a free-eligible fruit may still be bought for its reward.','Return the minimum coins needed to acquire every fruit.'],[([[3,1,2]],'Buy fruits one and two for four coins; fruit three is then free.'),([[1,10,1,1]],'Buy fruits one and three for two coins, covering the other fruits as rewards.')],[[p] for p in [[1],[5,1],[1,5],[1,1,1],[10,1,10],[3,1,2],[1,10,1,1],[5,4,3,2,1],[1,2,3,4,5],[9,1,9,1,9,1],[26,18,6,12,49,7,45,45],[2,100,2,100,2],[7,3,8,2,9,1],[4,6,1,7,2,8,3]]],FRUITS,[FRUITS.replace('range(position+1,2*position+2)','range(position+1,2*position+1)'),ODD_FRUITS],['Omits the first fruit immediately after the free coverage boundary as a next purchase option.','Always buys odd-positioned fruits instead of optimizing which free-eligible fruits are worth purchasing for later rewards.'],fruits_oracle,random_fruits,lesson('The next paid fruit determines all future choices; free eligibility does not forbid buying it.','Memoize the minimum cost when fruit position is the next required purchase.','Pay its price and choose the next purchase among positions position+1 through 2*position+1; stop when coverage reaches the end.','Every valid strategy has one next paid fruit in exactly that range, and the recurrence enumerates all such choices while memoization preserves the cheapest suffix.'),'O(n^2)','O(n)',5),
2947:entry('count_balanced_divisible_substrings',[('s','str'),('k','int')],'int',['strings','enumeration','number theory'],['s is a nonempty lowercase string and k is positive.','A substring is beautiful when vowel and consonant counts are equal and their product is divisible by k.','Count all nonempty contiguous beautiful substrings.'],[(['baeyh',2],'The substrings baey and aeyh each contain two vowels and two consonants, with product four divisible by two.'),(['abba',1],'The substrings ab, ba, and abba are balanced and automatically divisible by one.')],[[s,k] for s,k in [('a',1),('b',1),('ab',1),('ab',2),('ae',1),('bcdf',1),('abab',1),('abab',2),('aeiou',3),('leetcode',2),('abcde',4),('aabbcc',3),('beautiful',2),('aeiobcdf',4)]],BEAUTIFUL,[BEAUTIFUL.replace(' and vowel_count*consonants%k==0',''),BEAUTIFUL.replace('vowel_count*consonants%k==0','(vowel_count+consonants)%k==0')],['Counts every vowel/consonant-balanced substring without enforcing divisibility by k.','Tests whether substring length is divisible by k instead of the count product.'],beautiful_substrings_oracle,random_beautiful_substrings,lesson('Only running vowel and consonant counts are needed for a fixed start.','Enumerate each start and extend right while updating the vowel count in constant time.','Derive consonants from length and test equality plus product modulo k.','Every substring has one unique start/end pair, so the nested scan tests each exactly once with exact counts.'),'O(n^2)','O(1)',5),
2948:entry('lexicographically_smallest_swappable_array',[('nums','list[int]'),('limit','int')],'list[int]',['sorting','connected components','arrays'],['nums is nonempty and positive; limit is positive.','Values at any indices may swap when their current absolute difference is at most limit, repeatedly.','Return the lexicographically smallest reachable array.'],[([[1,5,3,9,8],2],'Value groups {1,3,5} and {8,9} can each permute, producing [1,3,5,8,9].'),([[1,7,6,18,2,1],3],'Transitive value connectivity lets each component’s smallest values occupy its earliest indices.')],[[n,l] for n,l in [([1],1),([2,1],1),([3,1],1),([3,1],2),([1,1,1],1),([5,4,3,2,1],1),([1,10,2,9],2),([4,1,7,3],3),([1,7,28,19,10],3),([2,8,5,11],3),([10,1,6,3,8],2),([5,5,1,1,3],2),([9,2,7,4,6],2),([1,20,10,11,2],1)]],LEXICAL,[LEXICAL.replace('<=limit','<limit'),LEXICAL.replace('indices=sorted(index for _,index in ordered[left:right])','indices=[index for _,index in ordered[left:right]]')],['Treats value differences equal to limit as disconnected.','Assigns sorted values to component indices in value order instead of earliest array-index order.'],lexical_oracle,random_lexical,lesson('Swap reachability forms components along consecutive gaps in value-sorted order.','Partition sorted (value,index) pairs wherever a gap exceeds limit; within each component assign smallest values to smallest original indices.','Sort pairs, scan components, sort their indices, and zip them with already-sorted component values.','Adjacent value-chain swaps connect every component permutation, while no operation crosses a larger gap; sorted assignment is therefore the lexicographic minimum independently per component.'),'O(n log n)','O(n)',5),
2950:entry('count_phone_divisible_substrings',[('word','str')],'int',['prefix sums','hash maps','strings'],['word is a nonempty lowercase string.','Map ab→1, cde→2, fgh→3, ijk→4, lmn→5, opq→6, rst→7, uvw→8, xyz→9.','Count substrings whose mapped-value sum is divisible by their length.'],[(['asdf'],'The four single letters plus as and sdf give six divisible substrings.'),(['bdh'],'The three single letters and bdh give four.')],[[w] for w in ['a','z','ab','ac','xyz','abcd','phone','leetcode','aaaa','azaz','mnop','rstuvw','algorithm','divisible']],DIVISIBLE,[DIVISIBLE.replace("'ab','cde'","'abc','de'"),DIVISIBLE.replace('range(1,10)','range(1,9)')],['Uses the wrong phone grouping for b and c.','Never checks average mapped value nine, missing all-x/y/z substrings.'],divisible_oracle,random_divisible,lesson('A sum divisible by length has an integer average from one through nine.','For each possible average d, transform each mapped value by subtracting d and count zero-sum substrings with equal prefix balances.','Run nine prefix-frequency passes and add prior occurrences of each balance.','Every divisible substring has one unique integer average, so exactly one pass counts it; equal transformed prefixes characterize that average exactly.'),'O(9n)','O(n)',5),
}
