import { describe, it, expect, beforeEach, vi } from "vitest";
import { login, logout, verifyAuth } from "@/lib/auth";

describe("Auth utilities", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe("login", () => {
    it("should send login credentials and return token", async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          userId: "user-123",
          username: "user",
          token: "jwt-token",
        }),
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const result = await login("user", "password");

      expect(global.fetch).toHaveBeenCalledWith(
        "/api/auth/login",
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ username: "user", password: "password" }),
        })
      );
      expect(result).toEqual({
        userId: "user-123",
        username: "user",
        token: "jwt-token",
      });
    });

    it("should throw error on failed login", async () => {
      const mockResponse = { ok: false };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await expect(login("user", "wrong")).rejects.toThrow("Login failed");
    });
  });

  describe("logout", () => {
    it("should call logout endpoint", async () => {
      const mockResponse = { ok: true };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await logout();

      expect(global.fetch).toHaveBeenCalledWith(
        "/api/auth/logout",
        expect.objectContaining({
          method: "POST",
          credentials: "include",
        })
      );
    });
  });

  describe("verifyAuth", () => {
    it("should return user if authenticated", async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          userId: "user-123",
          username: "user",
          isAuthenticated: true,
        }),
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const result = await verifyAuth();

      expect(result).toEqual({
        userId: "user-123",
        username: "user",
        token: "",
      });
    });

    it("should return null if not authenticated", async () => {
      const mockResponse = { ok: false };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const result = await verifyAuth();

      expect(result).toBeNull();
    });

    it("should return null on network error", async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

      const result = await verifyAuth();

      expect(result).toBeNull();
    });
  });
});
