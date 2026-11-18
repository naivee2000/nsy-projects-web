import type { CSSProperties, ReactNode } from "react";
import { useWorkspaceSplit } from "./useWorkspaceSplit";
import Editor, { type OnMount } from "@monaco-editor/react";
import { ArrowLeft, Code2, GripHorizontal, GripVertical, LoaderCircle, Play, RotateCcw, Send, TerminalSquare } from "lucide-react";

type Mode = "run" | "submit";

type AnswerEditor = {
  language: "python" | "sql"; label: ReactNode; source: string;
  onChange: (value: string) => void; onReset: () => void; onMount?: OnMount;
  running: Mode | null; onExecute: (mode: Mode) => void; readOnly?: boolean;
  regionLabel?: string; wordWrap?: "on"; ariaLabel?: string; modelKey?: string;
};

type Props = {
  title: string; topic?: string | null; meta: ReactNode; onBack: () => void;
  instructions: ReactNode; editor?: AnswerEditor; resultStatus?: string; children?: ReactNode;
};

export default function PracticeWorkspace({ title, topic, meta, onBack, instructions, editor, resultStatus, children }: Props) {
  const { workspaceSplit, setWorkspaceSplit, editorSplit, setEditorSplit, resizingWorkspace, setResizingWorkspace,
    resizingEditor, setResizingEditor, workspaceRef, editorPaneRef, resizeWorkspaceWithKeyboard, resizeEditorWithKeyboard } = useWorkspaceSplit("database");
  return <div className="workspace-page database-workspace">
    <header className="workspace-header">
      <button className="back-button" onClick={onBack}><ArrowLeft size={17} /> Back</button>
      <div className="workspace-title"><span>{topic}</span><h1>{title}</h1></div>
      <div className="workspace-meta">{meta}</div>
    </header>
    {editor ? <div className={`workspace-grid${resizingWorkspace ? " resizing" : ""}`} ref={workspaceRef}
      style={{ "--instruction-width": `${workspaceSplit}%` } as CSSProperties}>
      <section className="problem-pane">{instructions}</section>
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
      <section className={`editor-pane${resizingEditor ? " resizing" : ""}`} ref={editorPaneRef} aria-label={editor.regionLabel}
        style={{ "--code-share": `${editorSplit}fr`, "--result-share": `${100 - editorSplit}fr` } as CSSProperties}>
        <div className="editor-toolbar">
          <div className="editor-language"><Code2 size={17}/>{editor.label}</div>
          <button onClick={editor.onReset} disabled={editor.readOnly} title="Reset starter code"><RotateCcw size={16} /> Reset</button>
        </div>
        <Editor key={editor.modelKey} height="100%" theme="vs-dark" language={editor.language} value={editor.source} onMount={editor.onMount}
          onChange={value => editor.onChange(value ?? "")}
          options={{ minimap: { enabled: false }, fontSize: 17, lineHeight: 26, padding: { top: 18 }, scrollBeyondLastLine: false,
            automaticLayout: true, tabSize: 4, readOnly: !!editor.readOnly, wordWrap: editor.wordWrap ?? "off", ariaLabel: editor.ariaLabel ?? "Editor content" }} />
        <div className="run-bar">
          <span className="autosave"><span className="status-dot" /> Draft auto-saves</span>
          <button className="run-button" disabled={!!editor.running || editor.readOnly} onClick={() => editor.onExecute("run")}>
            {editor.running === "run" ? <LoaderCircle className="spin" size={17} /> : <Play size={17} />} Run examples
          </button>
          <button className="submit-button" disabled={!!editor.running || editor.readOnly} onClick={() => editor.onExecute("submit")}>
            {editor.running === "submit" ? <LoaderCircle className="spin" size={17} /> : <Send size={17} />} Submit
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
        <div className={`result-panel${resultStatus ? " result-" + resultStatus : ""}`} aria-label="Test results">
          {resultStatus ? children : <div className="result-empty"><TerminalSquare size={21} /><span role="status">
            {editor.running === "run" ? "Running examples…" : editor.running === "submit" ? "Checking submission…" : "Run your code to see test results."}
          </span></div>}
        </div>
      </section>
    </div> : <section className="problem-pane reading-pane">{instructions}</section>}
  </div>;
}
