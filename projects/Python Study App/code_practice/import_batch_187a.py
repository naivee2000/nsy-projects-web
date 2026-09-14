"""Easy string, digit, and pair-enumeration problems for workbook batch 187."""
from .import_batch_055 import entry

def faulty_oracle(a):
    out=[]
    for char in a[0]:
        if char=='i':out=list(reversed(out))
        else:out.append(char)
    return ''.join(out)
def random_faulty(r):return [''.join(r.choice('abcdefi') for _ in range(r.randint(1,80)))]

def digit_pair_oracle(a):
    nums=a[0];best=-1
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if max(str(nums[i]))==max(str(nums[j])):best=max(best,nums[i]+nums[j])
    return best
def random_digit_pair(r):return [[r.randint(1,10000) for _ in range(r.randint(2,30))]]

def less_pair_oracle(a):
    nums,target=a
    return sum(nums[i]+nums[j]<target for i in range(len(nums)) for j in range(i+1,len(nums)))
def random_less_pair(r):return [[r.randint(-50,50) for _ in range(r.randint(1,30))],r.randint(-50,50)]

def acronym_oracle(a):return len(a[0])==len(a[1]) and all(word[0]==char for word,char in zip(*a))
def random_acronym(r):
    words=[''.join(r.choice('abcde') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,15))]
    actual=''.join(w[0] for w in words)
    return [words,actual if r.random()<.5 else ''.join(r.choice('abcde') for _ in range(r.randint(0,15)))]

def origin_oracle(a):
    s=a[0];answers=[]
    def visit(i,position):
        if i==len(s):answers.append(abs(position));return
        if s[i]=='L':visit(i+1,position-1)
        elif s[i]=='R':visit(i+1,position+1)
        else:visit(i+1,position-1);visit(i+1,position+1)
    visit(0,0);return max(answers)
def random_origin(r):return [''.join(r.choice('LR_') for _ in range(r.randint(1,10)))]

FAULTY='''\
def faulty_keyboard_result(s):
    from collections import deque
    text=deque();reversed_order=False
    for char in s:
        if char=='i':reversed_order=not reversed_order
        elif reversed_order:text.appendleft(char)
        else:text.append(char)
    result=''.join(text)
    return result[::-1] if reversed_order else result
'''
DIGIT_PAIR='''\
def maximum_pair_sum_by_largest_digit(nums):
    best_by_digit={};answer=-1
    for value in nums:
        digit=max(str(value))
        if digit in best_by_digit:answer=max(answer,value+best_by_digit[digit])
        best_by_digit[digit]=max(value,best_by_digit.get(digit,0))
    return answer
'''
LESS_PAIR='''\
def count_pairs_below_target(nums,target):
    values=sorted(nums);left=0;right=len(values)-1;answer=0
    while left<right:
        if values[left]+values[right]<target:
            answer+=right-left;left+=1
        else:right-=1
    return answer
'''
ACRONYM='''\
def is_words_acronym(words,s):
    return ''.join(word[0] for word in words)==s
'''
ORIGIN='''\
def furthest_origin_distance(moves):
    displacement=moves.count('R')-moves.count('L')
    return abs(displacement)+moves.count('_')
'''

