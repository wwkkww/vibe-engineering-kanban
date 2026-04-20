"use client";

import { useState } from "react";
import type { Card } from "@/lib/kanban";

type EditCardModalProps = {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  onSave: (title: string, details: string) => void;
};

export const EditCardModal = ({
  card,
  isOpen,
  onClose,
  onSave,
}: EditCardModalProps) => {
  const [title, setTitle] = useState(card.title);
  const [details, setDetails] = useState(card.details);
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onSave(title, details);
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-md rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-modal-title"
      >
        <h2
          id="edit-modal-title"
          className="font-display text-2xl font-semibold text-[var(--navy-dark)]"
        >
          Edit Card
        </h2>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
          <div>
            <label
              htmlFor="card-title"
              className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]"
            >
              Title
            </label>
            <input
              id="card-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-2 w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm font-medium text-[var(--navy-dark)] placeholder-[var(--gray-text)] outline-none transition focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              placeholder="Card title"
              disabled={isSaving}
              required
            />
          </div>

          <div>
            <label
              htmlFor="card-details"
              className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]"
            >
              Details
            </label>
            <textarea
              id="card-details"
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              className="mt-2 w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm font-medium text-[var(--navy-dark)] placeholder-[var(--gray-text)] outline-none transition focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              placeholder="Card details"
              disabled={isSaving}
              rows={4}
            />
          </div>

          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 rounded-2xl border border-transparent bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-white transition hover:opacity-90 disabled:opacity-60"
              disabled={isSaving}
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
