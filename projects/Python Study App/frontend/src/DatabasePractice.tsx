import Editor from "@monaco-editor/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { forProfile } from "./api";

type Language = "mysql" | "pandas";
type Grade = "again" | "hard" | "good" | "easy";
type Cell = string | number | null;
type TableData = { columns: string[]; rows: Cell[][] };
type Example = { tables: Record<string, TableData>; expected: TableData; parameters: Record<string, Cell> };
type Item = {
  id: number; title: string; difficulty: string; topic: string | null;
  premium: boolean; url: string; runnable: boolean; passedLanguages: Language[];
};
type Problem = Item & {
  summary: string; sourceExample: string; advice?: string; officialLanguages: string;
  schema?: Record<string, string[][]>; examples?: Example[];
  starters?: Record<Language, string>; drafts?: Partial<Record<Language, string>>;
};
export type DatabaseOverview = {
  day: string; solved: number; total: number; runnable: number;
  newProblems: Item[]; reviews: Item[]; notes: string[];
};
type LibraryPage = { items: Item[]; total: number; pageSize: number };
type CaseResult = { actual?: TableData; error?: string };
type Verdict = { accepted: boolean; cases: Array<CaseResult & {
  passed: boolean; case: number; expected?: TableData; input?: Record<string, TableData>; parameters?: Record<string, Cell>
}>; review?: { grade: Grade; due: string } };
const labels: Record<Language, string> = { mysql: "MySQL", pandas: "Pandas" };

function display(value: Cell) {
  return value === null ? "NULL" : String(value);
}

function ResultTable({ name, data }: { name: string; data: TableData }) {
  return <div className="db-table-wrap"><table className="db-table">
    <caption>{name}</caption>
    <thead><tr>{data.columns.map((column, i) => <th key={i} scope="col">{column}</th>)}</tr></thead>
    <tbody>{data.rows.map((row, i) => <tr key={i}>
      {row.map((value, j) => <td key={j} className={value === null ? "db-null" : ""}>{display(value)}</td>)}
    </tr>)}</tbody>
  </table>{!data.rows.length && <p>0 rows</p>}</div>;
}

function Fixture({ example }: { example: Example }) {
  return <>{Object.entries(example.tables).map(([name, data]) => <ResultTable key={name} name={name} data={data} />)}
    {Object.entries(example.parameters).map(([key, value]) => <p key={key}><code>{key} = {display(value)}</code></p>)}
    <ResultTable name="Expected result" data={example.expected} /></>;
}

export function runPandas(worker: Worker, payload: object): Promise<CaseResult[]> {
  return new Promise((resolve, reject) => {
    let timer = window.setTimeout(() => finish(new Error("Pandas could not start. Check the local runtime.")), 25000);
    const finish = (error?: Error, result?: CaseResult[]) => {
      window.clearTimeout(timer);
      worker.terminate();
      if (error) reject(error);
      else resolve(result ?? []);
    };
    worker.onerror = () => finish(new Error("Pandas runtime could not load."));
    worker.onmessage = ({ data }) => {
      if (data.ready) {
        window.clearTimeout(timer);
        timer = window.setTimeout(() => finish(new Error("Pandas exceeded the time limit.")), 5000);
      } else if (data.error) {
        finish(new Error(data.error));
      } else {
        finish(undefined, data.results);
      }
    };
    worker.postMessage(payload);
  });
}

type Props = {
  path: string; profile: string; overview?: DatabaseOverview; onNavigate: (url: string) => void;
  onRefresh: () => Promise<void>; saver: React.MutableRefObject<(() => Promise<unknown>) | null>;
};

