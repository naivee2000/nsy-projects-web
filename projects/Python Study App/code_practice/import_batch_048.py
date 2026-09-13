"""Zuma's bounded insertion search, retaining preparatory non-removing moves."""
from collections import deque
from itertools import groupby

from .import_batch_003 import entry


def collapse_oracle(board):
    while True:
        groups=[list(group) for _,group in groupby(board)]
        reduced=''.join(''.join(group) for group in groups if len(group)<3)
        if reduced==board:return board
        board=reduced


def zuma_oracle(args):
    """Literal breadth-first legal moves; no color-feasibility or move pruning."""
    board,hand=args
    queue=deque([(board,''.join(sorted(hand)),0)])
    seen={(board,''.join(sorted(hand)))}
    while queue:
        board,hand,steps=queue.popleft()
        if not board:return steps
        for index,color in enumerate(hand):
            remaining=hand[:index]+hand[index+1:]
            for position in range(len(board)+1):
                updated=collapse_oracle(board[:position]+color+board[position:])
                state=(updated,remaining)
                if state not in seen:
                    seen.add(state)
                    queue.append((updated,remaining,steps+1))
    return -1


def relaxed_deletion_bound(board,budget):
    """Independent shortest path with paid partial-run deletion as a relaxation.

    Deleting k same-colored original balls pays max(0,3-k), ignoring hand
    inventory and mandatory reactions. Every real clearing sequence induces
    a path costing no more; failure within budget certifies impossibility.
    """
    from heapq import heappop,heappush
    queue=[(0,board)];distance={board:0}
    while queue:
        paid,row=heappop(queue)
        if distance[row]!=paid:continue
        if not row:return paid
        for left in range(len(row)):
            for right in range(left+1,len(row)+1):
                if row[right-1]!=row[left]:break
                cost=paid+max(0,3-(right-left))
                updated=row[:left]+row[right:]
                if cost<=budget and cost<distance.get(updated,budget+1):
                    distance[updated]=cost;heappush(queue,(cost,updated))
    return budget+1


REFERENCE='''\
def zuma_min_insertions(board,hand):
    from collections import Counter
    from functools import cache
    @cache
    def optimistic(row):
        @cache
        def cost(left,right,held):
            if left>right:
                return 0
            best=max(0,2-held)+cost(left+1,right,0)
            for next_index in range(left+1,right+1):
                if row[next_index]==row[left]:
                    candidate=cost(left+1,next_index-1,0)+cost(next_index,right,min(2,held+1))
                    best=min(best,candidate)
            return best
        answer=cost(0,len(row)-1,0)
        cost.cache_clear()
        return answer
    def insert(row,position,color):
        row=row[:position]+color+row[position:]
        while 0<=position<len(row):
            left,right=position,position+1
            while left>0 and row[left-1]==row[position]:
                left-=1
            while right<len(row) and row[right]==row[position]:
                right+=1
            if right-left<3:
                break
            row=row[:left]+row[right:]
            position=left-1
        return row
    @cache
    def search(row,balls):
        if not row:
            return 0
        if not balls:
            return 6
        counts=Counter(row)
        available=Counter(balls)
        lower=0
        for color,count in counts.items():
            need=max(0,3-count)
            if need>available[color]:
                return 6
            lower+=need
        lower=max(1,lower,optimistic(row))
        if lower>len(balls):
            return 6
        best=6
        for color in available:
            remaining=balls.replace(color,'',1)
            for position in range(len(row)+1):
                if position and row[position-1]==color:
                    continue
                updated=insert(row,position,color)
                updated=min(updated,updated[::-1])
                best=min(best,1+search(updated,remaining))
                if best==lower:
                    return best
        return best
    answer=search(min(board,board[::-1]),''.join(sorted(hand)))
    return answer if answer<=len(hand) else -1
'''


def random_zuma(rng):
    if rng.random()<0.5:
        board,hand=rng.choice([('A','AA'),('AA','A'),('AABBAA','B'),('AABBAACCAA','BC')])
        colors=dict(zip('ABC',rng.sample(list('RYBGW'),3)))
        board=''.join(colors[c] for c in board)
        hand=''.join(colors[c] for c in hand)
        hand+=''.join(rng.choice('RYBGW') for _ in range(rng.randint(0,3-len(hand))))
        balls=list(hand);rng.shuffle(balls)
        return [board,''.join(balls)]
    palette=rng.sample(list('RYBGW'),2) if rng.random()<0.5 else 'RYBGW'
    board=''
    for _ in range(rng.randint(1,6)):
        choices=[color for color in palette if not board.endswith(color*2)]
        board+=rng.choice(choices)
    return [board,''.join(rng.choice(palette) for _ in range(rng.randint(1,3)))]


IMMEDIATE_ONLY=REFERENCE.replace('updated=insert(row,position,color)',
    'updated=insert(row,position,color)\n                if len(updated)>=len(row):\n                    continue')
