"""Replacement slot completing batch 89 after one candidate quarantine."""
from .import_batch_055 import entry

def hexspeak_oracle(args):
    translated=format(int(args[0]),'X').replace('0','O').replace('1','I')
    return translated if set(translated)<=set('ABCDE FIO'.replace(' ','')) else 'ERROR'

def random_hexspeak(rng):return [str(rng.randint(1,10**12))]

HEXSPEAK='''def decimal_to_hexspeak(num):
 digits='0123456789ABCDEF';value=int(num);answer=''
 while value:answer=digits[value%16]+answer;value//=16
 answer=answer.replace('0','O').replace('1','I')
 return answer if all(char in 'ABCDEFIO' for char in answer) else 'ERROR'
'''

BATCH={1271:entry('decimal_to_hexspeak',[('num','str')],'str',['math','strings'],
 ['num is a decimal string representing an integer from 1 through 10^12.','Return uppercase Hexspeak or ERROR when any hexadecimal digit 2..9 occurs.'],
 [(['257'],'257 is hexadecimal 101, which maps to IOI.'),(['3'],'Hexadecimal 3 is not a Hexspeak character, so return ERROR.')],
 [[str(n)] for n in [1,10,11,15,16,17,26,31,32,160,161,255,256,1000000000000]],
 HEXSPEAK,[HEXSPEAK.replace(".replace('1','I')",""),HEXSPEAK.replace("'ABCDEFIO'","'0123456789ABCDEFIO'")],
 ['Leaves digit one unchanged instead of translating it to I.','Accepts numeric hexadecimal digits that make the representation invalid.'],
 hexspeak_oracle,random_hexspeak,
 ['Convert the decimal value to uppercase hexadecimal first.','Translate hexadecimal zero to O and one to I.','Reject the result if any character lies outside A–F, I, and O.','The conversion fixes the digit sequence; the final alphabet test exactly implements Hexspeak validity.'],
 'O(log num)','O(log num)',3)}
