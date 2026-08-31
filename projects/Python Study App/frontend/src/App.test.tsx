import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import App from "./App";

vi.mock("@monaco-editor/react", () => ({ default: () => <div>Editor</div> }));

const dashboard = {
  recommendations: [{ id: "pair-sum-indices", version: 1, title: "Pair Sum Indices", summary: "Find a pair.", topics: ["arrays"], prerequisites: [], difficulty: 2, estimatedMinutes: 15, solved: false }],
  reviewRecommendations: [{ id: "bracket-balance", version: 1, title: "Bracket Balance", summary: "Validate brackets.", topics: ["stacks"], prerequisites: [], difficulty: 2, estimatedMinutes: 15, solved: true }],
  reviewComplete: false,
  reviewAssignedCount: 1,
  reviewRemainingCount: 1,
  dailyComplete: false,
  dailyAssignedCount: 5,
  dailyRemainingCount: 5,
  weeklyChallenge: null,
  mastery: {},
  solvedCount: 0,
  totalProblems: 100,
  attemptCount: 0,
};

beforeEach(() => {
  window.localStorage.clear();
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.includes("dashboard") ? dashboard : dashboard.recommendations),
  })));
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("shows the daily recommendation and local-only boundary", async () => {
  render(<App />);
  await waitFor(() => expect(screen.getByText("Pair Sum Indices")).toBeInTheDocument());
  expect(screen.getByText("Local mode")).toBeInTheDocument();
  expect(screen.getByText("Your next problems")).toBeInTheDocument();
  expect(screen.getByText("Review completed problems")).toBeInTheDocument();
  expect(screen.getByText("Bracket Balance")).toBeInTheDocument();
});

test("returns from a problem to the page that opened it", async () => {
  const problem = {
    id: "pair-sum-indices",
    version: 1,
    title: "Pair Sum Indices",
    summary: "Find a pair.",
    statement: "Return two indices.",
    constraints: ["Two or more values."],
    topics: ["arrays"],
    prerequisites: [],
    difficulty: 2,
    estimated_minutes: 15,
    target_time_complexity: "O(n)",
    target_space_complexity: "O(n)",
    signature: { name: "pair_sum_indices", parameters: [], returns: "list[int]", return_adapter: "raw" },
    starter_code: "def pair_sum_indices(nums, target): return []",
    savedDraft: "def pair_sum_indices(nums, target): return []",
    tests: [],
    revealedHintLevel: 0,
    revealedHints: [],
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : dashboard.recommendations),
  })));

  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  expect(await screen.findByRole("button", { name: "Back" })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Back" }));
  expect(await screen.findByText("Your next problems")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Library" }));
  expect(await screen.findByText("Practice library")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /Pair Sum Indices/ }));
  fireEvent.click(await screen.findByRole("button", { name: "Back" }));
  expect(await screen.findByText("Practice library")).toBeInTheDocument();
});

