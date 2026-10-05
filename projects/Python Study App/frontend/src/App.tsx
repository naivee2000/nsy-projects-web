import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import {
  ArrowLeft,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleAlert,
  Clock3,
  Code2,
  Flame,
  Gauge,
  GripHorizontal,
  GripVertical,
  Library,
  Lightbulb,
  ListChecks,
  LoaderCircle,
  Play,
  RotateCcw,
  Search,
  Send,
  Sparkles,
  Target,
  TerminalSquare,
} from "lucide-react";
import type { CoachReply, Dashboard, JudgeResult, Problem, ProblemPage, ProblemSummary, Signature, StudyListBadge, StudyListInfo, TestCase } from "./types";
import { forProfile } from "./api";
import { AccountPanel, useAccount } from "./Accounts";


type View = "dashboard" | "library" | "problem" | "account";
type ProblemOrigin = "dashboard" | "library";
type AttemptEntryPoint = "daily" | "review" | "challenge" | "library";

function difficultyLabel(score: number) {
  if (score <= 3) return "Easy";
  if (score <= 7) return "Medium";
  return "Advanced";
}

function teachingExamples(tests: TestCase[]) {
  const explained = tests.filter((test) => Boolean(test.explanation));
  return explained.length ? explained : tests.slice(0, 2);
}

function testEvidence(item: JudgeResult["cases"][number], flexibleOutput: boolean) {
  return `Test case ${JSON.stringify(item.arguments)}\n${flexibleOutput ? "One valid output" : "Expected"} ${JSON.stringify(item.expected)}`
    + (item.actual !== undefined ? `\nYour code yielded ${JSON.stringify(item.actual)}` : "")
    + (item.error ? `\nError ${item.error}` : "");
}

function clampEditorSplit(requested: number, paneHeight: number) {
  const flexibleHeight = Math.max(1, paneHeight - 110);
  const minimum = Math.max(20, (180 / flexibleHeight) * 100);
  const maximum = Math.min(80, 100 - (130 / flexibleHeight) * 100);
  if (minimum > maximum) return 50;
  return Math.min(maximum, Math.max(minimum, requested));
}

function runJudge(source: string, signature: Signature, tests: TestCase[], timeoutMs = 3000, stopOnFailure = false): Promise<JudgeResult> {
  return new Promise((resolve) => {
    const worker = new Worker("/judge-worker.js");
    let executionTimer: number | undefined;
    const warmupTimer = window.setTimeout(() => {
      worker.terminate();
      resolve({ status: "runtime_error", message: "Python runtime could not start.", cases: [], runtimeMs: 15000 });
    }, 15000);

    worker.onmessage = (event) => {
      if (event.data?.type === "ready") {
        window.clearTimeout(warmupTimer);
        executionTimer = window.setTimeout(() => {
          worker.terminate();
          resolve({ status: "timeout", message: `Execution exceeded ${timeoutMs / 1000} seconds.`, cases: [], runtimeMs: timeoutMs });
        }, timeoutMs);
        worker.postMessage({ source, signature, tests, stopOnFailure });
        return;
      }
      if (event.data?.type === "warmup_error") {
        window.clearTimeout(warmupTimer);
        worker.terminate();
        resolve({ status: "runtime_error", message: event.data.message, cases: [], runtimeMs: 0 });
        return;
      }
      if (executionTimer) window.clearTimeout(executionTimer);
      worker.terminate();
      resolve(event.data as JudgeResult);
    };
    worker.onerror = (event) => {
      window.clearTimeout(warmupTimer);
      if (executionTimer) window.clearTimeout(executionTimer);
      worker.terminate();
      resolve({ status: "runtime_error", message: event.message, cases: [], runtimeMs: 0 });
    };
    worker.postMessage({ type: "warmup" });
  });
}

function fallbackCoach(result: JudgeResult, step: number): CoachReply {
  const safeStep = Math.max(1, Math.min(3, step));
  const nudges = [
    "Trace the first failing example and mark the first variable that differs from your expectation.",
    "Check loop boundaries, return paths, and whether every input position can be visited.",
    "State the invariant your loop or recursion should preserve, then repair only the line that breaks it.",
  ];
  const questions = [
    "What is the first index, character, node, or state your result is missing?",
    "Which branch prevents that state from being processed?",
    "What must be true immediately after every iteration?",
  ];
  return {
    step: safeStep,
    maxSteps: 3,
    title: "Isolate one mistaken assumption",
    observation: result.message,
    nudge: nudges[safeStep - 1],
    question: questions[safeStep - 1],
    canContinue: safeStep < 3,
    source: "offline-static-coach",
  };
}

function DifficultyPill({ score }: { score: number }) {
  return <span className={`difficulty difficulty-${difficultyLabel(score).toLowerCase()}`}>{difficultyLabel(score)} · {score}</span>;
}

function StudyBadges({ lists = [] }: { lists?: StudyListBadge[] }) {
  if (!lists.length) return null;
  return <span className="study-badges">{lists.map((list) => <span className="study-badge" key={list.id} title={`${list.label}: ${list.sourceTitle}${list.match === "equivalent" ? " (existing equivalent exercise)" : ""}`}>{list.label}</span>)}</span>;
}

