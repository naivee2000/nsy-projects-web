import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { ArrowLeft, ChevronRight, Flame, Search } from "lucide-react";
import { forProfile } from "./api";
import { EmptyState, PracticeCard, SessionHeader, StudyStats } from "./PracticeViews";
import { ReviewScores } from "./Review";

export type DatabaseLanguage = "mysql" | "pandas";
export type DatabaseItem = {
  id: number; title: string; difficulty: "Easy" | "Medium" | "Hard"; topic: string | null;
  prompt: string; premium: boolean; url: string; runnable: boolean; passedLanguages: DatabaseLanguage[];
  completedToday?: boolean;
};
export type DatabaseOverview = {
  day: string; solved: number; total: number; runnable: number; attemptCount: number; mastery: Record<string, number>;
  dailyAssignment: DatabaseItem[]; reviewAssignment: DatabaseItem[]; newProblems: DatabaseItem[]; reviews: DatabaseItem[]; notes: string[];
};
type LibraryPage = { items: DatabaseItem[]; total: number; pageSize: number; topics: string[] };
type Navigate = (path: string, replace?: boolean) => void;
type Props = { path: string; profile: string; overview?: DatabaseOverview; onNavigate: Navigate };

function useRestoreListScroll(ready: boolean) {
  const restored = useRef(false);
  useLayoutEffect(() => {
    if (!ready || restored.current) return;
    restored.current = true;
    const offset = window.history.state?.databaseScroll;
    if (typeof offset === "number") window.scrollTo(0, offset);
  }, [ready]);
}

function Cards({ items, start = 0, onOpen }: { items: DatabaseItem[]; start?: number; onOpen: (item: DatabaseItem) => void }) {
  return <div className="problem-stack">{items.map((item, i) =>
    <PracticeCard key={item.id} title={item.id + ". " + item.title} summary={item.prompt} topics={item.topic ? [item.topic] : []}
      index={start + i} onOpen={() => onOpen(item)} passed={!!item.passedLanguages.length} completedToday={item.completedToday}
      difficulty={item.difficulty} secondary={!item.runnable ? "Awaiting verification" : item.passedLanguages.length
        ? item.passedLanguages.map(l => l === "mysql" ? "MySQL" : "Pandas").join(" / ") : "MySQL · Pandas"}>
      {item.premium && <span className="study-badges"><span className="study-badge">Premium source</span></span>}
    </PracticeCard>)}</div>;
}

function DatabaseLibrary({ path, profile, overview, onNavigate }: Props) {
  const api = useMemo(() => forProfile(profile), [profile]);
  const query = path.split("?")[1] ?? "";
  const params = new URLSearchParams(query);
  const page = Math.max(1, Number.parseInt(params.get("page") ?? "1", 10) || 1);
  const [data, setData] = useState<LibraryPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useRestoreListScroll(!loading && !!data);
  function filter(key: string, value: string) {
    if (key !== "page") params.delete("page");
    if (!value || value === "all" || (key === "page" && value === "1")) params.delete(key);
    else params.set(key, value);
    const suffix = params.toString();
    onNavigate("/database/library" + (suffix ? "?" + suffix : ""), true);
  }
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError("");
    const timer = window.setTimeout(() => {
      void api<LibraryPage>("/api/database/problems?" + query, { signal: controller.signal })
        .then(reply => { if (!controller.signal.aborted) setData(reply); })
        .catch(e => { if (!controller.signal.aborted) setError(String(e.message)); })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 140);
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [api, query, overview?.attemptCount]);
  return <div className="page library-page">
    <header className="compact-header"><span className="eyebrow">PROBLEM CATALOG</span><h1>Database Library</h1>
      <p>{overview?.total ?? "…"} database problems. {overview?.runnable ?? "…"} are ready to practise in MySQL or Pandas.</p></header>
    <div className="library-tools">
      <label className="search-box"><Search size={18} /><input aria-label="Search Database" maxLength={160}
        placeholder="Search title, number, or topic" value={params.get("search") ?? ""} onChange={e => filter("search", e.target.value)} /></label>
      <select aria-label="Filter by topic" value={params.get("topic") ?? "all"} onChange={e => filter("topic", e.target.value)}>
        <option value="all">All topics</option>{data?.topics.map(topic => <option key={topic}>{topic}</option>)}</select>
      <select aria-label="Filter by difficulty" value={params.get("difficulty") ?? "all"} onChange={e => filter("difficulty", e.target.value)}>
        <option value="all">All levels</option>{["Easy", "Medium", "Hard"].map(v => <option key={v}>{v}</option>)}</select>
      <select aria-label="Filter by completion" value={params.get("completion") ?? "all"} onChange={e => filter("completion", e.target.value)}>
        <option value="all">All problems</option><option value="unsolved">Unsolved</option><option value="passed">Passed</option></select>
      <select aria-label="Filter by availability" value={params.get("playable") ?? "all"} onChange={e => filter("playable", e.target.value)}>
        <option value="all">All entries</option><option value="true">Ready to practise</option></select>
      <span className="result-count">{loading ? "Loading…" : (data?.total ?? 0) + " problems"}</span>
    </div>
    {error && <p role="alert">{error}</p>}
    {!loading && data && <>{data.items.length
      ? <Cards items={data.items} start={(page - 1) * data.pageSize} onOpen={item => onNavigate("/database/problem/" + item.id)} />
      : <EmptyState>No problems match these filters.</EmptyState>}</>}
    <nav className="library-pagination" aria-label="Library pages">
      <button disabled={loading || page === 1} onClick={() => filter("page", String(page - 1))}>Previous</button>
      <span>Page {page} of {Math.max(1, Math.ceil((data?.total ?? 0) / (data?.pageSize ?? 30)))}</span>
      <button disabled={loading || !data || page * data.pageSize >= data.total} onClick={() => filter("page", String(page + 1))}>Next</button>
    </nav>
  </div>;
}

