import { useEffect, useRef, useState } from "react";

function clampEditorSplit(requested: number, paneHeight: number) {
  const flexibleHeight = Math.max(1, paneHeight - 110);
  const minimum = Math.max(20, (180 / flexibleHeight) * 100);
  const maximum = Math.min(80, 100 - (130 / flexibleHeight) * 100);
  if (minimum > maximum) return 50;
  return Math.min(maximum, Math.max(minimum, requested));
}

export function useWorkspaceSplit(track: "algorithms" | "database") {
  const prefix = track === "algorithms" ? "code-practice" : "code-practice-database";
  const workspaceKey = prefix + "-workspace-split";
  const editorKey = prefix + "-editor-split";
  const [workspaceSplit, setWorkspaceSplit] = useState(() => {
    try {
      const saved = Number(window.localStorage.getItem(workspaceKey));
      return saved >= 30 && saved <= 70 ? saved : 42;
    } catch {
      return 42;
    }
  });
  const [editorSplit, setEditorSplit] = useState(() => {
    try {
      const saved = Number(window.localStorage.getItem(editorKey));
      return saved >= 20 && saved <= 80 ? saved : 55;
    } catch {
      return 55;
    }
  });
  const [resizingWorkspace, setResizingWorkspace] = useState(false);
  const [resizingEditor, setResizingEditor] = useState(false);
  const workspaceRef = useRef<HTMLDivElement | null>(null);
  const editorPaneRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    try {
      window.localStorage.setItem(workspaceKey, String(workspaceSplit));
    } catch {
      // Resizing should still work when browser storage is unavailable.
    }
  }, [workspaceSplit, workspaceKey]);

  useEffect(() => {
    try {
      window.localStorage.setItem(editorKey, String(editorSplit));
    } catch {
      // Resizing should still work when browser storage is unavailable.
    }
  }, [editorSplit, editorKey]);

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

  return { workspaceSplit, setWorkspaceSplit, editorSplit, setEditorSplit, resizingWorkspace, setResizingWorkspace,
    resizingEditor, setResizingEditor, workspaceRef, editorPaneRef, resizeWorkspaceWithKeyboard, resizeEditorWithKeyboard };
}
