"""Alternating-color triangle, circular colors, rotation cipher, parity swap, and coin game."""
from .import_batch_055 import entry

def triangle_oracle(a):
    red,blue=a;best=0
    for first_red in (True,False):
        r,b,height=red,blue,0
        while True:
            need=height+1
            if (height%2==0)==first_red:
                if r<need:break
                r-=need
            else:
                if b<need:break
                b-=need
            height+=1
        best=max(best,height)
    return best
def random_triangle(r):return [r.randint(1,100),r.randint(1,100)]
def colors_oracle(a):
    colors=a[0];n=len(colors)
    return sum(colors[(i-1)%n]!=colors[i]!=colors[(i+1)%n] for i in range(n))
def random_colors(r):return [[r.randint(0,1) for _ in range(r.randint(3,50))]]
def encrypted_oracle(a):return ''.join(a[0][(i+a[1])%len(a[0])] for i in range(len(a[0])))
def random_encrypted(r):
    s=''.join(r.choice('abcdef') for _ in range(r.randint(1,40)));return [s,r.randint(0,len(s)-1)]
def swap_oracle(a):
    s=a[0];answers=[s]
    for i in range(len(s)-1):
        if int(s[i])%2==int(s[i+1])%2:answers.append(s[:i]+s[i+1]+s[i]+s[i+2:])
    return min(answers)
