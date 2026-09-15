"""Divisible suffixes, game scores, square-area cuts, and wildcard matching."""
from itertools import product

from .import_batch_055 import entry


def divisible_oracle(args):
    text=args[0];answer=0
    for left in range(len(text)):
        value=0
        for right in range(left,len(text)):
            value=value*10+int(text[right]);last=int(text[right])
            answer+=last!=0 and value%last==0
    return answer


def random_divisible(rng):return [''.join(str(rng.randrange(10)) for _ in range(rng.randint(1,15)))]


def score_oracle(args):
    points,moves=args;n=len(points);best=0;scores=[0]*n
    def walk(position,remaining):
        nonlocal best
        best=max(best,min(scores))
        if remaining==0:return
        for following in (position-1,position+1):
            if 0<=following<n:
                scores[following]+=points[following];walk(following,remaining-1);scores[following]-=points[following]
    scores[0]+=points[0];walk(0,moves-1);return best


def random_score(rng):
    n=rng.randint(2,5);return [[rng.randint(1,8) for _ in range(n)],rng.randint(1,9)]


def square_rows(squares,unique):
    top=max(y+side for _,y,side in squares);bottom=min(y for _,y,_ in squares);widths=[]
    for row in range(bottom,top):
        if unique:
            cells=set()
            for x,y,side in squares:
                if y<=row<y+side:cells.update(range(x,x+side))
            widths.append(len(cells))
        else:widths.append(sum(side for _,y,side in squares if y<=row<y+side))
    return bottom,widths


def square_cut_oracle(args,unique=False):
    bottom,widths=square_rows(args[0],unique);target=sum(widths)/2;area=0
    for offset,width in enumerate(widths):
        if area+width>=target:return bottom+offset+(target-area)/width
        area+=width
    return float(bottom+len(widths))


def repeated_square_oracle(args):return square_cut_oracle(args,False)
def union_square_oracle(args):return square_cut_oracle(args,True)


def random_squares(rng):
    return [[[rng.randint(0,8),rng.randint(0,8),rng.randint(1,4)] for _ in range(rng.randint(1,6))]]


def pattern_matches(text,pattern):
    first,middle,last=pattern.split('*');n=len(text)
    if not text.startswith(first) or not text.endswith(last):return False
    low=len(first);high=n-len(last)
    return low<=high and text.find(middle,low,high+len(middle))!=-1 and text.find(middle,low,high+len(middle))<=high-len(middle)


def matching_oracle(args):
    text,pattern=args;answer=10**9
    for left in range(len(text)+1):
        for right in range(left,len(text)+1):
            if pattern_matches(text[left:right],pattern):answer=min(answer,right-left)
    return -1 if answer==10**9 else answer


def random_matching(rng):
    text=''.join(rng.choice('abc') for _ in range(rng.randint(1,10)))
    pieces=[''.join(rng.choice('abc') for _ in range(rng.randint(0,3))) for _ in range(3)]
    return [text,'*'.join(pieces)]


DIVISIBLE='''def count_substrings_divisible_by_last_digit(s):
    counts=[None]+[[0]*divisor for divisor in range(1,10)];answer=0
    for char in s:
        digit=int(char)
        for divisor in range(1,10):
            following=[0]*divisor;following[digit%divisor]+=1
            for remainder,amount in enumerate(counts[divisor]):following[(remainder*10+digit)%divisor]+=amount
            counts[divisor]=following
        if digit:answer+=counts[digit][0]
    return answer
'''

SCORE='''def maximize_minimum_game_score(points,m):
    def feasible(target):
        used=carry=0
        for index,value in enumerate(points):
            visits=max(0,(target+value-1)//value-carry)
            used+=(2*visits-1 if visits else 0) if index==len(points)-1 else (2*visits-1 if visits else 1)
            if used>m:return False
            carry=max(0,visits-1)
        return True
    low=0;high=max(points)*m+1
    while low+1<high:
        middle=(low+high)//2
        if feasible(middle):low=middle
        else:high=middle
    return low
'''

REPEATED='''def separate_squares_counting_overlap(squares):
    total=sum(side*side for _,_,side in squares);low=min(y for _,y,_ in squares);high=max(y+side for _,y,side in squares)
    for _ in range(60):
        middle=(low+high)/2;below=sum(side*max(0,min(side,middle-y)) for _,y,side in squares)
        if below*2>=total:high=middle
        else:low=middle
    return high
'''

UNION_MULTIPLE=REPEATED.replace('separate_squares_counting_overlap','separate_squares_unique_overlap')

