"""Read-only production replay preview; all derived writes stay in memory."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from code_practice import database, review_v2
from code_practice.catalog import Catalog, CATALOG_DIR

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--db', type=Path, required=True)
parser.add_argument('--profile', choices=('owner', 'member'), default='owner')
parser.add_argument('--now', type=datetime.fromisoformat, help='ISO timestamp with timezone for a reproducible comparison')
args = parser.parse_args()
now = args.now or datetime.now(timezone.utc)
if now.tzinfo is None:
    parser.error('--now must include a timezone')
source = sqlite3.connect(args.db.resolve().as_uri() + '?mode=ro', uri=True)
con = sqlite3.connect(':memory:')
source.backup(con)
source.close()
con.row_factory = sqlite3.Row
database.apply_migrations(con)
old = {r['problem_id']: str(review_v2.local_day(datetime.fromisoformat(r['due_at']))) for r in con.execute('SELECT problem_id,due_at FROM review_states')}
review_v2.initialize(con)
variants = []
for row in con.execute("SELECT problem_json FROM generated_variants WHERE status='approved'"):
    variant = json.loads(row[0]); variant['status'] = 'approved'; variants.append(variant)
catalog = Catalog(CATALOG_DIR, variants).metadata
rows = review_v2.priorities(con,catalog,now)
changes = Counter('earlier' if r['dueDate'] < old[r['id']] else 'later' if r['dueDate'] > old[r['id']] else 'same'
                  for r in rows if r['dueDate'] and r['id'] in old)
chosen, notes = review_v2.choose(rows,catalog,str(review_v2.local_day(now)),owner_focus=args.profile == 'owner')
print(json.dumps({'sourceUnchanged':True,'dueDateChanges':dict(changes),
    'selectionPolicyVersion':review_v2.SELECTION_POLICY_VERSION, 'profile':args.profile,
    'eligible':dict(Counter('Easy' if r['difficulty']<=3 else 'Medium' if r['difficulty']<=7 else 'Hard' for r in rows if r['status']=='eligible')),
    'previewSelection':[{'id':r['id'],'title':r['title'],'difficulty':r['difficulty'],'score':r['score'],
        'lastAssignmentDate':r['lastAssignmentDate'],'lastSubmissionDate':r['lastSubmissionDate'],
        'olderReviewEligible':r['olderReviewEligible'],'recentRecovery':r['recentRecovery'],
        'reason':r['selectionReason']} for r in chosen],
    'notes':notes},indent=2))
