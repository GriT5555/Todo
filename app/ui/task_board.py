from __future__ import annotations

from calendar import monthrange
from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk

from app.models import Task
from app.storage import load_tasks, save_tasks


PAD = 12
CARD_BG = "#f4f1ea"
OVERDUE_BG = "#f6e4e1"
WINDOW_BG = "#e8e4dc"


class DateFields(ttk.Frame):
    """Year / month / day selectors that always produce a real calendar date."""

    def __init__(self, parent: tk.Misc, initial: date | None = None) -> None:
        super().__init__(parent)
        today = initial or date.today()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=str(today.month))
        self.day_var = tk.StringVar(value=str(today.day))

        years = [str(year) for year in range(today.year, today.year + 6)]
        months = [str(month) for month in range(1, 13)]

        ttk.Label(self, text="Year").grid(row=0, column=0, sticky="w")
        ttk.Label(self, text="Month").grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(self, text="Day").grid(row=0, column=2, sticky="w", padx=(8, 0))

        self.year_box = ttk.Combobox(
            self, textvariable=self.year_var, values=years, width=6, state="readonly"
        )
        self.month_box = ttk.Combobox(
            self, textvariable=self.month_var, values=months, width=4, state="readonly"
        )
        self.day_box = ttk.Combobox(self, textvariable=self.day_var, width=4, state="readonly")

        self.year_box.grid(row=1, column=0, sticky="w")
        self.month_box.grid(row=1, column=1, sticky="w", padx=(8, 0))
        self.day_box.grid(row=1, column=2, sticky="w", padx=(8, 0))

        self.year_box.bind("<<ComboboxSelected>>", self._refresh_days)
        self.month_box.bind("<<ComboboxSelected>>", self._refresh_days)
        self._refresh_days()

    def _refresh_days(self, _event=None) -> None:
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        last_day = monthrange(year, month)[1]
        days = [str(day) for day in range(1, last_day + 1)]
        self.day_box["values"] = days
        if int(self.day_var.get() or 1) > last_day:
            self.day_var.set(str(last_day))

    def get_date(self) -> date:
        self._refresh_days()
        return date(int(self.year_var.get()), int(self.month_var.get()), int(self.day_var.get()))

    def reset(self, value: date | None = None) -> None:
        chosen = value or date.today()
        self.year_var.set(str(chosen.year))
        self.month_var.set(str(chosen.month))
        self.day_var.set(str(chosen.day))
        self._refresh_days()


class TaskCard(tk.Frame):
    def __init__(self, parent: tk.Misc, task: Task, on_delete) -> None:
        background = OVERDUE_BG if task.is_overdue() else CARD_BG
        super().__init__(parent, bg=background, highlightbackground="#c9c3b6", highlightthickness=1)
        self.columnconfigure(0, weight=1)

        header = tk.Frame(self, bg=background)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text=task.name,
            font=("Segoe UI", 12, "bold"),
            bg=background,
            anchor="w",
            wraplength=420,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        deadline_text = f"Deadline: {task.deadline_label()}"
        if task.is_overdue():
            deadline_text += "  · overdue"
        tk.Label(
            header,
            text=deadline_text,
            font=("Segoe UI", 9),
            fg="#6b3a32" if task.is_overdue() else "#4a5d3a",
            bg=background,
            anchor="e",
        ).grid(row=0, column=1, sticky="e", padx=(12, 0))

        notes = task.description.strip() or "No notes yet."
        tk.Label(
            self,
            text=notes,
            font=("Segoe UI", 10),
            bg=background,
            fg="#333",
            anchor="nw",
            justify="left",
            wraplength=520,
        ).grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))

        ttk.Button(self, text="Remove", command=lambda: on_delete(task.id)).grid(
            row=2, column=0, sticky="e", padx=10, pady=(0, 10)
        )


class TaskBoard(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=PAD)
        self.tasks = load_tasks()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_form()
        self._build_list()
        self.refresh_cards()

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self, text="New task", padding=PAD)
        form.grid(row=0, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="nw", pady=(0, 8))
        self.name_entry = ttk.Entry(form)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Notes").grid(row=1, column=0, sticky="nw", pady=(0, 8))
        self.notes_text = tk.Text(form, height=5, wrap="word", font=("Segoe UI", 10))
        self.notes_text.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(form, text="Deadline").grid(row=2, column=0, sticky="nw")
        self.deadline_fields = DateFields(form)
        self.deadline_fields.grid(row=2, column=1, sticky="w")

        ttk.Button(form, text="Add task", command=self.add_task).grid(
            row=3, column=1, sticky="e", pady=(12, 0)
        )

    def _build_list(self) -> None:
        list_frame = ttk.LabelFrame(self, text="Your tasks", padding=(PAD, PAD, PAD, 4))
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(PAD, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(list_frame, highlightthickness=0, bg=WINDOW_BG)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.cards_host = tk.Frame(self.canvas, bg=WINDOW_BG)

        self.cards_host.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_host, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", self._sync_card_width)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.empty_label = ttk.Label(
            self.cards_host,
            text="No tasks yet. Add one above.",
            foreground="#666",
        )

    def _sync_card_width(self, event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def add_task(self) -> None:
        name = self.name_entry.get().strip()
        description = self.notes_text.get("1.0", "end").strip()
        if not name:
            messagebox.showinfo("Missing name", "Give the task a name before adding it.")
            self.name_entry.focus_set()
            return

        task = Task(name=name, description=description, deadline=self.deadline_fields.get_date())
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.name_entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")
        self.deadline_fields.reset()
        self.refresh_cards()
        self.name_entry.focus_set()

    def delete_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_id]
        save_tasks(self.tasks)
        self.refresh_cards()

    def refresh_cards(self) -> None:
        for child in self.cards_host.winfo_children():
            child.destroy()

        if not self.tasks:
            self.empty_label = ttk.Label(
                self.cards_host,
                text="No tasks yet. Add one above.",
                foreground="#666",
            )
            self.empty_label.pack(anchor="w", pady=8)
            return

        ordered = sorted(self.tasks, key=lambda task: (task.deadline, task.name.lower()))
        for task in ordered:
            card = TaskCard(self.cards_host, task, on_delete=self.delete_task)
            card.pack(fill="x", pady=6, padx=2)
