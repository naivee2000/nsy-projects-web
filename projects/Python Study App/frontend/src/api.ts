let profileId: string | null = null;
export function setApiProfile(id: string | null) { profileId = id; }

// Capture the profile for an operation's lifetime, including an in-flight judge
// run whose user signs out before it finishes. Never stamp it with a new user.
export function forProfile(id: string) {
  return <T,>(path: string, options?: RequestInit): Promise<T> => api<T>(path, {
    ...options, headers: { ...(options?.headers || {}), "X-Study-Profile": id },
  });
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "CodePractice",
      ...(profileId ? { "X-Study-Profile": profileId } : {}),
      ...(options?.headers || {}),
    },
  });
  if (!response.ok) {
    const message = await response.text();
    let detail: { detail?: unknown; code?: string } = {};
    try { detail = JSON.parse(message); } catch { /* Plain HTTP error. */ }
    if ((response.status === 401 && path !== "/api/auth/login") || detail.code === "profile_changed" || detail.code === "password_change_required") {
      window.dispatchEvent(new Event("study-session-changed"));
    }
    throw new Error(typeof detail.detail === "string" ? detail.detail : message || `${response.status} ${response.statusText}`);
  }
  return response.json();
}