UNION='''def separate_squares_unique_overlap(squares):
    xs=sorted({value for x,_,side in squares for value in (x,x+side)});index={value:i for i,value in enumerate(xs)};segments=max(0,len(xs)-1)
    cover=[0]*(segments*4+4);length=[0]*(segments*4+4)
    def update(node,left,right,start,end,delta):
        if start<=left and right<=end:cover[node]+=delta
        else:
            middle=(left+right)//2
            if start<=middle:update(node*2,left,middle,start,end,delta)
            if end>middle:update(node*2+1,middle+1,right,start,end,delta)
        if cover[node]:length[node]=xs[right+1]-xs[left]
        elif left==right:length[node]=0
        else:length[node]=length[node*2]+length[node*2+1]
    events=[]
    for x,y,side in squares:events.append((y,x,x+side,1));events.append((y+side,x,x+side,-1))
    events.sort();strips=[];previous=events[0][0];active=0;position=0
    while position<len(events):
        y=events[position][0]
        if y>previous: strips.append((previous,y,active))
        while position<len(events) and events[position][0]==y:
            _,left,right,delta=events[position];update(1,0,segments-1,index[left],index[right]-1,delta);position+=1
        active=length[1];previous=y
    total=sum((top-bottom)*width for bottom,top,width in strips);target=total/2;area=0
    for bottom,top,width in strips:
        strip=(top-bottom)*width
        if area+strip>=target:return bottom+(target-area)/width
        area+=strip
    return float(previous)
'''

