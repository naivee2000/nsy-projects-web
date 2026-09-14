"""Final reviewed group of workbook batch 106."""
from .import_batch_055 import entry
def white_o(a):return (ord(a[0][0])-ord('a')+int(a[0][1])-1)%2==1
def similar_o(a):
 first,second=map(str.split,a)
 if len(first)>len(second):first,second=second,first
 gap=len(second)-len(first)
 return any(first==second[:place]+second[place+gap:] for place in range(len(first)+1))
def nice_o(a):
 nums=a[0]
 def rev(value):return int(str(value)[::-1])
 return sum(nums[i]+rev(nums[j])==nums[j]+rev(nums[i]) for i in range(len(nums)) for j in range(i+1,len(nums)))%(10**9+7)
def truncate_o(a):return ' '.join(a[0].split(' ')[:a[1]])
def active_o(a):
 logs,k=a;minutes={}
 for user,minute in logs:minutes.setdefault(user,set()).add(minute)
 return [sum(len(values)==count for values in minutes.values()) for count in range(1,k+1)]
def rwhite(r):return [r.choice('abcdefgh')+str(r.randint(1,8))]
def rsimilar(r):
 base=[r.choice(['a','b','cat','Dog']) for _ in range(r.randint(1,6))];extra=[r.choice(['x','y']) for _ in range(r.randint(0,3))];place=r.randint(0,len(base));return [' '.join(base),' '.join(base[:place]+extra+base[place:])]
def rnice(r):return [[r.randint(0,9999) for _ in range(r.randint(1,15))]]
def rtruncate(r):
 words=[r.choice(['one','Two','cat','word']) for _ in range(r.randint(1,10))];return [' '.join(words),r.randint(1,len(words))]
def ractive(r):
 logs=[[r.randint(0,5),r.randint(1,8)] for _ in range(r.randint(1,20))];maximum=max(len({minute for owner,minute in logs if owner==user}) for user in {row[0] for row in logs});return [logs,r.randint(maximum,maximum+5)]
