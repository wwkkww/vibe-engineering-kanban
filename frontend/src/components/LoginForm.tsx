"use client";

import React, { useState } from "react";
import { login } from "@/lib/auth";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import styles from "./LoginForm.module.css";

export function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { setUser } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const authToken = await login(username, password);
      setUser(authToken);
      router.push("/");
    } catch (err) {
      setError("Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Kanban Studio</h1>
        <p className={styles.subtitle}>A focused, single-board kanban workspace.</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="username" className={styles.label}>
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="user"
              className={styles.input}
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.label}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
              className={styles.input}
              disabled={isLoading}
            />
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <button
            type="submit"
            className={styles.button}
            disabled={isLoading || !username || !password}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className={styles.help}>
          <p>Demo credentials:</p>
          <p>
            <strong>Username:</strong> user
          </p>
          <p>
            <strong>Password:</strong> password
          </p>
        </div>
      </div>
    </div>
  );
}
