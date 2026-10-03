import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, forProfile, setApiProfile } from "./api";

export type StudyUser = { id: string; username: string; role: "admin" | "member"; disabled: boolean; must_change_password: boolean };
type Session = { user: StudyUser | null; loginRequired: boolean; ownerLoginAvailable: boolean; hasPassword: boolean };
type AccountContextType = { session: Session; reload: () => Promise<void>; logout: () => Promise<void> };
const AccountContext = createContext<AccountContextType | null>(null);
export const useAccount = () => useContext(AccountContext);
const errorText = (error: unknown) => error instanceof Error ? error.message : String(error);

function PasswordForm({ profileId, hasPassword, required, onDone }: { profileId: string; hasPassword: boolean; required?: boolean; onDone: () => Promise<void> }) {
  const api = forProfile(profileId);
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  return <form className="account-form" onSubmit={async (event) => {
    event.preventDefault(); setMessage("");
    if (password !== confirm) { setMessage("The new passwords do not match."); return; }
    setBusy(true);
    try {
      await api("/api/auth/password", { method: "POST", body: JSON.stringify({ password, current_password: current }) });
      setCurrent(""); setPassword(""); setConfirm(""); setMessage("Password updated."); await onDone();
    } catch (error) { setMessage(errorText(error)); } finally { setBusy(false); }
  }}>
    <h2>{required ? "Choose your own password" : "Change my password"}</h2>
    {required && <p>Your admin gave you a temporary password. Replace it before you start studying.</p>}
    {hasPassword && <label>Current password<input type="password" autoComplete="current-password" required maxLength={256} value={current} onChange={(event) => setCurrent(event.target.value)} /></label>}
    <label>New password<input type="password" autoComplete="new-password" required minLength={12} maxLength={256} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
    <label>Confirm new password<input type="password" autoComplete="new-password" required minLength={12} maxLength={256} value={confirm} onChange={(event) => setConfirm(event.target.value)} /></label>
    <small>Use at least 12 characters.</small>
    <button disabled={busy} type="submit">{busy ? "Saving…" : "Save password"}</button>
    {message && <p role="status">{message}</p>}
  </form>;
}