test("automatically opens progressive local coaching after a wrong run", async () => {
  const problem = {
    id: "pair-sum-indices",
    version: 1,
    title: "Pair Sum Indices",
    summary: "Find a pair.",
    statement: "Return two indices.",
    constraints: ["Two or more values."],
    topics: ["arrays"],
    prerequisites: [],
    difficulty: 2,
    estimated_minutes: 15,
    target_time_complexity: "O(n)",
    target_space_complexity: "O(n)",
    signature: { name: "pair_sum_indices", parameters: [], returns: "list[int]", return_adapter: "raw" },
    starter_code: "def pair_sum_indices(nums, target): return []",
    savedDraft: "def pair_sum_indices(nums, target): return []",
    tests: [{ id: "example-1", arguments: [[2, 7], 9], expected: [0, 1], comparator: "exact", visible: true, explanation: "The two values add to the target." }],
    revealedHintLevel: 0,
    revealedHints: [],
  };
  const coach = {
    step: 1,
    maxSteps: 3,
    title: "Compare one concrete mismatch",
    observation: "Expected [0, 1], but received [].",
    nudge: "Trace the first missing index.",
    question: "Which position was skipped?",
    canContinue: true,
    source: "offline-static-coach",
  };
  const codexCoach = {
    step: 4,
    maxSteps: 4,
    title: "Inspect the skipped boundary",
    observation: "The final candidate is never considered.",
    nudge: "Trace the highest index reached by the loop.",
    question: "Can the final position be visited?",
    canContinue: false,
    source: "codex-cli",
    fallbackReason: null,
  };

  vi.stubGlobal("fetch", vi.fn((url: string) => {
    const payload = url.includes("codex-coach") ? codexCoach
      : url.endsWith("/coach") ? coach
      : url.endsWith("/pair-sum-indices") ? problem
      : url.includes("dashboard") ? dashboard
      : dashboard.recommendations;
    return Promise.resolve({ ok: true, json: () => Promise.resolve(payload) });
  }));

  class WrongAnswerWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: ErrorEvent) => void) | null = null;
    postMessage(payload: { type?: string }) {
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup"
        ? { type: "ready" }
        : { status: "wrong_answer", message: "A test produced an unexpected result.", runtimeMs: 8, cases: [{ id: "example-1", passed: false, actual: [], expected: [0, 1], visible: true }] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", WrongAnswerWorker);

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  expect(await screen.findByText("The two values add to the target.")).toBeInTheDocument();
  fireEvent.click(await screen.findByRole("button", { name: "Run examples" }));
  expect(await screen.findByText("LOCAL COACH")).toBeInTheDocument();
  expect(screen.getByText("STEP 1 / 3")).toBeInTheDocument();
  expect(screen.getByText("Trace the first missing index.")).toBeInTheDocument();
  expect(screen.queryByText(/seen\[partner\]/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Ask Codex coach" }));
  expect(await screen.findByText("CODEX COACH")).toBeInTheDocument();
  expect(screen.getByText("Trace the highest index reached by the loop.")).toBeInTheDocument();
});

test("resizes the instructions and code panels with the keyboard and remembers the split", async () => {
  const problem = {
    id: "pair-sum-indices",
    version: 1,
    title: "Pair Sum Indices",
    summary: "Find a pair.",
    statement: "Return two indices.",
    constraints: ["Two or more values."],
    topics: ["arrays"],
    prerequisites: [],
    difficulty: 2,
    estimated_minutes: 15,
    target_time_complexity: "O(n)",
    target_space_complexity: "O(n)",
    signature: { name: "pair_sum_indices", parameters: [], returns: "list[int]", return_adapter: "raw" },
    starter_code: "def pair_sum_indices(nums, target): return []",
    savedDraft: "def pair_sum_indices(nums, target): return []",
    tests: [],
    revealedHintLevel: 0,
    revealedHints: [],
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : dashboard.recommendations),
  })));

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  const divider = await screen.findByRole("separator", { name: "Resize instructions and code panels" });
  expect(divider).toHaveAttribute("aria-valuenow", "42");
  fireEvent.keyDown(divider, { key: "ArrowRight" });
  expect(divider).toHaveAttribute("aria-valuenow", "44");
  expect(window.localStorage.getItem("code-practice-workspace-split")).toBe("44");
  fireEvent.doubleClick(divider);
  expect(divider).toHaveAttribute("aria-valuenow", "42");

  const editorDivider = screen.getByRole("separator", { name: "Resize code editor and results panels" });
  expect(editorDivider).toHaveAttribute("aria-valuenow", "55");
  fireEvent.keyDown(editorDivider, { key: "ArrowUp" });
  expect(editorDivider).toHaveAttribute("aria-valuenow", "52");
  expect(window.localStorage.getItem("code-practice-editor-split")).toBe("52");
  fireEvent.doubleClick(editorDivider);
  expect(editorDivider).toHaveAttribute("aria-valuenow", "55");
});