function ProblemCard({ problem, onOpen, index }: { problem: ProblemSummary; onOpen: (id: string) => void; index?: number }) {
  return (
    <button className="problem-card" onClick={() => onOpen(problem.id)}>
      <span className="problem-index">{problem.solved ? <Check size={16} /> : String((index ?? 0) + 1).padStart(2, "0")}</span>
      <span className="problem-card-copy">
        <span className="problem-card-title">{problem.title}{problem.solved && <span className="passed-label"><Check size={12} /> Passed</span>}</span>
        <span className="problem-card-summary">{problem.summary}</span>
        <span className="topic-row">{problem.topics.slice(0, 3).map((topic) => <span key={topic}>{topic}</span>)}</span>
        <StudyBadges lists={problem.studyLists} />
        {problem.preparationReason && <span className="preparation-reason">{problem.preparationReason}</span>}
      </span>
      <span className="problem-card-meta">
        <DifficultyPill score={problem.difficulty} />
        <span><Clock3 size={14} /> {problem.estimatedMinutes}m</span>
      </span>
      <ChevronRight size={18} className="card-arrow" />
    </button>
  );
}

function EmptyState({ children }: { children: string }) {
  return <div className="empty-state"><BookOpen size={22} /><span>{children}</span></div>;
}

export default function App() {
  const account = useAccount();
  const api = forProfile(account?.session.user?.id ?? "owner");
  const [view, setView] = useState<View>("dashboard");
  const [problemOrigin, setProblemOrigin] = useState<ProblemOrigin>("dashboard");
  const [attemptEntryPoint, setAttemptEntryPoint] = useState<AttemptEntryPoint>("daily");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [libraryTotal, setLibraryTotal] = useState(0);
  const [libraryPage, setLibraryPage] = useState(1);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [libraryRevision, setLibraryRevision] = useState(0);
  const [difficulty, setDifficulty] = useState("all");
  const [studyList, setStudyList] = useState("all");
  const [studyLists, setStudyLists] = useState<StudyListInfo[]>([]);
  const pageSize = 30;
  const [problem, setProblem] = useState<Problem | null>(null);
  const [source, setSource] = useState("");
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("all");
  const [completion, setCompletion] = useState<"all" | "unsolved" | "passed">("all");
  const [result, setResult] = useState<JudgeResult | null>(null);
  const [resultMode, setResultMode] = useState<"run" | "submit" | null>(null);
  const [coach, setCoach] = useState<CoachReply | null>(null);
  const [coaching, setCoaching] = useState(false);
  const [codexThinking, setCodexThinking] = useState(false);
  const [running, setRunning] = useState<"run" | "submit" | null>(null);
  const [error, setError] = useState("");
  const [revealedHints, setRevealedHints] = useState<Array<{ level: number; label: string; content: string }>>([]);
  const [startedAt, setStartedAt] = useState(Date.now());
  const [workspaceSplit, setWorkspaceSplit] = useState(() => {
    try {
      const saved = Number(window.localStorage.getItem("code-practice-workspace-split"));
      return saved >= 30 && saved <= 70 ? saved : 42;
    } catch {
      return 42;
    }
  });
  const [editorSplit, setEditorSplit] = useState(() => {
    try {
      const saved = Number(window.localStorage.getItem("code-practice-editor-split"));
      return saved >= 20 && saved <= 80 ? saved : 55;
    } catch {
      return 55;
    }
  });
  const [resizingWorkspace, setResizingWorkspace] = useState(false);
  const [resizingEditor, setResizingEditor] = useState(false);
  const draftTimer = useRef<number | undefined>();
  const workspaceRef = useRef<HTMLDivElement | null>(null);
  const editorPaneRef = useRef<HTMLElement | null>(null);

  const loadOverview = async () => {
    try {
      const nextDashboard = await api<Dashboard>("/api/dashboard");
      setDashboard(nextDashboard);
      setLibraryRevision((revision) => revision + 1);
      setError("");
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : String(loadError));
    }
  };

  useEffect(() => { void loadOverview(); }, []);

  useEffect(() => {
    if (view !== "library") return;
    const controller = new AbortController();
    let active = true;
    setLibraryLoading(true);
    const timer = window.setTimeout(() => {
      const params = new URLSearchParams({ page: String(libraryPage), page_size: String(pageSize), completion });
      if (query.trim()) params.set("search", query.trim());
      if (topic !== "all") params.set("topic", topic);
      if (studyList !== "all") params.set("study_list", studyList);
      if (difficulty !== "all") {
        const [min, max] = difficulty.split("-");
        params.set("difficulty_min", min);
        params.set("difficulty_max", max);
      }
      void api<ProblemPage>(`/api/problems?${params}`, { signal: controller.signal })
        .then((response) => {
          if (!active) return;
          setProblems(response.items);
          setLibraryTotal(response.total);
          setTopics(response.topics);
          setStudyLists(response.studyLists ?? []);
          setError("");
        })
        .catch((loadError) => {
          if (active) {
            setProblems([]);
            setError(loadError instanceof Error ? loadError.message : String(loadError));
          }
        })
        .finally(() => { if (active) setLibraryLoading(false); });
    }, 180);
    return () => { active = false; controller.abort(); window.clearTimeout(timer); };
  }, [view, libraryPage, completion, query, topic, difficulty, studyList, libraryRevision]);

  useEffect(() => {
    if (!problem || source === problem.savedDraft) return;
    window.clearTimeout(draftTimer.current);
    draftTimer.current = window.setTimeout(() => {
      void api(`/api/problems/${problem.id}/draft`, { method: "PUT", body: JSON.stringify({ source_code: source }) })
        .catch((saveError) => setError(saveError instanceof Error ? saveError.message : String(saveError)));
    }, 800);
    return () => window.clearTimeout(draftTimer.current);
  }, [source, problem]);

  useEffect(() => {
    try {
      window.localStorage.setItem("code-practice-workspace-split", String(workspaceSplit));
    } catch {
      // Resizing should still work when browser storage is unavailable.
    }
  }, [workspaceSplit]);

  useEffect(() => {
    try {
      window.localStorage.setItem("code-practice-editor-split", String(editorSplit));
    } catch {
      // Resizing should still work when browser storage is unavailable.
    }
  }, [editorSplit]);

  useEffect(() => {
    if (!resizingWorkspace) return;

    const resize = (event: PointerEvent) => {
      const bounds = workspaceRef.current?.getBoundingClientRect();
      if (!bounds || bounds.width <= 0) return;
      const requested = ((event.clientX - bounds.left) / bounds.width) * 100;
      setWorkspaceSplit(Math.min(70, Math.max(30, requested)));
    };
    const stop = () => setResizingWorkspace(false);

    document.body.classList.add("workspace-is-resizing");
    window.addEventListener("pointermove", resize);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);
    return () => {
      document.body.classList.remove("workspace-is-resizing");
      window.removeEventListener("pointermove", resize);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
    };
  }, [resizingWorkspace]);

  useEffect(() => {
    if (!resizingEditor) return;

    const resize = (event: PointerEvent) => {
      const bounds = editorPaneRef.current?.getBoundingClientRect();
      if (!bounds || bounds.height <= 0) return;
      const flexibleHeight = Math.max(1, bounds.height - 110);
      const requested = ((event.clientY - bounds.top - 105) / flexibleHeight) * 100;
      setEditorSplit(clampEditorSplit(requested, bounds.height));
    };
    const stop = () => setResizingEditor(false);

    document.body.classList.add("editor-is-resizing");
    window.addEventListener("pointermove", resize);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);
    return () => {
      document.body.classList.remove("editor-is-resizing");
      window.removeEventListener("pointermove", resize);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
    };
  }, [resizingEditor]);

  const resizeWorkspaceWithKeyboard = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const change = event.key === "ArrowLeft" ? -2 : event.key === "ArrowRight" ? 2 : 0;
    if (!change && event.key !== "Home" && event.key !== "End") return;
    event.preventDefault();
    if (event.key === "Home") setWorkspaceSplit(30);
    else if (event.key === "End") setWorkspaceSplit(70);
    else setWorkspaceSplit((current) => Math.min(70, Math.max(30, current + change)));
  };

  const resizeEditorWithKeyboard = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const change = event.key === "ArrowUp" ? -3 : event.key === "ArrowDown" ? 3 : 0;
    if (!change && event.key !== "Home" && event.key !== "End") return;
    event.preventDefault();
    const paneHeight = editorPaneRef.current?.getBoundingClientRect().height || 720;
    if (event.key === "Home") setEditorSplit(clampEditorSplit(0, paneHeight));
    else if (event.key === "End") setEditorSplit(clampEditorSplit(100, paneHeight));
    else setEditorSplit((current) => clampEditorSplit(current + change, paneHeight));
  };

  const openProblem = async (id: string, entryPoint?: AttemptEntryPoint) => {
    try {
      const detail = await api<Problem>(`/api/problems/${id}`);
      if (view === "dashboard" || view === "library") setProblemOrigin(view);
      setAttemptEntryPoint(entryPoint || (view === "library" ? "library" : "daily"));
      setProblem(detail);
      setSource(detail.savedDraft);
      setRevealedHints(detail.revealedHints || []);
      setResult(null);
      setResultMode(null);
      setCoach(null);
      setStartedAt(Date.now());
      setView("problem");
      setError("");
      window.scrollTo({ top: 0 });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : String(loadError));
    }
  };

  const execute = async (mode: "run" | "submit") => {
    if (!problem || running) return;
    setRunning(mode);
    setResult(null);
    setResultMode(mode);
    setCoach(null);
    try {
      const packageData = mode === "submit"
        ? await api<{ signature: Signature; tests: TestCase[]; timeoutMs: number }>(`/api/problems/${problem.id}/submission-package`, { method: "POST" })
        : { signature: problem.signature, tests: teachingExamples(problem.tests), timeoutMs: 3000 };
      const nextResult = await runJudge(source, packageData.signature, packageData.tests, packageData.timeoutMs);
      setResult(nextResult);
      if (nextResult.status !== "accepted") {
        setCoaching(true);
        try {
          const reply = await api<CoachReply>(`/api/problems/${problem.id}/coach`, {
            method: "POST",
            body: JSON.stringify({
              source_code: source,
              status: nextResult.status,
              message: nextResult.message,
              cases: nextResult.cases,
              step: 1,
            }),
          });
          setCoach(reply);
        } catch {
          setCoach(fallbackCoach(nextResult, 1));
        } finally {
          setCoaching(false);
        }
      }
      if (mode === "submit") {
        const passed = nextResult.status === "accepted" ? packageData.tests.length : nextResult.cases.filter((item) => item.passed).length;
        await api("/api/attempts", {
          method: "POST",
          body: JSON.stringify({
            problem_id: problem.id,
            problem_version: problem.version,
            source_code: source,
            result: nextResult.status,
            runtime_ms: nextResult.runtimeMs,
            tests_passed: passed,
            tests_total: packageData.tests.length,
            elapsed_study_seconds: Math.round((Date.now() - startedAt) / 1000),
            hint_level: revealedHints.length,
            entry_point: attemptEntryPoint,
          }),
        });
        if (nextResult.status === "accepted") {
          setProblem((current) => current ? { ...current, solved: true } : current);
        }
        await loadOverview();
      }
    } catch (runError) {
      setResult({ status: "runtime_error", message: runError instanceof Error ? runError.message : String(runError), cases: [], runtimeMs: 0 });
    } finally {
      setRunning(null);
    }
  };

  const askForNextNudge = async () => {
    if (!problem || !result || !coach?.canContinue || coaching) return;
    const nextStep = coach.step + 1;
    setCoaching(true);
    try {
      const reply = await api<CoachReply>(`/api/problems/${problem.id}/coach`, {
        method: "POST",
        body: JSON.stringify({
          source_code: source,
          status: result.status,
          message: result.message,
          cases: result.cases,
          step: nextStep,
        }),
      });
      setCoach(reply);
    } catch {
      setCoach(fallbackCoach(result, nextStep));
    } finally {
      setCoaching(false);
    }
  };

  const askCodexCoach = async () => {
    if (!problem || !result || codexThinking) return;
    setCodexThinking(true);
    try {
      const reply = await api<CoachReply>(`/api/problems/${problem.id}/codex-coach`, {
        method: "POST",
        body: JSON.stringify({
          source_code: source,
          status: result.status,
          message: result.message,
          cases: result.cases,
          step: 3,
        }),
      });
      setCoach(reply);
    } catch {
      setCoach(fallbackCoach(result, 3));
    } finally {
      setCodexThinking(false);
    }
  };

  const revealNextHint = async () => {
    if (!problem || revealedHints.length >= 4) return;
    try {
      const hint = await api<{ level: number; label: string; content: string }>(`/api/problems/${problem.id}/hints/${revealedHints.length + 1}`, { method: "POST" });
      setRevealedHints((current) => [...current, hint]);
    } catch (hintError) {
      setError(hintError instanceof Error ? hintError.message : String(hintError));
    }
  };

  const navigate = (next: View) => {
    setView(next);
    setProblem(null);
    setResult(null);
    setResultMode(null);
    setCoach(null);
  };

  const flexibleTreeOutput = Boolean(problem?.tests.some((test) => test.comparator === "balanced_bst"));
  const bstDeletionOutput = Boolean(problem?.tests.some((test) => test.comparator === "bst_delete"));
  const shortestEncodingOutput = Boolean(problem?.tests.some((test) => test.comparator === "shortest_encoding"));
  const decimalListOutput = Boolean(problem?.tests.some((test) => test.comparator === "float_list"));
  const flexibleWiggleOutput = Boolean(problem?.tests.some((test) => test.comparator === "wiggle"));
  const strictWiggleOutput = Boolean(problem?.tests.some((test) => test.comparator === "strict_wiggle"));
  const unorderedOutput = Boolean(problem?.tests.some((test) => test.comparator === "unordered"));
  const unorderedNestedOutput = Boolean(problem?.tests.some((test) => test.comparator === "unordered_nested"));
  const orderedGroupsOutput = Boolean(problem?.tests.some((test) => test.comparator === "unordered_rows"));
  const flexibleOutput = flexibleTreeOutput || bstDeletionOutput || shortestEncodingOutput || flexibleWiggleOutput || strictWiggleOutput || unorderedOutput || unorderedNestedOutput || orderedGroupsOutput;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate("dashboard")}>
          <span className="brand-mark"><TerminalSquare size={22} /></span>
          <span><strong>Code Practice</strong><small>LOCAL LAB</small></span>
        </button>
        <nav aria-label="Main navigation">
          <button className={view === "dashboard" ? "active" : ""} onClick={() => navigate("dashboard")}><Target size={18} /> Today</button>
          <button className={view === "library" ? "active" : ""} onClick={() => navigate("library")}><Library size={18} /> Library</button>
          {account && <button className={view === "account" ? "active" : ""} onClick={() => navigate("account")}><Gauge size={18} /> {account.session.user?.role === "admin" ? "Accounts" : "My account"}</button>}
          <a href="https://nsyprojects.com/projects"><ArrowLeft size={18} /> Back to Projects</a>
        </nav>
        <div className="sidebar-status">
          <span className="status-dot" />
          <span><strong>{account?.session.user?.username ?? "Local mode"}</strong><small>{account?.session.loginRequired ? "Your personal study progress" : "Progress stays on this computer"}</small></span>
        </div>
      </aside>

      <main>
        {view === "account" && <AccountPanel />}
        {error && <div className="global-error"><CircleAlert size={18} /> {error}</div>}

        {view === "dashboard" && (
          <div className="page dashboard-page">
            <header className="page-header">
              <div><span className="eyebrow">TODAY’S SESSION</span><h1>Build the pattern.<br /><em>Keep the instinct.</em></h1></div>
              <div className="date-card"><span>{new Intl.DateTimeFormat("en", { weekday: "long" }).format(new Date())}</span><strong>{new Date().getDate()}</strong><small>{new Intl.DateTimeFormat("en", { month: "short", year: "numeric" }).format(new Date())}</small></div>
            </header>

            <section className="stat-grid" aria-label="Study progress">
              <div className="stat-card accent"><span><ListChecks size={18} /> SOLVED</span><strong>{dashboard?.solvedCount ?? "—"}<small> / {dashboard?.totalProblems ?? 101}</small></strong><div className="meter"><i style={{ width: `${dashboard ? dashboard.solvedCount / dashboard.totalProblems * 100 : 0}%` }} /></div></div>
              <div className="stat-card"><span><BrainCircuit size={18} /> ATTEMPTS</span><strong>{dashboard?.attemptCount ?? "—"}</strong><small>Every attempt is useful data.</small></div>
              <div className="stat-card"><span><Gauge size={18} /> STRONGEST TOPIC</span><strong className="topic-stat">{dashboard && Object.keys(dashboard.mastery).length ? Object.entries(dashboard.mastery).sort((a,b) => b[1]-a[1])[0][0] : "Start solving"}</strong><small>{dashboard && Object.keys(dashboard.mastery).length ? `${Object.entries(dashboard.mastery).sort((a,b) => b[1]-a[1])[0][1]}% mastery` : "Your roadmap adapts here."}</small></div>
            </section>

            <section className="section-block">
              {dashboard?.interviewProgress && <div className="interview-roadmap">
                <div><span className="eyebrow">YOUR INTERVIEW PATH</span><h2>{dashboard.interviewProgress.solved} / {dashboard.interviewProgress.available} interview picks passed</h2>
                  <p>Build Easy foundations, then related Mediums, then Hard problems. Preparation exercises help unlock your next interview targets.</p>
                  <p>{dashboard.interviewProgress.lists.map((list) => `${list.label}: ${list.solved}/${list.available} available problems passed`).join(" · ")}</p>
                  {dashboard.interviewProgress.remaining === 0 && <p>All currently available interview picks are complete. Keep reviewing; additional list problems will join your path when they are added to the catalog.</p>}
                </div>
                <button className="text-button" onClick={() => { setStudyList("interview-picks"); setCompletion("unsolved"); setQuery(""); setTopic("all"); setDifficulty("all"); setLibraryPage(1); navigate("library"); }}>See remaining picks <ChevronRight size={16} /></button>
              </div>}
              <div className="section-heading"><div><span className="section-number">01</span><h2>Your next problems</h2><p>Interview targets and their foundations. Five Easy; two Medium plus one Easy (or at most three Medium); or one Hard plus at most one Medium.</p></div><button className="text-button" onClick={() => navigate("library")}>Browse all <ChevronRight size={16} /></button></div>
              <div className="problem-stack">
                {dashboard?.recommendations.length
                  ? dashboard.recommendations.map((item, index) => <ProblemCard key={item.id} problem={item} onOpen={(id) => openProblem(id, "daily")} index={index} />)
                  : <EmptyState>{!dashboard ? "Loading your daily recommendations…" : dashboard.dailyComplete ? "Daily session finished — you completed every assigned problem. Come back tomorrow for a new set." : dashboard.interviewProgress?.remaining === 0 ? "All available interview picks passed. Your review section is ready below." : "No new problems in today’s saved set. Review your foundations or practice from the Library; the next daily set will check your readiness again."}</EmptyState>}
              </div>
            </section>

            <section className="section-block review-section">
              <div className="section-heading"><div><span className="section-number">02</span><h2>Review completed problems</h2><p>Three daily focus groups randomly chosen from grid recursion, trees, linked lists, graphs, and heaps, plus up to two random reviews from your completed Hot 100 problems.</p></div><button className="text-button" onClick={() => { setCompletion("passed"); setLibraryPage(1); navigate("library"); }}>See all passed <ChevronRight size={16} /></button></div>
              <div className="problem-stack">
                {dashboard?.reviewRecommendations.length
                  ? dashboard.reviewRecommendations.map((item, index) => <ProblemCard key={item.id} problem={item} onOpen={(id) => openProblem(id, "review")} index={index} />)
                  : <EmptyState>{dashboard?.reviewComplete ? "Review finished — every assigned review problem was checked today." : "Passed problems will appear here for review."}</EmptyState>}
              </div>
            </section>

            <section className="challenge-banner">
              <div className="challenge-icon"><Flame size={24} /></div>
              <div><span className="eyebrow">WEEKLY STRETCH</span><h3>{dashboard?.weeklyChallenge?.title || "Build toward Hard interview problems"}</h3><p>{dashboard?.weeklyChallenge?.summary || "Pass related Medium problems and reach 70% topic mastery to unlock an interview challenge."}</p></div>
              {dashboard?.weeklyChallenge && <button onClick={() => openProblem(dashboard.weeklyChallenge!.id, "challenge")}>Open challenge <ChevronRight size={16} /></button>}
            </section>
          </div>
        )}

        {view === "library" && (
          <div className="page library-page">
            <header className="compact-header"><span className="eyebrow">PROBLEM CATALOG</span><h1>Practice library</h1><p>{dashboard?.totalProblems ?? "…"} coding problems, from fundamentals and recursion basics to advanced interview techniques.</p></header>
            <div className="library-tools">
              <label className="search-box"><Search size={18} /><input value={query} onChange={(event) => { setQuery(event.target.value); setLibraryPage(1); }} placeholder="Search title, topic, or pattern" /></label>
              <select value={topic} onChange={(event) => { setTopic(event.target.value); setLibraryPage(1); }} aria-label="Filter by topic">
                <option value="all">All topics</option>
                {topics.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <select value={difficulty} onChange={(event) => { setDifficulty(event.target.value); setLibraryPage(1); }} aria-label="Filter by difficulty">
                <option value="all">All levels</option><option value="1-3">Easy</option><option value="4-7">Medium</option><option value="8-10">Hard</option>
              </select>
              <select value={completion} onChange={(event) => { setCompletion(event.target.value as "all" | "unsolved" | "passed"); setLibraryPage(1); }} aria-label="Filter by completion">
                <option value="all">All problems</option>
                <option value="unsolved">Unsolved</option>
                <option value="passed">Passed</option>
              </select>
              <select value={studyList} onChange={(event) => { setStudyList(event.target.value); setLibraryPage(1); }} aria-label="Filter by study list">
                <option value="all">All study lists</option>
                <option value="interview-picks">Interview picks (either list)</option>
                <option value="hot-100">Hot 100</option>
                <option value="interview-150">Top Interview 150</option>
              </select>
              <span className="result-count" aria-live="polite">{libraryLoading ? "Loading…" : `${libraryTotal} problems`}</span>
            </div>
            {studyLists.length > 0 && <div className="study-list-note">
              <p>Interview picks are drawn from LeetCode’s official study plans: {studyLists.map((list, index) => <span key={list.id}>{index > 0 && " · "}<a href={list.url} target="_blank" rel="noreferrer">{list.label}</a> ({list.available}/{list.total} available)</span>)}.</p>
              {studyList !== "all" && <p>Includes existing equivalent exercises. Some list problems are not yet available in this app. These lists cover common interview patterns; they are not company-specific frequency rankings.</p>}
            </div>}
            <div className="problem-stack library-list">
              {!libraryLoading && problems.map((item, index) => <ProblemCard key={item.id} problem={item} onOpen={(id) => openProblem(id, "library")} index={(libraryPage - 1) * pageSize + index} />)}
              {!libraryLoading && !problems.length && <EmptyState>No problems match these filters.</EmptyState>}
            </div>
            <nav className="library-pagination" aria-label="Library pages">
              <button disabled={libraryLoading || libraryPage <= 1} onClick={() => setLibraryPage((page) => page - 1)}>Previous</button>
              <span>Page {libraryPage} of {Math.max(1, Math.ceil(libraryTotal / pageSize))}</span>
              <button disabled={libraryLoading || libraryPage * pageSize >= libraryTotal} onClick={() => setLibraryPage((page) => page + 1)}>Next</button>
            </nav>
          </div>
        )}

        {view === "problem" && problem && (
          <div className="workspace-page">
            <header className="workspace-header">
              <button className="back-button" onClick={() => navigate(problemOrigin)}><ArrowLeft size={17} /> Back</button>
              <div className="workspace-title"><span>{problem.topics[0]}</span><h1>{problem.title}</h1></div>
              <div className="workspace-meta">{problem.solved && <span className="workspace-passed"><Check size={14} /> Passed</span>}<DifficultyPill score={problem.difficulty} /><span><Clock3 size={15} /> {problem.estimated_minutes} min</span></div>
            </header>
            <div
              className={`workspace-grid${resizingWorkspace ? " resizing" : ""}`}
              ref={workspaceRef}
              style={{ "--instruction-width": `${workspaceSplit}%` } as React.CSSProperties}
            >
              <section className="problem-pane">
                <StudyBadges lists={problem.studyLists} />
                <p className="problem-lead">{problem.summary}</p>
                <p className="statement">{problem.statement}</p>
                <div className="complexity-row"><span>Target time <strong>{problem.target_time_complexity}</strong></span><span>Target space <strong>{problem.target_space_complexity}</strong></span></div>
                {bstDeletionOutput && <p className="statement" role="note">BST-deletion judging: return any valid BST with exactly the original values except the deleted key. Balancing is not required. The example shows one valid shape, not the only accepted answer.</p>}
                {shortestEncodingOutput && <p className="statement" role="note">Shortest-encoding judging: return any minimum-length encoding that expands to the entire input. Keep the literal input when encoding saves no space. The example shows one valid answer, not the only accepted string.</p>}
                {problem.signature.result_mode === "mutated_argument" && problem.signature.node_policy !== "delete_referenced_list_node" && <p className="statement" role="note">In-place judging: modify {problem.signature.parameters[problem.signature.mutated_parameter ?? 0].name} directly. Output shows that argument after your function runs; a returned copy is not used.</p>}
                {problem.signature.node_policy === "delete_referenced_list_node" && <p className="statement" role="note">Selected-node judging: the input shows the full linked list and the selected node index. Your function receives that actual non-tail node. Output shows the full list after mutation, and the judge checks the original node identities.</p>}
                {problem.signature.node_policy === "preserve_tree_structure" && <p className="statement" role="note">Tree-structure judging: change only integer node values. Keep every original node and its left/right links; rebuilding an identical-looking tree does not count. Temporary traversal links must be restored before returning.</p>}
                {Boolean(problem.signature.immutable_parameters?.length) && <p className="statement" role="note">Read-only input judging: the result is checked together with the requirement that {problem.signature.immutable_parameters!.map((index) => problem.signature.parameters[index].name).join(", ")} remain unchanged.</p>}
                {problem.signature.result_mode === "returned_prefix" && <p className="statement" role="note">In-place judging: return the integer count k and update the first k entries of {problem.signature.parameters[problem.signature.mutated_parameter ?? 0].name}. Output shows both “return” and “prefix”; the remaining entries are ignored.</p>}
                {flexibleTreeOutput && <p className="statement" role="note">Flexible tree judging: any height-balanced BST with the complete input as its inorder traversal is accepted. Preserve duplicate values when present. The displayed tree is only one valid output; its exact shape is not required.</p>}
                {flexibleWiggleOutput && <p className="statement" role="note">Flexible wiggle judging: modify the original list into any permutation that alternates ≤, ≥, ≤, ≥. The displayed arrangement is only one valid output.</p>}
                {strictWiggleOutput && <p className="statement" role="note">Strict wiggle judging: modify the original list into any permutation that alternates &lt;, &gt;, &lt;, &gt;. Adjacent values must not be equal. The displayed arrangement is only one valid output.</p>}
                {unorderedOutput && <p className="statement" role="note">Order-independent judging: return every required result with the correct multiplicity, but the outer list may be in any order. Order inside a path, partition, coordinate, or other nested result still matters.</p>}
                {unorderedNestedOutput && <p className="statement" role="note">Combination judging: the returned combinations may be rearranged, and values inside each combination may also be rearranged. Required duplicates and multiplicities must still be preserved.</p>}
                {orderedGroupsOutput && <p className="statement" role="note">Ordered-group judging: keep the groups in their required order. Values within each group may be rearranged, but every repeated value must be preserved. The displayed grouping is only one valid output.</p>}
                <h2>Examples</h2>
                {decimalListOutput && <p className="statement" role="note">Decimal-list judging: return one finite number per window, in window order. Each value may differ by at most 0.00001. This is an absolute tolerance, not relative error; integers and decimals are both accepted.</p>}
                {teachingExamples(problem.tests).map((test, index) => (
                  <div className="example" key={test.id}>
                    <span>EXAMPLE {index + 1}</span>
                    <code>Input: {JSON.stringify(test.arguments)}{"\n"}{["balanced_bst", "bst_delete", "wiggle", "strict_wiggle", "unordered", "unordered_nested", "unordered_rows", "shortest_encoding"].includes(test.comparator) ? "One valid output" : "Output"}: {JSON.stringify(test.expected)}</code>
                    {test.explanation && <p>{test.explanation}</p>}
                  </div>
                ))}
                <h2>Constraints</h2>
                <ul className="constraints">{problem.constraints.map((item) => <li key={item}>{item}</li>)}</ul>
                <div className="hint-section">
                  <div className="hint-title"><span><Lightbulb size={18} /> Hint ladder</span><small>{revealedHints.length} / 4 revealed</small></div>
                  {revealedHints.map((hint) => <details open={hint.level === revealedHints.length} key={hint.level}><summary>{hint.level}. {hint.label}</summary><p>{hint.content}</p></details>)}
                  {revealedHints.length < 4 && <button className="hint-button" onClick={revealNextHint}><Sparkles size={16} /> Reveal {['concept hint','strategy hint','pseudocode','editorial'][revealedHints.length]}</button>}
                </div>
              </section>
              <div
                className="workspace-divider"
                role="separator"
                aria-label="Resize instructions and code panels"
                aria-orientation="vertical"
                aria-valuemin={30}
                aria-valuemax={70}
                aria-valuenow={Math.round(workspaceSplit)}
                tabIndex={0}
                title="Drag to resize · Double-click to reset"
                onPointerDown={(event) => {
                  if (event.button !== 0) return;
                  event.preventDefault();
                  setResizingWorkspace(true);
                }}
                onDoubleClick={() => setWorkspaceSplit(42)}
                onKeyDown={resizeWorkspaceWithKeyboard}
              >
                <GripVertical size={17} aria-hidden="true" />
              </div>
              <section
                className={`editor-pane${resizingEditor ? " resizing" : ""}`}
                ref={editorPaneRef}
                style={{
                  "--code-share": `${editorSplit}fr`,
                  "--result-share": `${100 - editorSplit}fr`,
                } as React.CSSProperties}
              >
                <div className="editor-toolbar"><span><Code2 size={17} /> Python 3</span><button onClick={() => setSource(problem.starter_code)} title="Reset starter code"><RotateCcw size={16} /> Reset</button></div>
                <Editor
                  height="100%"
                  language="python"
                  theme="vs-dark"
                  value={source}
                  onChange={(value) => setSource(value || "")}
                  options={{ minimap: { enabled: false }, fontSize: 17, lineHeight: 26, padding: { top: 18 }, scrollBeyondLastLine: false, automaticLayout: true, tabSize: 4 }}
                />
                <div className="run-bar">
                  <span className="autosave"><span className="status-dot" /> Draft auto-saves</span>
                  <button className="run-button" disabled={!!running} onClick={() => execute("run")}>
                    {running === "run" ? <LoaderCircle className="spin" size={17} /> : <Play size={17} />} Run examples
                  </button>
                  <button className="submit-button" disabled={!!running} onClick={() => execute("submit")}>
                    {running === "submit" ? <LoaderCircle className="spin" size={17} /> : <Send size={17} />} Submit
                  </button>
                </div>
                <div
                  className="editor-divider"
                  role="separator"
                  aria-label="Resize code editor and results panels"
                  aria-orientation="horizontal"
                  aria-valuemin={20}
                  aria-valuemax={80}
                  aria-valuenow={Math.round(editorSplit)}
                  tabIndex={0}
                  title="Drag to resize · Double-click to reset"
                  onPointerDown={(event) => {
                    if (event.button !== 0) return;
                    event.preventDefault();
                    setResizingEditor(true);
                  }}
                  onDoubleClick={() => setEditorSplit(55)}
                  onKeyDown={resizeEditorWithKeyboard}
                >
                  <GripHorizontal size={17} aria-hidden="true" />
                </div>
                <div className={`result-panel ${result ? `result-${result.status}` : ""}`}>
                  {!result && <div className="result-empty"><TerminalSquare size={21} /><span>Run your code to see test results.</span></div>}
                  {result && <>
                    <div className="result-heading">
                      <span>{result.status === "accepted" ? <Check size={20} /> : <CircleAlert size={20} />} {result.status === "accepted" ? (resultMode === "run" ? "Examples passed" : "Passed") : result.status.replaceAll("_", " ")}</span>
                      <small>{Math.round(result.runtimeMs)} ms</small>
                    </div>
                    <p>{result.message}</p>
                    {result.status === "accepted" && resultMode === "run" && <p className="completion-note">Your code is correct for the examples shown. Submit next to check the hidden tests and mark this problem Passed.</p>}
                    {result.status === "accepted" && resultMode === "submit" && <p className="completion-note completion-saved"><Check size={14} /> This problem is marked Passed and saved to your progress.</p>}
                    {result.status !== "accepted" && resultMode === "submit" && attemptEntryPoint === "challenge" && <p className="completion-note">This challenge attempt is practice-only. It was not added to your attempts, mastery, or future retry schedule.</p>}
                    {result.stdout && <div className="console-output"><span>PRINT OUTPUT</span><pre>{result.stdout}</pre></div>}
                    {result.cases.map((item, index) => resultMode === "submit" && !item.passed ? (
                      <details className="case-row failed-case" key={item.id}>
                        <summary><CircleAlert size={14} /> Hidden test {index + 1} · needs work <span>Click to inspect</span></summary>
                        <code>{testEvidence(item, flexibleOutput)}</code>
                      </details>
                    ) : (
                      <div className="case-row" key={item.id}>
                        <span>{item.passed ? <Check size={14} /> : <CircleAlert size={14} />}{resultMode === "submit" ? "Hidden test" : "Example"} {index + 1} · {item.passed ? "passed" : "needs work"}</span>
                        {resultMode === "run" && <code>{testEvidence(item, flexibleOutput)}</code>}
                      </div>
                    ))}
                    {result.status !== "accepted" && (coach || coaching) && <aside className="coach-card" aria-live="polite">
                      <div className="coach-label"><BrainCircuit size={15} /><span>{coach?.source === "codex-cli" ? "CODEX COACH" : "LOCAL COACH"}</span>{coach && <small>STEP {coach.step} / {coach.maxSteps}</small>}</div>
                      {coaching && !coach ? <div className="coach-loading"><LoaderCircle className="spin" size={16} /> Reading the failed run…</div> : coach && <>
                        <h3>{coach.title}</h3>
                        <p>{coach.observation}</p>
                        <div className="coach-nudge"><strong>Try this next</strong><span>{coach.nudge}</span></div>
                        <div className="coach-question"><strong>Ask yourself</strong><span>{coach.question}</span></div>
                        {coach.fallbackReason && <div className="coach-fallback"><CircleAlert size={14} /> {coach.fallbackReason}</div>}
                        <div className="coach-footer">
                          <small>{coach.source === "codex-cli" ? "Generated through your local Codex CLI · filtered to withhold complete answers" : "Offline analysis · Codex uses your local ChatGPT login only when you explicitly ask"}</small>
                          <div className="coach-actions">
                            {coach.canContinue && <button disabled={coaching || codexThinking} onClick={askForNextNudge}>{coaching ? <LoaderCircle className="spin" size={14} /> : <Sparkles size={14} />} Next offline nudge</button>}
                            {coach.source !== "codex-cli" && (!account || account.session.user?.role === "admin") && <button className="codex-button" disabled={codexThinking || coaching} onClick={askCodexCoach}>{codexThinking ? <LoaderCircle className="spin" size={14} /> : <BrainCircuit size={14} />} {codexThinking ? "Asking Codex…" : "Ask Codex coach"}</button>}
                          </div>
                        </div>
                      </>}
                    </aside>}
                  </>}
                </div>
              </section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
