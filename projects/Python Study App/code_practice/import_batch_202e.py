"""Case and vowel-normalized spellchecking."""
from .import_batch_055 import entry

def _mask(word):return ''.join('*' if c in 'aeiou' else c for c in word.lower())

def spell_oracle(args):
    words,queries=args;answer=[]
    for query in queries:
        if query in words:answer.append(query);continue
        match=next((word for word in words if word.lower()==query.lower()),None)
        if match is not None:answer.append(match);continue
        answer.append(next((word for word in words if _mask(word)==_mask(query)),''))
    return answer

def random_spell(rng):
    alphabet='bcdfghjklmnpqrstvwxyz';vowels='aeiou'
    words=[]
    while len(words)<rng.randint(1,16):
        word=''.join(rng.choice(alphabet+vowels) for _ in range(rng.randint(1,7)))
        if word.lower() not in {item.lower() for item in words}:
            words.append(''.join(c.upper() if rng.random()<.35 else c for c in word))
    queries=[]
    for _ in range(rng.randint(1,16)):
        if rng.random()<.75:
            query=rng.choice(words)
            query=''.join((rng.choice(vowels) if c.lower() in vowels and rng.random()<.5 else c) for c in query)
            query=''.join(c.upper() if rng.random()<.4 else c.lower() for c in query)
        else:query=''.join(rng.choice(alphabet+vowels) for _ in range(rng.randint(1,7)))
        queries.append(query)
    return [words,queries]

SPELL='''def vowel_spellchecker(wordlist,queries):
    def mask(word):return ''.join('*' if c in 'aeiou' else c for c in word)
    exact=set(wordlist);lower={};vowels={}
    for word in wordlist:
        folded=word.lower();lower.setdefault(folded,word);vowels.setdefault(mask(folded),word)
    answer=[]
    for query in queries:
        if query in exact:answer.append(query)
        elif query.lower() in lower:answer.append(lower[query.lower()])
        else:answer.append(vowels.get(mask(query.lower()),''))
    return answer
'''

EXAMPLES=[
    ([['KiTe','kite','hare','Hare'],['kite','Kite','KiTe','Hare','HARE','Hear','hear','keti','keet','keto']], 'Exact case wins first; otherwise the first case-insensitive or vowel-normalized match is returned.'),
    ([['yellow'],['YellOw']], 'Ignoring capitalization matches the sole dictionary word yellow.'),
]
CASES=[
    [['KiTe','kite','hare','Hare'],['kite','Kite','KiTe','Hare','HARE','Hear','hear','keti','keet','keto']],
    [['yellow'],['YellOw']],
    [['a'],['a','A','e','b']],
    [['Apple','apply'],['apple','Opple','APPLY']],
    [['YellOw','yellow'],['yellow','yollow']],
    [['dog','Dig','dug'],['dag','DIG','Dug']],
    [['hello','hallo'],['hullo','HELLO']],
    [['cat'],['cut','cot','cit','cet']],
    [['Case','case'],['CASE','case','Case']],
    [['boat','boot'],['beat','BOOT']],
    [['rhythm'],['RHYTHM','rhythms']],
    [['A','e','I'],['o','i','E']],
    [['stone','stOne'],['STONE','stane']],
    [['abc','Abc','ebc'],['ABC','ibc','xbc']],
]

BATCH={966:entry(
    'vowel_spellchecker',[('wordlist','list[str]'),('queries','list[str]')],'list[str]',
    ['strings','hash maps'],
    ['Words contain only English letters and have length one through seven.','Apply matching precedence: exact case, then first case-insensitive match, then first vowel-normalized match.','Treat a, e, i, o, and u as interchangeable only in the third matching stage; return an empty string when no rule matches.'],
    EXAMPLES,CASES,SPELL,
    [SPELL.replace('lower.setdefault(folded,word)','lower[folded]=word'),SPELL.replace("elif query.lower() in lower","elif False")],
    ['Overwrites the first capitalization match with the last matching word.','Skips capitalization matches and can choose the wrong vowel-normalized candidate.'],
    spell_oracle,random_spell,
    ['Matching precedence matters as much as normalization.','Store the first word for each lowercase key and each vowel-masked lowercase key.','Check the exact set, lowercase map, and vowel map in that order for each query.','First-write maps preserve wordlist priority, and the three ordered lookups exactly implement the specification.'],
    'O(total word and query characters)','O(total wordlist characters)',5,
)}
