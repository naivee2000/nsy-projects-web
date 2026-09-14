"""Monotonic runs, string score, wildcard time, special letters, and 2x2 colors."""
from .import_batch_055 import entry

def monotonic_oracle(a):
    nums=a[0];best=1
    for left in range(len(nums)):
        for right in range(left+1,len(nums)):
            segment=nums[left:right+1]
            if all(x<y for x,y in zip(segment,segment[1:])) or all(x>y for x,y in zip(segment,segment[1:])):best=max(best,len(segment))
    return best
def random_monotonic(r):return [[r.randint(1,100) for _ in range(r.randint(1,40))]]
def score_oracle(a):return sum(abs(ord(x)-ord(y)) for x,y in zip(a[0],a[0][1:]))
def random_score(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(2,100)))]
def time_oracle(a):
    pattern=a[0];valid=[]
    for hour in range(12):
        for minute in range(60):
            value=f'{hour:02d}:{minute:02d}'
            if all(p=='?' or p==v for p,v in zip(pattern,value)):valid.append(value)
    return max(valid)
def random_time(r):
    value=f'{r.randrange(12):02d}:{r.randrange(60):02d}';return [''.join(c if i==2 else '?' if r.random()<.5 else c for i,c in enumerate(value))]
def special_oracle(a):return sum(chr(code) in a[0] and chr(code).upper() in a[0] for code in range(ord('a'),ord('z')+1))
def random_special(r):return [''.join(r.choice('abcdeABCDE') for _ in range(r.randint(1,80)))]
def square_oracle(a):
    grid=a[0]
    return any(sum(grid[r+i][c+j]=='B' for i in range(2) for j in range(2))!=2 for r in range(2) for c in range(2))
def random_square(r):return [[[r.choice('BW') for _ in range(3)] for _ in range(3)]]

MONOTONIC='''\
def longest_strict_monotonic_subarray(nums):
    increasing=decreasing=answer=1
    for previous,current in zip(nums,nums[1:]):
        increasing=increasing+1 if previous<current else 1
        decreasing=decreasing+1 if previous>current else 1
        answer=max(answer,increasing,decreasing)
    return answer
'''
SCORE='''\
def adjacent_character_score(s):
    return sum(abs(ord(a)-ord(b)) for a,b in zip(s,s[1:]))
'''
TIME='''\
def latest_twelve_hour_time(s):
    chars=list(s)
    if chars[0]=='?':chars[0]='1' if chars[1] in '?01' else '0'
    if chars[1]=='?':chars[1]='1' if chars[0]=='1' else '9'
    if chars[3]=='?':chars[3]='5'
    if chars[4]=='?':chars[4]='9'
    return ''.join(chars)
'''
SPECIAL='''\
def count_case_pair_letters(word):
    present=set(word)
    return sum(char in present and char.upper() in present for char in 'abcdefghijklmnopqrstuvwxyz')
'''
SQUARE='''\
def can_make_monochrome_two_by_two(grid):
    for row in range(2):
        for column in range(2):
            black=sum(grid[row+i][column+j]=='B' for i in range(2) for j in range(2))
            if black!=2:return True
    return False
'''

