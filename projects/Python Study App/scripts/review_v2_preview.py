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
args = parser.parse_args()
source = sqlite3.connect(f'file:{args.db.resolve()}?mode=ro', uri=True)
con = sqlite3.connect(':memory:')
source.backup(con)
source.close()
con.row_factory = sqlite3.Row
for sql in database.MIGRATION_4_STATEMENTS:
    con.execute(sql)
old = {r['problem_id']: str(review_v2.local_day(datetime.fromisoformat(r['due_at']))) for r in con.execute('SELECT problem_id,due_at FROM review_states')}
review_v2.initialize(con)
variants = []
for row in con.execute("SELECT problem_json FROM generated_variants WHERE status='approved'"):
    variant = json.loads(row[0]); variant['status'] = 'approved'; variants.append(variant)
catalog = Catalog(CATALOG_DIR, variants).metadata
now = datetime.now(timezone.utc)
rows = review_v2.priorities(con,catalog,now)
changes = Counter('earlier' if r['dueDate'] < old[r['id']] else 'later' if r['dueDate'] > old[r['id']] else 'same'
                  for r in rows if r['dueDate'] and r['id'] in old)
chosen, notes = review_v2.choose(rows,catalog,str(review_v2.local_day(now)))
print(json.dumps({'sourceUnchanged':True,'dueDateChanges':dict(changes),
    'eligible':dict(Counter('Easy' if r['difficulty']<=3 else 'Medium' if r['difficulty']<=7 else 'Hard' for r in rows if r['status']=='eligible')),
    'previewSelection':[{'title':r['title'],'difficulty':r['difficulty'],'score':r['score'],'reason':r['selectionReason']} for r in chosen],
    'notes':notes},indent=2))
