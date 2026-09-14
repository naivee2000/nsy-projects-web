"""Repeated minimum multiplication, digit-column key, chess color, binary date, and stable mountains."""
from .import_batch_055 import entry

def state_oracle(a):
    nums,k,multiplier=a;values=nums[:]
    for _ in range(k):
        index=min(range(len(values)),key=lambda i:(values[i],i));values[index]*=multiplier
    return values
def random_state(r):return [[r.randint(1,30) for _ in range(r.randint(1,15))],r.randint(0,30),r.randint(1,5)]
def key_oracle(a):
    strings=[str(value).zfill(4) for value in a]
    return int(''.join(min(chars) for chars in zip(*strings)))
def random_key(r):return [r.randint(1,9999),r.randint(1,9999),r.randint(1,9999)]
def color_oracle(a):
    def parity(square):return (ord(square[0])-ord('a')+int(square[1])-1)%2
    return parity(a[0])==parity(a[1])
def random_color(r):return [r.choice('abcdefgh')+str(r.randint(1,8)),r.choice('abcdefgh')+str(r.randint(1,8))]
def date_oracle(a):return '-'.join(bin(int(part))[2:] for part in a[0].split('-'))
def random_date(r):return [f'{r.randint(1900,2100):04d}-{r.randint(1,12):02d}-{r.randint(1,28):02d}']
def stable_oracle(a):return [i for i in range(1,len(a[0])) if a[0][i-1]>a[1]]
def random_stable(r):return [[r.randint(1,100) for _ in range(r.randint(2,40))],r.randint(1,100)]

STATE='''\
def final_array_after_minimum_multiplications(nums,k,multiplier):
    values=nums[:]
    for _ in range(k):
        index=min(range(len(values)),key=lambda i:(values[i],i))
        values[index]*=multiplier
    return values
'''
KEY='''\
def minimum_digit_column_key(num1,num2,num3):
    values=[str(num1).zfill(4),str(num2).zfill(4),str(num3).zfill(4)]
    return int(''.join(min(column) for column in zip(*values)))
'''
COLOR='''\
def same_chessboard_square_color(coordinate1,coordinate2):
    def parity(square):return (ord(square[0])-ord('a')+int(square[1])-1)%2
    return parity(coordinate1)==parity(coordinate2)
'''
DATE='''\
def date_components_to_binary(date):
    return '-'.join(bin(int(part))[2:] for part in date.split('-'))
'''
STABLE='''\
def stable_mountain_indices(height,threshold):
    return [i for i in range(1,len(height)) if height[i-1]>threshold]
'''

