"""Prove source adaptations to unchanged original catalog exercises, offline."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random

from .catalog_artifacts import write_json_atomic
from .catalog_evidence import content_digest, judge_contract_hash
from .import_batch_047 import OVERLAP_SPECS

ROOT=Path(__file__).resolve().parent.parent
DECISIONS={
    495:dict(target_id='total-covered-length',source_hash='d90bc83095e4521adf478150326a8c08d0f161748c45fec704bc2b76a036f30f',
        reason='Each attack at t with duration d is the half-open interval [t,t+d); its integer length equals the count of inclusive poisoned seconds t..t+d-1. Total poison time is exactly the existing interval-union length, including overlap, repeated times, gaps, and d=0. The existing sort-and-merge reference handles 10,000 intervals and the full time domain; no new progress ID is needed.'),
    496:dict(target_id='next-greater-values',source_hash='c0c9568dad4ade1d8e3f6d61654d9d7d5431ddb3e70c04ba89136ef02ead7e52',
        reason='The original exercise computes the first strictly greater value to the right for every input position. Source 496 adds only selecting those results for a unique-value subset in query order: zip nums2 to its complete next-greater output, then look up nums1. Its unique 0..10000 inputs are covered by the original arbitrary-integer contract. The mapping takes O(n+m) total time with the original stack; preserve its existing progress ID.'),
}


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
    def query(queries,nums):
        following=dict(zip(nums,function(nums)))
        return [following[value] for value in queries]
    return query


def check_original(source_id,payload,source):
    from .build_import_batch import workbook_sample
    spec=OVERLAP_SPECS[source_id]
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
                largest_input=10000 if source_id==495 else 1000,
                adaptation='[t,t+duration) interval union' if source_id==495 else 'value-to-result map followed by query-order projection')


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
            or report['oracle_inputs']<500 or not report['workbook_sample_checked']):
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
