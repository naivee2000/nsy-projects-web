import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, expect, test, vi } from "vitest";
import { ReviewFeedback, ReviewScores } from "./Review";
import type { ReviewEvent } from "./types";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

const initial: ReviewEvent = { id: 3, problemId: "p", date: "2026-11-03", automaticGrade: "good",
  manualGrade: null, effectiveGrade: "good", latestResult: "accepted", dueDate: "2026-11-10", inferred: false };

test("optional feedback uses the automatic grade and can be overridden or cleared", async () => {
  vi.stubGlobal("fetch", vi.fn((_url, options) => {
    const grade = JSON.parse(options.body).grade;
    return Promise.resolve({ ok: true, json: async () => ({ ...initial, manualGrade: grade,
      effectiveGrade: grade ?? "good", dueDate: grade === "easy" ? "2026-11-17" : initial.dueDate }) });
  }));
  function Wrapper() { const [event,setEvent] = useState(initial); return <ReviewFeedback event={event} onChange={setEvent} profile="owner" />; }
  render(<Wrapper />);
  expect(screen.getByText(/Suggested rating: Finished independently/)).toBeInTheDocument();
  expect(screen.queryByText(/2026-11-10/)).not.toBeInTheDocument();
  expect(fetch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Very easy" }));
  expect(await screen.findByText(/Your rating: Very easy/)).toBeInTheDocument();
  expect(screen.getByText("Review less often.")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Very easy" })).toHaveAttribute("aria-pressed","true");
  fireEvent.click(screen.getByRole("button", { name: "Use suggested rating" }));
  expect(await screen.findByText(/Suggested rating: Finished independently/)).toBeInTheDocument();
  expect(vi.mocked(fetch).mock.calls[0][1]?.headers).toMatchObject({ "X-Study-Profile": "owner" });
});

test("correction answer is saved independently of the manual rating", async () => {
  vi.stubGlobal("fetch", vi.fn((_url, options) => {
    const answer = JSON.parse(options.body).correction_answer;
    return Promise.resolve({ ok:true, json:async () => ({ ...initial, needsCorrectionAnswer:true,
      correctionAnswer:answer, ratingReason:"Passed independently after correcting implementation details." }) });
  }));
  function Wrapper() { const [event,setEvent] = useState<ReviewEvent>({ ...initial, automaticGrade:"hard", effectiveGrade:"hard", needsCorrectionAnswer:true });
    return <ReviewFeedback event={event} onChange={setEvent} profile="owner" />; }
  render(<Wrapper />);
  fireEvent.click(screen.getByRole("button", { name:"Fixed implementation details" }));
  expect(await screen.findByText(/Passed independently after correcting/)).toBeInTheDocument();
  expect(JSON.parse(vi.mocked(fetch).mock.calls[0][1]!.body as string)).toEqual({ correction_answer:"implementation" });
  expect(screen.queryByText(/Next due/)).not.toBeInTheDocument();
});

test("the score view loads only when expanded and explains score components", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok:true, json:async () => ({ total:1, asOf:"now", items:[{
    id:"p",title:"Unique Paths",difficulty:5,score:57,urgency:42,recentStruggle:15,dueDate:"2026-11-03",
    cooldownUntil:"2026-11-05",recoveryException:true,status:"eligible",reason:"Due recovery review.",
    assignedToday:true,assignmentScore:53,assignmentReason:"Daily DP. Older review: last practised 24 days ago",inferred:false,
    lastAssignmentDate:"2026-11-03",lastSubmissionDate:"2026-10-10",lastActivityDate:"2026-11-03",
    daysSinceLastActivity:0,olderReviewEligible:false,recentRecovery:true,
  }] }) })));
  render(<ReviewScores profile="owner" revision={0} />);
  expect(fetch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Review scores, due dates and cooldowns"));
  expect(await screen.findByText("Unique Paths")).toBeInTheDocument();
  expect(screen.getByText("57.00")).toBeInTheDocument();
  expect(screen.getByText(/Urgency: 42.00; recent struggle: 15.00/)).toBeInTheDocument();
  expect(screen.getByText(/Last assigned: 2026-11-03. Last submitted: 2026-10-10/)).toBeInTheDocument();
  expect(screen.getByText(/Saved selection: Daily DP. Older review: last practised 24 days ago/)).toBeInTheDocument();
  expect(screen.getByText(/Recent recovery repeat: assigned or submitted/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Filter review status"),{target:{value:"cooldown"}});
  await waitFor(() => expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).includes("status=cooldown"))).toBe(true));
});

test("selection shortages and older eligibility appear inside expandable review details", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok:true, json:async () => ({ total:1, asOf:"now",
    selectionPolicyVersion:"balanced-rotation-v1",
    selectionExplanations:["Recovery limit exception: 3 recent recovery reviews selected, the minimum needed."],
    items:[{ id:"p", title:"Older practice", difficulty:5, score:70, urgency:70, recentStruggle:0,
      dueDate:"2026-11-03", cooldownUntil:null, recoveryException:false, status:"eligible", reason:"Due and eligible.",
      assignedToday:false, assignmentScore:null, assignmentReason:null, inferred:false,
      lastAssignmentDate:"2026-10-24", lastSubmissionDate:"2026-10-24", lastActivityDate:"2026-10-24",
      daysSinceLastActivity:24, olderReviewEligible:true, recentRecovery:false }],
  }) })));
  render(<ReviewScores profile="member" revision={0} />);
  expect(screen.queryByText(/Recovery limit exception/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByText("Review scores, due dates and cooldowns"));
  expect(await screen.findByText(/Recovery limit exception: 3/)).toBeInTheDocument();
  expect(screen.getByText("Older review: last practised 24 days ago.")).toBeInTheDocument();
  expect(screen.getByText("Older practice").closest("details")).not.toHaveAttribute("open");
  expect(vi.mocked(fetch).mock.calls[0][1]?.headers).toMatchObject({ "X-Study-Profile":"member" });
});
