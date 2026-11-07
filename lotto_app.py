"""LottoPro: desktop analysis for historical Lotto 6 aus 49 draws.

This app organizes historical results; it cannot predict future draws or improve
odds in a fair lottery.
"""

from __future__ import annotations

import csv
import os
import random
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "LottoPro Analyse"
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "LottoPro"
DB_PATH = APP_DIR / "lotto_data.sqlite3"
LOW, HIGH, DRAW_SIZE = 1, 49, 6
MAX_TIPS = 100

COLORS = {
    "bg": "#f2f5fa", "card": "#ffffff", "ink": "#14263e",
    "muted": "#627188", "blue": "#315efb", "blue_light": "#e8efff",
    "line": "#dfe6ef", "green": "#16856b",
}


def connect_db() -> sqlite3.Connection:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("""
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT NOT NULL DEFAULT '',
            numbers TEXT NOT NULL,
            UNIQUE(draw_date, numbers)
        )
    """)
    db.commit()
    return db


def parse_date(text: str) -> str:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""


def read_csv_draws(path: str | Path) -> tuple[list[tuple[str, list[int]]], int]:
    """Accept CSV rows with six main numbers, optionally preceded by a date.

    Rows with more than six numeric cells are skipped rather than guessing which
    extra fields are bonus numbers or draw identifiers.
    """
    parsed: list[tuple[str, list[int]]] = []
    skipped = 0
    with open(path, "r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(4096)
        stream.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t,")
        except csv.Error:
            dialect = csv.excel
        for row in csv.reader(stream, dialect):
            if not row:
                continue
            date = ""
            numbers: list[int] = []
            for cell in row:
                text = cell.strip()
                if not date:
                    date = parse_date(text)
                try:
                    value = int(text)
                except ValueError:
                    continue
                if LOW <= value <= HIGH:
                    numbers.append(value)
                else:
                    # Numeric fields outside 1..49 may be IDs/bonus values; do not
                    # guess the layout of an unknown export.
                    continue
            if len(numbers) == DRAW_SIZE and len(set(numbers)) == DRAW_SIZE:
                parsed.append((date, sorted(numbers)))
            else:
                skipped += 1
    if not parsed:
        raise ValueError("Keine gültigen Zeilen mit genau sechs verschiedenen Hauptzahlen (1–49) gefunden.")
    return parsed, skipped


def import_draw_file(path: str | Path) -> tuple[int, int, int]:
    draws, skipped = read_csv_draws(path)
    added = 0
    duplicates = 0
    db = connect_db()
    try:
        with db:
            for date, numbers in draws:
                key = " ".join(str(n) for n in numbers)
                cursor = db.execute(
                    "INSERT OR IGNORE INTO draws (draw_date, numbers) VALUES (?, ?)",
                    (date, key),
                )
                if cursor.rowcount:
                    added += 1
                else:
                    duplicates += 1
    finally:
        db.close()
    return added, duplicates, skipped


def import_csv_folder(folder: str | Path) -> tuple[int, int, int, int]:
    files = sorted(Path(folder).glob("*.csv"))
    added = duplicates = skipped = errors = 0
    if not files:
        raise ValueError("Im ausgewählten Ordner wurden keine CSV-Dateien gefunden.")
    for path in files:
        try:
            a, d, s = import_draw_file(path)
            added += a
            duplicates += d
            skipped += s
        except (OSError, UnicodeError, csv.Error, ValueError):
            errors += 1
    return added, duplicates, skipped, errors


def load_draws() -> list[tuple[str, list[int]]]:
    db = connect_db()
    try:
        rows = db.execute("SELECT draw_date, numbers FROM draws ORDER BY CASE WHEN draw_date='' THEN 1 ELSE 0 END, draw_date, id").fetchall()
    finally:
        db.close()
    return [(date, [int(n) for n in numbers.split()]) for date, numbers in rows]


def calculate_stats(draws: list[tuple[str, list[int]]], recent_window: int = 20) -> dict[int, dict[str, int | str]]:
    recent = draws[-recent_window:] if recent_window else draws
    counts = {n: 0 for n in range(LOW, HIGH + 1)}
    recent_counts = {n: 0 for n in range(LOW, HIGH + 1)}
    last_seen: dict[int, int] = {}
    for i, (_, numbers) in enumerate(draws):
        for number in numbers:
            counts[number] += 1
            last_seen[number] = i
    for _, numbers in recent:
        for number in numbers:
            recent_counts[number] += 1
    final_index = len(draws) - 1
    return {
        n: {
            "total": counts[n],
            "recent": recent_counts[n],
            "gap": final_index - last_seen[n] if n in last_seen else len(draws),
        }
        for n in range(LOW, HIGH + 1)
    }


def build_tips(draws: list[tuple[str, list[int]]], amount: int, min_sum: int, max_sum: int,
               min_even: int, max_even: int, weighted: bool) -> list[list[int]]:
    if not 1 <= amount <= MAX_TIPS:
        raise ValueError(f"Bitte 1 bis {MAX_TIPS} Tipps anfordern.")
    if not 21 <= min_sum <= max_sum <= 279:
        raise ValueError("Die Summenfilter müssen zwischen 21 und 279 liegen.")
    if not 0 <= min_even <= max_even <= 6:
        raise ValueError("Der Gerade-Zahlenfilter muss zwischen 0 und 6 liegen.")
    pool = list(range(LOW, HIGH + 1))
    stats = calculate_stats(draws)
    weights = [1 + int(stats[n]["total"]) for n in pool] if weighted and draws else None
    found: set[tuple[int, ...]] = set()
    for _ in range(max(5000, amount * 2500)):
        if len(found) >= amount:
            break
        if weights:
            picked: list[int] = []
            while len(picked) < DRAW_SIZE:
                n = random.choices(pool, weights=weights, k=1)[0]
                if n not in picked:
                    picked.append(n)
            ticket = tuple(sorted(picked))
        else:
            ticket = tuple(sorted(random.sample(pool, DRAW_SIZE)))
        even = sum(n % 2 == 0 for n in ticket)
        if min_sum <= sum(ticket) <= max_sum and min_even <= even <= max_even:
            found.add(ticket)
    if len(found) < amount:
        raise ValueError("Mit diesen Filtern konnten nicht genügend unterschiedliche Tipps erzeugt werden. Bitte Filter lockern.")
    return [list(row) for row in sorted(found)]


def export_tips(path: str | Path, tips: list[list[int]]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Tipp", "Zahlen", "Summe", "Gerade", "Ungerade"])
        for i, ticket in enumerate(tips, 1):
            even = sum(n % 2 == 0 for n in ticket)
            writer.writerow([i, " ".join(f"{n:02d}" for n in ticket), sum(ticket), even, 6 - even])


class LottoProApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x820")
        self.minsize(980, 680)
        self.configure(bg=COLORS["bg"])
        self.draws = load_draws()
        self.tickets: list[list[int]] = []
        self.window_var = tk.StringVar(value="20")
        self._setup_style()
        self._build_ui()
        self.refresh()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure("TLabel", background=COLORS["card"], foreground=COLORS["ink"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["ink"], font=("Segoe UI", 23, "bold"))
        style.configure("CardHead.TLabel", background=COLORS["card"], foreground=COLORS["muted"], font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background=COLORS["card"], foreground=COLORS["ink"], font=("Segoe UI", 20, "bold"))
        style.configure("Primary.TButton", background=COLORS["blue"], foreground="white", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("Primary.TButton", background=[("active", "#244bd0")])
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=6)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(4, weight=1)

        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="LottoPro Analyse", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="6 aus 49 · lokale Ziehungsdaten · Statistik & Tipp-Organisation", style="Muted.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="CSV importieren", command=self.import_file).grid(row=0, column=1, rowspan=2, padx=4)
        ttk.Button(header, text="Ordner aktualisieren", command=self.import_folder).grid(row=0, column=2, rowspan=2, padx=4)

        tk.Label(root, text="Frühere Ziehungen sagen künftige Ergebnisse nicht voraus. Jede gültige Kombination hat bei einer fairen Ziehung dieselbe Gewinnchance.", bg=COLORS["blue_light"], fg="#294a8b", padx=12, pady=9, anchor="w", justify="left", wraplength=1100, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="ew", pady=(0, 13))

        cards = ttk.Frame(root)
        cards.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        for col in range(3):
            cards.columnconfigure(col, weight=1)
        self.draws_card = self._card(cards, 0, "GESPEICHERTE ZIEHUNGEN")
        self.hot_card = self._card(cards, 1, "HÄUFIGSTE ZAHL")
        self.gap_card = self._card(cards, 2, "LÄNGSTE PAUSE")

        import_bar = ttk.Frame(root, style="Card.TFrame", padding=10)
        import_bar.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        import_bar.columnconfigure(1, weight=1)
        ttk.Label(import_bar, text="Lokale Datenbank", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.status = ttk.Label(import_bar, text="Noch keine Ziehungen importiert", style="Muted.TLabel")
        self.status.grid(row=0, column=1, sticky="w")
        ttk.Button(import_bar, text="Datenbank öffnen", command=self.open_data_folder).grid(row=0, column=2)

        tabs = ttk.Notebook(root)
        tabs.grid(row=4, column=0, sticky="nsew")
        analysis = ttk.Frame(tabs, padding=12)
        history = ttk.Frame(tabs, padding=12)
        tabs.add(analysis, text="Analyse & Tipps")
        tabs.add(history, text="Ziehungen & Vergleich")
        self._build_analysis_tab(analysis)
        self._build_history_tab(history)

        ttk.Label(root, text=f"Datenbank: {DB_PATH}  ·  Analysewerkzeug, keine Gewinnprognose", style="Muted.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 0))

    def _card(self, parent: ttk.Frame, col: int, title: str) -> ttk.Label:
        card = ttk.Frame(parent, style="Card.TFrame", padding=13)
        card.grid(row=0, column=col, sticky="ew", padx=(0, 8 if col < 2 else 0))
        ttk.Label(card, text=title, style="CardHead.TLabel").pack(anchor="w")
        value = ttk.Label(card, text="—", style="CardValue.TLabel")
        value.pack(anchor="w", pady=(5, 0))
        return value

    def _build_analysis_tab(self, tab: ttk.Frame) -> None:
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)
        controls = ttk.Frame(tab, style="Card.TFrame", padding=14)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Tipp-Einstellungen", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        self.tip_count = self._entry(controls, "Anzahl Tipps", "10", 1, 0)
        self.sum_min = self._entry(controls, "Summe von", "90", 1, 2)
        self.sum_max = self._entry(controls, "bis", "190", 1, 4)
        self.even_min = self._entry(controls, "Gerade min.", "1", 2, 0)
        self.even_max = self._entry(controls, "max.", "5", 2, 2)
        ttk.Label(controls, text="Auswahl").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.mode = tk.StringVar(value="Zufällig")
        ttk.Combobox(controls, textvariable=self.mode, values=("Zufällig", "Häufige Zahlen berücksichtigen"), state="readonly", width=29).grid(row=3, column=1, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(controls, text="Tipps erzeugen", style="Primary.TButton", command=self.generate).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 12))
        ttk.Button(controls, text="Tipps als CSV speichern", command=self.export).grid(row=4, column=2, columnspan=2, sticky="w", pady=(12, 12))
        self.tip_table = ttk.Treeview(controls, columns=("no", "numbers", "sum", "even", "odd"), show="headings", height=12)
        for key, title, width in (("no", "Nr.", 45), ("numbers", "Zahlen", 205), ("sum", "Summe", 65), ("even", "Gerade", 65), ("odd", "Ungerade", 70)):
            self.tip_table.heading(key, text=title)
            self.tip_table.column(key, width=width, anchor="center")
        self.tip_table.grid(row=5, column=0, columnspan=4, sticky="nsew")

        chart_frame = ttk.Frame(tab, style="Card.TFrame", padding=14)
        chart_frame.grid(row=0, column=1, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(1, weight=1)
        ttk.Label(chart_frame, text="Häufigkeit 1–49", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.chart = tk.Canvas(chart_frame, bg="white", highlightthickness=0, height=260)
        self.chart.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        ttk.Label(chart_frame, text="Die Darstellung beschreibt nur die importierten vergangenen Ziehungen.", style="Muted.TLabel", wraplength=330).grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.chart.bind("<Configure>", lambda _event: self.draw_chart())

    @staticmethod
    def _entry(parent: ttk.Frame, label: str, initial: str, row: int, col: int) -> tk.StringVar:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", pady=5)
        var = tk.StringVar(value=initial)
        ttk.Entry(parent, textvariable=var, width=8).grid(row=row, column=col + 1, sticky="w", padx=(5, 12), pady=5)
        return var

    def _build_history_tab(self, tab: ttk.Frame) -> None:
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(tab)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        ttk.Label(toolbar, text="Vergleiche Gesamtzahl und jüngeren Zeitraum:").pack(side="left", padx=(0, 8))
        ttk.Combobox(toolbar, textvariable=self.window_var, values=("10", "20", "50"), state="readonly", width=6).pack(side="left")
        ttk.Button(toolbar, text="Vergleich aktualisieren", command=self.refresh).pack(side="left", padx=8)
        ttk.Label(toolbar, text="Datenstand: neueste Ziehung zuerst in der Liste", style="Muted.TLabel").pack(side="right")
        panes = ttk.Panedwindow(tab, orient="vertical")
        panes.grid(row=1, column=0, sticky="nsew")
        stats_frame = ttk.Frame(panes)
        draws_frame = ttk.Frame(panes)
        panes.add(stats_frame, weight=3)
        panes.add(draws_frame, weight=2)
        stats_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        self.stats_table = ttk.Treeview(stats_frame, columns=("n", "all", "recent", "gap"), show="headings", height=15)
        for key, title, width in (("n", "Zahl", 100), ("all", "Gesamt", 130), ("recent", "Letzte Ziehungen", 180), ("gap", "Ziehungen seit letztem Auftreten", 230)):
            self.stats_table.heading(key, text=title)
            self.stats_table.column(key, width=width, anchor="center")
        self.stats_table.grid(row=0, column=0, sticky="nsew")
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_table.yview)
        stats_scroll.grid(row=0, column=1, sticky="ns")
        self.stats_table.configure(yscrollcommand=stats_scroll.set)

        draws_frame.rowconfigure(0, weight=1)
        draws_frame.columnconfigure(0, weight=1)
        self.draw_table = ttk.Treeview(draws_frame, columns=("date", "numbers", "sum"), show="headings", height=8)
        for key, title, width in (("date", "Datum", 150), ("numbers", "Gezogene Zahlen", 330), ("sum", "Summe", 100)):
            self.draw_table.heading(key, text=title)
            self.draw_table.column(key, width=width, anchor="center")
        self.draw_table.grid(row=0, column=0, sticky="nsew")

    def refresh(self) -> None:
        self.draws = load_draws()
        stats = calculate_stats(self.draws, int(self.window_var.get()))
        recent_window = int(self.window_var.get())
        hottest = max(range(LOW, HIGH + 1), key=lambda n: (stats[n]["total"], -n))
        longest = max(range(LOW, HIGH + 1), key=lambda n: (stats[n]["gap"], -n))
        self.draws_card.configure(text=str(len(self.draws)))
        self.hot_card.configure(text=f"{hottest:02d} · {stats[hottest]['total']}×")
        self.gap_card.configure(text=f"{longest:02d} · {stats[longest]['gap']} Ziehungen")
        self.status.configure(text=f"{len(self.draws)} Ziehungen gespeichert · Fenstervergleich: letzte {min(recent_window, len(self.draws))}")
        self.stats_table.delete(*self.stats_table.get_children())
        for n in range(LOW, HIGH + 1):
            self.stats_table.insert("", "end", values=(f"{n:02d}", stats[n]["total"], stats[n]["recent"], stats[n]["gap"]))
        self.draw_table.delete(*self.draw_table.get_children())
        for date, numbers in reversed(self.draws[-200:]):
            self.draw_table.insert("", "end", values=(date or "ohne Datum", "  ·  ".join(f"{n:02d}" for n in numbers), sum(numbers)))
        self.draw_chart()

    def draw_chart(self) -> None:
        if not hasattr(self, "chart"):
            return
        canvas = self.chart
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 280), max(canvas.winfo_height(), 180)
        stats = calculate_stats(self.draws)
        values = [int(stats[n]["total"]) for n in range(LOW, HIGH + 1)]
        maximum = max(values, default=1) or 1
        margin_x, margin_y, bottom = 10, 10, 20
        plot_height = height - margin_y - bottom
        slot = (width - 2 * margin_x) / 49
        for i, value in enumerate(values):
            x = margin_x + i * slot
            bar_height = value / maximum * plot_height
            canvas.create_rectangle(x, margin_y + plot_height - bar_height, x + max(2, slot * .64), margin_y + plot_height, fill=COLORS["blue"], outline="")
        canvas.create_line(margin_x, height - bottom, width - margin_x, height - bottom, fill=COLORS["line"])
        for n in (1, 10, 20, 30, 40, 49):
            x = margin_x + (n - 1) * slot
            canvas.create_text(x, height - 5, text=str(n), fill=COLORS["muted"], font=("Segoe UI", 8), anchor="s")

    def import_file(self) -> None:
        path = filedialog.askopenfilename(title="CSV mit Ziehungen wählen", filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not path:
            return
        try:
            added, duplicates, skipped = import_draw_file(path)
            self.refresh()
            messagebox.showinfo("Import abgeschlossen", f"Neu gespeichert: {added}\nBereits vorhanden: {duplicates}\nÜbersprungen/ungültig: {skipped}", parent=self)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            messagebox.showerror("Import fehlgeschlagen", str(error), parent=self)

    def import_folder(self) -> None:
        folder = filedialog.askdirectory(title="Ordner mit CSV-Dateien auswählen")
        if not folder:
            return
        try:
            added, duplicates, skipped, errors = import_csv_folder(folder)
            self.refresh()
            messagebox.showinfo("Daten aktualisiert", f"Neu gespeichert: {added}\nBereits vorhanden: {duplicates}\nÜbersprungen/ungültig: {skipped}\nDateifehler: {errors}", parent=self)
        except (OSError, ValueError) as error:
            messagebox.showerror("Aktualisierung fehlgeschlagen", str(error), parent=self)

    def open_data_folder(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(APP_DIR)  # type: ignore[attr-defined]
        else:
            messagebox.showinfo("Datenbankordner", str(APP_DIR), parent=self)

    def generate(self) -> None:
        try:
            self.tickets = build_tips(
                self.draws, int(self.tip_count.get()), int(self.sum_min.get()), int(self.sum_max.get()),
                int(self.even_min.get()), int(self.even_max.get()),
                self.mode.get() == "Häufige Zahlen berücksichtigen",
            )
        except ValueError as error:
            messagebox.showerror("Einstellungen prüfen", str(error), parent=self)
            return
        self.tip_table.delete(*self.tip_table.get_children())
        for i, ticket in enumerate(self.tickets, 1):
            even = sum(n % 2 == 0 for n in ticket)
            self.tip_table.insert("", "end", values=(i, "  ·  ".join(f"{n:02d}" for n in ticket), sum(ticket), even, 6 - even))

    def export(self) -> None:
        if not self.tickets:
            messagebox.showinfo("Keine Tipps", "Erzeuge zuerst Tipps zum Exportieren.", parent=self)
            return
        path = filedialog.asksaveasfilename(title="Tipps speichern", defaultextension=".csv", filetypes=(("CSV-Datei", "*.csv"),))
        if path:
            try:
                export_tips(path, self.tickets)
                messagebox.showinfo("Export abgeschlossen", f"Gespeichert unter:\n{path}", parent=self)
            except OSError as error:
                messagebox.showerror("Export fehlgeschlagen", str(error), parent=self)


def main() -> None:
    connect_db().close()
    LottoProApp().mainloop()


if __name__ == "__main__":
    main()
