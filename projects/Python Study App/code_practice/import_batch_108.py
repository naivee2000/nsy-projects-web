"""Opening reviewed group of workbook batch 108."""
from itertools import permutations
from .import_batch_055 import entry
def palindrome_o(a):
 num=a[0];half=num[:len(num)//2];larger=sorted({''.join(value) for value in permutations(half) if ''.join(value)>half})
 if not larger:return ''
 next_half=larger[0];middle=num[len(num)//2] if len(num)%2 else ''
 return next_half+middle+next_half[::-1]
def rpalindrome(r):
 half=''.join(r.choice('123456789') for _ in range(r.randint(1,5)));middle=r.choice('0123456789') if r.random()<.5 else ''
 return [half+middle+half[::-1]]
PALINDROME='''def next_larger_palindrome(num):
 digits=list(num);half=len(digits)//2;pivot=half-2
 while pivot>=0 and digits[pivot]>=digits[pivot+1]:pivot-=1
 if pivot<0:return ''
 successor=half-1
 while digits[successor]<=digits[pivot]:successor-=1
 digits[pivot],digits[successor]=digits[successor],digits[pivot]
 digits[pivot+1:half]=reversed(digits[pivot+1:half])
 for index in range(half):digits[-1-index]=digits[index]
 return ''.join(digits)
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1842:E('next_larger_palindrome',[('num','str')],'str',['strings','two-pointers','permutations'],['num is already a palindrome and contains only decimal digits.','Rearrange the same digits into the smallest strictly larger palindrome, or return an empty string if impossible.'],[(['1221'],'The next permutation of the first half 12 is 21, which mirrors to 2112.'),(['32123'],'The first half 32 has no larger permutation, so no larger palindrome exists.')],[[s] for s in ['11','22','1221','2112','32123','12321','4554','35453','9999','112211','123321','543345','124421','1234321']],PALINDROME,[PALINDROME.replace('digits[pivot]>=digits[pivot+1]','digits[pivot]>digits[pivot+1]'),PALINDROME.replace('digits[successor]<=digits[pivot]','digits[successor]<digits[pivot]')],['Treats equal adjacent digits as an increasing pivot and may return the same palindrome.', 'Allows an equal successor instead of requiring a strictly larger digit.'],palindrome_o,rpalindrome,H('A palindrome is determined completely by its first half and optional center digit.','Find the next lexicographic permutation of the first half.', 'Swap the rightmost ascent pivot with its smallest larger suffix digit, reverse the suffix, then mirror.', 'Next-permutation produces the smallest larger half; mirroring preserves all digits and order comparison, so it produces the smallest larger palindrome.'),'O(n)','O(n)',8),
}
BATCH[1842]['wrong'][0]=PALINDROME.replace("if pivot<0:return ''","if pivot<0:return num")
BATCH[1842]['wrong_reasons'][0]='Returns the unchanged palindrome when no strictly larger rearrangement exists.'
BATCH[1842]['wrong'][1]=PALINDROME.replace('digits[-1-index]=digits[index]','digits[-1-index]=num[-1-index]')
BATCH[1842]['wrong_reasons'][1]='Leaves the original right half instead of mirroring the next-permutation half.'