BATCH={
3105:entry('longest_strict_monotonic_subarray',[('nums','list[int]')],'int',['arrays','dynamic programming'],['A qualifying subarray is either strictly increasing throughout or strictly decreasing throughout.','Equal adjacent values break both kinds of run.','Return the greatest qualifying contiguous length.'],[([[1,4,3,3,2]],'The best strict run has length two; the equal threes prevent a longer run.'),([[3,2,1]],'The whole array is strictly decreasing, so return three.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[1,4,3,3,2],[3,2,1],[1,2,3],[1,3,2,1],[3,1,2,3],[1,2,2,3],[5,4,3,4,5],[2,2,2],[1,5,4,3,2],[9,7,5,3,1]]],MONOTONIC,[MONOTONIC.replace('previous<current','previous<=current'),MONOTONIC.replace('decreasing+1','increasing+1')],['Allows equal values in an increasing run.','Extends decreasing runs from the unrelated increasing length.'],monotonic_oracle,random_monotonic,['Track the strict increasing and decreasing run lengths ending at the current element.','Extend a run only when its corresponding adjacent comparison holds; otherwise reset it to one.','Take the maximum of both states over the scan.','Each recurrence gives the unique longest run of its direction ending at that index, so their global maximum is exact.'],'O(n)','O(1)',3),
3110:entry('adjacent_character_score',[('s','str')],'int',['strings','simulation'],['For every adjacent character pair, take the absolute difference of their Unicode code points.','Add those differences across the string.','Return the resulting score.'],[(['hello'],'The adjacent differences 3,7,0,3 sum to thirteen.'),(['zaz'],'The two differences are both twenty-five, totaling fifty.')],[[s] for s in ['aa','ab','ba','hello','zaz','abc','cba','az','za','code','practice','aaaa','abcdz','xyyx']],SCORE,[SCORE.replace('abs(ord(a)-ord(b))','ord(a)-ord(b)'),SCORE.replace('s[1:]','s[2:]')],['Omits absolute value, allowing signed differences to cancel.','Pairs each character with one two positions later instead of its neighbor.'],score_oracle,random_score,['Adjacent pairs are obtained by zipping the string with its one-position suffix.','Convert each character to its code point.','Add the absolute difference for every pair.','The zip enumerates each adjacent boundary once, exactly matching the score definition.'],'O(n)','O(1)',3),
3114:entry('latest_twelve_hour_time',[('s','str')],'str',['strings','greedy'],['Replace each ? independently with a decimal digit.','The result must be a valid 12-hour time from 00:00 through 11:59.','Return the latest possible matching time.'],[(['1?:?4'],'The latest valid choices make 11:54.'),(['0?:5?'],'The latest hour matching 0? is 09 and the latest minute matching 5? is 59.')],[[s] for s in ['??:??','1?:?4','0?:5?','?1:??','?2:??','??:00','00:??','11:59','10:?9','?9:?0','0?:??','1?:59','??:5?','?0:0?']],TIME,[TIME.replace("chars[0]='1' if chars[1] in '?01' else '0'","chars[0]='1'"),TIME.replace("chars[3]='5'","chars[3]='9'")],['Chooses hour tens one even when the fixed ones digit would make an invalid hour.','Allows minute tens nine rather than at most five.'],time_oracle,random_time,['Choose digits from most significant to least significant.','Hour tens is one only when hour ones can be zero or one; then maximize hour ones under that choice.','Minute tens and ones independently maximize to five and nine.','Greedy digit choice is valid because lexicographic HH:MM order equals chronological order within one 12-hour cycle.'],'O(1)','O(1)',3),
3120:entry('count_case_pair_letters',[('word','str')],'int',['strings','sets'],['A letter is special when both its lowercase and uppercase forms occur somewhere in word.','Order and multiplicity do not matter.','Return the number of distinct special letters.'],[(['aaAbcBC'],'Letters a, b, and c appear in both cases, so the result is three.'),(['abc'],'No uppercase form appears, so the result is zero.')],[[s] for s in ['a','A','aA','aaAbcBC','abc','ABC','AbBCab','zZ','aAbB','xYzZ','mnopMN','sameS','AaAa','qQrRss']],SPECIAL,[SPECIAL.replace('and char.upper() in present','or char.upper() in present'),SPECIAL.replace("'abcdefghijklmnopqrstuvwxyz'","word")],['Counts a letter when only one case appears.','Counts occurrences from the input rather than distinct alphabet letters.'],special_oracle,random_special,['A set removes multiplicity while retaining presence.','Iterate each lowercase alphabet letter once.','Count it only if both that character and its uppercase form belong to the set.','This visits every possible letter identity once and applies exactly the two-presence condition.'],'O(n)','O(alphabet)',3),
3127:entry('can_make_monochrome_two_by_two',[('grid','list[list[str]]')],'bool',['matrices','enumeration'],['The grid is exactly three by three and every cell is B or W.','You may recolor at most one cell.','Return whether some two-by-two subgrid can be made a single color.'],[([[['B','W','B'],['B','W','W'],['B','W','B']]],'The lower-right two-by-two block contains three W cells and can be completed with one change.'),([[['B','W','B'],['W','B','W'],['B','W','B']]],'Every two-by-two block is evenly split, so one recoloring cannot make it uniform.')],[[g] for g in [[['B','B','B'],['B','B','B'],['B','B','B']],[['W','W','W'],['W','W','W'],['W','W','W']],[['B','W','B'],['W','B','W'],['B','W','B']],[['B','W','B'],['B','W','W'],['B','W','B']],[['B','B','W'],['B','W','W'],['W','W','W']],[['B','W','W'],['W','W','B'],['B','B','W']],[['W','B','W'],['B','B','W'],['W','W','B']],[['B','B','B'],['W','W','W'],['B','B','B']],[['B','W','B'],['B','B','W'],['W','W','W']],[['W','W','B'],['W','B','B'],['B','B','W']],[['B','W','W'],['B','W','B'],['W','B','W']],[['W','B','B'],['B','W','W'],['W','B','B']],[['B','B','W'],['W','B','W'],['W','W','B']],[['W','B','W'],['W','W','B'],['B','B','B']]]],SQUARE,[SQUARE.replace('black!=2','black==4'),SQUARE.replace('range(2)','range(1)',1)],['Accepts only already-all-black blocks and misses one-change cases.','Checks only the top row of candidate block positions.'],square_oracle,random_square,['A two-by-two block has four cells.','With at most one recoloring it can be uniform exactly when one color occupies at least three cells.','Count black cells in each of the four blocks; every count except two meets that condition.','Checking all block origins exhausts the possible target squares.'],'O(1)','O(1)',3),
}
BATCH[3127]['boundaries'].append([[['B','W','B'],['W','B','W'],['W','W','B']]])