MATCHING='''def shortest_two_star_matching_substring(s,p):
    from bisect import bisect_right
    def occurrences(word):
        if not word:return list(range(len(s)+1))
        joined=word+'#'+s;prefix=[0]*len(joined)
        for i in range(1,len(joined)):
            j=prefix[i-1]
            while j and joined[i]!=joined[j]:j=prefix[j-1]
            if joined[i]==joined[j]:j+=1
            prefix[i]=j
        return [i-2*len(word) for i,value in enumerate(prefix) if value==len(word)]
    first,middle,last=p.split('*');starts_first=occurrences(first);starts_middle=occurrences(middle);starts_last=occurrences(last)
    paired_middle=[];best_first=[];current=-1
    for start in starts_middle:
        position=bisect_right(starts_first,start-len(first))-1
        if position>=0:current=max(current,starts_first[position]);paired_middle.append(start);best_first.append(current)
    answer=10**30
    for start in starts_last:
        position=bisect_right(paired_middle,start-len(middle))-1
        if position>=0 and best_first[position]>=0:answer=min(answer,start+len(last)-best_first[position])
    return -1 if answer==10**30 else answer
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


DIVISIBLE_CASES=[[text] for text in ['12936','5701283','1','0','10','12','101','999','123456789','1005','80808','314159','222222','9876543210']]
SCORE_CASES=[[points,moves] for points,moves in [([2,4],3),([1,2,3],5),([5,2],1),([5,2],6),([1,1],1),([1,1],2),([1,1],3),([3,1,2],7),([10,2],5),([2,5,1,4],8),([7,3,9],9),([1,10,1],6),([4,4,4,4],7),([2,3,5,7,11],9)]]
SQUARE_CASES=[[[row[:] for row in squares]] for squares in [[[0,0,1],[2,2,1]],[[0,0,2]],[[0,0,1],[0,0,1]],[[0,0,2],[1,1,2]],[[2,3,4],[8,1,2]],[[0,0,3],[0,3,1]],[[1,1,2],[4,1,2]],[[0,5,2],[1,0,3]],[[3,2,1],[3,3,1],[3,4,1]],[[0,0,4],[1,1,1]],[[5,0,2],[0,2,2]],[[0,0,1],[1,0,1],[2,0,1]],[[2,2,3],[3,0,2],[0,4,1]],[[10,10,5],[0,0,2]]]]
MATCH_CASES=[[text,pattern] for text,pattern in [('abaacbaecebce','ba*c*ce'),('abc','**'),('abc','a**c'),('abc','*b*'),('aaaa','a*a*a'),('mississippi','mi*ss*pi'),('abc','d**'),('cabba','c*b*a'),('xyzxyz','x*z*z'),('ababab','ab**ab'),('leetcode','lee*c*de'),('aaaaab','*aa*b'),('abcabc','a*bc*c'),('bbbb','b**b')]]


BATCH={
3448:entry('count_substrings_divisible_by_last_digit',[('s','str')],'int',['strings','dynamic programming','modular arithmetic'],['s has 1–100,000 decimal digits and substrings may have leading zeros.','A substring qualifies only when its final digit is nonzero.','Count substrings whose integer value is divisible by that final digit.'],[(['12936'],'Tracking every ending position gives eleven qualifying substrings.'),(['10'],'The substring 1 qualifies; substrings ending in zero are excluded, so the answer is one.')],DIVISIBLE_CASES,DIVISIBLE,[DIVISIBLE.replace('if digit:answer+=counts[digit][0]','answer+=counts[1][0]'),DIVISIBLE.replace('following[digit%divisor]+=1','')],['Tests every suffix for divisibility by one instead of its actual last digit.','Omits the new one-character substring at each ending position.'],divisible_oracle,random_divisible,lesson('Only remainders modulo digits one through nine are needed for future divisibility checks.','Maintain remainder counts for all substrings ending at the previous position under each possible modulus.','Append the new digit to every remainder, add the one-digit substring, then read remainder zero for the nonzero last digit.','The transition represents every substring ending here exactly once, and its selected modulus equals its final digit.'),'O(45*n)','O(45)',8),
3449:entry('maximize_minimum_game_score',[('points','list[int]'),('m','int')],'int',['arrays','binary search','greedy'],['points contains 2–50,000 positive values and m is a positive move limit.','Start immediately before index zero; each move goes to an adjacent in-bounds index and adds that index’s points to its score.','Using at most m moves, maximize the minimum score across all indices.'],[([[2,4],3],'The walk 0,1,0 produces scores four and four, so the optimal minimum is four.'),([[1,1],2],'Two moves visit each index once, so the minimum score is one.')],SCORE_CASES,SCORE,[SCORE.replace('2*visits-1 if visits else 1','2*visits if visits else 1'),SCORE.replace('carry=max(0,visits-1)','carry=visits')],['Charges one extra move for every interior visit requirement and rejects feasible targets.','Credits the next index with one too many visits from bouncing.'],score_oracle,random_score,lesson('Feasibility of reaching a target minimum is monotone, enabling binary search.','Sweep left to right, greedily add the visits still needed after credits from prior back-and-forth moves.','At an interior index, each added visit costs a round trip except the final step onward; carry the induced visits to the next index.','Delaying a missing visit cannot help once an index is left, so the minimum-move greedy count exactly characterizes feasibility.'),'O(n log(max(points)*m))','O(1)',8),
3453:entry('separate_squares_counting_overlap',[('squares','list[list[int]]')],'float',['arrays','binary search','geometry'],['Each square is [x,y,side] with positive integer side length.','Overlapping regions count once for every square covering them.','Return the smallest horizontal y-coordinate with equal total area above and below; absolute error up to 0.00001 is accepted.'],[([[[0,0,1],[2,2,1]]],'One unit square lies below y=1 and the other lies above it, so the minimum balanced coordinate is one.'),([[[0,0,2]]],'A horizontal line through y=1 bisects the square.')],SQUARE_CASES,REPEATED,[REPEATED.replace('side*max(0,min(side,middle-y))','side*max(0,middle-y)'),REPEATED.replace('below*2>=total','below*2>total')],['Does not cap a square’s below-line height at its side length.','Uses a strict comparison and can move past the smallest coordinate on a flat balanced interval.'],repeated_square_oracle,random_squares,lesson('For any y, each square contributes side times its clipped height below the line.','Binary-search the first coordinate whose accumulated below-area reaches half the total multiplicity-counted area.','Sum clipped rectangle areas at the midpoint and move the upper bound when twice the below-area is at least the total.','Below-area is continuous and nondecreasing; lower-bound binary search converges to the smallest balancing coordinate.'),'O(n log(range/epsilon))','O(1)',6),
3454:entry('separate_squares_unique_overlap',[('squares','list[list[int]]')],'float',['geometry','sweep line','segment trees'],['Each square is [x,y,side] with positive integer side length.','The union area counts overlapping regions only once.','Return the smallest horizontal y-coordinate bisecting the union area; absolute error up to 0.00001 is accepted.'],[([[[0,0,1],[2,2,1]]],'The two disjoint unit squares balance at the beginning of the empty strip y=1.'),([[[0,0,2],[1,1,2]]],'A sweep tracks the union width of the overlapping squares rather than adding their widths twice.')],SQUARE_CASES,UNION,[UNION_MULTIPLE,UNION.replace('target=total/2','target=sum((top-bottom)*width for bottom,top,width in strips)/3')],['Adds every square area independently and double-counts overlaps.','Cuts at one third of the union area instead of one half.'],union_square_oracle,random_squares,lesson('Between consecutive horizontal square edges, the union width is constant.','Sweep y-events while a compressed segment tree maintains the covered x-length, then locate half the accumulated strip area.','Add the prior width times the y-gap before applying each event group; store strips, total them, and interpolate inside the crossing strip.','The strips partition the union by y, and the segment tree counts every covered x-coordinate once regardless of overlap depth.'),'O(n log n)','O(n)',8),
3455:entry('shortest_two_star_matching_substring',[('s','str'),('p','str')],'int',['strings','two pointers','string matching'],['s has up to 100,000 lowercase letters and p contains exactly two asterisks.','Each asterisk matches any sequence, including empty; the other characters are literal.','Return the shortest substring matching the entire pattern, or -1 if none exists; the empty substring is valid.'],[(['abaacbaecebce','ba*c*ce'],'The shortest ordered occurrence of the three literal pieces spans eight characters.'),(['abc','**'],'Both stars may match empty, so the empty substring has length zero.')],MATCH_CASES,MATCHING,[MATCHING.replace('start-len(first)','start'),MATCHING.replace('start-len(middle)','start')],['Allows the first literal piece to overlap the middle piece.','Allows the middle literal piece to overlap the final piece.'],matching_oracle,random_matching,lesson('Split the pattern into three literal pieces that must occur in order without overlap.','Find every piece occurrence with KMP, then link each middle occurrence to the latest valid first and each final occurrence to the best eligible pair.','Use binary search in sorted occurrence lists and prefix maxima of first starts; minimize final end minus first start.','For a fixed later endpoint, the latest compatible earlier start always gives the shortest span, including empty-piece boundary occurrences.'),'O(n+len(p)+matches*log n)','O(n)',8),
}

BATCH[3453]['comparator']='float'
BATCH[3454]['comparator']='float'
