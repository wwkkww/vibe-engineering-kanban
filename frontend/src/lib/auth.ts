/**
 * Authentication utilities and types
 */

export interface AuthToken {
  userId: string;
  username: string;
  token: string;
}

export async function login(username: string, password: string): Promise<AuthToken> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  const data = await response.json();
  return {
    userId: data.userId,
    username: data.username,
    token: data.token,
  };
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "include",
  });
}

export async function verifyAuth(): Promise<AuthToken | null> {
  try {
    const response = await fetch("/api/auth/verify", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return {
      userId: data.userId,
      username: data.username,
      token: "", // Not returned by verify endpoint
    };
  } catch {
    return null;
  }
}
