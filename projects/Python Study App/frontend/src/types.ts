export type ProblemSummary = {
  id: string;
  version: number;
  title: string;
  summary: string;
  topics: string[];
  prerequisites: string[];
  difficulty: number;
  estimatedMinutes: number;
  solved: boolean;
};

export type ProblemPage = {
  items: ProblemSummary[];
  total: number;
  catalogTotal: number;
  page: number;
  pageSize: number;
  topics: string[];
};

export type TestCase = {
  id: string;
  arguments: unknown[];
  expected: unknown;
  comparator: "exact" | "float" | "unordered" | "unordered_nested" | "unordered_rows" | "balanced_bst" | "wiggle" | "strict_wiggle";
  visible: boolean;
  explanation?: string;
  expected_node_order?: number[] | null;
};

export type Parameter = { name: string; annotation: string; adapter: "raw" | "listnode" | "listnode_ref" | "treenode" | "treenode_ref"; source_parameter?: number | null };
export type Signature = { name: string; parameters: Parameter[]; returns: string; return_adapter: string; node_policy?: "values" | "reuse_input_nodes" | "return_input_node" | "delete_referenced_list_node"; result_mode?: "return" | "mutated_argument" | "returned_prefix"; mutated_parameter?: number | null; immutable_parameters?: number[] };

export type Problem = {
  id: string;
  version: number;
  title: string;
  summary: string;
  statement: string;
  constraints: string[];
  topics: string[];
  prerequisites: string[];
  difficulty: number;
  estimated_minutes: number;
  target_time_complexity: string;
  target_space_complexity: string;
  signature: Signature;
  starter_code: string;
  tests: TestCase[];
  solved: boolean;
  savedDraft: string;
  revealedHintLevel: number;
  revealedHints: Array<{ level: number; label: string; content: string }>;
};

export type Dashboard = {
  recommendations: ProblemSummary[];
  reviewRecommendations: ProblemSummary[];
  reviewComplete: boolean;
  reviewAssignedCount: number;
  reviewRemainingCount: number;
  dailyComplete: boolean;
  dailyAssignedCount: number;
  dailyRemainingCount: number;
  weeklyChallenge: ProblemSummary | null;
  mastery: Record<string, number>;
  solvedCount: number;
  totalProblems: number;
  attemptCount: number;
};

export type JudgeResult = {
  status: "accepted" | "wrong_answer" | "syntax_error" | "runtime_error" | "timeout";
  message: string;
  runtimeMs: number;
  stdout?: string;
  cases: Array<{ id: string; passed: boolean; actual?: unknown; expected?: unknown; error?: string; visible?: boolean; arguments?: unknown[] }>;
};

export type CoachReply = {
  step: number;
  maxSteps: number;
  title: string;
  observation: string;
  nudge: string;
  question: string;
  canContinue: boolean;
  source: "offline-static-coach" | "codex-cli";
  fallbackReason?: string | null;
};
