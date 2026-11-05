"""Testimonial Studio — gather, polish, and export customer feedback."""

from __future__ import annotations

import csv
import json
import re
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Testimonial Studio"
BG = "#f5f7fb"
CARD = "#ffffff"
INK = "#172033"
MUTED = "#68748a"
ACCENT = "#5267e8"
SUCCESS = "#1f9d63"
WARNING = "#d97706"
DANGER = "#d14343"
BORDER = "#e4e9f2"

STATUS_OPTIONS = ["approved", "pending", "rejected"]
STATUS_LABELS = {"approved": "Freigegeben", "pending": "In Prüfung", "rejected": "Abgelehnt"}
RATING_LABELS = {"5": "★★★★★", "4": "★★★★☆", "3": "★★★☆☆", "2": "★★☆☆☆", "1": "★☆☆☆☆"}

TESTIMONIAL_TEMPLATES = {
    "Kurz & stark": "{quote}",
    "Spontan & freundlich": "{quote}\n\nVielen Dank für das Vertrauen in unser Team!",
    "Professionell": "{quote}\n\nWir freuen uns über das Vertrauen und die Unterstützung unserer Kunden.",
    "Case-Style": """{quote}\n\nDas hat uns besonders motiviert, weil wir damit einen echten Mehrwert für unsere Kunden schaffen konnten.""",
    "Kundenfeedback": """{quote}\n\nDas Feedback zeigt uns, worauf wir weiter bauen und was wir noch besser machen können.""",
}

SAMPLE_ITEMS = [
    {
        "name": "Anna K.",
        "company": "Müller & Partner",
        "role": "Marketing-Leiterin",
        "category": "B2B",
        "status": "approved",
        "rating": "5",
        "source": "Google",
        "quote": "Der Ablauf war unkompliziert, schnell und sehr professionell. Wir konnten unsere Kampagne ohne Reibung starten und direkt Ergebnisse sehen.",
    },
    {
        "name": "Thomas R.",
        "company": "Nordwerk GmbH",
        "role": "Geschäftsführer",
        "category": "Software",
        "status": "pending",
        "rating": "4",
        "source": "Survey",
        "quote": "Das Produkt ist intuitiv und das Team war bei Fragen immer schnell erreichbar. Wir würden es wieder nutzen.",
    },
    {
        "name": "Sofia L.",
        "company": "Blue Harbor",
        "role": "Projektmanagerin",
        "category": "Support",
        "status": "approved",
        "rating": "5",
        "source": "LinkedIn",
        "quote": "Der Support war freundlich, kompetent und extrem lösungsorientiert. Das hat unser Projekt deutlich vorangebracht.",
    },
]


def normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_filename(value: str) -> str:
    value = re.sub(r"[^\w.-]+", "_", value.strip(), flags=re.UNICODE).strip("_.")
    return value or "testimonials"


