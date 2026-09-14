"""Bit clearing, digit game, player frequencies, grid snake, and binary k-constraint batch."""
from collections import Counter
from .import_batch_055 import entry

def changes_oracle(a):
    n,k=a
    if n&k!=k:return -1
    return (n^k).bit_count()
def random_changes(r):return [r.randint(1,1000),r.randint(1,1000)]
def digit_game_oracle(a):
    small=sum(x for x in a[0] if x<10);large=sum(x for x in a[0] if x>=10)
    return small!=large
def random_digit_game(r):return [[r.randint(1,99) for _ in range(r.randint(1,30))]]
def winners_oracle(a):
    n,picks=a;counts=[Counter() for _ in range(n)]
    for player,color in picks:counts[player][color]+=1
    return sum(any(count>player for count in counts[player].values()) for player in range(n))
def random_winners(r):
    n=r.randint(1,15);return [n,[[r.randrange(n),r.randint(0,10)] for _ in range(r.randint(0,80))]]
def snake_oracle(a):
    n,commands=a;row=column=0
    for command in commands:
        if command=='UP':row-=1
        elif command=='DOWN':row+=1
        elif command=='LEFT':column-=1
        else:column+=1
    return row*n+column
def random_snake(r):
    n=r.randint(2,10);row=column=0;commands=[]
    for _ in range(r.randint(1,30)):
        choices=[]
        if row:choices.append('UP')
        if row+1<n:choices.append('DOWN')
        if column:choices.append('LEFT')
        if column+1<n:choices.append('RIGHT')
        command=r.choice(choices);commands.append(command)
        row+=command=='DOWN';row-=command=='UP';column+=command=='RIGHT';column-=command=='LEFT'
    return [n,commands]
def constraint_oracle(a):
    s,k=a;answer=0
    for left in range(len(s)):
        zero=one=0
        for right in range(left,len(s)):
            zero+=s[right]=='0';one+=s[right]=='1';answer+=zero<=k or one<=k
    return answer
def random_constraint(r):return [''.join(r.choice('01') for _ in range(r.randint(1,40))),r.randint(0,10)]

CHANGES='''\
def minimum_one_to_zero_bit_changes(n,k):
    if n&k!=k:return -1
    return (n^k).bit_count()
'''
DIGIT_GAME='''\
def can_alice_win_digit_group_game(nums):
    single=sum(value for value in nums if value<10)
    double=sum(value for value in nums if value>=10)
    return single!=double
'''
WINNERS='''\
def count_winning_players(n,pick):
    from collections import Counter
    counts=[Counter() for _ in range(n)]
    for player,color in pick:counts[player][color]+=1
    return sum(any(amount>player for amount in counts[player].values()) for player in range(n))
'''
SNAKE='''\
def final_snake_matrix_position(n,commands):
    position=0
    for command in commands:
        if command=='UP':position-=n
        elif command=='DOWN':position+=n
        elif command=='LEFT':position-=1
        else:position+=1
    return position
'''
CONSTRAINT='''\
def count_binary_k_constraint_substrings(s,k):
    answer=0
    for left in range(len(s)):
        zeros=ones=0
        for right in range(left,len(s)):
            zeros+=s[right]=='0';ones+=s[right]=='1'
            if zeros<=k or ones<=k:answer+=1
    return answer
'''

