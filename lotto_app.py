"""LottoPro Analyse – desktop app for Lotto 6 aus 49.

Historical statistics describe past draws only. They do not predict future draws
or improve the odds of any valid combination in a fair lottery.
"""

from __future__ import annotations

import csv
import itertools
import random
import sys
from collections import Counter
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "LottoPro | 6 aus 49"
MIN_NUMBER = 1
MAX_NUMBER = 49
NUMBERS_PER_DRAW = 6
MAX_TICKETS = 100

COLORS = {
    "background": "#f3f6fb",
    "surface": "#ffffff",
    "navy": "#14243a",
    "blue": "#315efb",
    "blue_light": "#e9efff",
    "text": "#182230",
    "muted": "#66758a",
    "border": "#e1e7ef",
    "green": "#16856b",
    "orange": "#d88722",
}


def demo_draws(count: int = 240) -> list[list[int]]:
    """Return clearly synthetic sample data for a first look at the app."""
    rng = random.Random(42)
    return [sorted(rng.sample(range(MIN_NUMBER, MAX_NUMBER + 1), NUMBERS_PER_DRAW)) for _ in range(count)]


def parse_draw_csv(path: str | Path) -> list[list[int]]:
    """Read rows containing six distinct main numbers (1–49), ignoring headers."""
    result: list[list[int]] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as source:
        for row in csv.reader(source, delimiter=None, skipinitialspace=True):
            # csv.reader needs a one-character delimiter; normalize common separators.
            # This branch is retained for compatibility with comma-separated exports.
            values = _extract_numbers(row)
            if len(values) != NUMBERS_PER_DRAW:
                continue
            if len(set(values)) != NUMBERS_PER_DRAW:
                continue
            result.append(sorted(values))
    if not result:
        raise ValueError("Keine gültigen Zeilen mit genau sechs verschiedenen Zahlen von 1 bis 49 gefunden.")
    return result


def _extract_numbers(row: list[str]) -> list[int]:
    values: list[int] = []
    for cell in row:
        # Also accept six values written in one cell using spaces/semicolons.
        for token in cell.replace(";", ",").replace("\t", ",").split(","):
            token = token.strip()
            if not token:
                continue
            try:
                number = int(token)
            except ValueError:
                continue
            if MIN_NUMBER <= number <= MAX_NUMBER:
                values.append(number)
    return values


def number_statistics(draws: list[list[int]]) -> dict[int, dict[str, int | None]]:
    """Calculate appearances and draws since last appearance; input oldest first."""
    stats: dict[int, dict[str, int | None]] = {
        n: {"count": 0, "last_index": None, "draws_ago": None}
        for n in range(MIN_NUMBER, MAX_NUMBER + 1)
    }
    for index, draw in enumerate(draws):
        for number in draw:
            entry = stats[number]
            entry["count"] = int(entry["count"]) + 1
            entry["last_index"] = index
    last_index = len(draws) - 1
    for entry in stats.values():
        index = entry["last_index"]
        entry["draws_ago"] = last_index - int(index) if index is not None else len(draws)
    return stats


def ticket_is_valid(numbers: list[int], low_sum: int, high_sum: int,
                    min_even: int, max_even: int) -> bool:
    total_even = sum(number % 2 == 0 for number in numbers)
    return low_sum <= sum(numbers) <= high_sum and min_even <= total_even <= max_even