export function AccountGate({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [error, setError] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const reload = async () => {
    const next = await api<Session>("/api/auth/me");
    setApiProfile(next.user?.id ?? null); setSession(next);
  };
  const logout = async () => {
    await api("/api/auth/logout", { method: "POST" });
    setApiProfile(null); setSession((old) => old ? { ...old, user: null } : null);
    setPassword(""); setError("");
  };
  useEffect(() => {
    void reload().catch((error) => setError(errorText(error)));
    const refresh = () => { void reload().catch((error) => setError(errorText(error))); };
    const changed = () => { setSession(null); setApiProfile(null); refresh(); };
    window.addEventListener("focus", refresh);
    window.addEventListener("study-session-changed", changed);
    return () => {
      window.removeEventListener("focus", refresh);
      window.removeEventListener("study-session-changed", changed);
    };
  }, []);
  if (!session) return <main className="login-page"><section className="account-card"><h1>Code Practice</h1><p role="status">{error || "Loading your account…"}</p>{error && <button onClick={() => window.location.reload()}>Try again</button>}</section></main>;
  if (!session.user) return <main className="login-page"><section className="account-card">
    <span className="eyebrow">CODE PRACTICE LAB</span><h1>Welcome back.</h1><p>Sign in to continue your own study progress.</p>
    <form className="account-form" onSubmit={async (event) => {
      event.preventDefault(); setBusy(true); setError("");
      try {
        await api("/api/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
        setPassword(""); await reload();
      } catch (error) { setError(errorText(error)); } finally { setBusy(false); }
    }}>
      <label>Username<input autoComplete="username" required maxLength={64} value={username} onChange={(event) => setUsername(event.target.value)} /></label>
      <label>Password<input type="password" autoComplete="current-password" required maxLength={256} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      <button type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      {error && <p role="alert">{error}</p>}
    </form>
    <p className="account-note">Ask the admin for an account or a password reset.</p>
    {session.ownerLoginAvailable && <a href="/api/auth/owner">Admin: continue with NSY login</a>}
    {!session.loginRequired && <a href="/api/auth/owner">Continue as local owner</a>}
  </section></main>;
  if (session.user.must_change_password) return <main className="login-page"><section className="account-card">
    <PasswordForm profileId={session.user.id} hasPassword={true} required onDone={reload} /><button onClick={() => void logout().catch((error) => setError(errorText(error)))}>Sign out</button>{error && <p role="alert">{error}</p>}
  </section></main>;
  return <AccountContext.Provider value={{ session, reload, logout }}><div key={session.user.id}>{children}</div></AccountContext.Provider>;
}

export function AccountPanel() {
  const account = useAccount();
  const api = forProfile(account?.session.user?.id ?? "owner");
  const [users, setUsers] = useState<StudyUser[]>([]);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [resetId, setResetId] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const loadUsers = async () => setUsers((await api<{ accounts: StudyUser[] }>("/api/admin/accounts")).accounts);
  useEffect(() => { if (account?.session.user?.role === "admin") void loadUsers().catch((error) => setMessage(errorText(error))); }, [account?.session.user?.id]);
  if (!account?.session.user) return null;
  const admin = account.session.user.role === "admin";
  const action = async (work: () => Promise<void>) => {
    setBusy(true); setMessage("");
    try { await work(); await loadUsers(); } catch (error) { setMessage(errorText(error)); } finally { setBusy(false); }
  };
  return <div className="page account-page">
    <header className="compact-header"><span className="eyebrow">YOUR ACCOUNT</span><h1>{account.session.user.username}</h1><p>{admin ? "Admin" : "Study account"} · Your progress is saved on the computer hosting this app.</p></header>
    <section className="account-card"><PasswordForm profileId={account.session.user.id} hasPassword={account.session.hasPassword} onDone={account.reload} /></section>
    {admin && <>
      <section className="account-card"><form className="account-form" onSubmit={(event) => {
        event.preventDefault(); void action(async () => {
          await api("/api/admin/accounts", { method: "POST", body: JSON.stringify({ username, password }) });
          setMessage(`Account created for ${username}. Share the username and temporary password privately.`); setUsername(""); setPassword("");
        });
      }}><h2>Create an account</h2><p>New accounts start with empty progress and choose their own password at first sign-in.</p>
        <label>New username<input required minLength={3} maxLength={32} pattern="[A-Za-z0-9][A-Za-z0-9_.\-]{2,31}" value={username} onChange={(event) => setUsername(event.target.value)} /></label>
        <label>Temporary password<input type="password" autoComplete="new-password" required minLength={12} maxLength={256} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        <button disabled={busy} type="submit">Create account</button>
      </form></section>
      <section className="account-card"><h2>Accounts</h2><div className="account-list">{users.map((user) => <div className="account-row" key={user.id}>
        <span><strong>{user.username}</strong><small>{user.role === "admin" ? "Admin" : user.disabled ? "Disabled — progress retained" : user.must_change_password ? "Temporary password" : "Active"}</small></span>
        {user.role !== "admin" && <div className="account-actions"><button disabled={busy} onClick={() => { setResetId(user.id); setResetPassword(""); }}>Reset password</button><button disabled={busy} onClick={() => void action(async () => {
          await api(`/api/admin/accounts/${user.id}`, { method: "PATCH", body: JSON.stringify({ disabled: !user.disabled }) });
          setMessage(user.disabled ? "Account enabled." : "Account disabled. Saved progress is retained.");
        })}>{user.disabled ? "Enable" : "Disable"}</button></div>}
      </div>)}</div>
      {resetId && <form className="account-form" onSubmit={(event) => { event.preventDefault(); void action(async () => {
        await api(`/api/admin/accounts/${resetId}/password`, { method: "POST", body: JSON.stringify({ password: resetPassword }) });
        setResetId(""); setResetPassword(""); setMessage("Password reset. Share the temporary password privately; previous sessions were signed out.");
      }); }}><label>Temporary password for {users.find((user) => user.id === resetId)?.username}<input type="password" autoComplete="new-password" required minLength={12} maxLength={256} value={resetPassword} onChange={(event) => setResetPassword(event.target.value)} /></label><button disabled={busy} type="submit">Save temporary password</button><button type="button" onClick={() => setResetId("")}>Cancel</button></form>}
      </section>
    </>}
    {message && <p role="status">{message}</p>}
    <button className="account-signout" onClick={() => void account.logout().catch((error) => setMessage(errorText(error)))}>Sign out</button>
  </div>;
}