export default function DatabasePractice({ path, profile, overview, onNavigate, onRefresh, saver }: Props) {
  const api = useMemo(() => forProfile(profile), [profile]);
  const match = /^\/database\/problem\/(\d+)$/.exec(path.split("?")[0]);
  const id = match ? Number(match[1]) : null;
  const reviewDay = new URLSearchParams(path.split("?")[1]).get("review");
  const [problem, setProblem] = useState<Problem | null>(null);
  const [language, setLanguage] = useState<Language>("mysql");
  const [source, setSource] = useState("");
  const [drafts, setDrafts] = useState<Partial<Record<Language, string>>>({});
  const [result, setResult] = useState<Verdict | null>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("all");
  const [playable, setPlayable] = useState(false);
  const [library, setLibrary] = useState<LibraryPage | null>(null);
  const [exampleIndex, setExampleIndex] = useState(0);
  const queue = useRef<Promise<unknown>>(Promise.resolve());
  const persistedDrafts = useRef<Partial<Record<Language, string>>>({});
  const generation = useRef(0);
  const worker = useRef<Worker | null>(null);
  const pending = useRef<{ key: string; id: string } | null>(null);
  const libraryMode = path === "/database/library";
  const reviewMode = path === "/database/review";

  useEffect(() => {
    const current = ++generation.current;
    const controller = new AbortController();
    setProblem(null);
    setResult(null);
    setStatus("");
    setBusy(false);
    setExampleIndex(0);
    setLanguage("mysql");
    if (id !== null) {
      const suffix = reviewDay ? "?review_day=" + encodeURIComponent(reviewDay) : "";
      void api<Problem>("/api/database/problems/" + id + suffix, { signal: controller.signal }).then(item => {
        if (current === generation.current) {
          setProblem(item);
          persistedDrafts.current = { ...item.starters, ...item.drafts };
          setDrafts(item.drafts ?? {});
          setSource(item.drafts?.mysql ?? item.starters?.mysql ?? "");
        }
      }).catch(error => { if (!controller.signal.aborted) setStatus(String(error.message)); });
    }
    return () => {
      ++generation.current;
      controller.abort();
      worker.current?.terminate();
    };
  }, [api, id, reviewDay, path]);

  useEffect(() => {
    if (!libraryMode) return;
    const controller = new AbortController();
    const params = new URLSearchParams({ search, difficulty, playable: String(playable), page: String(page) });
    void api<LibraryPage>("/api/database/problems?" + params, { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setLibrary(result); })
      .catch(error => { if (!controller.signal.aborted) setStatus(String(error.message)); });
    return () => controller.abort();
  }, [api, libraryMode, search, difficulty, playable, page, overview?.solved]);

  useEffect(() => {
    if (!problem?.runnable || problem.id !== id) return;
    const save = () => {
      const body = JSON.stringify({ source, review_day: reviewDay });
      const current = generation.current;
      queue.current = queue.current.catch(() => {}).then(async () => {
        if (generation.current === current && persistedDrafts.current[language] === source) return;
        await api(`/api/database/problems/${problem.id}/draft/${language}`, { method: "PUT", body });
        if (generation.current === current) persistedDrafts.current[language] = source;
      });
      return queue.current;
    };
    saver.current = save;
    const timer = window.setTimeout(() => {
      void save().catch(error => setStatus(error.message));
    }, 500);
    return () => {
      window.clearTimeout(timer);
      if (saver.current === save) saver.current = null;
    };
  }, [api, problem, id, source, language, reviewDay, saver]);

  async function changeLanguage(next: Language) {
    if (next === language || !problem?.starters) return;
    try {
      await saver.current?.();
      setDrafts(current => ({ ...current, [language]: source }));
      setSource(drafts[next] ?? problem.starters[next]);
      setLanguage(next);
      setResult(null);
      setStatus("");
    } catch (error) {
      setStatus(String(error instanceof Error ? error.message : error));
    }
  }

  async function judge(examples: boolean) {
    if (!problem || busy) return;
    const current = generation.current;
    const key = JSON.stringify([problem.id, language, source, reviewDay, examples]);
    const request = pending.current?.key === key ? pending.current.id : crypto.randomUUID();
    pending.current = { key, id: request };
    setBusy(true);
    setStatus("");
    setResult(null);
    try {
      await saver.current?.();
      let results: CaseResult[] | undefined;
      if (language === "pandas") {
        const pack = await api<object>(`/api/database/problems/${problem.id}/pandas-cases?examples=${examples}`);
        if (current !== generation.current) return;
        worker.current = new Worker("/database-worker.js");
        results = await runPandas(worker.current, { ...pack, source });
      }
      if (current !== generation.current) return;
      const reply = await api<Verdict>(`/api/database/problems/${problem.id}/judge`, { method: "POST",
        body: JSON.stringify({ source, language, request_id: request, review_day: reviewDay, examples, results }) });
      if (current !== generation.current) return;
      setResult(reply);
      pending.current = null;
      if (!examples && reply.accepted) {
        setProblem(p => p && { ...p, passedLanguages: [...new Set([...p.passedLanguages, language])] });
      }
      if (!examples) await onRefresh();
    } catch (error) {
      if (current === generation.current) setStatus(String(error instanceof Error ? error.message : error));
    } finally {
      if (current === generation.current) setBusy(false);
    }
  }

  async function rate(grade: Grade | null) {
    if (!problem) return;
    const current = generation.current;
    try {
      const review = await api<NonNullable<Verdict["review"]>>(`/api/database/problems/${problem.id}/rating`, {
        method: "PUT", body: JSON.stringify({ grade }),
      });
      if (current === generation.current) setResult(previous => previous && { ...previous, review });
    } catch (error) {
      if (current === generation.current) setStatus(String(error instanceof Error ? error.message : error));
    }
  }

  const open = (item: Item, due = false) => onNavigate(
    `/database/problem/${item.id}${due ? "?review=" + overview?.day : ""}`);
  const list = (items: Item[], due = false) => <ul className="db-list">
    {items.map(item => <li key={item.id}><button onClick={() => open(item, due)}>
      <span>{item.id}. {item.title}</span><small>{item.difficulty}{item.topic ? " · " + item.topic : ""}
        {!item.runnable ? " · Awaiting verification" : ""}
        {item.passedLanguages.length ? " · Passed " + item.passedLanguages.map(l => labels[l]).join(" / ") : ""}</small>
    </button></li>)}
  </ul>;

  return <div className="page db-page">
    {status && <div className="global-error" role="alert">{status}</div>}
    {id !== null ? problem && <>
      <h1>{problem.id}. {problem.title}</h1>
      <p>{problem.difficulty}{problem.premium ? " · Premium source" : ""} · <a href={problem.url} target="_blank" rel="noreferrer">Source problem</a></p>
      <div className="db-workspace">
        <section>
          <pre className="db-summary">{problem.summary}</pre>
          {problem.examples?.length ? <>
            <div className="db-nav" aria-label="Examples">{problem.examples.map((_, i) =>
              <button key={i} aria-pressed={i === exampleIndex} onClick={() => setExampleIndex(i)}>Example {i + 1}</button>
            )}</div>
            <Fixture example={problem.examples[exampleIndex]} />
          </> : <pre className="db-summary">{problem.sourceExample}</pre>}
        </section>
        <section aria-label="Database editor">
          {problem.runnable ? <>
            {!!problem.advice && <p>{problem.advice}</p>}
            {problem.premium && language === "pandas" && <p>Pandas adaptation for this practice site.</p>}
            <div className="db-nav" aria-label="Answer language">
              {(["mysql", "pandas"] as const).map(lang => <button key={lang} disabled={busy}
                aria-pressed={language === lang} onClick={() => void changeLanguage(lang)}>
                {labels[lang]}{problem.passedLanguages.includes(lang) ? " · Passed" : ""}
              </button>)}
            </div>
            <Editor height="330px" theme="vs-dark" language={language === "mysql" ? "sql" : "python"}
              options={{ minimap: { enabled: false }, readOnly: busy, ariaLabel: "Database answer", wordWrap: "on" }}
              value={source} onChange={value => setSource(value ?? "")} />
            <div className="db-nav">
              <button disabled={busy} onClick={() => void judge(true)}>Run examples</button>
              <button disabled={busy} onClick={() => void judge(false)}>Submit</button>
              {busy && <span role="status">Checking…</span>}
            </div>
            {result && <section aria-label="Database results">
              <h2>{result.accepted ? "All cases passed" : "Some cases did not pass"}</h2>
              {result.cases.filter(item => item.expected).map(item => <details key={item.case} open={!item.passed}>
                <summary>Case {item.case} · {item.passed ? "Passed" : "Failed"}</summary>
                {!!item.error && <p>{item.error}</p>}
                {item.input && Object.entries(item.input).map(([name, table]) => <ResultTable key={name} name={name} data={table} />)}
                {item.expected && <ResultTable name="Expected" data={item.expected} />}
                {item.actual && <ResultTable name="Your result" data={item.actual} />}
              </details>)}
              {result.review && result.accepted && <div className="db-nav" aria-label="Review feedback">
                <span>Next review {result.review.due}</span>
                {(["again", "hard", "good", "easy"] as const).map(grade => <button key={grade}
                  aria-pressed={result.review?.grade === grade} onClick={() => void rate(grade)}>{grade}</button>)}
                <button onClick={() => void rate(null)}>Use suggested</button>
              </div>}
            </section>}
          </> : <p>Awaiting local judge verification. This problem can be read in the library.</p>}
        </section>
      </div>
    </> : libraryMode ? <><h1>Database Library</h1>
      <div className="db-nav">
        <input aria-label="Search Database" placeholder="Search by title or number" value={search}
          onChange={e => { setPage(1); setSearch(e.target.value); }} />
        <select aria-label="Difficulty" value={difficulty} onChange={e => { setPage(1); setDifficulty(e.target.value); }}>
          {["all", "Easy", "Medium", "Hard"].map(d => <option key={d} value={d}>{d === "all" ? "All difficulty levels" : d}</option>)}
        </select>
        <label><input type="checkbox" checked={playable} onChange={e => { setPage(1); setPlayable(e.target.checked); }} /> Ready to practise</label>
      </div>
      {library && <><p>{library.total} problems</p>{list(library.items)}
        <div className="db-nav">
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page}</span>
          <button disabled={page * library.pageSize >= library.total} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </>}
    </> : <><h1>{reviewMode ? "Database Review" : "Database Today"}</h1>
      {overview && <><p>{overview.solved} passed · {overview.runnable} / {overview.total} ready to practise · {overview.day}</p>
        {!reviewMode && <><h2>New problems</h2>{overview.newProblems.length ?
          list(overview.newProblems) : <p>No new problems remaining today.</p>}</>}
        <h2>Due reviews</h2>{overview.reviews.length ? list(overview.reviews, true) : <p>No Database reviews remaining today.</p>}
        <details><summary>Selection details</summary>{overview.notes.map(note => <p key={note}>{note}</p>)}</details>
      </>}
    </>}
  </div>;
}
