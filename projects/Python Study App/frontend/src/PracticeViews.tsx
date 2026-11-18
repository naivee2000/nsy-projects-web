import type { ReactNode } from "react";
import { BookOpen, BrainCircuit, Check, ChevronRight, Gauge, ListChecks } from "lucide-react";

function difficultyLabel(score: number) {
  if (score <= 3) return "Easy";
  if (score <= 7) return "Medium";
  return "Advanced";
}

export function DifficultyPill({ score }: { score: number | "Easy" | "Medium" | "Hard" }) {
  const label = typeof score === "number" ? difficultyLabel(score) : score;
  return <span className={`difficulty difficulty-${label === "Hard" ? "advanced" : label.toLowerCase()}`}>{label}{typeof score === "number" && ` · ${score}`}</span>;
}

export function PracticeCard({ title, summary, topics, difficulty, passed, completedToday, index, onOpen, secondary, children }: {
  title: string; summary: string; topics: string[]; difficulty: number | "Easy" | "Medium" | "Hard";
  passed: boolean; completedToday?: boolean; index: number; onOpen: () => void; secondary?: ReactNode; children?: ReactNode;
}) {
  const checked = completedToday ?? passed;
  return <button className="problem-card" onClick={onOpen}>
    <span className="problem-index" aria-hidden="true">{checked ? <Check size={16} /> : String(index + 1).padStart(2, "0")}</span>
    <span className="problem-card-copy">
      <span className="problem-card-title">{title}{checked && <span className="passed-label"><Check size={12} />{completedToday ? "Done today" : "Passed"}</span>}</span>
      <span className="problem-card-summary">{summary}</span>
      {!!topics.length && <span className="topic-row">{topics.map(topic => <span key={topic}>{topic}</span>)}</span>}
      {children}
    </span>
    <span className="problem-card-meta"><DifficultyPill score={difficulty} />{secondary && <span>{secondary}</span>}</span>
    <ChevronRight size={18} className="card-arrow" />
  </button>;
}

export function EmptyState({ children }: { children: string }) {
  return <div className="empty-state"><BookOpen size={22} /><span>{children}</span></div>;
}

export function SessionHeader({ children, date = new Date() }: { children: ReactNode; date?: Date }) {
  return <header className="page-header">
    <div><span className="eyebrow">TODAY’S SESSION</span><h1>{children}</h1></div>
    <div className="date-card"><span>{new Intl.DateTimeFormat("en", { weekday: "long" }).format(date)}</span>
      <strong>{date.getDate()}</strong><small>{new Intl.DateTimeFormat("en", { month: "short", year: "numeric" }).format(date)}</small></div>
  </header>;
}

export function StudyStats({ solved, total, attempts, mastery }: {
  solved?: number; total?: number; attempts?: number; mastery?: Record<string, number>;
}) {
  const strongest = Object.entries(mastery ?? {}).sort((a,b) => b[1] - a[1])[0];
  return <section className="stat-grid" aria-label="Study progress">
    <div className="stat-card accent"><span><ListChecks size={18} /> SOLVED</span><strong>{solved ?? "—"}<small> / {total ?? "—"}</small></strong>
      <div className="meter"><i style={{ width: `${total ? (solved ?? 0) * 100 / total : 0}%` }} /></div></div>
    <div className="stat-card"><span><BrainCircuit size={18} /> ATTEMPTS</span><strong>{attempts ?? "—"}</strong><small>Every attempt is useful data.</small></div>
    <div className="stat-card"><span><Gauge size={18} /> STRONGEST TOPIC</span><strong className="topic-stat">{strongest?.[0] ?? "Start solving"}</strong>
      <small>{strongest ? `${strongest[1]}% mastery` : "Your roadmap adapts here."}</small></div>
  </section>;
}
