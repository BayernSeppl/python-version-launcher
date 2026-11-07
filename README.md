import csv
import sqlite3
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "LottoPro Analyse"
DATABASE_PATH = Path(__file__).resolve().with_name("lotto_data.sqlite3")
MIN_NUMBER = 1
MAX_NUMBER = 49
NUMBERS_PER_DRAW = 6


def init_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT,
            game TEXT DEFAULT '6aus49',
            numbers TEXT NOT NULL,
            sum_total INTEGER,
            even_count INTEGER,
            odd_count INTEGER,
            UNIQUE(game, draw_date, numbers)
        )
        """
    )
    connection.commit()
    return connection


def normalize_numbers(items) -> list[int]:
    values: list[int] = []
    for item in items:
        if item is None:
            continue
        for token in str(item).replace(";", ",").replace("\t", ",").split(","):
            token = token.strip()
            if not token:
                continue
            try:
                value = int(float(token))
            except ValueError:
                continue
            if MIN_NUMBER <= value <= MAX_NUMBER:
                values.append(value)
    return values


def parse_date_cell(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    candidates = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%Y-%d-%m",
        "%d.%m.%y",
        "%d/%m/%y",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_row_data(row: list[str]) -> tuple[str | None, list[int]]:
    date_value = None
    values: list[int] = []
    for index, cell in enumerate(row):
        text = str(cell).strip()
        if not text:
            continue
        if index == 0 and any(word in text.lower() for word in ["datum", "date"]) and len(row) > 1:
            continue
        if index == 0 and parse_date_cell(text):
            date_value = parse_date_cell(text)
        if any(word in text.lower() for word in ["datum", "date", "draw", "ziehung"]):
            continue
        values.extend(normalize_numbers([text]))
    if not values:
        values = normalize_numbers(row)
    if len(values) < NUMBERS_PER_DRAW:
        return date_value, []
    unique = sorted(set(values))
    if len(unique) < NUMBERS_PER_DRAW:
        return date_value, []
    return date_value, unique[:NUMBERS_PER_DRAW]


def import_csv_file(path: str | Path) -> int:
    database = init_db()
    imported = 0
    path_obj = Path(path)
    with open(path_obj, "r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        first_row = True
        for row in reader:
            if not row:
                continue
            row_text = [str(value).strip() for value in row]
            if first_row:
                first_row = False
                if any("datum" in value.lower() for value in row_text) or any("date" in value.lower() for value in row_text):
                    continue
            draw_date, numbers = extract_row_data(row)
            if len(numbers) != NUMBERS_PER_DRAW:
                continue
            if draw_date is None:
                draw_date = "0000-00-00"
            total = sum(numbers)
            even_count = sum(n % 2 == 0 for n in numbers)
            odd_count = NUMBERS_PER_DRAW - even_count
            try:
                database.execute(
                    "INSERT OR IGNORE INTO draws (draw_date, game, numbers, sum_total, even_count, odd_count) VALUES (?, ?, ?, ?, ?, ?)",
                    (draw_date, "6aus49", "|".join(str(n) for n in numbers), total, even_count, odd_count),
                )
                if database.total_changes:
                    imported += 1
            except sqlite3.Error:
                continue
    database.commit()
    database.close()
    return imported


def list_draws() -> list[tuple[str, list[int]]]:
    database = init_db()
    rows = database.execute(
        "SELECT draw_date, numbers FROM draws WHERE game = '6aus49' ORDER BY draw_date ASC, id ASC"
    ).fetchall()
    database.close()
    result = []
    for draw_date, numbers_field in rows:
        numbers = [int(value) for value in str(numbers_field).split("|") if value]
        result.append((draw_date, numbers))
    return result


def number_statistics(draws: list[tuple[str, list[int]]]) -> dict[int, dict[str, int | None]]:
    stats = {n: {"count": 0, "last_index": None, "draws_ago": None} for n in range(MIN_NUMBER, MAX_NUMBER + 1)}
    for index, (_, numbers) in enumerate(draws):
        for number in numbers:
            info = stats[number]
            info["count"] = int(info["count"]) + 1
            info["last_index"] = index
    last_index = len(draws) - 1
    for number in range(MIN_NUMBER, MAX_NUMBER + 1):
        info = stats[number]
        index = info["last_index"]
        info["draws_ago"] = last_index - int(index) if index is not None else len(draws)
    return stats


def build_tickets(draws: list[tuple[str, list[int]]], count: int,
                 low_sum: int, high_sum: int, min_even: int,
                 max_even: int, mode: str) -> list[list[int]]:
    if not 1 <= count <= 200:
        raise ValueError("Bitte eine Anzahl von 1 bis 200 auswählen.")
    if not 21 <= low_sum <= high_sum <= 279:
        raise ValueError("Die Summe muss zwischen 21 und 279 liegen.")
    if not 0 <= min_even <= max_even <= 6:
        raise ValueError("Gerade-Zahlenfilter muss zwischen 0 und 6 liegen.")

    stats = number_statistics(draws)
    universe = list(range(MIN_NUMBER, MAX_NUMBER + 1))
    weights = [1.0 + int(stats[n]["count"] or 0) for n in universe] if mode == "Häufige Zahlen berücksichtigen" else None

    result: set[tuple[int, ...]] = set()
    attempts = 0
    while len(result) < count and attempts < 100000:
        attempts += 1
        if weights:
            picks: list[int] = []
            while len(picks) < NUMBERS_PER_DRAW:
                choice = __import__("random").choices(universe, weights=weights, k=1)[0]
                if choice not in picks:
                    picks.append(choice)
            ticket = tuple(sorted(picks))
        else:
            ticket = tuple(sorted(__import__("random").sample(universe, NUMBERS_PER_DRAW)))
        even_count = sum(number % 2 == 0 for number in ticket)
        if not low_sum <= sum(ticket) <= high_sum:
            continue
        if not min_even <= even_count <= max_even:
            continue
        result.add(ticket)

    if len(result) < count:
        raise ValueError("Bei den aktuellen Filtern konnten nicht genügend unterschiedliche Tipps erzeugt werden. Bitte Filter etwas lockern.")
    return [list(ticket) for ticket in sorted(result)]


def export_tickets_csv(path: str | Path, tickets: list[list[int]]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as file_handle:
        writer = csv.writer(file_handle, delimiter=";")
        writer.writerow(["Tipp", "Zahlen", "Summe", "Gerade", "Ungerade"])
        for index, ticket in enumerate(tickets, start=1):
            writer.writerow([
                index,
                " ".join(f"{n:02d}" for n in ticket),
                sum(ticket),
                sum(n % 2 == 0 for n in ticket),
                NUMBERS_PER_DRAW - sum(n % 2 == 0 for n in ticket),
            ])


class LottoProApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x800")
        self.minsize(980, 700)
        self.configure(bg="#edf3fb")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Info.TLabel", background="#edf3fb", foreground="#41536d", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#edf3fb", foreground="#10283f", font=("Segoe UI", 24, "bold"))
        self.style.configure("Small.TLabel", background="#ffffff", foreground="#46586d", font=("Segoe UI", 9, "bold"))
        self.style.configure("Value.TLabel", background="#ffffff", foreground="#10283f", font=("Segoe UI", 20, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("Primary.TButton", foreground="#ffffff", background="#2e65ff", font=("Segoe UI", 10, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#214ee0")])
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#edf1f7")
        self.draws = list_draws()
        self.tickets: list[list[int]] = []
        self.status_text = "Lokale Datenbank: leer"
        self.build_ui()
        self.refresh_dashboard()

    def build_ui(self) -> None:
        outer = ttk.Frame(self, padding=(18, 18, 18, 12))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="LottoPro Analyse", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="6 aus 49 · Historische Analyse · lokale Datensätze", style="Info.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Button(header, text="CSV importieren", command=self.import_selected_csv).grid(row=0, column=1, padx=(6, 4), sticky="e")
        ttk.Button(header, text="Ordner importieren", command=self.import_directory).grid(row=1, column=1, padx=(6, 4), sticky="e")

        note = tk.Label(
            outer,
            text="Hinweis: Historische Ziehungen helfen bei Analyse und Organisation. Jede gültige Nummernkombination hat bei einem fairen Lotto dieselbe Wahrscheinlichkeit. Es gibt keine Garantie für zukünftige Gewinne.",
            bg="#e8eefb", fg="#294a8b", justify="left", anchor="w", padx=12, pady=10, wraplength=1100,
            font=("Segoe UI", 9),
        )
        note.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        cards = ttk.Frame(outer)
        cards.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)
        cards.columnconfigure(2, weight=1)

        self.card_total = self.make_card(cards, 0, "ZIEHUNGEN")
        self.card_hot = self.make_card(cards, 1, "HÄUFIGSTE ZAHL")
        self.card_pause = self.make_card(cards, 2, "LÄNGSTE PAUSE")

        body = ttk.Frame(outer)
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Card.TFrame", padding=(16, 14, 16, 12))
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(1, weight=1)

        ttk.Label(left, text="Tipp-Filter", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        self.count_var = tk.StringVar(value="10")
        self.sum_min_var = tk.StringVar(value="90")
        self.sum_max_var = tk.StringVar(value="190")
        self.even_min_var = tk.StringVar(value="1")
        self.even_max_var = tk.StringVar(value="5")
        self.mode_var = tk.StringVar(value="Zufällig")

        tk.Label(left, text="Anzahl Tipps", bg="#ffffff", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6)
        tk.Entry(left, textvariable=self.count_var, width=10).grid(row=1, column=1, sticky="w", pady=6)

        tk.Label(left, text="Summe von", bg="#ffffff", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=6)
        tk.Entry(left, textvariable=self.sum_min_var, width=10).grid(row=2, column=1, sticky="w", pady=6)
        tk.Label(left, text="bis", bg="#ffffff", font=("Segoe UI", 10)).grid(row=2, column=2, sticky="w", pady=6)
        tk.Entry(left, textvariable=self.sum_max_var, width=10).grid(row=2, column=3, sticky="w", pady=6)

        tk.Label(left, text="Gerade Zahlen min.", bg="#ffffff", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=6)
        tk.Entry(left, textvariable=self.even_min_var, width=10).grid(row=3, column=1, sticky="w", pady=6)
        tk.Label(left, text="max.", bg="#ffffff", font=("Segoe UI", 10)).grid(row=3, column=2, sticky="w", pady=6)
        tk.Entry(left, textvariable=self.even_max_var, width=10).grid(row=3, column=3, sticky="w", pady=6)

        ttk.Label(left, text="Auswahlmodus").grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Combobox(left, textvariable=self.mode_var, values=("Zufällig", "Häufige Zahlen berücksichtigen"), state="readonly", width=24).grid(row=4, column=1, columnspan=2, sticky="w", pady=(12, 0))

        button_frame = ttk.Frame(left)
        button_frame.grid(row=5, column=0, columnspan=4, sticky="w", pady=(18, 0))
        ttk.Button(button_frame, text="Tipps erstellen", command=self.generate_tickets, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="CSV exportieren", command=self.export_tickets).pack(side="left")

        result_box = ttk.Frame(left, style="Card.TFrame", padding=(12, 12, 12, 10))
        result_box.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(20, 0))
        result_box.columnconfigure(0, weight=1)
        result_box.rowconfigure(1, weight=1)

        ttk.Label(result_box, text="Erzeugte Zahlenkombinationen", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.tree = ttk.Treeview(result_box, columns=("nr", "zahlen", "summe", "gerade", "ungerade"), show="headings", height=10)
        self.tree.heading("nr", text="Nr.")
        self.tree.heading("zahlen", text="Zahlen")
        self.tree.heading("summe", text="Summe")
        self.tree.heading("gerade", text="Gerade")
        self.tree.heading("ungerade", text="Ungerade")
        self.tree.column("nr", width=55, anchor="center")
        self.tree.column("zahlen", width=240, anchor="center")
        self.tree.column("summe", width=80, anchor="center")
        self.tree.column("gerade", width=80, anchor="center")
        self.tree.column("ungerade", width=90, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        right = ttk.Frame(body, style="Card.TFrame", padding=(16, 14, 16, 12))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, text="Zahlen-Häufigkeit", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.data_status = ttk.Label(right, text="Lokale Datenbank: leer", style="Info.TLabel")
        self.data_status.grid(row=1, column=0, sticky="w", pady=(4, 10))
        self.chart_canvas = tk.Canvas(right, bg="#ffffff", highlightthickness=0, height=260)
        self.chart_canvas.grid(row=2, column=0, sticky="nsew")

        ttk.Button(right, text="Demo-Daten laden", command=self.load_demo_data).grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.chart_canvas.bind("<Configure>", lambda event: self.draw_chart())

        footer = ttk.Label(outer, text="Lokale Lotto-Datenbank • Daten aus CSV/Excel-Exporten • keine Vorhersage- oder Gewinngarantie", style="Info.TLabel")
        footer.grid(row=4, column=0, sticky="w", pady=(16, 0))

    def make_card(self, parent: ttk.Frame, column: int, label: str) -> ttk.Label:
        card = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        card.grid(row=0, column=column, sticky="nsew", padx=(0, 8 if column < 2 else 0))
        ttk.Label(card, text=label, style="Small.TLabel").pack(anchor="w")
        value = ttk.Label(card, text="—", style="Value.TLabel")
        value.pack(anchor="w", pady=(6, 0))
        return value

    def refresh_dashboard(self) -> None:
        stats = number_statistics(self.draws)
        most_common = max(range(MIN_NUMBER, MAX_NUMBER + 1), key=lambda n: (stats[n]["count"], -n))
        longest_pause = max(range(MIN_NUMBER, MAX_NUMBER + 1), key=lambda n: (stats[n]["draws_ago"], -n))

        self.card_total.configure(text=str(len(self.draws)))
        self.card_hot.configure(text=f"{most_common:02d} · {stats[most_common]['count']}×")
        self.card_pause.configure(text=f"{longest_pause:02d} · {stats[longest_pause]['draws_ago']} Ziehungen")
        self.data_status.configure(text=f"Lokale Datenbank: {len(self.draws)} Ziehungen geladen")
        self.draw_chart()

    def draw_chart(self) -> None:
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 200)
        stats = number_statistics(self.draws)
        values = [int(stats[n]["count"]) for n in range(MIN_NUMBER, MAX_NUMBER + 1)]
        maximum = max(values) if values else 1
        margin_left = 20
        margin_right = 10
        margin_top = 10
        margin_bottom = 18
        inner_width = width - margin_left - margin_right
        inner_height = height - margin_top - margin_bottom
        step = inner_width / 49
        bar_width = max(2, step * 0.7)
        for index, value in enumerate(values):
            x0 = margin_left + index * step
            bar_height = (value / maximum) * inner_height
            y0 = height - margin_bottom - bar_height
            canvas.create_rectangle(x0, y0, x0 + bar_width, height - margin_bottom, fill="#345ef8", outline="")
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, fill="#d5d9e0")

    def import_selected_csv(self) -> None:
        path = filedialog.askopenfilename(title="CSV mit Lotto-Ziehungen wählen", filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")))
        if not path:
            return
        try:
            imported = import_csv_file(path)
            self.draws = list_draws()
            self.refresh_dashboard()
            messagebox.showinfo("Erfolgreich", f"{imported} Ziehungen importiert.", parent=self)
        except Exception as exc:
            messagebox.showerror("Import fehlgeschlagen", str(exc), parent=self)

    def import_directory(self) -> None:
        directory = filedialog.askdirectory(title="Ordner mit CSV-Dateien wählen")
        if not directory:
            return
        count = 0
        for path in sorted(Path(directory).glob("*.csv")):
            try:
                count += import_csv_file(path)
            except Exception:
                continue
        self.draws = list_draws()
        self.refresh_dashboard()
        messagebox.showinfo("Erfolgreich", f"{count} Ziehungen aus dem Ordner importiert.", parent=self)

    def load_demo_data(self) -> None:
        database = init_db()
        database.execute("DELETE FROM draws WHERE game = '6aus49'")
        demo = [
            [1, 7, 12, 18, 27, 49],
            [3, 8, 15, 21, 32, 42],
            [4, 9, 13, 24, 37, 45],
            [2, 5, 11, 19, 31, 43],
            [6, 12, 17, 26, 34, 47],
            [8, 16, 22, 28, 39, 46],
            [1, 10, 14, 23, 35, 41],
            [5, 9, 18, 25, 33, 48],
            [2, 7, 15, 20, 30, 44],
            [4, 11, 16, 29, 36, 49],
            [3, 13, 19, 24, 38, 45],
            [1, 8, 17, 27, 35, 42],
            [6, 14, 20, 28, 37, 46],
            [2, 11, 16, 26, 31, 48],
            [5, 9, 18, 24, 39, 45],
        ]
        for index, numbers in enumerate(demo, start=1):
            draw_date = f"2024-01-{index:02d}"
            total = sum(numbers)
            even_count = sum(n % 2 == 0 for n in numbers)
            odd_count = NUMBERS_PER_DRAW - even_count
            database.execute(
                "INSERT OR IGNORE INTO draws (draw_date, game, numbers, sum_total, even_count, odd_count) VALUES (?, ?, ?, ?, ?, ?)",
                (draw_date, "6aus49", "|".join(str(n) for n in numbers), total, even_count, odd_count),
            )
        database.commit()
        database.close()
        self.draws = list_draws()
        self.refresh_dashboard()

    def generate_tickets(self) -> None:
        try:
            count = int(self.count_var.get())
            low_sum = int(self.sum_min_var.get())
            high_sum = int(self.sum_max_var.get())
            min_even = int(self.even_min_var.get())
            max_even = int(self.even_max_var.get())
        except ValueError:
            messagebox.showerror("Eingabe prüfen", "Bitte nur ganze Zahlen eingeben.", parent=self)
            return
        try:
            tickets = build_tickets(self.draws, count, low_sum, high_sum, min_even, max_even, self.mode_var.get())
        except ValueError as exc:
            messagebox.showerror("Filter zu streng", str(exc), parent=self)
            return
        self.tickets = tickets
        self.tree.delete(*self.tree.get_children())
        for index, ticket in enumerate(tickets, start=1):
            total = sum(ticket)
            even_count = sum(number % 2 == 0 for number in ticket)
            self.tree.insert("", "end", values=(index, "  ".join(f"{n:02d}" for n in ticket), total, even_count, NUMBERS_PER_DRAW - even_count))

    def export_tickets(self) -> None:
        if not self.tickets:
            messagebox.showinfo("Keine Tipps", "Zuerst Tipps erstellen, dann exportieren.", parent=self)
            return
        path = filedialog.asksaveasfilename(title="Tipps als CSV exportieren", defaultextension=".csv", filetypes=(("CSV-Datei", "*.csv"),))
        if not path:
            return
        try:
            export_tickets_csv(path, self.tickets)
            messagebox.showinfo("Erfolgreich", f"Tipps gespeichert unter:\n{path}", parent=self)
        except OSError as exc:
            messagebox.showerror("Export fehlgeschlagen", str(exc), parent=self)


def main() -> None:
    init_db()
    app = LottoProApp()
    app.mainloop()


if __name__ == "__main__":
    main()