def create_tickets(draws: list[list[int]], count: int, low_sum: int, high_sum: int,
                   min_even: int, max_even: int, strategy: str) -> list[list[int]]:
    """Create unique, filtered combinations. Historical mode only changes sampling preference."""
    if not 1 <= count <= MAX_TICKETS:
        raise ValueError(f"Bitte eine Tippanzahl von 1 bis {MAX_TICKETS} eingeben.")
    if not 21 <= low_sum <= high_sum <= 279:
        raise ValueError("Die Summenfilter müssen zwischen 21 und 279 liegen; Minimum darf Maximum nicht überschreiten.")
    if not 0 <= min_even <= max_even <= 6:
        raise ValueError("Die Anzahl gerader Zahlen muss zwischen 0 und 6 liegen.")
    if min_even > 6 or max_even < 0:
        raise ValueError("Ungültiger Gerade-Filter.")

    universe = list(range(MIN_NUMBER, MAX_NUMBER + 1))
    weights = None
    if strategy == "Häufige Zahlen berücksichtigen" and draws:
        stats = number_statistics(draws)
        # Smooth weights avoid zero-probability numbers. This is a preference, not a forecast.
        weights = [1.0 + int(stats[n]["count"] or 0) for n in universe]

    found: set[tuple[int, ...]] = set()
    # Attempt cap prevents a restrictive filter from trapping the app in a loop.
    for _ in range(max(5000, count * 2500)):
        if len(found) >= count:
            break
        if weights:
            selected: list[int] = []
            while len(selected) < NUMBERS_PER_DRAW:
                candidate = random.choices(universe, weights=weights, k=1)[0]
                if candidate not in selected:
                    selected.append(candidate)
            combination = tuple(sorted(selected))
        else:
            combination = tuple(sorted(random.sample(universe, NUMBERS_PER_DRAW)))
        if ticket_is_valid(list(combination), low_sum, high_sum, min_even, max_even):
            found.add(combination)

    if len(found) < count:
        raise ValueError(
            f"Mit diesen Filtern konnten {len(found)} unterschiedliche Tipps gefunden werden. "
            "Bitte Filter lockern oder weniger Tipps anfordern."
        )
    return [list(ticket) for ticket in sorted(found)]


