import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { AuthProvider } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { initialData } from "@/lib/kanban";

vi.mock("next/navigation");
vi.mock("@/lib/auth", () => ({
  logout: vi.fn(),
  verifyAuth: vi.fn().mockResolvedValue(null),
}));

global.fetch = vi.fn();

const renderWithAuth = (component: React.ReactElement) => {
  return render(<AuthProvider>{component}</AuthProvider>);
};

beforeEach(() => {
  vi.clearAllMocks();
  (useRouter as any).mockReturnValue({ push: vi.fn() });
  (global.fetch as any).mockResolvedValueOnce({
    ok: true,
    json: vi.fn().mockResolvedValueOnce(initialData),
  });
});

describe("KanbanBoard", () => {
  it("renders five columns", async () => {
    renderWithAuth(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("renames a column", async () => {
    renderWithAuth(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });

    const column = screen.getAllByTestId(/column-/i)[0];
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    renderWithAuth(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });

    const column = screen.getAllByTestId(/column-/i)[0];
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