class TestimonialStudio(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Testimonial Studio")
        self.geometry("1180x800")
        self.minsize(980, 650)
        self.configure(bg=BG)
        self.items: list[dict[str, str]] = []
        self.selected_index: int | None = None
        self.filter_var = tk.StringVar(value="all")
        self._configure_style()
        self._build_ui()
        self.load_examples()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=CARD, foreground=INK, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=BG, foreground=INK, font=("Segoe UI", 22, "bold"))
        style.configure("Subheader.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=CARD, foreground=INK, font=("Segoe UI", 12, "bold"))
        style.configure("TEntry", padding=8, fieldbackground="#ffffff")
        style.configure("TCombobox", padding=7)
        style.configure("TButton", padding=(11, 8), font=("Segoe UI", 9))
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", padding=(13, 9), font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#4053cf")], foreground=[("active", "#ffffff")])
        style.configure("Treeview", rowheight=32, background="#ffffff", fieldbackground="#ffffff", font=("Segoe UI", 9), borderwidth=0)
        style.configure("Treeview.Heading", background="#f0f3f9", foreground=INK, font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#e8ecff")], foreground=[("selected", INK)])

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(24, 20, 24, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Testimonial Studio", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Vertrauliche Kundenstimmen sammeln, aufbereiten und exportieren.", style="Subheader.TLabel").pack(anchor="w", pady=(3, 0))

        toolbar = ttk.Frame(self, padding=(24, 2, 24, 12))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="＋ Neuer Eintrag", style="Accent.TButton", command=self.clear_form).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="CSV / Excel importieren", command=self.import_file).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt öffnen", command=self.open_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt speichern", command=self.save_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Exportieren", command=self.export_menu).pack(side="left", padx=4)
        self.count_label = ttk.Label(toolbar, text="0 Einträge", style="Subheader.TLabel")
        self.count_label.pack(side="right", padx=4)

        body = ttk.Frame(self, padding=(24, 0, 24, 14))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=4, uniform="columns")
        body.columnconfigure(1, weight=6, uniform="columns")
        body.rowconfigure(0, weight=1)

        editor = ttk.Frame(body, style="Card.TFrame", padding=18)
        editor.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        listing = ttk.Frame(body, style="Card.TFrame", padding=18)
        listing.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ttk.Label(editor, text="Testimonial erfassen", style="Section.TLabel").pack(anchor="w", pady=(0, 14))

        fields = ttk.Frame(editor, style="Card.TFrame")
        fields.pack(fill="x")
        row1 = ttk.Frame(fields)
        row1.pack(fill="x", pady=(0, 10))
        ttk.Label(row1, text="Name").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.name_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.name_var).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(row1, text="Unternehmen").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.company_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.company_var).pack(side="left", fill="x", expand=True)

        row2 = ttk.Frame(fields)
        row2.pack(fill="x", pady=(0, 10))
        ttk.Label(row2, text="Rolle").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.role_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.role_var).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(row2, text="Kategorie").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.category_var = tk.StringVar(value="Allgemein")
        ttk.Entry(row2, textvariable=self.category_var).pack(side="left", fill="x", expand=True)

        row3 = ttk.Frame(fields)
        row3.pack(fill="x", pady=(0, 10))
        ttk.Label(row3, text="Status").pack(side="left", pady=(0, 4), padx=(0, 12))
        self.status_var = tk.StringVar(value="approved")
        ttk.Combobox(row3, textvariable=self.status_var, values=[STATUS_LABELS[k] for k in STATUS_OPTIONS], state="readonly", width=18).pack(side="left", padx=(0, 12))
        ttk.Label(row3, text="Bewertung").pack(side="left", pady=(0, 4), padx=(0, 12))
        self.rating_var = tk.StringVar(value="5")
        ttk.Combobox(row3, textvariable=self.rating_var, values=["5", "4", "3", "2", "1"], state="readonly", width=8).pack(side="left", padx=(0, 10))
        ttk.Label(row3, text="Quelle").pack(side="left", pady=(0, 4), padx=(0, 10))
        self.source_var = tk.StringVar(value="Google")
        ttk.Entry(row3, textvariable=self.source_var, width=18).pack(side="left")

        ttk.Label(editor, text="Zitat / Feedback").pack(anchor="w", pady=(14, 5))
        self.quote_text = tk.Text(editor, height=10, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, padx=10, pady=9, undo=True)
        self.quote_text.pack(fill="both", expand=True)

        template_header = ttk.Frame(editor, style="Card.TFrame")
        template_header.pack(fill="x", pady=(12, 6))
        ttk.Label(template_header, text="Vorlage für die Formulierung").pack(side="left")
        self.template_var = tk.StringVar(value="Kurz & stark")
        template_combo = ttk.Combobox(template_header, textvariable=self.template_var, values=list(TESTIMONIAL_TEMPLATES.keys()), state="readonly", width=26)
        template_combo.pack(side="right")

        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Eintrag speichern", style="Accent.TButton", command=self.save_entry).pack(side="left")
        ttk.Button(actions, text="Löschen", command=self.delete_entry).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Vorlage anwenden", command=self.apply_template).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Anfrage-Prompt kopieren", command=self.copy_request_prompt).pack(side="left", padx=(8, 0))

        ttk.Label(listing, text="Kundenstimmen", style="Section.TLabel").pack(anchor="w", pady=(0, 11))
        filter_row = ttk.Frame(listing)
        filter_row.pack(fill="x", pady=(0, 10))
        ttk.Label(filter_row, text="Filter").pack(side="left", padx=(0, 8))
        self.filter_combo = ttk.Combobox(filter_row, textvariable=self.filter_var, values=["all", "approved", "pending", "rejected"], state="readonly", width=16)
        self.filter_combo.pack(side="left", fill="x")
        self.filter_var.trace_add("write", lambda *_: self.refresh_list())

        self.tree = ttk.Treeview(listing, columns=("name", "status", "rating"), show="headings", selectmode="browse")
        self.tree.heading("name", text="NAME")
        self.tree.heading("status", text="STATUS")
        self.tree.heading("rating", text="BEWERTUNG")
        self.tree.column("name", width=220, minwidth=150)
        self.tree.column("status", width=120, minwidth=80)
        self.tree.column("rating", width=120, minwidth=80)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        ttk.Label(listing, text="Live-Vorschau", style="Section.TLabel").pack(anchor="w", pady=(14, 8))
        self.preview = tk.Text(listing, height=12, wrap="word", font=("Segoe UI", 9), relief="solid", bd=1, padx=10, pady=8, background="#fbfcff", foreground=INK)
        self.preview.pack(fill="both", expand=True)
        self.preview.configure(state="disabled")

        self.status_bar = tk.StringVar(value="Bereit. Die Daten bleiben lokal auf deinem Computer.")
        ttk.Label(self, textvariable=self.status_bar, anchor="w", padding=(24, 9), background="#eaf0f8", foreground=MUTED, font=("Segoe UI", 9)).pack(fill="x", side="bottom")

    def load_examples(self) -> None:
        self.items = [dict(item) for item in SAMPLE_ITEMS]
        self.refresh_list()
        self.refresh_preview()

    def clear_form(self) -> None:
        self.selected_index = None
        self.name_var.set("")
        self.company_var.set("")
        self.role_var.set("")
        self.category_var.set("Allgemein")
        self.status_var.set("approved")
        self.rating_var.set("5")
        self.source_var.set("Google")
        self.quote_text.delete("1.0", "end")
        self.name_var_entry_focus()

    def name_var_entry_focus(self) -> None:
        self.focus_set()

    def save_entry(self) -> None:
        record = {
            "name": self.name_var.get().strip(),
            "company": self.company_var.get().strip(),
            "role": self.role_var.get().strip(),
            "category": self.category_var.get().strip() or "Allgemein",
            "status": self.status_var.get().strip() or "approved",
            "rating": self.rating_var.get().strip() or "5",
            "source": self.source_var.get().strip() or "Google",
            "quote": self.quote_text.get("1.0", "end").strip(),
        }
        if not record["name"] or not record["quote"]:
            messagebox.showwarning("Unvollständig", "Bitte Name und Zitat ausfüllen.", parent=self)
            return
        if record["status"] not in STATUS_OPTIONS:
            record["status"] = "pending"
        if record["status"] == "approved":
            label = STATUS_LABELS["approved"]
        elif record["status"] == "pending":
            label = STATUS_LABELS["pending"]
        else:
            label = STATUS_LABELS["rejected"]
        record["status_label"] = label

        if self.selected_index is not None and 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index] = record
        else:
            self.items.append(record)
            self.selected_index = len(self.items) - 1
        self.refresh_list()
        self.refresh_preview()
        self.status_bar.set("Eintrag gespeichert.")

    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        try:
            index = int(selected[0])
            record = self.items[index]
        except (ValueError, IndexError):
            return
        self.selected_index = index
        self.name_var.set(record.get("name", ""))
        self.company_var.set(record.get("company", ""))
        self.role_var.set(record.get("role", ""))
        self.category_var.set(record.get("category", "Allgemein"))
        self.status_var.set(record.get("status", "approved"))
        self.rating_var.set(record.get("rating", "5"))
        self.source_var.set(record.get("source", "Google"))
        self.quote_text.delete("1.0", "end")
        self.quote_text.insert("1.0", record.get("quote", ""))

    def delete_entry(self) -> None:
        if self.selected_index is None or not 0 <= self.selected_index < len(self.items):
            messagebox.showinfo("Eintrag auswählen", "Bitte zuerst einen Eintrag aus der Liste wählen.", parent=self)
            return
        if messagebox.askyesno("Eintrag löschen", "Diesen Kundenstimmen-Eintrag wirklich löschen?", parent=self):
            del self.items[self.selected_index]
            self.selected_index = None
            self.clear_form()
            self.refresh_list()
            self.refresh_preview()
            self.status_bar.set("Eintrag gelöscht.")

    def apply_template(self) -> None:
        quote = self.quote_text.get("1.0", "end").strip()
        if not quote:
            messagebox.showinfo("Zitat fehlt", "Bitte zuerst den Kundeninput oder den groben Text in das Zitatfeld schreiben.", parent=self)
            return
        template = TESTIMONIAL_TEMPLATES.get(self.template_var.get(), "{quote}")
        polished = template.format(quote=quote)
        self.quote_text.delete("1.0", "end")
        self.quote_text.insert("1.0", polished)
        self.status_bar.set("Vorlage angewendet. Bitte Text noch stichprobenartig prüfen.")

    def copy_request_prompt(self) -> None:
        name = self.name_var.get().strip() or "[Kundenname]"
        company = self.company_var.get().strip() or "[Unternehmen]"
        status = self.status_var.get() or "approved"
        rating = self.rating_var.get() or "5"
        quote = self.quote_text.get("1.0", "end").strip() or "[Hier ein kurzer Überblick zum Ergebnis, Wert und Ablauf eintragen]"
        prompt = (
            "Du bist ein professioneller Kundenservice-Verantwortlicher. Bitte formuliere eine kurze, echte und glaubwürdige "
            "Kundenstimme auf Deutsch. Verwende keine erfundenen Zahlen oder Behauptungen. Wenn Details fehlen, markiere sie als [BITTE ERGÄNZEN]. "
            "Halte den Ton ehrlich, konkret und positiv.\n\n"
            f"Name: {name}\n"
            f"Unternehmen: {company}\n"
            f"Status: {STATUS_LABELS.get(status, 'Freigegeben')}\n"
            f"Bewertung: {rating}/5\n"
            f"Vorhandene Notizen: {quote}\n\n"
            "Gib nur den fertigen Testimonial-Text im Stil einer Kundenbewertung zurück."
        )
        self.clipboard_clear()
        self.clipboard_append(prompt)
        self.status_bar.set("Prompt für die Kundenfeedback-Anfrage wurde kopiert.")
        messagebox.showinfo("Prompt kopiert", "Der Anfrage-Prompt wurde in die Zwischenablage kopiert.", parent=self)

    def refresh_list(self) -> None:
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())
        status_filter = self.filter_var.get()
        for index, item in enumerate(self.items):
            status_value = item.get("status", "approved")
            if status_filter != "all" and status_value != status_filter:
                continue
            label = STATUS_LABELS.get(status_value, "Freigegeben")
            self.tree.insert("", "end", iid=str(index), values=(item.get("name", "Unbekannt"), label, RATING_LABELS.get(item.get("rating", "5"), "★★★★★")))
        self.count_label.configure(text=f"{len(self.items)} Einträge")

    def refresh_preview(self) -> None:
        if not hasattr(self, "preview"):
            return
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        if not self.items:
            self.preview.insert("1.0", "Noch keine Kundenstimmen vorhanden.")
            self.preview.configure(state="disabled")
            return
        lines = []
        grouped = defaultdict(list)
        for item in self.items:
            grouped[item.get("category", "Allgemein")].append(item)
        for category, entries in grouped.items():
            lines.append(f"{category}")
            lines.append("-" * len(category))
            for entry in entries:
                rating = RATING_LABELS.get(entry.get("rating", "5"), "★★★★★")
                status = STATUS_LABELS.get(entry.get("status", "approved"), "Freigegeben")
                lines.append(f"{entry.get('name', 'Unbekannt')} — {rating} — {status}")
                lines.append(f"{entry.get('company', '')} | {entry.get('role', '')} | {entry.get('source', '')}")
                lines.append(entry.get("quote", ""))
                lines.append("")
        self.preview.insert("1.0", "\n".join(lines))
        self.preview.configure(state="disabled")

    def import_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Testimonial-Datei importieren",
            filetypes=[("CSV oder Excel", "*.csv *.xlsx *.xlsm"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xlsm"), ("Alle Dateien", "*.*")],
            parent=self,
        )
        if not path:
            return
        try:
            imported = self._read_file(Path(path))
            if not imported:
                raise ValueError("Keine gültigen Einträge gefunden. Erwartet werden Spalten wie Name, Unternehmen, Quote, Rating, Status, Kategorie, Quelle.")
        except ImportError as exc:
            messagebox.showerror("Excel-Unterstützung fehlt", f"{exc}\n\nInstalliere sie mit: py -m pip install -r requirements-testimonials.txt", parent=self)
            return
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror("Import fehlgeschlagen", str(exc), parent=self)
            return
        self.items.extend(imported)
        self.refresh_list()
        self.refresh_preview()
        self.status_bar.set(f"{len(imported)} Einträge importiert aus {Path(path).name}.")

    @staticmethod
    def _read_file(path: Path) -> list[dict[str, str]]:
        if path.suffix.casefold() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                sample = fh.read(4096)
                fh.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
                except csv.Error:
                    dialect = csv.excel
                    try:
                        dialect.delimiter = ";" if sample.count(";") > sample.count(",") else ","
                    except Exception:
                        dialect.delimiter = ";"
                reader = csv.DictReader(fh, dialect=dialect)
                return TestimonialStudio._normalize_rows(list(reader))
        if path.suffix.casefold() in {".xlsx", ".xlsm"}:
            try:
                from openpyxl import load_workbook
            except ImportError as exc:
                raise ImportError("Für Excel-Dateien wird das Paket openpyxl benötigt.") from exc
            workbook = load_workbook(path, read_only=True, data_only=True)
            try:
                sheet = workbook.active
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    return []
                headers = [normalize(h) for h in rows[0]]
                data_rows = [dict(zip(headers, row)) for row in rows[1:]]
                return TestimonialStudio._normalize_rows(data_rows)
            finally:
                workbook.close()
        raise ValueError("Bitte eine CSV-, XLSX- oder XLSM-Datei auswählen.")

    @staticmethod
    def _normalize_rows(rows: list[dict]) -> list[dict[str, str]]:
        result = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            mapping = {normalize(k).casefold(): v for k, v in row.items() if k is not None}
            name = normalize(next((mapping.get(key) for key in ("name", "kunde", "customer", "person", "client") if mapping.get(key) is not None), ""))
            company = normalize(next((mapping.get(key) for key in ("company", "unternehmen", "firma", "business") if mapping.get(key) is not None), ""))
            role = normalize(next((mapping.get(key) for key in ("role", "rolle", "position", "funktion") if mapping.get(key) is not None), ""))
            category = normalize(next((mapping.get(key) for key in ("category", "kategorie", "bereich", "segment") if mapping.get(key) is not None), "Allgemein")) or "Allgemein"
            status = normalize(next((mapping.get(key) for key in ("status", "statuswert", "freigabe") if mapping.get(key) is not None), "approved")).casefold()
            if status not in STATUS_OPTIONS:
                status = "approved" if status not in {"rejected", "pending"} else status
            rating = normalize(next((mapping.get(key) for key in ("rating", "bewertung", "stars", "score") if mapping.get(key) is not None), "5"))
            if rating not in {"1", "2", "3", "4", "5"}:
                rating = "5"
            source = normalize(next((mapping.get(key) for key in ("source", "quelle", "channel", "medium") if mapping.get(key) is not None), "Google")) or "Google"
            quote = normalize(next((mapping.get(key) for key in ("quote", "zitat", "feedback", "text", "testimonial", "review") if mapping.get(key) is not None), ""))
            if not name or not quote:
                continue
            result.append({
                "name": name,
                "company": company,
                "role": role,
                "category": category,
                "status": status,
                "rating": rating,
                "source": source,
                "quote": quote,
            })
        return result

    def save_project(self) -> None:
        path = filedialog.asksaveasfilename(title="Projekt speichern", defaultextension=".json", initialfile="testimonial_projekt.json", filetypes=[("Projekt (JSON)", "*.json")], parent=self)
        if not path:
            return
        try:
            Path(path).write_text(json.dumps({"format": "testimonial-studio", "version": 1, "items": self.items}, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status_bar.set(f"Projekt gespeichert: {Path(path).name}")
        except OSError as exc:
            messagebox.showerror("Speichern fehlgeschlagen", str(exc), parent=self)

    def open_project(self) -> None:
        path = filedialog.askopenfilename(title="Projekt öffnen", filetypes=[("Projekt (JSON)", "*.json")], parent=self)
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            records = data.get("items", data) if isinstance(data, dict) else data
            if not isinstance(records, list):
                raise ValueError("Die Datei enthält keine gültige Liste mit Kundenstimmen.")
            if not records:
                self.items = []
            else:
                self.items = self._normalize_rows(records)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("Projekt konnte nicht geöffnet werden", str(exc), parent=self)
            return
        self.selected_index = None
        self.clear_form()
        self.refresh_list()
        self.refresh_preview()
        self.status_bar.set(f"Projekt geladen: {Path(path).name}")

    def export_menu(self) -> None:
        if not self.items:
            messagebox.showinfo("Keine Einträge", "Es gibt noch keine Kundenstimmen zum Exportieren.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            title="Exportieren",
            defaultextension=".html",
            initialfile=f"{safe_filename('testimonials')}.html",
            filetypes=[("HTML", "*.html"), ("Markdown", "*.md"), ("CSV", "*.csv"), ("JSON", "*.json")], parent=self,
        )
        if not path:
            return
        destination = Path(path)
        suffix = destination.suffix.casefold()
        try:
            if suffix in {".html", ".htm"}:
                content = self._as_html()
            elif suffix == ".md":
                content = self._as_markdown()
            elif suffix == ".csv":
                with destination.open("w", encoding="utf-8-sig", newline="") as fh:
                    writer = csv.DictWriter(fh, fieldnames=["name", "company", "role", "category", "status", "rating", "source", "quote"], delimiter=";")
                    writer.writeheader()
                    writer.writerows(self.items)
                content = None
            elif suffix == ".json":
                content = json.dumps({"format": "testimonial-studio", "version": 1, "items": self.items}, ensure_ascii=False, indent=2)
            else:
                raise ValueError("Bitte HTML, Markdown, CSV oder JSON auswählen.")
            if content is not None:
                destination.write_text(content, encoding="utf-8")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export fehlgeschlagen", str(exc), parent=self)
            return
        self.status_bar.set(f"Export abgeschlossen: {destination.name}")
        messagebox.showinfo("Erfolgreich", f"Die Kundenstimmen wurden exportiert:\n{destination}", parent=self)

    def _as_markdown(self) -> str:
        lines = ["# Kundenstimmen", ""]
        for category, entries in self._grouped(self.items).items():
            lines.extend((f"## {category}", ""))
            for entry in entries:
                lines.extend((f"### {entry['name']} — {RATING_LABELS.get(entry.get('rating', '5'), '★★★★★')}", ""))
                if entry.get("company"):
                    lines.append(f"{entry['company']} | {entry.get('role', '')}")
                lines.append(entry["quote"])
                lines.append("")
        return "\n".join(lines)

    def _as_html(self) -> str:
        sections = []
        for category, entries in self._grouped(self.items).items():
            cards = []
            for entry in entries:
                cards.append(
                    """
                    <article class="testimonial-card">
                        <div class="rating">{rating}</div>
                        <blockquote>{quote}</blockquote>
                        <div class="meta">{name} · {company} · {role}</div>
                        <div class="source">{source} · {status}</div>
                    </article>
                    """.format(
                        rating=RATING_LABELS.get(entry.get("rating", "5"), "★★★★★"),
                        quote=entry["quote"],
                        name=entry.get("name", "Unbekannt"),
                        company=entry.get("company", ""),
                        role=entry.get("role", ""),
                        source=entry.get("source", "Google"),
                        status=STATUS_LABELS.get(entry.get("status", "approved"), "Freigegeben"),
                    )
                )
            sections.append(f"<section><h2>{category}</h2>{''.join(cards)}</section>")
        return """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>Kundenstimmen</title>
<style>
body{margin:0;padding:48px 20px;background:#f5f7fb;font-family:Segoe UI,Arial,sans-serif;color:#172033}
main{max-width:980px;margin:auto;background:white;padding:36px;border-radius:18px;box-shadow:0 14px 40px rgba(23,32,51,0.09)}
section{margin-top:20px}
h1{margin:0 0 18px;font-size:2.2rem}h2{font-size:1.3rem;color:#5267e8;margin:28px 0 12px}
.testimonial-card{padding:18px 20px;border:1px solid #e4e9f2;border-radius:12px;margin:10px 0;background:#fff}
.rating{font-size:1.1rem;color:#d4a933;letter-spacing:4px;margin-bottom:10px}
blockquote{margin:0 0 12px;font-size:1.05rem;line-height:1.6;color:#24314d}
.meta,.source{font-size:0.9rem;color:#68748a}
</style></head><body><main><h1>Kundenstimmen</h1>""" + "\n".join(sections) + "</main></body></html>"

    @staticmethod
    def _grouped(items: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for item in items:
            groups[item.get("category", "Allgemein")].append(item)
        return groups


if __name__ == "__main__":
    TestimonialStudio().mainloop()
