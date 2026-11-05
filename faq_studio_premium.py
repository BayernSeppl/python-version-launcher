"""FAQ Studio Premium — a local-first FAQ authoring and publishing tool."""

from __future__ import annotations

import csv
import html
import json
import re
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk

BG = "#f4f7fb"
CARD = "#ffffff"
INK = "#172033"
MUTED = "#68748a"
ACCENT = "#5267e8"

TEMPLATES = {
    "Freundlich & klar": "Gerne! {answer}\n\nWenn du noch Fragen hast, hilft dir unser Team gerne weiter.",
    "Kurz & direkt": "{answer}",
    "Schritt für Schritt": "So geht’s:\n1. {answer}\n2. Folge den Anweisungen auf dem Bildschirm.\n3. Bei Fragen kontaktiere bitte unseren Support.",
    "Support-Antwort": "Danke für deine Frage. {answer}\n\nFalls das Problem weiterhin besteht, wende dich bitte mit einer kurzen Beschreibung an unseren Support.",
    "Kauf & Versand": "{answer}\n\nDie aktuell gültigen Details und Bedingungen findest du im Bestellprozess.",
    "Eigene Vorlage": "{answer}",
}
SAMPLES = [
    {"category": "Bestellung", "question": "Wie kann ich eine Bestellung aufgeben?", "answer": "Wähle die gewünschten Produkte aus und schließe die Bestellung sicher über unseren Checkout ab."},
    {"category": "Versand", "question": "Wie lange dauert der Versand?", "answer": "Die voraussichtliche Lieferzeit wird dir vor dem Abschluss der Bestellung angezeigt."},
    {"category": "Support", "question": "Wie erreiche ich den Kundenservice?", "answer": "Schreibe unserem Support über das Kontaktformular. Bitte gib deine Bestellnummer an, damit wir dir schneller helfen können."},
]
DEFAULT_SETTINGS = {"title": "Häufig gestellte Fragen", "brand": "", "intro": "Hier findest du schnelle Antworten auf die häufigsten Fragen.", "contact_url": "", "accent": ACCENT}


def text(value: object) -> str:
    return "" if value is None else str(value).strip()


