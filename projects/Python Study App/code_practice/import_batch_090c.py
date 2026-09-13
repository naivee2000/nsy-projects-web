"""Replacement slot completing batch 90 after one candidate quarantine."""
from .import_batch_055 import entry

def maximum_oracle(args):
 text=str(args[0]);values=[int(text)]
 for i,char in enumerate(text):values.append(int(text[:i]+('9' if char=='6' else '6')+text[i+1:]))
 return max(values)
def random_number(rng):return [int(''.join(rng.choice('69') for _ in range(rng.randint(1,9))))]
REFERENCE='''def maximum_69_number(num):
 text=str(num);index=text.find('6')
 return num if index<0 else int(text[:index]+'9'+text[index+1:])
'''
BATCH={1323:entry('maximum_69_number',[('num','int')],'int',['greedy','strings'],
 ['num is positive and contains only digits six and nine.','Change at most one digit and maximize the resulting value.'],
 [([9669],'Changing the first six to nine gives 9969.'),([9999],'No change can improve a number containing only nines.')],
 [[n] for n in [6,9,66,69,96,99,666,669,696,699,966,969,996,6969]],REFERENCE,
 [REFERENCE.replace("text.find('6')","text.rfind('6')"),REFERENCE.replace("'9'","'6'")],
 ['Changes the least significant six instead of the most significant one.','Replaces a six with another six and never improves the number.'],maximum_oracle,random_number,
 ['Changing a more significant digit dominates every less significant change.','Find the leftmost six.','Replace that digit with nine; if no six exists, return the original number.','This adds three times the largest available place value, which is the maximum possible gain.'],
 'O(digits)','O(digits)',3)}