export default function DatabaseHome(props: Props) {
  const { path, profile, overview, onNavigate } = props;
  const route = path.split("?")[0];
  useRestoreListScroll(route !== "/database/library" && !!overview);
  if (route === "/database/library") return <DatabaseLibrary {...props} />;
  const open = (item: DatabaseItem) => onNavigate("/database/problem/" + item.id);
  const review = <section className="section-block review-section">
    <div className="section-heading"><div><span className="section-number">02</span><h2>Review completed problems</h2>
      <p>Up to five due reviews from your passed database problems. A checkmark marks today’s completed review.</p></div>
      <button className="text-button" onClick={() => onNavigate("/database/library?completion=passed")}>See all passed <ChevronRight size={16} /></button></div>
    {overview?.reviewAssignment.length ? <Cards items={overview.reviewAssignment}
      onOpen={item => onNavigate("/database/problem/" + item.id + "?review=" + overview.day)} />
      : <EmptyState>{overview ? "No database reviews are due today." : "Loading your reviews…"}</EmptyState>}
    {!!overview?.notes.length && <details className="review-selection-details"><summary>Review selection details</summary>
      {overview.notes.map(note => <p key={note}>{note}</p>)}</details>}
    <ReviewScores database profile={profile} revision={overview?.attemptCount ?? 0} />
  </section>;
  if (route === "/database/review") return <div className="page">
    <button className="back-button" onClick={() => onNavigate("/database")}><ArrowLeft size={17} /> Back to Today</button>
    <header className="compact-header"><span className="eyebrow">TODAY’S SESSION</span><h1>Database Review</h1></header>{review}
  </div>;
  return <div className="page dashboard-page">
    <SessionHeader date={overview ? new Date(overview.day + "T12:00:00") : undefined}>Database<br /><em>Today</em></SessionHeader>
    <StudyStats solved={overview?.solved} total={overview?.total} attempts={overview?.attemptCount} mastery={overview?.mastery} />
    <section className="section-block">
      <div className="interview-roadmap"><div><span className="eyebrow">YOUR DATABASE PATH</span>
        <h2>{overview?.solved ?? "—"} / {overview?.total ?? "—"} practice problems passed</h2>
        <p>Build from filtering and joins to aggregation, ranking and reshaping. Passing in either language completes a problem.</p></div>
        <button className="text-button" onClick={() => onNavigate("/database/library?completion=unsolved&playable=true")}>See remaining problems <ChevronRight size={16} /></button></div>
      <div className="section-heading"><div><span className="section-number">01</span><h2>Your next problems</h2>
        <p>Five daily credits. Easy = 1, Medium = 2, Hard = 3.</p></div>
        <button className="text-button" onClick={() => onNavigate("/database/library")}>Browse all <ChevronRight size={16} /></button></div>
      {overview?.dailyAssignment.length ? <Cards items={overview.dailyAssignment} onOpen={open} />
        : <EmptyState>{overview ? "No new database problems in today’s saved set." : "Loading your daily recommendations…"}</EmptyState>}
    </section>
    {review}
    <section className="challenge-banner"><div className="challenge-icon"><Flame size={24} /></div>
      <div><span className="eyebrow">CHALLENGE PRACTICE</span><h3>Hard database problems</h3>
        <p>Practise a harder problem from the library.</p></div>
      <button onClick={() => onNavigate("/database/library?difficulty=Hard&playable=true")}>Browse challenges <ChevronRight size={16} /></button>
    </section>
  </div>;
}
