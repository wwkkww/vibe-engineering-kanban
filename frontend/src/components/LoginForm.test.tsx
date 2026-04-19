import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LoginForm } from "@/components/LoginForm";
import { AuthProvider } from "@/context/AuthContext";
import * as authLib from "@/lib/auth";
import { useRouter } from "next/navigation";

vi.mock("@/lib/auth", () => ({
  login: vi.fn(),
  verifyAuth: vi.fn().mockResolvedValue(null),
}));
vi.mock("next/navigation");

const renderWithAuth = (component: React.ReactElement) => {
  return render(<AuthProvider>{component}</AuthProvider>);
};

describe("LoginForm", () => {
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue({ push: mockPush });
  });

  it("should render login form", () => {
    renderWithAuth(<LoginForm />);

    expect(screen.getByText("Kanban Studio")).toBeInTheDocument();
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("should submit login with credentials", async () => {
    const user = userEvent.setup();
    (authLib.login as any).mockResolvedValueOnce({
      userId: "user-123",
      username: "user",
      token: "jwt",
    });

    renderWithAuth(<LoginForm />);

    const usernameInput = screen.getByLabelText("Username") as HTMLInputElement;
    const passwordInput = screen.getByLabelText("Password") as HTMLInputElement;

    await user.type(usernameInput, "user");
    await user.type(passwordInput, "password");

    const submitButton = screen.getByRole("button", { name: /sign in/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(authLib.login).toHaveBeenCalledWith("user", "password");
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/");
    });
  });

  it("should display error on failed login", async () => {
    const user = userEvent.setup();
    (authLib.login as any).mockRejectedValueOnce(new Error("Invalid credentials"));

    renderWithAuth(<LoginForm />);

    const usernameInput = screen.getByLabelText("Username") as HTMLInputElement;
    const passwordInput = screen.getByLabelText("Password") as HTMLInputElement;

    await user.type(usernameInput, "user");
    await user.type(passwordInput, "wrong");

    const submitButton = screen.getByRole("button", { name: /sign in/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Invalid username or password")).toBeInTheDocument();
    });
  });

  it("should disable inputs while loading", async () => {
    const user = userEvent.setup();
    (authLib.login as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({}), 100))
    );

    renderWithAuth(<LoginForm />);

    const usernameInput = screen.getByLabelText("Username") as HTMLInputElement;
    const passwordInput = screen.getByLabelText("Password") as HTMLInputElement;
    const submitButton = screen.getByRole("button", { name: /sign in/i }) as HTMLButtonElement;

    await user.type(usernameInput, "user");
    await user.type(passwordInput, "password");
    await user.click(submitButton);

    // Button should be disabled while loading
    expect(submitButton).toBeDisabled();

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/");
    });
  });
});
