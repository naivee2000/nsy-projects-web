import { useEffect, useState } from "react";
import { forProfile } from "./api";
import type { ReviewEvent, ReviewGrade, ReviewPriority } from "./types";

const labels: Record<ReviewGrade, string> = {
  again: "Need more review", hard: "Hard to finish", good: "Finished independently", easy: "Very easy",
};

export function ReviewFeedback({ event, profile, onChange }: {
  event: ReviewEvent; profile: string; onChange: (event: ReviewEvent) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const rate = async (grade: ReviewGrade | null) => {
    setBusy(true);
    try {
      const next = await forProfile(profile)<ReviewEvent>(`/api/reviews/events/${event.id}/feedback`, {
        method: "PUT", body: JSON.stringify({ grade }),
      });
      onChange(next); setError("");
    } catch (e) { setError(String(e)); }
    finally { setBusy(false); }
  };
  return <aside className="review-feedback" aria-label="Review feedback">
    <strong>How did this feel? <small>Optional</small></strong>
    <p>{event.manualGrade ? "Your rating" : "Automatic rating"}: {labels[event.effectiveGrade]}. Next due: {event.dueDate}.</p>
    <div className="review-rating-buttons">{(Object.keys(labels) as ReviewGrade[]).map(grade =>
      <button key={grade} aria-pressed={event.manualGrade === grade} disabled={busy} onClick={() => void rate(grade)}>{labels[grade]}</button>)}</div>
    <button className="text-button" disabled={busy || !event.manualGrade} onClick={() => void rate(null)}>Use automatic rating</button>
    {error && <p role="alert">{error}</p>}
  </aside>;
}

export function ReviewScores({ profile, revision }: { profile: string; revision: number }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<{ items: ReviewPriority[]; total: number; asOf: string } | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setLoading(true);
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams({ search, status, page: String(page) });
      void forProfile(profile)<typeof data>(`/api/reviews/priorities?${params}`, { signal: controller.signal })
        .then(value => { if (!controller.signal.aborted) { setData(value); setError(""); } })
        .catch(e => { if (!controller.signal.aborted) setError(String(e)); })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 180);
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [open, search, status, page, profile, revision]);
  return <details className="review-scores" onToggle={e => setOpen(e.currentTarget.open)}>
    <summary>Review scores, due dates and cooldowns</summary>
    {open && <>
      <p>Current priority = urgency (up to 70) + recent struggle (up to 30). Saved daily order also considers DP, Medium and topic coverage.</p>
      <div className="review-score-tools">
        <input aria-label="Search review scores" placeholder="Search review scores" value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
        <select aria-label="Filter review status" value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="all">All problems</option><option value="assigned">Today's saved set</option>
          <option value="eligible">Due and eligible</option><option value="not_due">Not due</option>
          <option value="cooldown">Cooling down</option><option value="retry">Needs retry</option><option value="unlearned">Not yet passed</option>
        </select>
      </div>
      {error && <p role="alert">{error}</p>}
      <div className="review-score-table" aria-busy={loading}><table>
        <thead><tr><th>Problem</th><th>Priority</th><th>Next due</th><th>Cooldown ends</th></tr></thead>
        <tbody>{data?.items.map(row => <tr key={row.id}>
          <td><details><summary>{row.title} <small>{row.difficulty <= 3 ? "Easy" : row.difficulty <= 7 ? "Medium" : "Hard"}</small></summary>
            <p>{row.reason}</p><p>Urgency: {row.urgency?.toFixed(2) ?? "—"}; recent struggle: {row.recentStruggle?.toFixed(2) ?? "—"}.</p>
            {row.assignedToday && <p>Saved selection: {row.assignmentReason} Score at selection: {row.assignmentScore?.toFixed(2) ?? "not recorded"}.</p>}
            {row.inferred && <p>Historical rating inferred from submissions.</p>}
          </details></td>
          <td>{row.score?.toFixed(2) ?? "—"}</td><td>{row.dueDate ?? "—"}</td>
          <td>{row.cooldownUntil ?? "—"}{row.recoveryException && <small>Recovery exception when due</small>}</td>
        </tr>)}</tbody>
      </table></div>
      <div className="library-pagination">
        <button disabled={loading || page === 1} onClick={() => setPage(page-1)}>Previous</button>
        <span>{data?.total ?? 0} problems · Page {page}</span>
        <button disabled={loading || !data || page*30 >= data.total} onClick={() => setPage(page+1)}>Next</button>
      </div>
    </>}
  </details>;
}
