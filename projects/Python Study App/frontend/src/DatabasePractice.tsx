import { ArrowLeft, Check, CircleAlert, ExternalLink } from "lucide-react";
import DatabaseHome, { type DatabaseItem, type DatabaseLanguage as Language, type DatabaseOverview } from "./DatabaseHome";
import PracticeWorkspace from "./PracticeWorkspace";
import { DifficultyPill } from "./PracticeViews";
import { reviewGradeLabels } from "./Review";
import { useEffect, useMemo, useRef, useState } from "react";
import { forProfile } from "./api";
export type { DatabaseOverview } from "./DatabaseHome";

type Grade = "again" | "hard" | "good" | "easy";
type Cell = string | number | null;
type TableData = { columns: string[]; rows: Cell[][] };
type Example = { tables: Record<string, TableData>; expected: TableData; parameters: Record<string, Cell> };
type Feedback = { grade: Grade; manualGrade: Grade | null; due: string };
type Problem = DatabaseItem & {
  summary: string; sourceExample: string; advice?: string; officialLanguages: string;
  schema?: Record<string, string[][]>; examples?: Example[]; reviewFeedback: Feedback | null;
  starters?: Record<Language, string>; drafts?: Partial<Record<Language, string>>;
};
type CaseResult = { actual?: TableData; error?: string };
type Verdict = { accepted: boolean; cases: Array<CaseResult & {
  passed: boolean; case: number; expected?: TableData; input?: Record<string, TableData>; parameters?: Record<string, Cell>
}>; review?: Feedback | null };
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
  path: string; profile: string; overview?: DatabaseOverview; onNavigate: (url: string, replace?: boolean) => void;
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
  const [running, setRunning] = useState<"run" | "submit" | null>(null);
  const [resultMode, setResultMode] = useState<"run" | "submit" | null>(null);
  const [ratingBusy, setRatingBusy] = useState(false);
  const [switchingLanguage, setSwitchingLanguage] = useState(false);
  const queue = useRef<Promise<unknown>>(Promise.resolve());
  const persistedDrafts = useRef<Partial<Record<Language, string>>>({});
  const generation = useRef(0);
  const worker = useRef<Worker | null>(null);
  const pending = useRef<{ key: string; id: string } | null>(null);
  useEffect(() => {
    const current = ++generation.current;
    const controller = new AbortController();
    setProblem(null);
    setResult(null);
    setStatus("");
    setRunning(null);
    setResultMode(null);
    setRatingBusy(false);
    setSwitchingLanguage(false);
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
    if (next === language || !problem?.starters || running || switchingLanguage) return;
    const current = generation.current;
    setSwitchingLanguage(true);
    try {
      await saver.current?.();
      if (generation.current !== current) return;
      setDrafts(saved => ({ ...saved, [language]: source }));
      setSource(drafts[next] ?? problem.starters[next]);
      setLanguage(next);
      setResult(null);
      setStatus("");
    } catch (error) {
      if (current === generation.current) setStatus(String(error instanceof Error ? error.message : error));
    } finally {
      if (generation.current === current) setSwitchingLanguage(false);
    }
  }

  async function judge(examples: boolean) {
    if (!problem || running || switchingLanguage) return;
    const current = generation.current;
    const key = JSON.stringify([problem.id, language, source, reviewDay, examples]);
    const request = pending.current?.key === key ? pending.current.id : crypto.randomUUID();
    pending.current = { key, id: request };
    setRunning(examples ? "run" : "submit");
    setResultMode(examples ? "run" : "submit");
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
        setProblem(p => p && { ...p, reviewFeedback: reply.review ?? null, passedLanguages: [...new Set([...p.passedLanguages, language])] });
      }
      if (!examples && !reply.accepted) setProblem(p => p && { ...p, reviewFeedback: null });
      if (!examples) await onRefresh();
    } catch (error) {
      if (current === generation.current) setStatus(String(error instanceof Error ? error.message : error));
    } finally {
      if (current === generation.current) setRunning(null);
    }
  }

  async function rate(grade: Grade | null) {
    if (!problem || ratingBusy) return;
    setRatingBusy(true);
    const current = generation.current;
    try {
      const review = await api<NonNullable<Verdict["review"]>>(`/api/database/problems/${problem.id}/rating`, {
        method: "PUT", body: JSON.stringify({ grade }),
      });
      if (current === generation.current) {
        setProblem(p => p && { ...p, reviewFeedback: review });
        setResult(previous => previous && { ...previous, review });
      }
    } catch (error) {
      if (current === generation.current) setStatus(String(error instanceof Error ? error.message : error));
    } finally {
      if (current === generation.current) setRatingBusy(false);
    }
  }

  async function back() {
    if (!window.history.state?.fromDatabaseList) {
      onNavigate(reviewDay ? "/database/review" : "/database/library");
      return;
    }
    try {
      await saver.current?.();
      window.history.back();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  if (id === null) return <DatabaseHome path={path} profile={profile} overview={overview} onNavigate={onNavigate} />;
  if (!problem || problem.id !== id) return <div className="page">
    <button className="back-button" onClick={() => void back()}><ArrowLeft size={17} /> Back</button>
    <p role={status ? "alert" : "status"}>{status || "Loading problem…"}</p>
  </div>;

  const lines = problem.summary.split(/\r?\n/);
  const metadata = /^(?:Source:|Language evidence:|Premium\. Public reconstruction source:)/i;
  const statement = lines.filter(line => !line.startsWith("Task:") && !metadata.test(line)).join("\n");
  const notes = lines.filter(line => metadata.test(line));
  const feedback = problem.reviewFeedback;
  const instructions = <>
    {reviewDay && <aside className="review-workspace-note"><strong>Fresh review workspace</strong>
      <p>Your earlier solution is saved separately. Today’s review draft resumes when you reopen this problem.</p></aside>}
    {feedback && <aside className="review-feedback" aria-label="Review feedback">
      <strong>How did this feel? <small>Optional</small></strong>
      <p>{feedback.manualGrade ? "Your rating" : "Suggested rating"}: {reviewGradeLabels[feedback.grade]}. Next review {feedback.due}.</p>
      <div className="review-rating-buttons">{(Object.keys(reviewGradeLabels) as Grade[]).map(grade =>
        <button key={grade} disabled={ratingBusy} aria-pressed={feedback.manualGrade === grade} onClick={() => void rate(grade)}>{reviewGradeLabels[grade]}</button>)}</div>
      <button className="text-button" disabled={ratingBusy || !feedback.manualGrade} onClick={() => void rate(null)}>Use suggested rating</button>
    </aside>}
    <p className="problem-lead">{problem.prompt}</p>
    <p className="statement db-prose">{statement}</p>
    {problem.advice && <p className="statement" role="note">{problem.advice}</p>}
    {problem.premium && language === "pandas" && <p className="statement" role="note">Pandas adaptation for this practice site.</p>}
    <h2>Examples</h2>
    {problem.examples?.length ? problem.examples.map((example, index) => <div className="example" key={index}>
      <span>EXAMPLE {index + 1}</span><div className="db-fixture"><Fixture example={example} /></div></div>)
      : <div className="example"><code>{problem.sourceExample}</code></div>}
    {!!notes.length && <details className="db-source-notes"><summary>Source notes</summary>
      {notes.map(note => <p key={note} className="statement db-prose">{note}</p>)}</details>}
    {!problem.runnable && <p className="statement">Awaiting judge verification. This problem is available to read in the library.</p>}
  </>;
  const languageControl = <div className="db-language-switch" role="group" aria-label="Answer language">
    {(["mysql", "pandas"] as const).map(lang => {
      const passed = problem.passedLanguages.includes(lang);
      return <button key={lang} disabled={!!running || switchingLanguage} aria-pressed={language === lang}
        aria-label={labels[lang] + (passed ? " · Passed" : "")} onClick={() => void changeLanguage(lang)}>
        {labels[lang]}{passed && <Check size={14} aria-hidden="true" />}
      </button>;
    })}
  </div>;
  return <>
    {status && <div className="global-error" role="alert"><CircleAlert size={18} />{status}</div>}
    <PracticeWorkspace title={problem.id + ". " + problem.title} topic={problem.topic ?? "Database"} onBack={() => void back()}
      meta={<>{!!problem.passedLanguages.length && <span className="workspace-passed"><Check size={14} /> Passed</span>}
        <DifficultyPill score={problem.difficulty}/>
        <a className="db-source-link" href={problem.url} target="_blank" rel="noreferrer"><ExternalLink size={14} /> Source problem</a></>}
      instructions={instructions} resultStatus={result ? result.accepted ? "accepted" : "wrong_answer" : undefined}
      editor={problem.runnable && problem.starters ? {
        source, language: language === "mysql" ? "sql" : "python", label: languageControl, running,
        modelKey: [profile, id, reviewDay ?? "practice", language].join("/"), readOnly: !!running || switchingLanguage, wordWrap: "on",
        regionLabel: "Database editor", ariaLabel: "Database answer", onChange: setSource,
        onReset: () => setSource(problem.starters![language]), onExecute: mode => void judge(mode === "run"),
      } : undefined}>
      {result && <>
        <div className="result-heading"><h2 className="db-result-heading">{result.accepted ? <Check size={20} /> : <CircleAlert size={20} />}
          {result.accepted ? "All cases passed" : "Some cases did not pass"}</h2>
          <small>{result.cases.filter(c => c.passed).length} / {result.cases.length}</small></div>
        {result.accepted && (resultMode === "run"
          ? <p className="completion-note">Examples passed. Submit to check the hidden tests and save your progress.</p>
          : <p className="completion-note completion-saved"><Check size={14} /> This problem is marked Passed and saved to your progress.</p>)}
        {result.cases.map(item => item.expected ? <details className="case-row db-case" key={item.case} open={!item.passed}>
          <summary>{item.passed ? <Check size={14} /> : <CircleAlert size={14} />} Case {item.case} · {item.passed ? "Passed" : "Failed"}</summary>
          {!!item.error && <code>{item.error}</code>}
          {item.input && Object.entries(item.input).map(([name, table]) => <ResultTable key={name} name={name} data={table} />)}
          {Object.entries(item.parameters ?? {}).map(([key, value]) => <code key={key}>{key} = {display(value)}</code>)}
          <ResultTable name="Expected" data={item.expected} />
          {item.actual && <ResultTable name="Your result" data={item.actual} />}
        </details> : <div key={item.case} className="case-row"><span><Check size={14} /> Case {item.case} · Passed</span></div>)}
      </>}
    </PracticeWorkspace>
  </>;
}
