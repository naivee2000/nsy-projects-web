"""Prove source adaptations to unchanged original catalog exercises, offline."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
from math import comb

from .catalog_artifacts import write_json_atomic
from .catalog_evidence import content_digest, judge_contract_hash
from .import_batch_047 import OVERLAP_SPECS

ROOT=Path(__file__).resolve().parent.parent
DECISIONS={
    495:dict(target_id='total-covered-length',source_hash='d90bc83095e4521adf478150326a8c08d0f161748c45fec704bc2b76a036f30f',
        reason='Each attack at t with duration d is the half-open interval [t,t+d); its integer length equals the count of inclusive poisoned seconds t..t+d-1. Total poison time is exactly the existing interval-union length, including overlap, repeated times, gaps, and d=0. The existing sort-and-merge reference handles 10,000 intervals and the full time domain; no new progress ID is needed.'),
    496:dict(target_id='next-greater-values',source_hash='c0c9568dad4ade1d8e3f6d61654d9d7d5431ddb3e70c04ba89136ef02ead7e52',
        reason='The original exercise computes the first strictly greater value to the right for every input position. Source 496 adds only selecting those results for a unique-value subset in query order: zip nums2 to its complete next-greater output, then look up nums1. Its unique 0..10000 inputs are covered by the original arbitrary-integer contract. The mapping takes O(n+m) total time with the original stack; preserve its existing progress ID.'),
    509:dict(target_id='recursive-step-combinations',source_hash='861f81c7998ae17a090daa99c078e921ad360c1b4dadc8b330a01361c8c3d7bb',
        reason='Fibonacci F(n) equals the existing ordered 1/2-step count for n-1 when n>=1; F(0)=0 is explicit. All 31 valid source inputs (0..30) are covered without changing the original 0..30 domain or its ID. An independent binomial placement count verifies the complete source domain and 500 seeded inputs. This is an index/base-case adaptation of the same recurrence, not a new library problem.'),
    525:dict(target_id='longest-target-sum-subarray',source_hash='7c86553f091438f28b95b221bbd2be0cd6df196b6329529110f888eeefa625c1',
        reason='Replacing each binary zero by -1 and each one by +1 makes a segment sum to zero exactly when it has equal zero/one counts. The unchanged original longest target-sum function with target=0 therefore returns exactly the source contiguous length. Its arbitrary-integer domain and O(n) prefix-map reference cover 100,000 binary entries; enumerate subarrays independently on 500 seeded cases and verify full-size boundaries. Preserve the existing progress ID.'),
}


def fibonacci_oracle(args):
    n=args[0]
    return 0 if n==0 else sum(comb(n-1-k,k) for k in range((n-1)//2+1))


def contiguous_oracle(args):
    nums=args[0];best=0
    for left in range(len(nums)):
        zeros=ones=0
        for right in range(left,len(nums)):
            if nums[right]==0:zeros+=1
            else:ones+=1
            if zeros==ones:best=max(best,right-left+1)
    return best


SPECS={**OVERLAP_SPECS,509:dict(params=[('n','int','raw')],
    examples=[([2],'F(2)=1'),([0],'F(0)=0')],
    boundaries=[[n] for n in range(1,30) if n!=2],
    stress=[([30],832040)],oracle=fibonacci_oracle,generator=lambda rng:[rng.randrange(31)]),
    525:dict(params=[('nums','list[int]','raw')],examples=[([[0,1]],'Equal counts'),([[0,1,0]],'Either length-two window')],
        boundaries=[[a] for a in ([0],[1],[1,0],[0,0],[1,1],[0,0,1],[1,1,0],[0,1,1,0],
            [0,0,1,0,0,1],[0,1,1,1,1,1,0,0,0],[0,0,0,1],[1,0,1,0,1],[0,1,0,1,0,1])],
        stress=[([[0,1]*50000],100000),([[0]*100000],0),([[1]*100000],0),
                ([[0]*50000+[1]*50000],100000),([[0]*75000+[1]*25000],50000),
                ([[1]+[0]*99998+[1]],2)],
        oracle=contiguous_oracle,generator=lambda rng:[[rng.randrange(2) for _ in range(rng.randint(1,70))]])}


def implementation_hash():
    digest=hashlib.sha256()
    for name in ('code_practice/reconcile_original_overlaps.py','code_practice/import_batch_047.py'):
        digest.update(name.encode());digest.update((ROOT/name).read_bytes())
    return digest.hexdigest()


def target_payload(source_id):
    from .content import PROBLEMS
    return next(p for p in PROBLEMS if p.id==DECISIONS[source_id]['target_id']).model_dump(mode='json')


def adapted_function(source_id,payload):
    namespace={}
    exec(compile(payload['reference_solution'],'<reviewed-original-overlap>','exec'),namespace)
    function=namespace[payload['signature']['name']]
    if source_id==495:
        return lambda times,duration:function([[t,t+duration] for t in times])
    if source_id==509:
        return lambda n:0 if n==0 else function(n-1)
    if source_id==525:
        return lambda nums:function([1 if bit else -1 for bit in nums],0)
    def query(queries,nums):
        following=dict(zip(nums,function(nums)))
        return [following[value] for value in queries]
    return query


def check_original(source_id,payload,source):
    from .build_import_batch import workbook_sample
    spec=SPECS[source_id]
    solve=adapted_function(source_id,payload)
    sample=workbook_sample(source['sample'],[{'name':p[0]} for p in spec['params']])
    if sample is None or solve(*sample[0])!=sample[1]:
        raise ValueError('Original adaptation disagrees with workbook sample')
    rng=random.Random(4047+source_id)
    small=[a for a,_ in spec['examples']]+spec['boundaries']
    for args in small+[spec['generator'](rng) for _ in range(500)]:
        copied=deepcopy(args)
        if solve(*copied)!=spec['oracle'](args) or copied!=args:
            raise ValueError('Original adaptation disagrees with independent oracle or mutates input')
    for args,expected in spec['stress']:
        copied=deepcopy(args)
        if solve(*copied)!=expected or copied!=args:
            raise ValueError('Original adaptation disagrees with full-size fixture')
    return dict(oracle_inputs=500,oracle_seed=4047+source_id,workbook_sample_checked=True,
                deterministic_inputs=len(small)+len(spec['stress']),
                largest_input={495:10000,496:1000,509:30,525:100000}[source_id],
                exhaustive_domain_inputs=31 if source_id==509 else None,
                adaptation={495:'[t,t+duration) interval union',
                    496:'value-to-result map followed by query-order projection',
                    509:'F(0)=0; F(n)=ordered 1/2-step count(n-1) for n>=1',
                    525:'0 -> -1, 1 -> +1; longest target-sum subarray with target=0'}[source_id])


def validate_original_overlap(record,root=ROOT):
    try:
        source_id=record['source_id'];decision=DECISIONS[source_id]
        report=json.loads((root/record['overlap_report']).read_text())
        if (record['status']!='overlap' or record['existing_id']!=decision['target_id']
            or record['source_hash']!=decision['source_hash'] or not report['valid']
            or report['source_id']!=source_id or report['source_hash']!=record['source_hash']
            or report['target_problem_id']!=decision['target_id'] or report['decision']!=decision
            or report['target_content_sha256']!=content_digest(target_payload(source_id))
            or report['implementation_sha256']!=implementation_hash()
            or report['judge_contract_sha256']!=judge_contract_hash()
            or report['oracle_inputs']<500 or not report['workbook_sample_checked']
            or (source_id==509 and (report.get('exhaustive_domain_inputs')!=31
                                   or report.get('deterministic_inputs')!=31))):
            raise ValueError('Original overlap evidence does not match')
        return report
    except (KeyError,ValueError,TypeError,OSError) as error:
        raise ValueError(f"{record.get('source_id')}: missing, stale, or failing original overlap evidence") from error


def restore_original_overlaps(records,previous,root=ROOT):
    for record in records:
        if record['source_id'] not in DECISIONS:continue
        old=previous.get(record['source_id'],{})
        if old.get('status')!='overlap' or old.get('source_hash')!=record['source_hash']:continue
        try:validate_original_overlap(old,root)
        except ValueError:
            record.update(status='pending',existing_id=None,reason='Original overlap needs revalidation.')
        else:record.update(old)


def reconcile(root=ROOT):
    ledger=json.loads((root/'catalog_import/ledger.json').read_text())
    records={r['source_id']:r for r in ledger['records']}
    sources={s['source_id']:s for s in map(json.loads,(root/'catalog_import/sources.jsonl').read_text().splitlines())}
    for source_id,decision in DECISIONS.items():
        record=records[source_id]
        if record['status'] in ('imported','excluded'):
            raise ValueError('Cannot replace an existing import or exclusion; review draft state explicitly first')
        relative=Path('catalog_import/overlap_reports')/f'leetcode-{source_id}.json'
        try:
            if record['source_hash']!=decision['source_hash'] or content_digest(sources[source_id])!=record['source_hash']:
                raise ValueError('Source changed since review')
            payload=target_payload(source_id)
            evidence=check_original(source_id,payload,sources[source_id])
            report=dict(valid=True,source_id=source_id,source_hash=record['source_hash'],
                target_problem_id=decision['target_id'],target_content_sha256=content_digest(payload),
                implementation_sha256=implementation_hash(),judge_contract_sha256=judge_contract_hash(),
                decision=decision,**evidence)
        except (ValueError,AssertionError,KeyError) as error:
            report=dict(valid=False,source_id=source_id,failures=[str(error)])
            record.update(status='quarantined',existing_id=None,reason='Original overlap proof failed.')
        else:record.update(status='overlap',existing_id=decision['target_id'],reason=decision['reason'])
        write_json_atomic(root/relative,report);record['overlap_report']=str(relative)
    ledger['counts']=dict(Counter(r['status'] for r in ledger['records']))
    write_json_atomic(root/'catalog_import/ledger.json',ledger)
    return ledger['counts']


if __name__=='__main__':
    print(json.dumps(reconcile()))