def random_swap(r):return [''.join(str(r.randint(0,9)) for _ in range(r.randint(2,40)))]
def coins_oracle(a):return 'Alice' if min(a[0],a[1]//4)%2 else 'Bob'
def random_coins(r):return [r.randint(0,100),r.randint(0,100)]

TRIANGLE='''\
def maximum_alternating_color_triangle_height(red,blue):
    def build(first,second):
        height=0
        while True:
            needed=height+1
            if height%2==0:
                if first<needed:return height
                first-=needed
            else:
                if second<needed:return height
                second-=needed
            height+=1
    return max(build(red,blue),build(blue,red))
'''
COLORS='''\
def count_alternating_circular_triples(colors):
    n=len(colors)
    return sum(colors[i]!=colors[(i-1)%n] and colors[i]!=colors[(i+1)%n] for i in range(n))
'''
ENCRYPTED='''\
def circular_shift_encryption(s,k):
    k%=len(s)
    return s[k:]+s[:k]
'''
SWAP='''\
def smallest_one_same_parity_swap(s):
    chars=list(s)
    for i in range(len(chars)-1):
        if chars[i]>chars[i+1] and int(chars[i])%2==int(chars[i+1])%2:
            chars[i],chars[i+1]=chars[i+1],chars[i];break
    return ''.join(chars)
'''
COINS='''\
def coin_game_winner(x,y):
    turns=min(x,y//4)
    return 'Alice' if turns%2 else 'Bob'
'''

BATCH={
3200:entry('maximum_alternating_color_triangle_height',[('red','int'),('blue','int')],'int',['greedy','simulation','math'],['Build rows of lengths one, two, three, and so on.','Each row uses one color and adjacent rows must alternate colors.','Return the maximum complete height using at most red red balls and blue blue balls; either color may start.'],[([2,4],'Starting red uses one red, two blue, and three red cannot fit; starting blue reaches height three.'),([2,1],'Rows of one red and two blue cannot fit, but one blue then two red gives height two.')],[[r,b] for r,b in [(1,1),(1,2),(2,1),(2,4),(4,2),(5,5),(10,1),(1,10),(10,10),(3,6),(6,3),(20,15),(100,100),(7,8)]],TRIANGLE,[TRIANGLE.replace('height+1','height'),TRIANGLE.replace('max(build(red,blue),build(blue,red))','build(red,blue)')],['Charges row index rather than row length, allowing a free first row.','Considers only triangles starting with red.'],triangle_oracle,random_triangle,['For a fixed starting color, row colors and required counts are forced.','Simulate increasing row lengths until the needed color lacks enough balls.','Repeat with the colors exchanged and take the larger height.','Each simulation greedily builds every possible prefix, and the two starts exhaust all valid triangles.'],'O(sqrt(red+blue))','O(1)',3),
3206:entry('count_alternating_circular_triples',[('colors','list[int]')],'int',['arrays','circular arrays'],['colors is circular and contains zeros and ones.','A group centered at i alternates when both circular neighbors have the opposite color from colors[i].','Return the number of alternating length-three groups.'],[([[1,1,1]],'Every center has equal-colored neighbors, so no group alternates.'),([[0,1,0,0,1]],'Three circular centers have opposite-colored neighbors.')],[[x] for x in [[0,0,0],[1,1,1],[0,1,0],[0,1,1],[0,1,0,1],[0,1,0,0,1],[1,0,1],[1,0,0,1],[0,0,1,0],[1,1,0,1,0],[0,1,1,0],[1,0,1,1,0],[0,0,1,1,0],[1,0,0,0,1]]],COLORS,[COLORS.replace('and','or'),COLORS.replace('(i+1)%n','i+1')],['Accepts a center when only one neighbor differs.','Does not wrap the right neighbor at the final index.'],colors_oracle,random_colors,['Treat each array index as the center of one circular triple.','Use modulo n to obtain both neighbors.','Count centers differing from both neighbors.','Every circular length-three group has one unique center, so the scan counts all qualifying groups exactly once.'],'O(n)','O(1)',3),
3210:entry('circular_shift_encryption',[('s','str'),('k','int')],'str',['strings','circular arrays'],['Replace each character at index i with the character originally k positions to its right, wrapping around.','All replacements are simultaneous.','Return the encrypted string.'],[(['dart',3],'Indices read t,d,a,r after shifting three, producing tdar.'),(['aaa',1],'Every shifted source is a, so the string is unchanged.')],[[s,k] for s,k in [('a',0),('ab',0),('ab',1),('dart',3),('aaa',1),('abcdef',2),('abcdef',5),('code',1),('code',3),('xyz',2),('rotation',4),('hello',0),('abab',2),('qwerty',5)]],ENCRYPTED,[ENCRYPTED.replace('s[k:]+s[:k]','s[-k:]+s[:-k]'),ENCRYPTED.replace('k%=len(s)','k=(k+1)%len(s)')],['Rotates right rather than selecting characters to the right.','Adds one to the requested shift.'],encrypted_oracle,random_encrypted,['The replacement source for index zero is index k modulo n.','Following sources continue contiguously through the end and wrap to the prefix.','Thus concatenate s[k:] with s[:k] after reducing k modulo length.','This sequence lists source indices k,k+1,... modulo n exactly once in destination order.'],'O(n)','O(n)',3),
3216:entry('smallest_one_same_parity_swap',[('s','str')],'str',['strings','greedy'],['You may perform at most one swap of adjacent decimal digits.','The two swapped digits must have the same parity.','Return the lexicographically smallest obtainable string.'],[(['45320'],'The first useful same-parity descent is 5,3; swapping it produces 43520.'),(['001'],'No allowed adjacent swap makes the string smaller.')],[[s] for s in ['12','21','31','13','45320','001','8642','97531','12345','54321','1023','908172','24680','13579']],SWAP,[SWAP.replace('chars[i]>chars[i+1]','chars[i]<chars[i+1]'),SWAP.replace('break','')],['Swaps the first increasing pair and makes the string larger.','Performs every useful swap rather than at most one.'],swap_oracle,random_swap,['A beneficial swap must be a same-parity adjacent descent.','The earliest changed position dominates all later lexicographic effects.','Scan left to right and swap the first allowed descent, then stop.','Any later swap leaves this earliest improvable digit larger, while a non-descent cannot improve the string.'],'O(n)','O(n)',3),
3222:entry('coin_game_winner',[('x','int'),('y','int')],'str',['math','games'],['Each turn removes one 75-value coin and four 10-value coins, totaling 115.','Alice moves first and players alternate until the required coins are unavailable.','Return Alice if she makes the last move, otherwise Bob.'],[([2,7],'Only one complete move is possible, so Alice wins.'),([4,11],'Two moves are possible, so Bob makes the last move.')],[[x,y] for x,y in [(0,0),(1,0),(0,4),(1,4),(2,7),(4,11),(2,8),(3,12),(10,40),(10,39),(1,100),(100,4),(5,20),(6,23)]],COINS,[COINS.replace('y//4','y//3'),COINS.replace('turns%2','turns%2==0')],['Uses only three 10-value coins per turn.','Declares Alice the winner after an even number of moves.'],coins_oracle,random_coins,['Every legal move consumes the same fixed resources, so the total move count is predetermined.','At most x moves use 75-value coins and at most floor(y/4) use 10-value coins.','Take their minimum and inspect its parity.','Players alternate from Alice, so an odd number of moves ends with Alice and an even number with Bob.'],'O(1)','O(1)',3),
}
BATCH[3206]['wrong'][1]=COLORS.replace('range(n)','range(n-1)')