WHITE='''def is_white_chessboard_square(coordinates):
 return (ord(coordinates[0])-ord('a')+int(coordinates[1])-1)%2==1
'''
SIMILAR='''def are_sentences_similar(sentence1, sentence2):
 first,second=sentence1.split(),sentence2.split()
 if len(first)>len(second):first,second=second,first
 prefix=0
 while prefix<len(first) and first[prefix]==second[prefix]:prefix+=1
 suffix=0
 while suffix<len(first)-prefix and first[-1-suffix]==second[-1-suffix]:suffix+=1
 return prefix+suffix>=len(first)
'''
NICE='''def count_nice_reverse_pairs(nums):
 counts={};answer=0
 for value in nums:
  key=value-int(str(value)[::-1]);answer+=counts.get(key,0);counts[key]=counts.get(key,0)+1
 return answer%(10**9+7)
'''
TRUNCATE='''def truncate_sentence(s, k):
 return ' '.join(s.split()[:k])
'''
ACTIVE='''def user_active_minute_counts(logs, k):
 minutes={}
 for user,minute in logs:minutes.setdefault(user,set()).add(minute)
 answer=[0]*k
 for values in minutes.values():answer[len(values)-1]+=1
 return answer
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1812:E('is_white_chessboard_square',[('coordinates','str')],'bool',['strings','math'],['The coordinate is a lowercase file a-h followed by a rank 1-8.','Return true for a white square and false for a black square.'],[(['a1'],'a1 is black, so return false.'),(['h3'],'File h and rank three have opposite parity, making the square white.')],[[x] for x in ['a2','a8','b1','b2','c3','c4','d5','e7','f6','g1','g8','h1','h8','d2']],WHITE,[WHITE.replace('==1','==0'),WHITE.replace("-ord('a')","-ord('b')")],['Reverses the white and black parity.', 'Offsets the file parity by one.'],white_o,rwhite,H('Chessboard colors alternate with every file and rank step.','Convert the file and rank to zero-based coordinates and inspect their sum parity.','An odd coordinate sum is white when a1 is defined black.','Moving one square changes parity and color; therefore parity exactly reproduces the full alternating board.'),'O(1)','O(1)',3),
1813:E('are_sentences_similar',[('sentence1','str'),('sentence2','str')],'bool',['strings','two-pointers'],['Words are separated by single spaces without leading or trailing spaces.','Return whether inserting one contiguous sequence of whole words into either sentence can make them equal.'],[(['My name is Haley','My Haley'],'Insert name is between the shared prefix My and suffix Haley.'),(['of','A lot of words'],'The word of is neither a matching prefix nor suffix, so one insertion cannot suffice.')],[[a,b] for a,b in [('a','a'),('a','a b'),('a','b a'),('a','b'),('Hello Jane','Hello my name is Jane'),('Eating right now','Eating'),('Frog cool','Frogs are cool'),('x y','x a y'),('x y','a x y'),('x y','x y a'),('one two three','one three'),('a b','a c b'),('a b c','a x b c'),('a b c','a b x')]],SIMILAR,[SIMILAR.replace('prefix+suffix>=len(first)','prefix+suffix>len(first)'),SIMILAR.replace('second[-1-suffix]','second[-2-suffix]')],['Rejects the exact coverage needed for valid similarity.','Compares suffix words with the wrong offset in the longer sentence.'],similar_o,rsimilar,H('The shorter sentence must remain as a prefix plus a suffix of the longer one.','Count matching words from the left and independently from the right.','Similarity holds when those counts cover every word of the shorter sentence.','The uncovered middle of the longer sentence is exactly one insertable block; if any shorter word remains uncovered, no single insertion can preserve order.'),'O(words)','O(words)',5),
1814:E('count_nice_reverse_pairs',[('nums','list[int]')],'int',['arrays','hash-maps','math','counting'],['rev(x) reverses decimal digits and discards leading zeros in the result.','Count i<j satisfying nums[i]+rev(nums[j])=nums[j]+rev(nums[i]), modulo 1,000,000,007.'],[([[42,11,1,97]],'Pairs 42/97 and 11/1 share the required transformed value, so the answer is two.'),([[13,10,35,24,76]],'Four index pairs satisfy the equality.')],[[x] for x in [[0],[1,1],[10,1],[12,21],[42,11,1,97],[13,10,35,24,76],[100,1,10],[5,50,500],[123,321,111],[0,0,0],[20,2,200],[91,19,10,1],[101,101],[7,70,700,7000]]],NICE,[NICE.replace('value-int','value+int'),NICE.replace('answer+=counts.get(key,0)','answer+=1')],['Groups by value plus reverse instead of their difference.','Counts every element instead of only earlier matching transformed values.'],nice_o,rnice,H('Rearrange the equality so each side depends on only one array value.','Two values form a nice pair exactly when value-rev(value) is equal.','Count earlier occurrences of each transformed key while scanning.','The algebraic transformation is equivalent to the original equation, and adding prior frequency counts each ordered index pair once.'),'O(n*d)','O(n)',5),
1816:E('truncate_sentence',[('s','str'),('k','int')],'str',['strings','arrays'],['The sentence has single spaces and no leading or trailing whitespace.','Return exactly the first k complete words.'],[(['Hello how are you Contestant',4],'The first four words form Hello how are you.'),(['chopper is not a tanuki',5],'k includes every word, so the sentence is unchanged.')],[[*x] for x in [('one',1),('one two',1),('one two',2),('What is the solution to this problem',4),('a b c d',3),('A B C',2),('hello world again',1),('hello world again',3),('x y z',2),('red green blue yellow',2),('Keep All Words',3),('first second third fourth fifth',4),('Cat dog',1),('single',1)]],TRUNCATE,[TRUNCATE.replace('[:k]','[:k-1]'),TRUNCATE.replace("' '.join","''.join")],['Returns one fewer word than requested.','Removes required spaces between retained words.'],truncate_o,rtruncate,H('The input guarantees that spaces already mark exact word boundaries.','Split into words, take the first k, and join with single spaces.','A slice ending at k contains indices zero through k-1.','Splitting preserves word order and the join reconstructs exactly the requested prefix without partial words.'),'O(len(s))','O(len(s))',3),
1817:E('user_active_minute_counts',[('logs','list[list[int]]'),('k','int')],'list[int]',['arrays','hash-maps','sets'],['Each log is [user_id,minute], and duplicate actions in the same minute count once per user.','Return a length-k array whose index j-1 counts users with exactly j distinct active minutes.'],[([[[0,5],[1,2],[0,2],[0,5],[1,3]],5],'Both users have exactly two distinct active minutes, producing [0,2,0,0,0].'),([[[1,1],[2,2],[2,3]],4],'One user has one active minute and one has two.')],[[*x] for x in [([[1,1]],1),([[1,1],[1,1]],2),([[1,1],[1,2]],2),([[1,1],[2,1]],2),([[0,5],[1,2],[0,2],[0,5],[1,3]],5),([[1,1],[2,2],[2,3]],4),([[1,1],[1,2],[1,3]],5),([[1,1],[2,1],[3,1]],3),([[5,2],[5,4],[6,2],[6,4]],4),([[1,1],[1,1],[2,2]],3),([[0,1],[0,2],[1,2],[1,3],[1,4]],5),([[9,9],[8,8],[9,8]],2),([[1,1],[2,2],[3,3],[3,4]],4),([[4,1],[4,2],[4,2],[5,1]],3)]],ACTIVE,[ACTIVE.replace('set()).add(minute)','list()).append(minute)'),ACTIVE.replace('len(values)-1','len(values)')],['Counts duplicate actions rather than distinct active minutes.','Writes each user into the next bucket, causing an index shift.'],active_o,ractive,H('Each user needs a set of minutes to discard duplicate actions.','Group log minutes by user ID, then measure every set size.','Increment answer[size-1] for each user.','Sets exactly encode distinct minutes, and the one-based UAM definition maps size j to zero-based index j-1.'),'O(logs)','O(logs)',5),
}