BATCH={
3226:entry('minimum_one_to_zero_bit_changes',[('n','int'),('k','int')],'int',['bit manipulation'],['In one operation, change a set bit of n from one to zero.','Bits cannot change from zero to one.','Return the minimum operations needed to reach k, or -1 if impossible.'],[([13,4],'Binary 1101 becomes 0100 by clearing two set bits.'),([21,21],'The values already match, so zero changes are needed.')],[[n,k] for n,k in [(1,1),(1,0),(2,1),(13,4),(21,21),(7,3),(8,0),(8,4),(15,8),(10,2),(5,6),(100,4),(31,1),(16,15)]],CHANGES,[CHANGES.replace('n&k!=k','n&k==k'),CHANGES.replace('(n^k).bit_count()','(n|k).bit_count()')],['Rejects possible transformations and allows impossible ones.','Counts all set bits in the union instead of only bits that must be cleared.'],changes_oracle,random_changes,['Every one bit required by k must already be set in n.','Test this subset condition with n&k==k.','When possible, differing bits are precisely extra one bits of n; count them in n XOR k.','Each extra bit requires one operation independently, proving the count minimal.'],'O(bits)','O(1)',3),
3232:entry('can_alice_win_digit_group_game',[('nums','list[int]')],'bool',['arrays','greedy','sums'],['Alice chooses either all one-digit values or all two-digit values.','She wins when her chosen sum is strictly greater than the sum left for Bob.','Return whether Alice has a winning choice.'],[([[1,2,3,4,10]],'The one-digit sum and two-digit sum both equal ten, so neither choice wins.'),([[1,2,3,4,5,14]],'One-digit values total fifteen, which exceeds fourteen.')],[[x] for x in [[1],[10],[1,9],[1,10],[1,2,3,4,10],[1,2,3,4,5,14],[9,9,18],[5,5,10],[1,99],[8,8,8,20],[10,20,30],[1,2,30],[9,10,11],[3,7,20]]],DIGIT_GAME,[DIGIT_GAME.replace('single!=double','single>double'),DIGIT_GAME.replace('value<10','value<=10')],['Considers only choosing one-digit numbers and misses a winning two-digit group.','Incorrectly classifies ten as a one-digit value.'],digit_game_oracle,random_digit_game,['The two allowed choices partition nums into one-digit and two-digit groups.','Compute both group sums.','Alice can choose the larger group, so she loses only when the sums are equal.','If unequal, the larger group strictly beats the remainder; if equal, neither choice does.'],'O(n)','O(1)',3),
3238:entry('count_winning_players',[('n','int'),('pick','list[list[int]]')],'int',['arrays','hash maps','counting'],['Each pick entry [player,color] records one ball of that color obtained by the player.','Player i wins when some color count is strictly greater than i.','Return the number of winning players.'],[([4,[[0,0],[1,0],[1,0],[2,1],[2,1],[2,0]]],'Player zero wins with one ball and player one with two matching balls; player two lacks three matching balls.'),([5,[[1,1],[1,2],[1,3],[1,4]]],'Player one has no color twice, so no player wins.')],[[n,p] for n,p in [(1,[]),(1,[[0,0]]),(2,[[1,0],[1,0]]),(2,[[1,0]]),(4,[[0,0],[1,0],[1,0],[2,1],[2,1],[2,0]]),(5,[[1,1],[1,2],[1,3],[1,4]]),(3,[[2,1],[2,1],[2,1]]),(3,[[0,5]]),(4,[[3,1]]*4),(4,[[3,1]]*3),(2,[[0,0],[1,1],[1,1]]),(5,[[4,2]]*5),(3,[[1,2],[1,2],[2,3]]),(6,[[5,0]]*6)]],WINNERS,[WINNERS.replace('amount>player','amount>=player'),WINNERS.replace('counts[player][color]+=1','counts[player][player]+=1')],['Uses at least i rather than strictly more than i, especially misclassifying player zero without a ball.','Counts all colors together under the player ID instead of separately by color.'],winners_oracle,random_winners,['Maintain a color frequency table for each player.','After all picks, inspect whether any frequency for player i exceeds i.','Count players satisfying that existential condition.','The tables preserve exactly the per-player per-color totals used by the win rule.'],'O(n+picks)','O(picks)',3),
3248:entry('final_snake_matrix_position',[('n','int'),('commands','list[str]')],'int',['matrices','simulation'],['A snake begins at cell [0,0] of an n by n matrix.','Apply valid commands UP, DOWN, LEFT, and RIGHT.','Return the final cell index row*n+column.'],[([2,['RIGHT','DOWN']],'The snake finishes at row one, column one, whose flattened index is three.'),([3,['DOWN','RIGHT','UP']],'The final cell is row zero, column one, index one.')],[[n,c] for n,c in [(2,['RIGHT']),(2,['DOWN']),(2,['RIGHT','DOWN']),(3,['DOWN','RIGHT','UP']),(3,['DOWN','DOWN']),(3,['RIGHT','RIGHT']),(4,['DOWN','RIGHT','DOWN']),(4,['RIGHT','DOWN','LEFT']),(5,['DOWN']*4),(5,['RIGHT']*4),(3,['DOWN','RIGHT','LEFT','UP']),(4,['DOWN','DOWN','RIGHT','UP']),(2,['DOWN','RIGHT','UP','LEFT']),(5,['RIGHT','DOWN','DOWN','LEFT'])]],SNAKE,[SNAKE.replace("position-=n","position-=1"),SNAKE.replace("position+=1","position+=n")],['Moves UP by one flattened cell instead of one row.','Moves RIGHT by an entire row width.'],snake_oracle,random_snake,['Flattening maps a vertical move to plus or minus n and a horizontal move to plus or minus one.','Maintain the flattened position directly.','Apply the corresponding offset for each valid command.','Because commands never leave the grid, these offsets exactly mirror the two-dimensional moves.'],'O(commands)','O(1)',3),
3258:entry('count_binary_k_constraint_substrings',[('s','str'),('k','int')],'int',['strings','subarrays','counting'],['A binary substring satisfies the k-constraint when its zero count is at most k or its one count is at most k.','The logical condition is inclusive OR; only substrings with both counts above k fail.','Return the number of nonempty satisfying substrings.'],[(['10101',1],'Twelve of the fifteen substrings satisfy the constraint.'),(['1010101',2],'Twenty-five substrings have at least one digit count no greater than two.')],[[s,k] for s,k in [('0',0),('1',0),('01',0),('00',0),('10101',1),('1010101',2),('000',1),('111',1),('0011',1),('0101',0),('1100',2),('101',3),('000111',1),('011010',2)]],CONSTRAINT,[CONSTRAINT.replace('zeros<=k or ones<=k','zeros<=k and ones<=k'),CONSTRAINT.replace('<=k','<k')],['Requires both digit counts to be small instead of either one.','Uses strict bounds and rejects substrings whose count equals k.'],constraint_oracle,random_constraint,['Enumerate each start under the source-I constraints.','Extend the endpoint while maintaining zero and one counts.','Count the substring when either count is at most k.','Every substring is visited once and its maintained counts make the stated Boolean test exact.'],'O(n^2)','O(1)',3),
}
