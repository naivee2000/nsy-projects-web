"""Replacement for the twice-quarantined batch-81 matrix candidate."""
from itertools import permutations
from .import_batch_055 import entry

def tiles_oracle(a):
 tiles=a[0];return sum(len(set(permutations(tiles,size))) for size in range(1,len(tiles)+1))

def random_tiles(r):return [''.join(r.choice('ABCDE') for _ in range(r.randint(1,7)))]

TILES='''def count_tile_sequences(tiles):
 from collections import Counter
 counts=Counter(tiles)
 def search():
  answer=0
  for letter in counts:
   if counts[letter]:
    answer+=1;counts[letter]-=1;answer+=search();counts[letter]+=1
  return answer
 return search()
'''

BATCH={1079:entry('count_tile_sequences',[('tiles','str')],'int',['backtracking','counting'],['Tiles contain uppercase letters and length is at most seven.','Count distinct nonempty sequences of every possible length.'],[(['AAB'],'The sequences A,B,AA,AB,BA,AAB,ABA,BAA total eight.'),(['V'],'The sole nonempty sequence is V.')],[[s] for s in ['AA','AB','ABC','AAA','AABC','AAABBC','ABCD','AABB','ABCDE','AAAAAAA','ABCABC','AABBC','XYZ','ZZYX']],TILES,[TILES.replace('answer+=1','answer-=1'),TILES.replace('counts[letter]+=1','counts[letter]-=1')],['Subtracts rather than counts each newly formed sequence.','Fails to restore a tile after recursion, losing valid sibling choices.'],tiles_oracle,random_tiles,['Branch by the next letter value rather than by physical tile index to avoid duplicate sequences.','Track remaining frequency for each distinct letter.','For every positive count, count the new sequence, consume one tile, recurse, and restore it.','Each distinct sequence follows one unique path of letter choices, and all nonempty prefixes are counted.'],'O(unique^n)','O(n+unique)',5)}
BATCH[1079]['wrong'][1]=TILES.replace('if counts[letter]:','if counts[letter]>0:').replace('counts[letter]+=1','pass')