def normalized_header(value: object) -> str:
    result = text(value).casefold()
    return result.translate(str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss"}))


def safe_name(value: str) -> str:
    return re.sub(r"[^\w.-]+", "_", value, flags=re.UNICODE).strip("_.") or "faq"


class FAQStudioPremium(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("FAQ Studio Premium")
        self.geometry("1260x850")
        self.minsize(1000, 680)
        self.configure(bg=BG)
        self.items: list[dict[str, str]] = []
        self.settings = dict(DEFAULT_SETTINGS)
        self.selected_index: int | None = None
        self._style()
        self._build()
        self.items = [dict(item) for item in SAMPLES]
        self.refresh()

    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=CARD, foreground=INK, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=BG, foreground=INK, font=("Segoe UI", 23, "bold"))
        style.configure("Subheader.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=CARD, foreground=INK, font=("Segoe UI", 12, "bold"))
        style.configure("TEntry", padding=8, fieldbackground="#ffffff")
        style.configure("TCombobox", padding=7)
        style.configure("TButton", padding=(10, 8), font=("Segoe UI", 9))
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", padding=(13, 9), font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#4053cf")], foreground=[("active", "#ffffff")])
        style.configure("Treeview", rowheight=32, background="#ffffff", fieldbackground="#ffffff", font=("Segoe UI", 9), borderwidth=0)
        style.configure("Treeview.Heading", background="#f0f3f9", foreground=INK, font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#e8ecff")], foreground=[("selected", INK)])

    def _build(self) -> None:
        header = ttk.Frame(self, padding=(24, 19, 24, 10))
        header.pack(fill="x")
        ttk.Label(header, text="FAQ Studio Premium", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Eine professionelle FAQ erstellen, gestalten und direkt als Website veröffentlichen.", style="Subheader.TLabel").pack(anchor="w", pady=(3, 0))

        toolbar = ttk.Frame(self, padding=(24, 3, 24, 12))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="＋ Neue Frage", style="Accent.TButton", command=self.clear_form).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="CSV / Excel importieren", command=self.import_file).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt öffnen", command=self.open_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt speichern", command=self.save_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Website exportieren", command=lambda: self.export("html")).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Weitere Exporte…", command=self.export_other).pack(side="left", padx=4)
        self.count_label = ttk.Label(toolbar, text="0 Fragen", style="Subheader.TLabel")
        self.count_label.pack(side="right")

        body = ttk.Frame(self, padding=(24, 0, 24, 13))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=5, uniform="panels")
        body.columnconfigure(1, weight=6, uniform="panels")
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Card.TFrame", padding=17)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        right = ttk.Frame(body, style="Card.TFrame", padding=17)
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))

        ttk.Label(left, text="Deine FAQ-Seite", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self.title_var = tk.StringVar(value=DEFAULT_SETTINGS["title"])
        self.brand_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.intro_var = tk.StringVar(value=DEFAULT_SETTINGS["intro"])
        self.accent_var = tk.StringVar(value=ACCENT)
        self._field(left, "Seitentitel", self.title_var)
        self._field(left, "Unternehmen / Marke (optional)", self.brand_var)
        self._field(left, "Einleitung", self.intro_var)
        self._field(left, "Kontakt-Link (optional, z. B. https://…)", self.contact_var)
        color_row = ttk.Frame(left, style="Card.TFrame")
        color_row.pack(fill="x", pady=(0, 12))
        ttk.Label(color_row, text="Akzentfarbe").pack(side="left")
        ttk.Entry(color_row, textvariable=self.accent_var, width=12).pack(side="right", padx=(8, 6))
        ttk.Button(color_row, text="Farbe wählen", command=self.choose_color).pack(side="right")

        ttk.Separator(left).pack(fill="x", pady=(2, 12))
        ttk.Label(left, text="FAQ-Eintrag", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(left, text="Kategorie").pack(anchor="w", pady=(0, 4))
        self.category_var = tk.StringVar(value="Allgemein")
        ttk.Entry(left, textvariable=self.category_var).pack(fill="x", pady=(0, 9))
        ttk.Label(left, text="Frage").pack(anchor="w", pady=(0, 4))
        self.question_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.question_var).pack(fill="x", pady=(0, 9))
        ttk.Label(left, text="Antwort").pack(anchor="w", pady=(0, 4))
        self.answer_text = tk.Text(left, height=8, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, padx=9, pady=8, undo=True, background="#ffffff", foreground=INK, insertbackground=INK)
        self.answer_text.pack(fill="both", expand=True, pady=(0, 8))

        template_row = ttk.Frame(left, style="Card.TFrame")
        template_row.pack(fill="x", pady=(0, 8))
        self.template_var = tk.StringVar(value="Freundlich & klar")
        ttk.Combobox(template_row, textvariable=self.template_var, values=list(TEMPLATES), state="readonly", width=22).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(template_row, text="Vorlage anwenden", command=self.apply_template).pack(side="left")
        tools_row = ttk.Frame(left, style="Card.TFrame")
        tools_row.pack(fill="x", pady=(0, 10))
        ttk.Button(tools_row, text="KI-Prompt kopieren", command=self.copy_prompt).pack(side="left")
        ttk.Label(tools_row, text="Kein KI-Konto/API nötig", style="Muted.TLabel").pack(side="left", padx=8)
        action_row = ttk.Frame(left, style="Card.TFrame")
        action_row.pack(fill="x")
        ttk.Button(action_row, text="Eintrag speichern", style="Accent.TButton", command=self.save_entry).pack(side="left")
        ttk.Button(action_row, text="Löschen", command=self.delete_entry).pack(side="left", padx=(7, 0))

        ttk.Label(right, text="Fragen verwalten", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        search_row = ttk.Frame(right, style="Card.TFrame")
        search_row.pack(fill="x", pady=(0, 9))
        ttk.Label(search_row, text="Suche").pack(side="left", padx=(0, 7))
        self.search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        self.category_filter = tk.StringVar(value="Alle Kategorien")
        self.category_combo = ttk.Combobox(search_row, textvariable=self.category_filter, state="readonly", width=19)
        self.category_combo.pack(side="left", padx=(8, 0))
        self.category_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_list())

        self.tree = ttk.Treeview(right, columns=("category", "question"), show="headings", selectmode="browse")
        self.tree.heading("category", text="KATEGORIE")
        self.tree.heading("question", text="FRAGE")
        self.tree.column("category", width=125, minwidth=90, stretch=False)
        self.tree.column("question", width=350, minwidth=150, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        preview_header = ttk.Frame(right, style="Card.TFrame")
        preview_header.pack(fill="x", pady=(14, 6))
        ttk.Label(preview_header, text="Live-Vorschau", style="Section.TLabel").pack(side="left")
        ttk.Label(preview_header, text="Vorschau der veröffentlichten FAQ", style="Muted.TLabel").pack(side="right")
        self.preview = tk.Text(right, height=8, wrap="word", font=("Segoe UI", 9), relief="solid", bd=1, padx=9, pady=8, background="#fbfcff", foreground=INK)
        self.preview.pack(fill="both", expand=True)
        self.preview.configure(state="disabled")
        self.status = tk.StringVar(value="Bereit. Inhalte werden lokal auf deinem Computer bearbeitet.")
        ttk.Label(self, textvariable=self.status, anchor="w", padding=(24, 9), background="#eaf0f8", foreground=MUTED, font=("Segoe UI", 9)).pack(fill="x", side="bottom")

    @staticmethod
    def _field(parent, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label).pack(anchor="w", pady=(0, 4))
        ttk.Entry(parent, textvariable=variable).pack(fill="x", pady=(0, 9))

    def choose_color(self) -> None:
        chosen = colorchooser.askcolor(color=self.accent_var.get(), title="Akzentfarbe wählen", parent=self)[1]
        if chosen:
            self.accent_var.set(chosen)

    def _settings_from_form(self) -> dict[str, str]:
        accent = self.accent_var.get().strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            raise ValueError("Die Akzentfarbe muss ein gültiger Hex-Farbwert sein, z. B. #5267e8.")
        contact = self.contact_var.get().strip()
        if contact and not re.match(r"^https?://", contact, flags=re.IGNORECASE):
            raise ValueError("Der Kontakt-Link muss mit http:// oder https:// beginnen.")
        return {
            "title": self.title_var.get().strip() or "Häufig gestellte Fragen",
            "brand": self.brand_var.get().strip(),
            "intro": self.intro_var.get().strip(),
            "contact_url": contact,
            "accent": accent,
        }

    def _apply_settings(self, settings: dict) -> None:
        self.settings = {**DEFAULT_SETTINGS, **{k: text(v) for k, v in settings.items() if k in DEFAULT_SETTINGS}}
        self.title_var.set(self.settings["title"])
        self.brand_var.set(self.settings["brand"])
        self.intro_var.set(self.settings["intro"])
        self.contact_var.set(self.settings["contact_url"])
        self.accent_var.set(self.settings["accent"])

    def clear_form(self) -> None:
        self.selected_index = None
        if hasattr(self, "tree"):
            self.tree.selection_remove(self.tree.selection())
        self.category_var.set("Allgemein")
        self.question_var.set("")
        self.answer_text.delete("1.0", "end")

    def save_entry(self) -> None:
        category = self.category_var.get().strip() or "Allgemein"
        question = self.question_var.get().strip()
        answer = self.answer_text.get("1.0", "end").strip()
        if not question or not answer:
            messagebox.showwarning("Noch nicht vollständig", "Bitte fülle Frage und Antwort aus.", parent=self)
            return
        normalized = question.casefold().strip().rstrip("?!.")
        duplicate = next((i for i, item in enumerate(self.items) if i != self.selected_index and item["question"].casefold().strip().rstrip("?!.") == normalized), None)
        if duplicate is not None and not messagebox.askyesno("Ähnliche Frage gefunden", "Eine Frage mit sehr ähnlichem Wortlaut existiert bereits. Trotzdem speichern?", parent=self):
            return
        record = {"category": category, "question": question, "answer": answer}
        if self.selected_index is not None and 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index] = record
        else:
            self.items.append(record)
            self.selected_index = len(self.items) - 1
        self.refresh()
        self.status.set("FAQ-Eintrag gespeichert.")

    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        try:
            index = int(selected[0])
            item = self.items[index]
        except (ValueError, IndexError):
            return
        self.selected_index = index
        self.category_var.set(item["category"])
        self.question_var.set(item["question"])
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", item["answer"])

    def delete_entry(self) -> None:
        if self.selected_index is None or not 0 <= self.selected_index < len(self.items):
            messagebox.showinfo("Eintrag auswählen", "Wähle zuerst einen Eintrag in der Liste aus.", parent=self)
            return
        if messagebox.askyesno("Eintrag löschen", "Diesen FAQ-Eintrag wirklich löschen?", parent=self):
            del self.items[self.selected_index]
            self.clear_form()
            self.refresh()
            self.status.set("Eintrag gelöscht.")

    def apply_template(self) -> None:
        answer = self.answer_text.get("1.0", "end").strip()
        if not answer:
            messagebox.showinfo("Fakten ergänzen", "Trage zuerst deine Fakten oder Stichpunkte als Antwort ein.", parent=self)
            return
        formatted = TEMPLATES.get(self.template_var.get(), "{answer}").format(answer=answer)
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", formatted)
        self.status.set("Vorlage angewendet — bitte Fakten vor Veröffentlichung prüfen.")

    def copy_prompt(self) -> None:
        question = self.question_var.get().strip()
        if not question:
            messagebox.showinfo("Frage fehlt", "Bitte zuerst eine FAQ-Frage eingeben.", parent=self)
            return
        prompt = (
            "Schreibe eine präzise, freundliche und hilfreiche FAQ-Antwort auf Deutsch. Verwende ausschließlich die angegebenen Fakten; "
            "erfinde keine Preise, Fristen, Garantien oder rechtlichen Aussagen. Fehlende Angaben als [BITTE ERGÄNZEN] markieren. "
            "Nutze kurze Absätze und klare Sprache. Gib nur den Antworttext zurück.\n\n"
            f"Kategorie: {self.category_var.get().strip() or 'Allgemein'}\nFrage: {question}\n"
            f"Bekannte Fakten / Entwurf: {self.answer_text.get('1.0', 'end').strip() or '[Fakten hier einfügen]'}"
        )
        self.clipboard_clear()
        self.clipboard_append(prompt)
        self.status.set("KI-Prompt kopiert. In deinem KI-Dienst einfügen und die Antwort prüfen.")
        messagebox.showinfo("Prompt kopiert", "Der Prompt wurde kopiert. Er wird nicht automatisch an einen KI-Dienst gesendet.", parent=self)

    def refresh(self) -> None:
        self.refresh_list()
        self.refresh_preview()

    def refresh_list(self) -> None:
        if not hasattr(self, "tree"):
            return
        cats = sorted({item["category"] for item in self.items}, key=str.casefold)
        options = ["Alle Kategorien", *cats]
        self.category_combo.configure(values=options)
        if self.category_filter.get() not in options:
            self.category_filter.set("Alle Kategorien")
        query = self.search_var.get().strip().casefold()
        category = self.category_filter.get()
        self.tree.delete(*self.tree.get_children())
        for index, item in enumerate(self.items):
            if category != "Alle Kategorien" and item["category"] != category:
                continue
            if query and query not in " ".join(item.values()).casefold():
                continue
            self.tree.insert("", "end", iid=str(index), values=(item["category"], item["question"]))
        self.count_label.configure(text=f"{len(self.items)} Fragen · {len(cats)} Kategorien")

    def refresh_preview(self) -> None:
        if not hasattr(self, "preview"):
            return
        settings = {**DEFAULT_SETTINGS, "title": self.title_var.get().strip() or DEFAULT_SETTINGS["title"], "brand": self.brand_var.get().strip(), "intro": self.intro_var.get().strip()}
        lines = [settings["brand"] or "FAQ-VORSCHAU", settings["title"], settings["intro"], ""]
        for category, entries in self._grouped(self.items).items():
            lines.extend((category, ""))
            for item in entries:
                lines.extend((f"▸ {item['question']}", item["answer"], ""))
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", "\n".join(lines) if self.items else "Noch keine FAQ-Einträge vorhanden.")
        self.preview.configure(state="disabled")

    @staticmethod
    def _grouped(items: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        result: dict[str, list[dict[str, str]]] = defaultdict(list)
        for item in items:
            result[item["category"]].append(item)
        return result

    def import_file(self) -> None:
        filename = filedialog.askopenfilename(title="FAQ-Datei importieren", filetypes=[("CSV oder Excel", "*.csv *.xlsx *.xlsm"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xlsm"), ("Alle Dateien", "*.*")], parent=self)
        if not filename:
            return
        try:
            imported = self._read_import(Path(filename))
            if not imported:
                raise ValueError("Keine gültigen Zeilen gefunden. Benötigt werden Spalten für Frage und Antwort.")
        except ImportError as exc:
            messagebox.showerror("Excel-Unterstützung fehlt", f"{exc}\n\nInstalliere sie mit: python -m pip install -r requirements-faq.txt", parent=self)
            return
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror("Import fehlgeschlagen", str(exc), parent=self)
            return
        self.items.extend(imported)
        self.refresh()
        self.status.set(f"{len(imported)} Einträge aus {Path(filename).name} importiert.")

    @staticmethod
    def _read_import(path: Path) -> list[dict[str, str]]:
        if path.suffix.casefold() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                sample = file.read(4096)
                file.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
                except csv.Error:
                    dialect = csv.excel
                    dialect.delimiter = ";" if sample.count(";") > sample.count(",") else ","
                return FAQStudioPremium._normalize_rows(list(csv.DictReader(file, dialect=dialect)))
        if path.suffix.casefold() in {".xlsx", ".xlsm"}:
            try:
                from openpyxl import load_workbook
            except ImportError as exc:
                raise ImportError("Für Excel-Dateien wird openpyxl benötigt.") from exc
            workbook = load_workbook(path, read_only=True, data_only=True)
            try:
                values = workbook.active.iter_rows(values_only=True)
                headers = next(values, None)
                if not headers:
                    return []
                rows = [dict(zip([text(value) for value in headers], row)) for row in values]
                return FAQStudioPremium._normalize_rows(rows)
            finally:
                workbook.close()
        raise ValueError("Bitte eine CSV-, XLSX- oder XLSM-Datei auswählen.")

    @staticmethod
    def _normalize_rows(rows: list[dict]) -> list[dict[str, str]]:
        output = []
        for row in rows:
            headers = {re.sub(r"[^a-z]", "", normalized_header(key)): value for key, value in row.items() if key is not None}
            question = next((text(headers.get(key)) for key in ("frage", "question", "q", "title") if text(headers.get(key))), "")
            answer = next((text(headers.get(key)) for key in ("antwort", "answer", "a", "response") if text(headers.get(key))), "")
            category = next((text(headers.get(key)) for key in ("kategorie", "category", "bereich", "topic") if text(headers.get(key))), "Allgemein")
            if question and answer:
                output.append({"category": category or "Allgemein", "question": question, "answer": answer})
        return output

    def save_project(self) -> None:
        try:
            settings = self._settings_from_form()
        except ValueError as exc:
            messagebox.showerror("Einstellungen prüfen", str(exc), parent=self)
            return
        filename = filedialog.asksaveasfilename(title="FAQ-Projekt speichern", defaultextension=".json", initialfile="mein_faq_projekt.json", filetypes=[("FAQ-Projekt (JSON)", "*.json")], parent=self)
        if not filename:
            return
        try:
            data = {"format": "faq-studio-premium", "version": 1, "settings": settings, "items": self.items}
            Path(filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Speichern fehlgeschlagen", str(exc), parent=self)
            return
        self.settings = settings
        self.status.set(f"Projekt gespeichert: {Path(filename).name}")

    def open_project(self) -> None:
        filename = filedialog.askopenfilename(title="FAQ-Projekt öffnen", filetypes=[("FAQ-Projekt (JSON)", "*.json")], parent=self)
        if not filename:
            return
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                records = data.get("items", [])
                settings = data.get("settings", {})
            else:
                records, settings = data, {}
            if not isinstance(records, list):
                raise ValueError("Die Datei enthält keine FAQ-Liste.")
            items = self._normalize_rows(records)
            if records and not items:
                raise ValueError("Keine gültigen Fragen und Antworten in der Projektdatei gefunden.")
            self._apply_settings(settings if isinstance(settings, dict) else {})
            self.items = items
            self.selected_index = None
            self.clear_form()
            self.refresh()
        except (OSError, json.JSONDecodeError, ValueError, AttributeError) as exc:
            messagebox.showerror("Projekt konnte nicht geöffnet werden", str(exc), parent=self)
            return
        self.status.set(f"Projekt geladen: {Path(filename).name}")

    def export_other(self) -> None:
        if not self.items:
            messagebox.showinfo("Keine Einträge", "Füge zuerst mindestens eine Frage und Antwort hinzu.", parent=self)
            return
        filename = filedialog.asksaveasfilename(title="FAQ exportieren", defaultextension=".md", initialfile=f"{safe_name(self.title_var.get())}.md", filetypes=[("Markdown", "*.md"), ("CSV", "*.csv"), ("JSON", "*.json")], parent=self)
        if filename:
            self._write_export(Path(filename))

    def export(self, kind: str) -> None:
        if not self.items:
            messagebox.showinfo("Keine Einträge", "Füge zuerst mindestens eine Frage und Antwort hinzu.", parent=self)
            return
        try:
            settings = self._settings_from_form()
        except ValueError as exc:
            messagebox.showerror("Einstellungen prüfen", str(exc), parent=self)
            return
        filename = filedialog.asksaveasfilename(title="FAQ-Webseite exportieren", defaultextension=".html", initialfile=f"{safe_name(settings['title'])}.html", filetypes=[("HTML-Webseite", "*.html")], parent=self)
        if not filename:
            return
        try:
            Path(filename).write_text(self._html(settings), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Export fehlgeschlagen", str(exc), parent=self)
            return
        self.settings = settings
        self.status.set(f"Responsive FAQ-Webseite exportiert: {Path(filename).name}")
        messagebox.showinfo("Export fertig", f"Deine Website-FAQ wurde erstellt:\n{filename}\n\nDie HTML-Datei kannst du direkt im Browser öffnen oder auf deiner Website veröffentlichen.", parent=self)

    def _write_export(self, path: Path) -> None:
        suffix = path.suffix.casefold()
        try:
            if suffix == ".md":
                path.write_text(self._markdown(), encoding="utf-8")
            elif suffix == ".json":
                path.write_text(json.dumps({"format": "faq-studio-premium", "version": 1, "settings": self._settings_from_form(), "items": self.items}, ensure_ascii=False, indent=2), encoding="utf-8")
            elif suffix == ".csv":
                with path.open("w", encoding="utf-8-sig", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["category", "question", "answer"], delimiter=";")
                    writer.writeheader()
                    writer.writerows(self.items)
            else:
                raise ValueError("Wähle eine Markdown-, CSV- oder JSON-Datei aus.")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export fehlgeschlagen", str(exc), parent=self)
            return
        self.status.set(f"Export erstellt: {path.name}")
        messagebox.showinfo("Export fertig", f"Datei gespeichert:\n{path}", parent=self)

    def _markdown(self) -> str:
        settings = self._settings_from_form()
        lines = [f"# {settings['title']}", ""]
        if settings["intro"]:
            lines.extend((settings["intro"], ""))
        for category, entries in self._grouped(self.items).items():
            lines.extend((f"## {category}", ""))
            for item in entries:
                lines.extend((f"### {item['question']}", "", item["answer"], ""))
        return "\n".join(lines)

    def _html(self, settings: dict[str, str]) -> str:
        sections = []
        schema_entries = []
        for category, entries in self._grouped(self.items).items():
            cards = []
            for item in entries:
                q = html.escape(item["question"])
                answer_html = html.escape(item["answer"]).replace("\n", "<br>")
                cards.append(f'<details class="faq-item"><summary>{q}</summary><div class="answer">{answer_html}</div></details>')
                schema_entries.append({"@type": "Question", "name": item["question"], "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}})
            sections.append(f'<section class="category"><h2>{html.escape(category)}</h2>{"".join(cards)}</section>')
        structured_data = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": schema_entries}, ensure_ascii=False).replace("<", "\\u003c")
        brand = html.escape(settings["brand"])
        title = html.escape(settings["title"])
        intro = html.escape(settings["intro"])
        contact = settings["contact_url"]
        contact_link = f'<a class="contact" href="{html.escape(contact, quote=True)}">Kontaktiere uns</a>' if contact else ""
        brand_markup = f'<p class="brand">{brand}</p>' if brand else ""
        return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(intro, quote=True)}"><title>{title}</title>
<script type="application/ld+json">{structured_data}</script>
<style>
:root{{--ink:#172033;--muted:#68748a;--line:#e4e9f2;--accent:{settings['accent']};--paper:#fff;--bg:#f4f7fb}}
*{{box-sizing:border-box}}body{{margin:0;padding:48px 20px;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:900px;margin:auto;padding:clamp(24px,5vw,58px);background:var(--paper);border-radius:22px;box-shadow:0 12px 45px #17203312}}
.brand{{margin:0 0 8px;color:var(--accent);font-weight:750;letter-spacing:.04em}}h1{{font-size:clamp(2rem,5vw,3rem);line-height:1.13;letter-spacing:-.03em;margin:0 0 12px}}.intro{{color:var(--muted);margin:0 0 26px}}
.search-wrap{{position:relative;margin:22px 0 26px}}.search{{width:100%;padding:14px 16px;border:1px solid var(--line);border-radius:12px;font:inherit}}.search:focus{{outline:3px solid color-mix(in srgb,var(--accent) 25%,transparent);border-color:var(--accent)}}
h2{{font-size:1.2rem;color:var(--accent);margin:28px 0 12px}}.faq-item{{border:1px solid var(--line);border-radius:13px;margin:10px 0;padding:0 18px;transition:box-shadow .15s}}.faq-item:hover{{box-shadow:0 5px 18px #1720330b}}
summary{{cursor:pointer;list-style:none;padding:17px 30px 17px 0;font-weight:650;position:relative}}summary::-webkit-details-marker{{display:none}}summary:after{{content:"+";position:absolute;right:2px;color:var(--accent);font-size:1.35rem;line-height:1}}details[open] summary:after{{content:"−"}}.answer{{padding:0 0 18px;color:var(--muted)}}.empty{{display:none;text-align:center;padding:22px;color:var(--muted)}}.contact{{display:inline-block;margin-top:24px;color:var(--accent);font-weight:650;text-decoration:none}}.contact:hover{{text-decoration:underline}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}@media(max-width:600px){{body{{padding:16px 10px}}main{{border-radius:14px;padding:24px 18px}}}}
</style></head><body><main>{brand_markup}<h1>{title}</h1><p class="intro">{intro}</p>
<label class="search-wrap"><span class="sr-only" style="position:absolute;left:-10000px">FAQ durchsuchen</span><input id="faq-search" class="search" type="search" placeholder="Frage oder Antwort durchsuchen…" aria-label="FAQ durchsuchen"></label>
<div id="faq-content">{"".join(sections)}</div><p id="no-results" class="empty">Keine passenden Antworten gefunden.</p>{contact_link}</main>
<script>
const search=document.getElementById('faq-search');
search.addEventListener('input',()=>{{const query=search.value.trim().toLocaleLowerCase('de');let visible=0;document.querySelectorAll('.faq-item').forEach(item=>{{const match=item.textContent.toLocaleLowerCase('de').includes(query);item.hidden=!match;if(match)visible++;}});document.querySelectorAll('.category').forEach(section=>{{section.hidden=!section.querySelector('.faq-item:not([hidden])');}});document.getElementById('no-results').style.display=visible?'none':'block';}});
</script></body></html>'''


if __name__ == "__main__":
    FAQStudioPremium().mainloop()