BATCH={
3264:entry('final_array_after_minimum_multiplications',[('nums','list[int]'),('k','int'),('multiplier','int')],'list[int]',['arrays','simulation'],['Repeat exactly k operations on a copied array.','Each operation selects the smallest current value, breaking ties by lowest index, and multiplies it by multiplier.','Return the final array in original index order.'],[([[2,1,3,5,6],5,2],'The selected values evolve at indices 1,0,1,2,0, producing [8,4,6,5,6].'),([[1,2],3,1],'Multiplying by one leaves the array unchanged through all operations.')],[[nums,k,m] for nums,k,m in [([1],0,2),([1],3,2),([2,1,3,5,6],5,2),([1,2],3,1),([1,1],1,2),([1,1],2,2),([5,4,3],2,3),([2,4,8],4,2),([10,1],5,3),([3,3,3],4,2),([1,10,100],6,10),([7,2,5],0,4),([2,9,3,8],3,2),([6,1,6,1],2,5)]],STATE,[STATE.replace('key=lambda i:(values[i],i)','key=lambda i:(values[i],-i)'),STATE.replace('range(k)','range(k-1)')],['Breaks equal minima by the greatest index.','Performs one fewer operation.'],state_oracle,random_state,['The source-I constraints permit direct simulation.','Find the minimum index using a key of current value then index.','Multiply that position and repeat k times on a copy.','Each iteration exactly applies the deterministic operation to the current state.'],'O(k*n)','O(n)',3),
3270:entry('minimum_digit_column_key',[('num1','int'),('num2','int'),('num3','int')],'int',['strings','digits'],['Write each input as exactly four decimal digits by adding leading zeros.','At each digit position choose the smallest of the three digits.','Return the integer represented by the four chosen digits; leading zeros disappear numerically.'],[([1,10,1000],'The padded forms 0001,0010,1000 have minimum digit zero in every column, giving zero.'),([987,879,798],'Column minima form 0777, whose integer value is 777.')],[[a,b,c] for a,b,c in [(1,1,1),(1,10,1000),(987,879,798),(9999,9999,9999),(1234,2345,3456),(1000,100,10),(5,55,555),(8080,8800,8008),(4321,1234,2143),(999,99,9),(1020,2010,2100),(7777,7000,7070),(2468,1357,9999),(5000,400,30)]],KEY,[KEY.replace('min(column)','max(column)'),KEY.replace("zfill(4)","zfill(3)")],['Chooses the largest digit in each column.','Pads to only three places and misaligns shorter inputs.'],key_oracle,random_key,['Normalize all inputs to four-character strings.','Zip equal digit positions across the three strings.','Take the minimum character in each column, concatenate, and convert to int.','Decimal character order matches digit order, and padding makes every place align.'],'O(1)','O(1)',3),
3274:entry('same_chessboard_square_color',[('coordinate1','str'),('coordinate2','str')],'bool',['math','strings','parity'],['Coordinates name chessboard squares from a1 through h8.','Square colors alternate across every rank and file.','Return whether the two squares have the same color.'],[(['a1','c3'],'Both coordinate sums have even parity, so the squares share a color.'),(['a1','h3'],'The coordinate parities differ, so the colors differ.')],[[a,b] for a,b in [('a1','a1'),('a1','b1'),('a1','a2'),('a1','c3'),('a1','h3'),('h8','a1'),('h8','h7'),('d4','f6'),('b2','c3'),('g1','a7'),('c5','d7'),('e8','f7'),('h1','a8'),('b7','g2')]],COLOR,[COLOR.replace('==','!=',1),COLOR.replace("int(square[1])-1","int(square[1])")],['Returns different-color equality instead of same-color equality.','The altered coordinate offset is paired with an asymmetric defect below.'],color_oracle,random_color,['Assign files and ranks zero-based numeric coordinates.','A square color is determined by the parity of file+rank.','Compare this parity for both coordinates.','Moving one square flips parity and color, so equal parity is exactly equal color.'],'O(1)','O(1)',3),
3280:entry('date_components_to_binary',[('date','str')],'str',['strings','binary conversion'],['date is formatted YYYY-MM-DD.','Convert year, month, and day independently to binary without leading zeros.','Join the three binary components with hyphens.'],[(['2080-02-29'],'The components become 100000100000, 10, and 11101.'),(['1900-01-01'],'The month and day each become binary one.')],[[s] for s in ['1900-01-01','2000-12-31','2080-02-29','2024-06-15','1999-09-09','2100-10-10','2001-01-02','2048-08-16','2020-03-04','1980-07-30','2050-11-05','1901-02-03','2099-12-28','2012-04-08']],DATE,[DATE.replace("bin(int(part))[2:]","bin(int(part))"),DATE.replace("date.split('-')","date.split('/')")],['Keeps Python’s 0b binary prefixes.','Splits on slashes instead of the date’s hyphens.'],date_oracle,random_date,['Split the fixed-format date on hyphens.','Parse each component as an integer to discard decimal leading zeros.','Use binary conversion without its 0b prefix and rejoin with hyphens.','Each field is transformed independently and remains in the required year-month-day order.'],'O(length)','O(length)',3),
3285:entry('stable_mountain_indices',[('height','list[int]'),('threshold','int')],'list[int]',['arrays','local comparisons'],['A mountain at index i is stable when the immediately previous mountain’s height exceeds threshold.','Only indices one through n-1 can qualify.','Return all stable indices in increasing order.'],[([[1,2,3,4,5],2],'Previous heights at indices two and three exceed two, so return [3,4].'),([[10,1,10,1],3],'Indices one and three follow height ten, so both are stable.')],[[h,t] for h,t in [([1,2],0),([1,2],1),([1,2],2),([1,2,3,4,5],2),([10,1,10,1],3),([5,4,3],4),([5,4,3],5),([1,10,1],5),([9,9,9],8),([2,8,3,7],6),([100,1],99),([3,1,4,1,5],3),([6,5,4,3],1),([1,1,1,1],0)]],STABLE,[STABLE.replace('height[i-1]>threshold','height[i]>threshold'),STABLE.replace('>threshold','>=threshold')],['Tests the current mountain rather than its predecessor.','Uses an inclusive threshold even though the requirement is strict.'],stable_oracle,random_stable,['Eligibility depends solely on the immediately preceding height.','Enumerate candidate indices from one onward.','Append i exactly when height[i-1] is strictly above threshold.','The scan checks every eligible index once and preserves increasing return order.'],'O(n)','O(output)',3),
}
BATCH[3274]['wrong'][1]='''def same_chessboard_square_color(coordinate1,coordinate2):
    def parity(square):return (ord(square[0])-ord('a')+int(square[1])-1)%2
    return parity(coordinate1)==0
'''
BATCH[3270]['wrong'][1]=KEY.replace('.zfill(4)','')
BATCH[3280]['wrong'][1]="def date_components_to_binary(date):\n    return date\n"
