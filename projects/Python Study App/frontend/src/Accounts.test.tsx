import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { AccountGate, AccountPanel } from "./Accounts";
import { forProfile, setApiProfile } from "./api";

const owner = { id: "owner", username: "admin", role: "admin", disabled: false, must_change_password: false };
const learner = { ...owner, id: "learner-id", username: "learner", role: "member", must_change_password: true };
const session = (user: typeof owner | null) => ({ user, loginRequired: true, ownerLoginAvailable: true, hasPassword: true });
const reply = (value: unknown, status = 200) => Promise.resolve({ ok: status < 400, status, json: async () => value, text: async () => JSON.stringify(value) });
beforeEach(() => { setApiProfile(null); });
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

test("login gates private content and requires a replacement for temporary passwords", async () => {
  let current: typeof owner | null = null;
  vi.stubGlobal("fetch", vi.fn((path: string) => {
    if (path === "/api/auth/me") return reply(session(current));
    if (path === "/api/auth/login") { current = learner; return reply({ user: current }); }
    if (path === "/api/auth/password") { current = { ...learner, must_change_password: false }; return reply({ ok: true }); }
    return reply({});
  }));
  render(<AccountGate><p>Study workspace</p></AccountGate>);
  expect(await screen.findByRole("button", { name: "Sign in" })).toBeInTheDocument();
  expect(screen.queryByText("Study workspace")).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Username"), { target: { value: "learner" } });
  fireEvent.change(screen.getByLabelText("Password", { exact: true }), { target: { value: "temporary-password" } });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
  expect(await screen.findByRole("heading", { name: "Choose your own password" })).toBeInTheDocument();
  expect(screen.queryByText("Study workspace")).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Current password"), { target: { value: "temporary-password" } });
  fireEvent.change(screen.getByLabelText("New password", { exact: true }), { target: { value: "my-new-password" } });
  fireEvent.change(screen.getByLabelText("Confirm new password"), { target: { value: "my-new-password" } });
  fireEvent.click(screen.getByRole("button", { name: "Save password" }));
  expect(await screen.findByText("Study workspace")).toBeInTheDocument();
  const call = vi.mocked(fetch).mock.calls.find(([path]) => path === "/api/auth/password");
  expect(call?.[1]?.headers).toMatchObject({ "X-Study-Profile": learner.id, "X-Requested-With": "CodePractice" });
});

test("admin creates accounts and members do not see account management", async () => {
  let current = owner;
  let users = [owner];
  vi.stubGlobal("fetch", vi.fn((path: string, options?: RequestInit) => {
    if (path === "/api/auth/me") return reply(session(current));
    if (path === "/api/admin/accounts" && options?.method === "POST") { users = [...users, learner]; return reply(learner, 201); }
    if (path === "/api/admin/accounts") return reply({ accounts: users });
    return reply({});
  }));
  render(<AccountGate><AccountPanel /></AccountGate>);
  fireEvent.change(await screen.findByLabelText("New username"), { target: { value: "learner" } });
  fireEvent.change(screen.getByLabelText("Temporary password"), { target: { value: "temporary-password" } });
  fireEvent.click(screen.getByRole("button", { name: "Create account" }));
  expect(await screen.findByText("learner", { selector: "strong" })).toBeInTheDocument();
  expect(screen.getByLabelText("Temporary password")).toHaveValue("");
  current = { ...learner, must_change_password: false };
  window.dispatchEvent(new Event("study-session-changed"));
  await waitFor(() => expect(screen.queryByRole("heading", { name: "Create an account" })).not.toBeInTheDocument());
  expect(await screen.findByRole("heading", { name: "learner" })).toBeInTheDocument();
});

test("a delayed operation keeps its original profile after account switching", async () => {
  vi.stubGlobal("fetch", vi.fn(() => reply({ saved: true })));
  setApiProfile("owner");
  const ownerRequest = forProfile("owner");
  setApiProfile(learner.id);
  await ownerRequest("/api/problems/pair-sum-indices/draft", { method: "PUT", body: JSON.stringify({ source_code: "old draft" }) });
  expect(vi.mocked(fetch).mock.calls[0][1]?.headers).toMatchObject({ "X-Study-Profile": "owner" });
});

test("incorrect password stays on login and shows the server message", async () => {
  vi.stubGlobal("fetch", vi.fn((path: string) => path === "/api/auth/me" ? reply(session(null)) : reply({ detail: "Incorrect username or password." }, 401)));
  render(<AccountGate><p>Study workspace</p></AccountGate>);
  fireEvent.change(await screen.findByLabelText("Username"), { target: { value: "learner" } });
  fireEvent.change(screen.getByLabelText("Password", { exact: true }), { target: { value: "wrong" } });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Incorrect username or password.");
  expect(screen.queryByText("Study workspace")).not.toBeInTheDocument();
});