test("marks a problem Passed after a successful full submission", async () => {
  const problem = {
    id: "pair-sum-indices",
    version: 1,
    title: "Pair Sum Indices",
    summary: "Find a pair.",
    statement: "Return two indices.",
    constraints: ["Two or more values."],
    topics: ["arrays"],
    prerequisites: [],
    difficulty: 2,
    estimated_minutes: 15,
    target_time_complexity: "O(n)",
    target_space_complexity: "O(n)",
    signature: { name: "pair_sum_indices", parameters: [], returns: "list[int]", return_adapter: "raw" },
    starter_code: "def pair_sum_indices(nums, target): return [0, 1]",
    savedDraft: "def pair_sum_indices(nums, target): return [0, 1]",
    tests: [],
    solved: false,
    revealedHintLevel: 0,
    revealedHints: [],
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => {
    const payload = url.includes("submission-package")
      ? { signature: problem.signature, tests: [{ id: "hidden-1", arguments: [[2, 7], 9], expected: [0, 1], comparator: "exact", visible: false }], timeoutMs: 3000 }
      : url.endsWith("/pair-sum-indices") ? problem
      : url.includes("dashboard") ? dashboard
      : url.endsWith("/api/problems") ? dashboard.recommendations
      : {};
    return Promise.resolve({ ok: true, json: () => Promise.resolve(payload) });
  }));

  class AcceptedWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: ErrorEvent) => void) | null = null;
    postMessage(payload: { type?: string }) {
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup"
        ? { type: "ready" }
        : { status: "accepted", message: "All hidden tests passed.", runtimeMs: 5, cases: [{ id: "hidden-1", passed: true, visible: false }] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", AcceptedWorker);

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  fireEvent.click(await screen.findByRole("button", { name: "Submit" }));
  expect(await screen.findByText("This problem is marked Passed and saved to your progress.")).toBeInTheDocument();
  expect(screen.getByText("Passed", { selector: ".workspace-passed" })).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith("/api/attempts", expect.objectContaining({ method: "POST" }));
});

test("filters the library to passed or unsolved problems", async () => {
  const libraryProblems = [
    { ...dashboard.recommendations[0], id: "passed-problem", title: "Passed Problem", solved: true },
    { ...dashboard.recommendations[0], id: "unsolved-problem", title: "Unsolved Problem", solved: false },
  ];
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.includes("dashboard") ? dashboard : libraryProblems),
  })));

  render(<App />);
  await waitFor(() => expect(screen.getByText("Pair Sum Indices")).toBeInTheDocument());
  fireEvent.click(screen.getByRole("button", { name: "Library" }));

  const completionFilter = screen.getByRole("combobox", { name: "Filter by completion" });
  fireEvent.change(completionFilter, { target: { value: "passed" } });
  expect(screen.getByText("Passed Problem")).toBeInTheDocument();
  expect(screen.queryByText("Unsolved Problem")).not.toBeInTheDocument();

  fireEvent.change(completionFilter, { target: { value: "unsolved" } });
  expect(screen.getByText("Unsolved Problem")).toBeInTheDocument();
  expect(screen.queryByText("Passed Problem")).not.toBeInTheDocument();
});

test("shows a finished sentence instead of refilling the completed daily set", async () => {
  const finishedDashboard = {
    ...dashboard,
    recommendations: [],
    dailyComplete: true,
    dailyRemainingCount: 0,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.includes("dashboard") ? finishedDashboard : dashboard.recommendations),
  })));

  render(<App />);
  expect(await screen.findByText("Daily session finished — you completed every assigned problem. Come back tomorrow for a new set.")).toBeInTheDocument();
  expect(screen.queryByText("Loading your daily recommendations…")).not.toBeInTheDocument();
});

test("shows a finished sentence after all assigned reviews are checked", async () => {
  const finishedReviews = {
    ...dashboard,
    reviewRecommendations: [],
    reviewComplete: true,
    reviewRemainingCount: 0,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.includes("dashboard") ? finishedReviews : dashboard.recommendations),
  })));

  render(<App />);
  expect(await screen.findByText("Review finished — every assigned review problem was checked today.")).toBeInTheDocument();
});
