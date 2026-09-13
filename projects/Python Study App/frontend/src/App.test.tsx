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
  totalProblems: 101,
  attemptCount: 0,
};

const libraryPage = (items = dashboard.recommendations, total = items.length) => ({
  items, total, catalogTotal: 105, page: 1, pageSize: 30, topics: ["arrays", "stacks"],
});

beforeEach(() => {
  window.localStorage.clear();
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.includes("dashboard") ? dashboard : libraryPage()),
  })));
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test.each(["returned_prefix", "mutated_argument"])("explains %s grading beside the examples", async (mode) => {
  const problem = {
    id: "pair-sum-indices", version: 1, title: "Mutation exercise", summary: "Modify the input.",
    statement: "Work in place.", constraints: ["Mutable list."], topics: ["arrays"], prerequisites: [],
    difficulty: 2, estimated_minutes: 15, target_time_complexity: "O(n)", target_space_complexity: "O(1)",
    signature: { name: "compact", parameters: [{ name: "nums", annotation: "list[int]", adapter: "raw" }],
      returns: mode === "returned_prefix" ? "int" : "None", return_adapter: "raw", result_mode: mode, mutated_parameter: 0 },
    starter_code: "def compact(nums): pass", savedDraft: "def compact(nums): pass", tests: [],
    revealedHintLevel: 0, revealedHints: [], solved: false,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({ ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  const note = await screen.findByRole("note");
  expect(note).toHaveTextContent("In-place judging");
  expect(note).toHaveTextContent(mode === "returned_prefix" ? "return the integer count k" : "a returned copy is not used");
  expect(note).toHaveTextContent("nums");
});

test("explains value-only tree recovery without permitting replacement nodes", async () => {
  const problem = {
    id: "pair-sum-indices", version: 1, title: "Recover BST", summary: "Fix two values.",
    statement: "Keep the original links.", constraints: ["Two swapped values."], topics: ["trees"], prerequisites: [],
    difficulty: 6, estimated_minutes: 35, target_time_complexity: "O(n)", target_space_complexity: "O(1)",
    signature: { name: "recover_bst", parameters: [{ name: "root", annotation: "TreeNode | None", adapter: "treenode" }],
      returns: "None", return_adapter: "raw", result_mode: "mutated_argument", mutated_parameter: 0, node_policy: "preserve_tree_structure" },
    starter_code: "def recover_bst(root): pass", savedDraft: "def recover_bst(root): pass", tests: [],
    revealedHintLevel: 0, revealedHints: [], solved: false,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({ ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  const note = await screen.findByText(/Tree-structure judging/);
  expect(note).toHaveTextContent("change only integer node values");
  expect(note).toHaveTextContent("rebuilding an identical-looking tree does not count");
  expect(note).toHaveTextContent("Temporary traversal links must be restored");
});

test.each(["wiggle", "strict_wiggle"])("explains %s inequalities and alternative outputs", async (comparator) => {
  const problem = {
    id: "pair-sum-indices", version: 1, title: "Wiggle exercise", summary: "Arrange the values.",
    statement: "Modify the list.", constraints: ["Integer list."], topics: ["arrays"], prerequisites: [],
    difficulty: 6, estimated_minutes: 35, target_time_complexity: "O(n log n)", target_space_complexity: "O(n)",
    signature: { name: "arrange", parameters: [{ name: "nums", annotation: "list[int]", adapter: "raw" }],
      returns: "None", return_adapter: "raw", result_mode: "mutated_argument", mutated_parameter: 0 },
    starter_code: "def arrange(nums): pass", savedDraft: "def arrange(nums): pass",
    tests: [{ id: "wiggle-example", arguments: [[1, 2, 2, 3]], expected: [2, 3, 1, 2], comparator, visible: true, explanation: "One arrangement." }],
    revealedHintLevel: 0, revealedHints: [], solved: false,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({ ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  const note = await screen.findByText(comparator === "strict_wiggle" ? /Strict wiggle judging/ : /Flexible wiggle judging/);
  expect(note).toHaveTextContent(comparator === "strict_wiggle" ? "<, >, <, >" : "≤, ≥, ≤, ≥");
  if (comparator === "strict_wiggle") expect(note).toHaveTextContent("Adjacent values must not be equal");
  expect(await screen.findByText(/One valid output:/)).toBeInTheDocument();
});

test("explains ordered groups and labels failure evidence as one valid output", async () => {
  const problem = {
    id: "pair-sum-indices", version: 1, title: "Leaf rounds", summary: "Collect leaves.",
    statement: "Return removal rounds.", constraints: ["Keep rounds ordered."], topics: ["trees"], prerequisites: [],
    difficulty: 5, estimated_minutes: 35, target_time_complexity: "O(n)", target_space_complexity: "O(n)",
    signature: { name: "leaf_removal_rounds", parameters: [{ name: "root", annotation: "TreeNode | None", adapter: "treenode" }],
      returns: "list[list[int]]", return_adapter: "raw", result_mode: "return" },
    starter_code: "def leaf_removal_rounds(root): pass", savedDraft: "def leaf_removal_rounds(root): pass",
    tests: [{ id: "leaf-example", arguments: [[1,2,3]], expected: [[2,3],[1]], comparator: "unordered_rows", visible: true, explanation: "Remove both leaves before the root." }],
    revealedHintLevel: 0, revealedHints: [], solved: false,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({ ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));
  class LeafWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    postMessage(payload: { type?: string }) {
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup" ? { type: "ready" }
        : { status: "wrong_answer", message: "Wrong groups.", runtimeMs: 2,
          cases: [{ id: "leaf-example", passed: false, actual: [[1],[2,3]], expected: [[2,3],[1]], arguments: [[1,2,3]], visible: true }] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", LeafWorker);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  expect(await screen.findByRole("note")).toHaveTextContent("keep the groups in their required order");
  expect(screen.getByRole("note")).toHaveTextContent("every repeated value must be preserved");
  fireEvent.click(screen.getByRole("button", { name: "Run examples" }));
  const evidence = await screen.findByText(/Your code yielded/);
  expect(evidence).toHaveTextContent("One valid output [[2,3],[1]]");
  expect(evidence).toHaveTextContent("Your code yielded [[1],[2,3]]");
});

test.each(["balanced_bst", "bst_delete"])("explains %s tree shapes and preserves actual output with a contract error", async (comparator) => {
  const problem = {
    id: "pair-sum-indices", version: 1, title: "Build a balanced tree", summary: "Build a tree.",
    statement: "Return a balanced BST.", constraints: ["Sorted input."], topics: ["trees"], prerequisites: [],
    difficulty: 3, estimated_minutes: 20, target_time_complexity: "O(n)", target_space_complexity: "O(log n)",
    signature: { name: "build", parameters: comparator === "bst_delete"
      ? [{ name: "root", annotation: "TreeNode | None", adapter: "treenode" }, { name: "key", annotation: "int", adapter: "raw" }]
      : [{ name: "nums", annotation: "list[int]", adapter: "raw" }],
      returns: "TreeNode | None", return_adapter: "treenode" },
    starter_code: "def build(nums): pass", savedDraft: "def build(nums): pass",
    tests: [{ id: "tree-example", arguments: comparator === "bst_delete" ? [[2, 1, 3], 2] : [[1, 3]], expected: [3, 1], comparator, visible: true, explanation: "Two shapes are valid." }],
    revealedHintLevel: 0, revealedHints: [], solved: false,
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({ ok: true,
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));
  class TreeWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    postMessage(payload: { type?: string }) {
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup" ? { type: "ready" }
        : { status: "wrong_answer", message: "Tree contract failed.", runtimeMs: 3,
          cases: [{ id: "tree-example", passed: false, actual: [1, 3], expected: [3, 1],
            arguments: [[1, 3]], visible: true, error: "The inorder traversal does not preserve the input." }] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", TreeWorker);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  expect(await screen.findByRole("note")).toHaveTextContent(comparator === "balanced_bst" ? "exact shape is not required" : "Balancing is not required");
  expect(screen.getByText(/One valid output: \[3,1\]/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Run examples" }));
  const evidence = await screen.findByText(/Your code yielded \[1,3\]/);
  expect(evidence).toHaveTextContent("One valid output [3,1]");
  expect(evidence).toHaveTextContent("Error The inorder traversal does not preserve the input.");
});

test("shows the daily recommendation and local-only boundary", async () => {
  render(<App />);
  await waitFor(() => expect(screen.getByText("Pair Sum Indices")).toBeInTheDocument());
  expect(screen.getByText("Local mode")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Back to Projects" })).toHaveAttribute("href", "https://nsyprojects.com/projects");
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
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
  })));

  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  expect(await screen.findByRole("button", { name: "Back" })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Back" }));
  expect(await screen.findByText("Your next problems")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Library" }));
  expect(await screen.findByText("Practice library")).toBeInTheDocument();
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
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
        : { status: "wrong_answer", message: "A test produced an unexpected result.", runtimeMs: 8, cases: [{ id: "example-1", passed: false, actual: [], expected: [0, 1], visible: true, arguments: [[2, 7], 9] }] } } as MessageEvent));
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
    json: () => Promise.resolve(url.endsWith("/pair-sum-indices") ? problem : url.includes("dashboard") ? dashboard : libraryPage()),
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
      ? { signature: problem.signature, tests: [
          { id: "case-1", arguments: [[2, 7], 9], expected: [0, 1], comparator: "exact", visible: false },
          { id: "case-2", arguments: [[3, 2, 4], 6], expected: [1, 2], comparator: "exact", visible: false },
        ], timeoutMs: 3000 }
      : url.endsWith("/pair-sum-indices") ? problem
      : url.includes("dashboard") ? dashboard
      : url.includes("/api/problems?") ? libraryPage()
      : {};
    return Promise.resolve({ ok: true, json: () => Promise.resolve(payload) });
  }));

  class AcceptedWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: ErrorEvent) => void) | null = null;
    postMessage(payload: { type?: string }) {
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup"
        ? { type: "ready" }
        : { status: "accepted", message: "All tests passed.", runtimeMs: 5, cases: [
            { id: "case-1", passed: true, visible: false, expected: [0, 1], actual: [0, 1] },
            { id: "case-2", passed: true, visible: false, expected: [1, 2], actual: [1, 2] },
          ] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", AcceptedWorker);

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  fireEvent.click(await screen.findByRole("button", { name: "Submit" }));
  expect(await screen.findByText("This problem is marked Passed and saved to your progress.")).toBeInTheDocument();
  expect(screen.getByText(/Hidden test 2 · passed/)).toBeInTheDocument();
  expect(screen.queryByText(/Test case \[\[3,2,4\],6\]/)).not.toBeInTheDocument();
  expect(screen.getByText("Passed", { selector: ".workspace-passed" })).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith("/api/attempts", expect.objectContaining({ method: "POST" }));
});

test("reveals a failed hidden test only after its dropdown is opened", async () => {
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
    solved: false,
    revealedHintLevel: 0,
    revealedHints: [],
  };
  const hiddenTests = [
    { id: "case-1", arguments: [[2, 7], 9], expected: [0, 1], comparator: "exact", visible: false },
    { id: "case-2", arguments: [[3, 2, 4], 6], expected: [1, 2], comparator: "exact", visible: false },
  ];
  const coach = {
    step: 1,
    maxSteps: 3,
    title: "Compare one mismatch",
    observation: "One test needs work.",
    nudge: "Trace the input.",
    question: "Which index was skipped?",
    canContinue: false,
    source: "offline-static-coach",
  };
  vi.stubGlobal("fetch", vi.fn((url: string) => {
    const payload = url.includes("submission-package") ? { signature: problem.signature, tests: hiddenTests, timeoutMs: 3000 }
      : url.endsWith("/coach") ? coach
      : url.endsWith("/pair-sum-indices") ? problem
      : url.includes("dashboard") ? dashboard
      : url.includes("/api/problems?") ? libraryPage()
      : {};
    return Promise.resolve({ ok: true, json: () => Promise.resolve(payload) });
  }));

  const submittedJobs: Array<{ stopOnFailure?: boolean; tests?: unknown[] }> = [];
  class FailedHiddenWorker {
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: ErrorEvent) => void) | null = null;
    postMessage(payload: { type?: string; stopOnFailure?: boolean; tests?: unknown[] }) {
      if (!payload.type) submittedJobs.push(payload);
      queueMicrotask(() => this.onmessage?.({ data: payload.type === "warmup"
        ? { type: "ready" }
        : { status: "wrong_answer", message: "A test produced an unexpected result.", runtimeMs: 6, cases: [
            { id: "case-1", passed: true, visible: false, expected: [0, 1], actual: [0, 1] },
            { id: "case-2", passed: false, visible: false, arguments: [[3, 2, 4], 6], expected: [1, 2], actual: [] },
          ] } } as MessageEvent));
    }
    terminate() {}
  }
  vi.stubGlobal("Worker", FailedHiddenWorker);

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Pair Sum Indices/ }));
  fireEvent.click(await screen.findByRole("button", { name: "Submit" }));

  const inspectLabel = await screen.findByText("Click to inspect");
  const details = inspectLabel.closest("details");
  expect(details).not.toHaveAttribute("open");
  expect(screen.getByText(/Hidden test 1 · passed/)).toBeInTheDocument();
  expect(submittedJobs[0].tests).toHaveLength(2);
  expect(submittedJobs[0].stopOnFailure).toBe(false);

  fireEvent.click(inspectLabel.closest("summary")!);
  expect(details).toHaveAttribute("open");
  expect(screen.getByText(/Test case \[\[3,2,4\],6\]/)).toBeInTheDocument();
  expect(screen.getByText(/Expected \[1,2\]/)).toBeInTheDocument();
  expect(screen.getByText(/Your code yielded \[\]/)).toBeInTheDocument();
});

test("filters the library to passed or unsolved problems", async () => {
  const libraryProblems = [
    { ...dashboard.recommendations[0], id: "passed-problem", title: "Passed Problem", solved: true },
    { ...dashboard.recommendations[0], id: "unsolved-problem", title: "Unsolved Problem", solved: false },
  ];
  vi.stubGlobal("fetch", vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => {
      const completion = new URL(url, "http://localhost").searchParams.get("completion");
      const items = libraryProblems.filter((p) => completion === "passed" ? p.solved : completion === "unsolved" ? !p.solved : true);
      return Promise.resolve(url.includes("dashboard") ? dashboard : libraryPage(items));
    },
  })));

  render(<App />);
  await waitFor(() => expect(screen.getByText("Pair Sum Indices")).toBeInTheDocument());
  fireEvent.click(screen.getByRole("button", { name: "Library" }));

  const completionFilter = screen.getByRole("combobox", { name: "Filter by completion" });
  fireEvent.change(completionFilter, { target: { value: "passed" } });
  expect(await screen.findByText("Passed Problem")).toBeInTheDocument();
  expect(screen.queryByText("Unsolved Problem")).not.toBeInTheDocument();

  fireEvent.change(completionFilter, { target: { value: "unsolved" } });
  expect(await screen.findByText("Unsolved Problem")).toBeInTheDocument();
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
