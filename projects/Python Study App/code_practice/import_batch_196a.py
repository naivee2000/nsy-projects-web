"""Prefix reversal, binary-digit even values, residue prefixes, text scores, and dual reversal."""
from .import_batch_055 import entry

def prefix_oracle(a):return a[0][:a[1]][::-1]+a[0][a[1]:]
def random_prefix(r):
    s=''.join(r.choice('abcdef') for _ in range(r.randint(1,40)));return [s,r.randint(1,len(s))]
def largest_even_oracle(a):
    s=a[0];i=s.rfind('2');return s[:i+1] if i>=0 else ''
def random_largest_even(r):return [''.join(r.choice('12') for _ in range(r.randint(1,50)))]
def residue_oracle(a):
    seen=set();answer=0
    for i,c in enumerate(a[0],1):seen.add(c);answer+=len(seen)==i%3
    return answer
def random_residue(r):return [''.join(r.choice('abcdef') for _ in range(r.randint(1,50)))]
def score_oracle(a):
    vowels=sum(c in 'aeiou' for c in a[0]);consonants=sum(c.isalpha() and c not in 'aeiou' for c in a[0]);return vowels//consonants if consonants else 0
def random_score(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz 0123456789') for _ in range(r.randint(1,60)))]
def reverse_oracle(a):
    s=a[0];letters=iter([c for c in s if c.isalpha()][::-1]);special=iter([c for c in s if not c.isalpha()][::-1]);return ''.join(next(letters) if c.isalpha() else next(special) for c in s)
def random_reverse(r):return [''.join(r.choice('abcde#@()!') for _ in range(r.randint(1,50)))]

PREFIX='''def reverse_string_prefix(s,k):
    return s[:k][::-1]+s[k:]
'''
LARGEST='''def largest_even_subsequence_number(s):
    last=s.rfind('2')
    return s[:last+1] if last!=-1 else ''
'''
RESIDUE='''def count_residue_matching_prefixes(s):
    seen=set();answer=0
    for length,char in enumerate(s,1):
        seen.add(char)
        if len(seen)==length%3:answer+=1
    return answer
'''
SCORE='''def vowel_consonant_floor_score(s):
    vowels=sum(char in 'aeiou' for char in s)
    consonants=sum(char.isalpha() and char not in 'aeiou' for char in s)
    return vowels//consonants if consonants else 0
'''
REVERSE='''def reverse_letters_and_specials_separately(s):
    letters=[char for char in s if char.isalpha()][::-1]
    specials=[char for char in s if not char.isalpha()][::-1]
    return ''.join(letters.pop(0) if char.isalpha() else specials.pop(0) for char in s)
'''

BATCH={
3794:entry('reverse_string_prefix',[('s','str'),('k','int')],'str',['strings','two pointers'],['Reverse exactly the first k characters of s.','Leave every character from index k onward unchanged.','Return the combined string.'],[(['abcd',2],'Reversing ab produces bacd.'),(['hello',5],'Reversing the complete string produces olleh.')],[[s,k] for s,k in [('a',1),('ab',1),('ab',2),('abcd',2),('hello',5),('python',3),('aaaa',2),('abcdef',6),('racecar',4),('xy',2),('testing',1),('prefix',4),('12345',3),('zebra',2)]],PREFIX,[PREFIX.replace(':k',':k-1'),PREFIX.replace('[::-1]','')],['Reverses one fewer prefix character.','Returns the original string without reversing.'],prefix_oracle,random_prefix,['Slice the first k characters.','Reverse that slice.','Append the untouched suffix beginning at k.','The two slices partition s exactly once.'],'O(n)','O(n)',3),
3798:entry('largest_even_subsequence_number',[('s','str')],'str',['strings','greedy'],['s contains only digits one and two.','Delete zero or more characters while preserving order to form the numerically largest even result.','Return an empty string if no even result can be formed.'],[(['1112'],'The complete value already ends in two and is the longest possible result.'),(['12111'],'Keep the prefix through its only two, producing 12.')],[[s] for s in ['1','2','11','12','21','1112','12111','222','11211','21112','111','212121','12221','22111']],LARGEST,[LARGEST.replace("rfind('2')","find('2')"),LARGEST.replace("if last!=-1 else ''","if last!=-1 else s")],['Stops at the first two instead of the last, losing useful leading digits.','Returns an odd string when no two exists.'],largest_even_oracle,random_largest_even,['An even result must end in digit two.','Using the last two permits retaining the longest possible prefix.','Every earlier digit increases digit count and therefore numeric value.','If no two exists, no even subsequence is possible.'],'O(n)','O(n)',3),
3803:entry('count_residue_matching_prefixes',[('s','str')],'int',['strings','sets','prefixes'],['For each nonempty prefix of s, count its distinct letters.','The prefix qualifies when that count equals the prefix length modulo three.','Return the number of qualifying prefixes.'],[(['abc'],'Lengths one and two have distinct counts one and two; length three has residue zero, so return two.'),(['aaaa'],'Prefixes of lengths one and four qualify, producing two.')],[[s] for s in ['a','aa','ab','abc','aaaa','abab','abcd','abcabc','zzzzzz','abca','aabbcc','abcdefg','xyzxyz','leetcode']],RESIDUE,[RESIDUE.replace('length%3','length%2'),RESIDUE.replace('seen.add(char)','seen=set(char)')],['Uses modulo two instead of modulo three.','Forgets all distinct characters before the current position.'],residue_oracle,random_residue,['Maintain a set of letters seen in the growing prefix.','Its size is the current distinct count.','Compare that size with one-based prefix length modulo three.','Increment once for every equality.'],'O(n)','O(distinct letters)',3),
3813:entry('vowel_consonant_floor_score',[('s','str')],'int',['strings','counting'],['Count lowercase vowels and lowercase consonants in s; ignore spaces and digits.','If consonants exist, return floor(vowels/consonants).','Return zero when there are no consonants.'],[(['cooear'],'There are four vowels and two consonants, so the floor score is two.'),(['aeiou 123'],'There are no consonants, so return zero.')],[[s] for s in ['a','b','aeiou 123','cooear','abc','rhythm','hello world','12345','a1b2c3','queueing','zzzaaa',' ','leetcode','education']],SCORE,[SCORE.replace("char not in 'aeiou'","char in 'aeiou'"),SCORE.replace('vowels//consonants','consonants//vowels')],['Counts vowels as consonants too.','Reverses the division ratio.'],score_oracle,random_score,['Classify only alphabetic characters.','Count membership in the five-vowel set separately from other letters.','Use integer division for the required floor.','Guard a zero consonant count with the specified zero result.'],'O(n)','O(1)',3),
3823:entry('reverse_letters_and_specials_separately',[('s','str')],'str',['strings','two pointers'],['Keep letter positions and nonletter positions as two separate classes.','Reverse the sequence of letters across letter positions and independently reverse the sequence of special characters across nonletter positions.','Return the reconstructed string.'],[([')ebc#da@f('],'Reversed letters and reversed specials reconstruct (fad@cb#e).'),(['ab#cd!'],'Letters become dcba while specials become !#, yielding dc!ba#.')],[[s] for s in ['a','#','a#','ab#cd! ',')ebc#da@f(','abc','###','a@b','!ab@c#','xy(z)','a!b!c','(@ab)','hello#world','1a2b3c']],REVERSE,[REVERSE.replace("[::-1]",'',1),REVERSE.replace("if char.isalpha() else specials.pop(0)","if not char.isalpha() else specials.pop(0)")],['Leaves letters in their original order.','Places special characters into letter positions.'],reverse_oracle,random_reverse,['Extract letters and nonletters into separate reversed sequences.','Walk the original position pattern.','At a letter position take the next reversed letter; otherwise take the next reversed special.','Each class keeps its positions while reversing its internal order.'],'O(n^2)','O(n)',3),
}
BATCH[3823]['wrong'][1]="def reverse_letters_and_specials_separately(s):\n    return s[::-1]\n"
