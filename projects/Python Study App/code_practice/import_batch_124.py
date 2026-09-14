"""First slice of workbook batch 124."""

from itertools import combinations

from .import_batch_055 import entry


def triangular_oracle(args):
    row = tuple(args[0])
    while len(row) > 1:
        row = tuple((left + right) % 10 for left, right in zip(row, row[1:]))
    return row[0]


def random_triangular(rng):
    return [[rng.randrange(10) for _ in range(rng.randint(1, 16))]]


def buildings_oracle(args):
    text = args[0]
    return sum(text[a] == text[c] != text[b] for a, b, c in combinations(range(len(text)), 3))


def random_buildings(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(3, 18)))]


def scores_oracle(args):
    text = args[0]
    total = 0
    for start in range(len(text)):
        matched = 0
        while start + matched < len(text) and text[matched] == text[start + matched]:
            matched += 1
        total += matched
    return total


def random_scores(rng):
    return ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 35)))]


def time_oracle(args):
    current, correct = args
    def minutes(value):
        hour, minute = map(int, value.split(":"))
        return hour * 60 + minute
    remaining = minutes(correct) - minutes(current)
    dp = [0] + [10**9] * remaining
    for value in range(1, remaining + 1):
        dp[value] = 1 + min(dp[value - step] for step in (1, 5, 15, 60) if step <= value)
    return dp[remaining]


def random_time(rng):
    start = rng.randint(0, 1439)
    end = rng.randint(start, 1439)
    encode = lambda value: f"{value // 60:02d}:{value % 60:02d}"
    return [encode(start), encode(end)]


def players_oracle(args):
    played = set()
    losses = {}
    for winner, loser in args[0]:
        played.update((winner, loser))
        losses[loser] = losses.get(loser, 0) + 1
    return [sorted(player for player in played if losses.get(player, 0) == 0),
            sorted(player for player in played if losses.get(player, 0) == 1)]


def random_players(rng):
    size = rng.randint(2, 10)
    players = list(range(1, size + 1))
    possible = [(winner, loser) for winner in players for loser in players if winner != loser]
    rng.shuffle(possible)
    return [[list(match) for match in possible[:rng.randint(1, min(20, len(possible)))]]]


TRIANGULAR = '''\
def triangular_array_sum(nums):
    values=list(nums)
    while len(values)>1:
        values=[(values[index]+values[index+1])%10 for index in range(len(values)-1)]
    return values[0]
'''

BUILDINGS = '''\
def count_alternating_building_selections(s):
    total_zeros=s.count('0');total_ones=len(s)-total_zeros
    left_zeros=left_ones=answer=0
    for char in s:
        if char=='0':
            answer+=left_ones*(total_ones-left_ones)
            left_zeros+=1
        else:
            answer+=left_zeros*(total_zeros-left_zeros)
            left_ones+=1
    return answer
'''

SCORES = '''\
def sum_built_string_scores(s):
    n=len(s);z=[0]*n;left=right=0
    for index in range(1,n):
        if index<=right:z[index]=min(right-index+1,z[index-left])
        while index+z[index]<n and s[z[index]]==s[index+z[index]]:z[index]+=1
        if index+z[index]-1>right:left,right=index,index+z[index]-1
    return n+sum(z)
'''

TIME = '''\
def minimum_time_conversion_operations(current,correct):
    def minutes(value):
        hour,minute=map(int,value.split(':'))
        return hour*60+minute
    remaining=minutes(correct)-minutes(current);operations=0
    for step in (60,15,5,1):
        used,remaining=divmod(remaining,step);operations+=used
    return operations
'''

PLAYERS = '''\
def players_with_zero_or_one_loss(matches):
    from collections import Counter
    players=set();losses=Counter()
    for winner,loser in matches:
        players.update((winner,loser));losses[loser]+=1
    return [sorted(player for player in players if losses[player]==0),sorted(player for player in players if losses[player]==1)]
'''