BATCH={
2810:entry('faulty_keyboard_result',[('s','str')],'str',['strings','simulation','deques'],['Process the typed characters from left to right.','Typing i reverses all text currently on the screen and does not insert i.','Every other lowercase letter is appended; return the final screen text.'],[(['string'],'Typing i reverses str to rts, then n and g are appended, producing rtsng.'),(['poiinter'],'The two consecutive i keys reverse twice, so the final text is ponter.')],[[s] for s in ['i','a','ii','iii','ai','ia','aib','ibia','abc','iiiiii','code','icodex','abcidef','iabcidefi']],FAULTY,[FAULTY.replace("reversed_order=not reversed_order","reversed_order=True"),FAULTY.replace("elif reversed_order:text.appendleft(char)","elif reversed_order:text.append(char)")],['Treats every i after the first as leaving the orientation reversed.','Appends in the wrong deque direction while the screen is logically reversed.'],faulty_oracle,random_faulty,['Repeated physical reversal can be represented by one orientation flag.','Use a deque so a normal character is added to the logical end in either orientation.','Toggle the flag for i; append right normally and left when reversed, then orient once at the end.','The deque plus flag always represents exactly the visible text, so each typed character preserves the simulation invariant.'],'O(n)','O(n)',3),
2815:entry('maximum_pair_sum_by_largest_digit',[('nums','list[int]')],'int',['arrays','hash maps','digits'],['Choose two different array indices whose numbers have the same largest decimal digit.','Maximize the sum of the chosen values.','Return -1 when no qualifying pair exists.'],[([[112,131,411]],'Their largest digits are two, three, and four, so no pair qualifies.'),([[2536,1613,3366,162]],'The two largest values with largest digit six are 3366 and 2536, totaling 5902.')],[[x] for x in [[1,2],[1,1],[9,9],[51,71,17,24,42],[10,20,30],[90,89],[123,321],[9999,9998],[10000,1],[12,21,31],[444,44,4],[98,89,77],[2,22,222],[305,503,350]]],DIGIT_PAIR,[DIGIT_PAIR.replace('max(str(value))','str(value)[0]'),DIGIT_PAIR.replace('value+best_by_digit[digit]','value+digit')],['Groups by the first digit rather than the largest digit.','Adds a digit label instead of the best earlier number in its group.'],digit_pair_oracle,random_digit_pair,['Group each value by its largest decimal digit.','For each digit retain the largest value seen so far.','Before updating a group, combine the current value with that saved maximum and update the answer.','Every valid pair is considered when its later endpoint arrives, and keeping only the largest earlier partner dominates all others.'],'O(n*d)','O(1)',3),
2824:entry('count_pairs_below_target',[('nums','list[int]'),('target','int')],'int',['arrays','two pointers','sorting'],['Count index pairs i,j with i less than j.','A pair qualifies only when nums[i]+nums[j] is strictly less than target.','Return the total number of qualifying pairs, including pairs formed by equal values at different indices.'],[([[-1,1,2,3,1],2],'Exactly three pairs use -1 with either one or with two.'),([[-6,2,5,-2,-7,-1,3],-2],'Ten distinct index pairs have sums strictly below negative two.')],[[nums,t] for nums,t in [([1],2),([1,2],4),([1,2],3),([0,0,0],1),([0,0,0],0),([-5,-4,-3],-6),([-1,1],1),([2,2,2,2],5),([2,2,2,2],4),([-10,10,0],1),([5,1,3,2],7),([-3,-2,4,8],3),([1,-1,1,-1],0),([100,-100,50,-50],10)]],LESS_PAIR,[LESS_PAIR.replace('<target','<=target'),LESS_PAIR.replace('answer+=right-left','answer+=1')],['Counts pairs equal to the target even though the inequality is strict.','Counts only one partner when a small left value qualifies with every index through right.'],less_pair_oracle,random_less_pair,['Sort a copy so pair sums change monotonically.','If the two endpoints are too large, decrease the right endpoint.','If they qualify, the left value also qualifies with every index through right, adding right-left pairs at once.','Sorting preserves values and multiplicities; monotonicity proves every pair is counted once without checking it individually.'],'O(n log n)','O(n)',3),
2828:entry('is_words_acronym',[('words','list[str]'),('s','str')],'bool',['arrays','strings'],['Form an acronym by taking the first character of every word in order.','Return whether that complete acronym equals s exactly.','Every input word is nonempty; no word may be skipped.'],[([['alice','bob','charlie'],'abc'],'The initials a, b, and c concatenate to abc.'),([['an','apple'],'a'],'Both words contribute, making aa rather than a.')],[[w,s] for w,s in [(['a'],'a'),(['a'],'b'),(['apple','banana'],'ab'),(['bear','aardvark'],'ba'),(['never','gonna','give','up','on','you'],'ngguoy'),(['x','y','z'],'xyz'),(['x','y','z'],'xy'),(['same','start'],'ss'),(['Code','Practice'],'CP'),(['Code','Practice'],'cp'),(['one','two','three'],'ott'),(['ab','bc','ca'],'abc'),(['longword','x'],'lx'),(['zebra','zero'],'zz')]],ACRONYM,[ACRONYM.replace("word[0]","word[-1]"),ACRONYM.replace("==s",".startswith(s)")],['Uses last characters rather than initials.','Accepts a proper prefix and therefore permits missing words.'],acronym_oracle,random_acronym,['The required output string is uniquely determined.','Take exactly one first character from every word.','Concatenate those characters in array order and compare the entire result with s.','Exact string equality enforces both character order and the required one-character-per-word length.'],'O(total words)','O(number of words)',3),
2833:entry('furthest_origin_distance',[('moves','str')],'int',['strings','greedy','math'],['Start at position zero on a number line.','L moves one unit left, R moves one unit right, and each underscore may be replaced independently by L or R.','Return the greatest possible absolute distance from the origin after all moves.'],[(['L_RL__R'],'Fixed moves end one step left, and three wildcards extend that direction for distance four.'),(['_R__LL_'],'Fixed moves end one step left; four wildcards can all go left for distance five.')],[[s] for s in ['L','R','_','LR','RL','__','L__','R__','LR_','LLRR','LLLL','RRRR','L_R','R_L','LRLR____','________']],ORIGIN,[ORIGIN.replace('abs(displacement)+','displacement+'),ORIGIN.replace("moves.count('_')","-moves.count('_')")],['Fails to take absolute value when fixed moves lean left.','Moves wildcards toward the origin instead of away from the fixed displacement.'],origin_oracle,random_origin,['First compute the signed displacement forced by L and R.','Every underscore can be aimed in whichever direction increases the final magnitude.','Choose all wildcards in the direction of the fixed displacement, giving abs(R-L)+underscores.','No wildcard can add more than one to absolute distance, and this construction adds exactly one for each, so it is optimal.'],'O(n)','O(1)',3),
}
BATCH[2815]['wrong'][1]=DIGIT_PAIR.replace('value+best_by_digit[digit]','value')