INDEPENDENT_RUNS='''\
def zuma_min_insertions(board,hand):
    from collections import Counter
    from itertools import groupby
    remaining=Counter(hand)
    total=0
    for color,group in groupby(board):
        needed=3-len(list(group))
        if remaining[color]<needed:
            return -1
        remaining[color]-=needed
        total+=needed
    return total
'''

BATCH={488:entry('zuma_min_insertions',[('board','str'),('hand','str')],'int',
    ['strings','backtracking','recursion','search','dynamic-programming'],
    ['1 <= len(board) <= 16 and 1 <= len(hand) <= 5. Every character is one of R, Y, B, G, W.',
     'The initial board has no run of three or more equal colors. A move spends one ball from hand and inserts it into ANY gap, including either end.',
     'After each insertion, remove a run of THREE OR MORE matching balls; continue all resulting chain reactions until the board is stable.',
     'Return the minimum number of inserted balls that clears the whole board, or -1 if impossible. Unused hand balls are allowed.',
     'An insertion that removes nothing immediately is legal and may be necessary. The remaining count of every hand color matters.'],
    [(['WRRBBW','RB'],'There are only two white balls in total and no white ball in hand, so no group can ever remove the whites. Clearing the red and blue groups still leaves WW; return -1.'),
     (['WWRRBBWW','WRBRW'],'Insert R into RR, leaving WWBBWW. Insert B into BB: removing BBB joins four white balls, which also disappear. Two insertions suffice, and each of the red/blue pairs needs at least one.')],
    [[board,hand] for board,hand in [('R','R'),('R','RR'),('RR','R'),('RR','B'),('G','GGGGG'),
      ('RRBB','RB'),('RRBB','R'),('RBR','BB'),('RBR','BBR'),('RRBBRR','B'),('RY','RRYY'),
      ('RY','RY'),('WW','WWWWW'),('RGGBBR','GBR'),('Y','YY'),('RRWWRRBBRR','WB')]],
    REFERENCE,[IMMEDIATE_ONLY,INDEPENDENT_RUNS],
    ['Allows only insertions that immediately remove balls, losing required preparatory moves.',
     'Pays to complete each original run separately and ignores beneficial chain reactions.'],
    zuma_oracle,random_zuma,
    ['A search state needs both the stable board and the remaining multiset of hand balls.',
     'Combine exact insertion search with an optimistic interval-clearing bound. Try every available color in every distinct gap and fully resolve reactions; do not require immediate removal.',
     'For each legal insertion, spend that color, collapse around the inserted position until stable, and minimize 1+search(next_board,remaining_hand). Empty board costs zero.',
     'For a relaxed interval with k held matching balls, either pay max(0,2-k) to remove its first ball or clear an interior and join a later match. Cap k at two. This ignores inventory and forced reactions, so its cost is a lower bound: if it exceeds the hand size, stop. Identical insertion positions and mirrored boards can also be merged safely.'],
    'The hand contains at most five balls, so enumerate bounded insertion sequences with memoization on '
    '(stable board, sorted remaining hand). Full chain reactions are resolved around the insertion seam. '
    'Deleting a group can create another matching group on that seam, including a group of four or more. '
    'Only exact duplicate positions and mirror-symmetric boards are merged. For every color still on the '
    'board, at least max(0,3-board_count) balls of that color must be available; summing these deficits gives '
    'an admissible move lower bound. A nonempty stable board needs at least one move. Reaching that bound '
    'permits an early return, but no non-removing move type is discarded. An interval DP supplies another '
    'lower bound: allow unlimited inserted colors and allow matching balls to be held apart until their '
    'interior disappears. cost(l,r,k) either completes the first ball plus k held copies, or clears an '
    'interior interval and joins a later matching original ball. Held counts saturate at two. This relaxed '
    'game includes every real deletion sequence and can only require fewer insertions; a bound above the '
    'remaining hand size proves impossibility. Do not compress original matching runs in this DP, since '
    'a preparatory insertion may split one. For RRWWRRBBRR with hand WB, '
    'insert B between the first two R balls, then insert W into WW: the W, R, B, and R groups disappear in '
    'successive reactions. Completing an existing group first misses this two-move solution. The independent '
    'oracle uses breadth-first search over every hand index and every gap, with global run rescanning and '
    'no feasibility or symmetry pruning. Two adversarial full-size impossible boards also have independent '
    'bounded shortest-path certificates in a relaxed partial-run deletion game. Here n=len(board), '
    'h=len(hand), and S is the number of memoized states; '
    'the search remains exponential in h, bounded by the source limit h<=5.',
    'O(S*5*(n+h)^3), S memoized states','O(S*(n+h)+(n+h)^2)',difficulty=8,
    stress=[(['RRYGGYYRRYYGGYRR','GGBBB'],5),(['RRWWRRBBRRYYGGYY','WBGYY'],3),
      (['RGRGRGRGRGRGRGRG','RRRRR'],-1),(['RYBGWRYBGWRYBGWR','RRYYY'],-1),
      (['RYBGWRYBGWRYBGWR','RYBGW'],-1),(['RRYYBBGGWWRRYBGW','RYBGW'],-1)])}
BATCH[488]['prerequisites']=['recursion','backtracking','dynamic-programming']