BATCH = {
    2221: entry('triangular_array_sum',[('nums','list[int]')],'int',['arrays','simulation'],['Every input value is a digit from zero through nine.','Replace the current row by adjacent pair sums modulo ten.','Repeat until one digit remains, and return that digit.'],[([[1,2,3,4,5]],'The rows become [3,5,7,9], [8,2,6], [0,8], then [8].'),([[5]],'A one-element row is already reduced, so its triangular sum is five.')],[[x] for x in [[0],[9],[1,2],[9,9],[1,2,3],[1,2,3,4,5],[5],[0,0,0,0],[9,8,7,6],[3,1,4,1,5],[2,7,1,8,2,8],[5,5,5,5,5],[0,9,0,9,0,9],[1,0,0,0,1]]],TRIANGULAR,[TRIANGULAR.replace('%10','%9'),TRIANGULAR.replace('range(len(values)-1)','range(len(values)-2)')],['Reduces pair sums modulo nine instead of ten.','Drops the final adjacent pair at every reduction step.'],triangular_oracle,random_triangular,['Each round is a direct simulation of the definition.','Keep only the current row; the prior row is unnecessary after producing all adjacent sums.','While the row has more than one value, replace it with pair sums modulo ten.','Every loop produces exactly the next defined row and decreases its length by one, so termination returns the required final digit.'],'O(n^2)','O(n)',5),
    2222: entry('count_alternating_building_selections',[('s','str')],'int',['strings','prefix sums','dynamic programming'],['Choose exactly three indices in strictly increasing order.','The selected types must be 010 or 101; adjacency in the original street is not required.','Return the number of index triples, counting equal type patterns at different positions separately.'],[(['001101'],'Four selections form 010 and two form 101, giving six valid triples.'),(['11100'],'There is no zero between two ones and no one between two zeros, so the result is zero.')],[[x] for x in ['010','101','000','111','001101','11100','0101','1010','00100','11011','0001000','1110111','010101','100001','011110','0010110']],BUILDINGS,[BUILDINGS.replace('left_ones*(total_ones-left_ones)','left_ones*(total_zeros-left_zeros)'),BUILDINGS.replace("if char=='0'","if char=='1'",1)],['Uses remaining zeros instead of remaining ones around a zero center.','Treats a one as the center of a 101 pattern and corrupts both prefix counters.'],buildings_oracle,random_buildings,['Every valid triple is determined by its middle building.','For a zero center, multiply ones before it by ones after it; do the symmetric calculation for a one center.','Track left counts during one scan and derive right counts from global totals.','Each valid triple has one unique middle index, so summing the independent choices on its two sides counts every valid selection exactly once.'],'O(n)','O(1)',6),
    2223: entry('sum_built_string_scores',[('s','str')],'int',['strings','string matching','z algorithm'],['For each suffix s[i:], its score is the longest prefix it shares with the full string.','Include the full string itself, whose score is len(s).','Return the sum of all suffix scores.'],[(['babab'],'The suffix scores are 5,0,3,0,1, which sum to nine.'),(['azbazbzaz'],'Only suffix starts zero, three, and seven contribute scores 9,3,2, totaling fourteen.')],[[x] for x in ['a','aa','ab','babab','azbazbzaz','aaaaa','abcde','ababab','aabaaab','mississippi','banana','abcabcabc','abacaba','zzxyzzxy','abcdabc','aaaabaaa']],SCORES,[SCORES.replace('return n+sum(z)','return sum(z)'),SCORES.replace('s[z[index]]','s[0]')],['Omits the full string score, which is not stored in z[0].','Compares every extension to only the first character instead of the corresponding prefix position.'],scores_oracle,random_scores,['The desired suffix-prefix match lengths are precisely the Z-array values.','Maintain the rightmost known matching interval and reuse its earlier Z values before extending by direct comparisons.','Compute z[1:] with the standard [left,right] window, then return len(s)+sum(z).','The Z invariant records the longest prefix match at every suffix start; adding all entries and the full-string length is exactly the requested score sum.'],'O(n)','O(n)',8),
    2224: entry('minimum_time_conversion_operations',[('current','str'),('correct','str')],'int',['strings','greedy'],['Both times use 24-hour HH:MM format and current is not later than correct.','One operation adds exactly 1, 5, 15, or 60 minutes.','Return the fewest additions needed; the interval never wraps past midnight.'],[(['02:30','04:35'],'Two sixty-minute additions and one five-minute addition use three operations.'),(['11:00','11:01'],'A single one-minute addition reaches the target.')],[[a,b] for a,b in [('00:00','00:00'),('00:00','00:01'),('02:30','04:35'),('11:00','11:01'),('00:00','01:00'),('12:00','12:15'),('12:00','12:05'),('12:00','12:59'),('23:00','23:59'),('01:17','08:42'),('05:55','06:00'),('10:10','10:26'),('00:01','23:59'),('18:44','19:44')]],TIME,[TIME.replace('(60,15,5,1)','(60,5,15,1)'),TIME.replace('operations+=used','operations+=1 if used else 0')],['Uses denominations out of descending order, so greedy consumes fives before fifteens.','Counts each denomination at most once even when several equal additions are required.'],time_oracle,random_time,['Convert each clock string to minutes after midnight and take the nonnegative difference.','Always consume the largest allowed increment that fits the remaining difference.','For steps 60,15,5,1, use divmod and add each quotient to the operation count.','Each larger increment equals an integer number of smaller increments but costs only one operation, so replacing smaller groups proves descending greedy is optimal.'],'O(1)','O(1)',3),
    2225: entry('players_with_zero_or_one_loss',[('matches','list[list[int]]')],'list[list[int]]',['arrays','hash maps','sorting'],['Each match is [winner,loser], and every listed player has played at least once.','The first result row contains players with zero losses; the second contains players with exactly one.','Sort both rows in increasing order and omit players with two or more losses.'],[([[[1,3],[2,3],[3,6],[5,6],[5,7],[4,5],[4,8],[4,9],[10,4],[10,9]]],'Players 1,2,10 have zero losses, while 4,5,7,8 have exactly one.'),([[[2,3],[1,3],[5,4],[6,4]]],'Players 1,2,5,6 never lose; players 3 and 4 lose twice, so the second row is empty.')],[[m] for m in [[[1,2]],[[1,2],[2,3]],[[1,3],[2,3]],[[1,2],[3,2],[2,4]],[[1,3],[2,3],[3,6],[5,6],[5,7],[4,5],[4,8],[4,9],[10,4],[10,9]],[[2,3],[1,3],[5,4],[6,4]],[[10,20],[20,10]],[[1,2],[1,3],[1,4]],[[2,1],[3,1],[4,1]],[[5,6],[7,8]],[[1,2],[2,1],[3,1]],[[4,5],[5,6],[6,7],[7,8]],[[9,1],[9,2],[1,2]],[[100,200],[300,200],[200,400]]]],PLAYERS,[PLAYERS.replace('losses[player]==1','losses[player]<=1'),PLAYERS.replace('players.update((winner,loser))','players.add(loser)')],['Includes undefeated players again in the exactly-one-loss row.','Tracks only losers, omitting winners who never lose.'],players_oracle,random_players,['Count losses while collecting every player appearing as either winner or loser.','Players absent from the loss counter have zero losses; a count of one selects the second group.','Filter the player set by loss count and sort each resulting row.','Every played participant enters the set, every loss is counted once, and the two exact count predicates match the requested categories.'],'O(m+p log p)','O(p)',5),
}