def save_tickets_csv(path: str | Path, tickets: list[list[int]]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Tipp", "Zahlen", "Summe", "Gerade", "Ungerade"])
        for index, ticket in enumerate(tickets, start=1):
            writer.writerow([
                index,
                " ".join(f"{number:02d}" for number in ticket),
                sum(ticket),
                sum(number % 2 == 0 for number in ticket),
                sum(number % 2 != 0 for number in ticket),
            ])


class LottoApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1120x790")
        self.minsize(940, 680)
        self.configure(bg=COLORS["background"])
        self.draws = demo_draws()
        self.tickets: list[list[int]] = []
        self.data_label = "Beispiel-Daten (synthetisch)"
        self._configure_style()
        self._build_ui()
        self.refresh_dashboard()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["background"])
        style.configure("Card.TFrame", background=COLORS["surface"])
        style.configure("TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", foreground=COLORS["muted"], background=COLORS["surface"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", foreground=COLORS["navy"], background=COLORS["background"], font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", foreground=COLORS["muted"], background=COLORS["background"], font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", foreground=COLORS["muted"], font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", foreground=COLORS["navy"], font=("Segoe UI", 20, "bold"))
        style.configure("Primary.TButton", background=COLORS["blue"], foreground="white", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.map("Primary.TButton", background=[("active", "#244bd0")])
        style.configure("TButton", padding=(10, 7), font=("Segoe UI", 9))
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#edf1f7", padding=7)
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=5)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=(24, 20, 24, 16))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(4, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="LottoPro Analyse", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Lotto 6 aus 49  ·  Statistik und Tipp-Organisation", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Button(header, text="Ziehungen importieren", command=self.import_csv).grid(row=0, column=1, rowspan=2, sticky="e")

        self.notice = tk.Label(
            outer,
            text="Zur Einordnung: Frühere Ziehungen sagen künftige Ergebnisse nicht voraus. Jede gültige Kombination hat bei einer fairen Ziehung dieselbe Chance.",
            bg=COLORS["blue_light"], fg="#28468e", anchor="w", justify="left",
            font=("Segoe UI", 9), padx=12, pady=10, wraplength=1040,
        )
        self.notice.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        self.cards_frame = ttk.Frame(outer)
        self.cards_frame.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        for col in range(3):
            self.cards_frame.columnconfigure(col, weight=1)
        self.draws_value = self._make_stat_card(self.cards_frame, 0, "AUSGEWERTETE ZIEHUNGEN")
        self.hot_value = self._make_stat_card(self.cards_frame, 1, "HÄUFIGSTE ZAHL")
        self.cold_value = self._make_stat_card(self.cards_frame, 2, "LÄNGSTE PAUSE")

        content = ttk.Frame(outer)
        content.grid(row=3, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        controls = ttk.Frame(left, style="Card.TFrame", padding=16)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Tipp-Einstellungen", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        self.tip_count = self._field(controls, "Anzahl Tipps", "10", 1, 0)
        self.sum_min = self._field(controls, "Summe von", "90", 1, 2)
        self.sum_max = self._field(controls, "bis", "190", 1, 4)
        self.even_min = self._field(controls, "Gerade Zahlen min.", "1", 2, 0)
        self.even_max = self._field(controls, "max.", "5", 2, 2)

        ttk.Label(controls, text="Auswahlmodus").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.mode = tk.StringVar(value="Zufällig")
        ttk.Combobox(controls, textvariable=self.mode, state="readonly", values=("Zufällig", "Häufige Zahlen berücksichtigen"), width=27).grid(row=3, column=1, columnspan=2, sticky="ew", padx=(8, 12), pady=(8, 0))
        ttk.Button(controls, text="Tipps erstellen", style="Primary.TButton", command=self.generate).grid(row=3, column=3, columnspan=2, sticky="e", pady=(8, 0))

        results = ttk.Frame(left, style="Card.TFrame", padding=14)
        results.grid(row=1, column=0, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(1, weight=1)
        result_head = ttk.Frame(results, style="Card.TFrame")
        result_head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        result_head.columnconfigure(0, weight=1)
        ttk.Label(result_head, text="Deine Tipps", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Button(result_head, text="CSV exportieren", command=self.export_csv).grid(row=0, column=1, sticky="e")
        columns = ("index", "numbers", "total", "even", "odd")
        self.table = ttk.Treeview(results, columns=columns, show="headings", height=10)
        for key, title, width in (("index", "Nr.", 55), ("numbers", "Zahlen", 230), ("total", "Summe", 70), ("even", "Gerade", 70), ("odd", "Ungerade", 80)):
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="center")
        self.table.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(results, orient="vertical", command=self.table.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)

        right = ttk.Frame(content, style="Card.TFrame", padding=16)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)
        ttk.Label(right, text="Zahlen-Überblick", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.data_status = ttk.Label(right, text=self.data_label, style="Muted.TLabel")
        self.data_status.grid(row=1, column=0, sticky="w", pady=(4, 12))
        self.frequency_canvas = tk.Canvas(right, bg="white", height=250, highlightthickness=0)
        self.frequency_canvas.grid(row=2, column=0, sticky="nsew")
        ttk.Label(right, text="Häufigkeit je Zahl · absteigend nach Zahlen sortiert", style="Muted.TLabel", wraplength=320).grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Button(right, text="Demo-Daten wiederherstellen", command=self.restore_demo).grid(row=4, column=0, sticky="w", pady=(14, 0))

        footer = ttk.Label(outer, text="Analyse und Organisation – keine Gewinnprognose. Bitte verantwortungsvoll spielen.", style="Subtitle.TLabel")
        footer.grid(row=4, column=0, sticky="w", pady=(12, 0))
        self.frequency_canvas.bind("<Configure>", lambda _event: self.draw_frequency_chart())

    def _make_stat_card(self, parent: ttk.Frame, column: int, title: str) -> ttk.Label:
        card = ttk.Frame(parent, style="Card.TFrame", padding=(16, 12))
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 6, 6 if column < 2 else 0))
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        value = ttk.Label(card, text="—", style="CardValue.TLabel")
        value.pack(anchor="w", pady=(4, 0))
        return value

    @staticmethod
    def _field(parent: ttk.Frame, label: str, initial: str, row: int, col: int) -> tk.StringVar:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", pady=(4, 0))
        variable = tk.StringVar(value=initial)
        ttk.Entry(parent, textvariable=variable, width=7).grid(row=row, column=col + 1, sticky="w", padx=(7, 14), pady=(4, 0))
        return variable

    def refresh_dashboard(self) -> None:
        stats = number_statistics(self.draws)
        frequent = sorted(stats, key=lambda n: (-int(stats[n]["count"] or 0), n))[0]
        long_pause = sorted(stats, key=lambda n: (-int(stats[n]["draws_ago"] or 0), n))[0]
        self.draws_value.configure(text=str(len(self.draws)))
        self.hot_value.configure(text=f"{frequent:02d}  ·  {stats[frequent]['count']}×")
        self.cold_value.configure(text=f"{long_pause:02d}  ·  {stats[long_pause]['draws_ago']} Ziehungen")
        self.data_status.configure(text=self.data_label)
        self.draw_frequency_chart()

    def draw_frequency_chart(self) -> None:
        canvas = self.frequency_canvas
        if not canvas.winfo_exists():
            return
        canvas.delete("all")
        width = max(canvas.winfo_width(), 240)
        height = max(canvas.winfo_height(), 200)
        stats = number_statistics(self.draws)
        counts = [int(stats[n]["count"] or 0) for n in range(1, 50)]
        maximum = max(counts) or 1
        margin_x, top, bottom = 10, 10, 22
        plot_height = height - top - bottom
        slot = (width - 2 * margin_x) / 49
        bar_width = max(2, slot * 0.62)
        for index, count in enumerate(counts):
            x = margin_x + index * slot
            bar_height = (count / maximum) * plot_height
            canvas.create_rectangle(x, top + plot_height - bar_height, x + bar_width, top + plot_height, fill=COLORS["blue"] if count else COLORS["border"], outline="")
        canvas.create_line(margin_x, height - bottom, width - margin_x, height - bottom, fill=COLORS["border"])
        for number in (1, 10, 20, 30, 40, 49):
            x = margin_x + (number - 1) * slot
            canvas.create_text(x, height - 8, text=str(number), fill=COLORS["muted"], font=("Segoe UI", 8), anchor="s")

    def import_csv(self) -> None:
        path = filedialog.askopenfilename(title="Ziehungsdaten auswählen", filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not path:
            return
        try:
            self.draws = parse_draw_csv(path)
            self.data_label = f"Importiert: {Path(path).name} (Zeilen: älteste zuerst)"
            self.tickets.clear()
            self._clear_table()
            self.refresh_dashboard()
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("Import fehlgeschlagen", str(error), parent=self)

    def restore_demo(self) -> None:
        self.draws = demo_draws()
        self.data_label = "Beispiel-Daten (synthetisch)"
        self.tickets.clear()
        self._clear_table()
        self.refresh_dashboard()

    def generate(self) -> None:
        try:
            count = int(self.tip_count.get())
            low_sum = int(self.sum_min.get())
            high_sum = int(self.sum_max.get())
            min_even = int(self.even_min.get())
            max_even = int(self.even_max.get())
            self.tickets = create_tickets(self.draws, count, low_sum, high_sum, min_even, max_even, self.mode.get())
        except ValueError as error:
            messagebox.showerror("Einstellungen prüfen", str(error), parent=self)
            return
        self._clear_table()
        for index, ticket in enumerate(self.tickets, start=1):
            even = sum(number % 2 == 0 for number in ticket)
            self.table.insert("", "end", values=(index, "  ·  ".join(f"{n:02d}" for n in ticket), sum(ticket), even, 6 - even))

    def _clear_table(self) -> None:
        self.table.delete(*self.table.get_children())

    def export_csv(self) -> None:
        if not self.tickets:
            messagebox.showinfo("Noch keine Tipps", "Erzeuge zuerst Tipps, die exportiert werden können.", parent=self)
            return
        path = filedialog.asksaveasfilename(title="Tipps exportieren", defaultextension=".csv", filetypes=(("CSV-Datei", "*.csv"),))
        if not path:
            return
        try:
            save_tickets_csv(path, self.tickets)
            messagebox.showinfo("Export abgeschlossen", f"Die Tipps wurden gespeichert:\n{path}", parent=self)
        except OSError as error:
            messagebox.showerror("Export fehlgeschlagen", str(error), parent=self)


def main() -> None:
    LottoApp().mainloop()


if __name__ == "__main__":
    main()
