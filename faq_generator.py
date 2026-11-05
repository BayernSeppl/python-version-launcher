"""FAQ Studio: a polished, local-first FAQ authoring tool built with Tkinter."""

from __future__ import annotations

import csv
import html
import json
import re
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "FAQ Studio"
BG = "#f4f7fb"
CARD = "#ffffff"
INK = "#172033"
MUTED = "#68748a"
ACCENT = "#5267e8"
BORDER = "#e4e9f2"

ANSWER_TEMPLATES = {
    "Freundlich & klar": "Gerne! {answer}\n\nWenn du noch Fragen hast, hilft dir unser Team gerne weiter.",
    "Kurz & direkt": "{answer}",
    "Schritt für Schritt": "So geht’s:\n1. {answer}\n2. Folge den Anweisungen auf dem Bildschirm.\n3. Bei Fragen kontaktiere bitte unseren Support.",
    "Support-Antwort": "Danke für deine Frage. {answer}\n\nFalls das Problem weiterhin besteht, wende dich bitte mit einer kurzen Beschreibung an unseren Support.",
    "Kauf & Versand": "{answer}\n\nAlle Angaben können je nach Produkt und Lieferadresse variieren. Die aktuellen Details findest du im Bestellprozess.",
    "Eigene Vorlage": "{answer}",
}

SAMPLE_ITEMS = [
    {"category": "Bestellung", "question": "Wie kann ich eine Bestellung aufgeben?", "answer": "Wähle die gewünschten Produkte aus und schließe die Bestellung sicher über unseren Checkout ab."},
    {"category": "Versand", "question": "Wie lange dauert der Versand?", "answer": "Die voraussichtliche Lieferzeit wird dir vor dem Abschluss der Bestellung angezeigt."},
    {"category": "Support", "question": "Wie erreiche ich den Kundenservice?", "answer": "Schreibe unserem Support über das Kontaktformular. Bitte gib deine Bestellnummer an, damit wir dir schneller helfen können."},
]


def clean_text(value: object) -> str:
    """Normalize imported cell values without turning None into the word 'None'."""
    if value is None:
        return ""
    return str(value).strip()


def safe_filename(value: str) -> str:
    value = re.sub(r"[^\w.-]+", "_", value.strip(), flags=re.UNICODE).strip("_.")
    return value or "faq"


class FAQStudio(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("FAQ Studio — Professionelle FAQs einfach erstellen")
        self.geometry("1180x790")
        self.minsize(900, 650)
        self.configure(bg=BG)
        self.items: list[dict[str, str]] = []
        self.selected_id: str | None = None
        self._configure_style()
        self._build_ui()
        self._load_examples()

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
        ttk.Label(header, text="FAQ Studio", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Professionelle Antworten erstellen, organisieren und exportieren.", style="Subheader.TLabel").pack(anchor="w", pady=(3, 0))

        toolbar = ttk.Frame(self, padding=(24, 2, 24, 13))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="＋ Neue Frage", style="Accent.TButton", command=self.clear_form).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="Import: CSV / Excel", command=self.import_file).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt öffnen", command=self.open_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Projekt speichern", command=self.save_project).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Exportieren", command=self.export_menu).pack(side="left", padx=4)
        self.count_label = ttk.Label(toolbar, text="0 Fragen", style="Subheader.TLabel")
        self.count_label.pack(side="right", padx=4)

        body = ttk.Frame(self, padding=(24, 0, 24, 14))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=5, uniform="columns")
        body.columnconfigure(1, weight=6, uniform="columns")
        body.rowconfigure(0, weight=1)

        editor = ttk.Frame(body, style="Card.TFrame", padding=18)
        editor.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        listing = ttk.Frame(body, style="Card.TFrame", padding=18)
        listing.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ttk.Label(editor, text="FAQ-Eintrag", style="Section.TLabel").pack(anchor="w", pady=(0, 14))
        ttk.Label(editor, text="Kategorie").pack(anchor="w", pady=(0, 4))
        self.category_var = tk.StringVar(value="Allgemein")
        ttk.Entry(editor, textvariable=self.category_var).pack(fill="x", pady=(0, 12))
        ttk.Label(editor, text="Frage").pack(anchor="w", pady=(0, 4))
        self.question_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.question_var).pack(fill="x", pady=(0, 12))
        answer_head = ttk.Frame(editor, style="Card.TFrame")
        answer_head.pack(fill="x", pady=(0, 4))
        ttk.Label(answer_head, text="Antwort").pack(side="left")
        ttk.Label(answer_head, text="Klar, konkret und hilfreich", style="Muted.TLabel").pack(side="right")
        self.answer_text = tk.Text(editor, height=9, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, padx=10, pady=9, undo=True, background="#ffffff", foreground=INK, insertbackground=INK)
        self.answer_text.pack(fill="both", expand=True, pady=(0, 12))

        ttk.Label(editor, text="Antwortvorlage (lokal, ohne API-Schlüssel)").pack(anchor="w", pady=(0, 5))
        template_row = ttk.Frame(editor, style="Card.TFrame")
        template_row.pack(fill="x", pady=(0, 6))
        self.template_var = tk.StringVar(value="Freundlich & klar")
        self.template_combo = ttk.Combobox(template_row, textvariable=self.template_var, values=list(ANSWER_TEMPLATES), state="readonly")
        self.template_combo.pack(side="left", fill="x", expand=True, padx=(0, 7))
        ttk.Button(template_row, text="Vorlage anwenden", command=self.apply_template).pack(side="left")
        ttk.Button(editor, text="KI-Prompt erstellen & kopieren", command=self.copy_ai_prompt).pack(anchor="w", pady=(2, 12))

        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.pack(fill="x")
        ttk.Button(actions, text="Speichern / aktualisieren", style="Accent.TButton", command=self.save_entry).pack(side="left")
        ttk.Button(actions, text="Eintrag löschen", command=self.delete_entry).pack(side="left", padx=(8, 0))

        ttk.Label(listing, text="Deine Fragen", style="Section.TLabel").pack(anchor="w", pady=(0, 11))
        search_row = ttk.Frame(listing, style="Card.TFrame")
        search_row.pack(fill="x", pady=(0, 9))
        ttk.Label(search_row, text="Suche").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        search = ttk.Entry(search_row, textvariable=self.search_var)
        search.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", lambda *_: self.refresh_list())

        columns = ("category", "question")
        self.tree = ttk.Treeview(listing, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("category", text="KATEGORIE")
        self.tree.heading("question", text="FRAGE")
        self.tree.column("category", width=115, minwidth=85, stretch=False)
        self.tree.column("question", width=300, minwidth=150, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        ttk.Label(listing, text="Live-Vorschau", style="Section.TLabel").pack(anchor="w", pady=(15, 7))
        self.preview = tk.Text(listing, height=8, wrap="word", font=("Segoe UI", 9), relief="solid", bd=1, padx=10, pady=8, background="#fbfcff", foreground=INK)
        self.preview.pack(fill="both", expand=True)
        self.preview.configure(state="disabled")
        self.status_var = tk.StringVar(value="Bereit. Deine Daten bleiben auf diesem Computer.")
        ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(24, 9), background="#eaf0f8", foreground=MUTED, font=("Segoe UI", 9)).pack(fill="x", side="bottom")

    def _load_examples(self) -> None:
        self.items = [dict(item) for item in SAMPLE_ITEMS]
        self.refresh_list()
        self.refresh_preview()

    def clear_form(self) -> None:
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        self.category_var.set("Allgemein")
        self.question_var.set("")
        self.answer_text.delete("1.0", "end")
        self.question_var_entry_focus()

    def question_var_entry_focus(self) -> None:
        # The editor stays keyboard-friendly without relying on widget order.
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                pass
        self.focus_set()

    def save_entry(self) -> None:
        category = self.category_var.get().strip() or "Allgemein"
        question = self.question_var.get().strip()
        answer = self.answer_text.get("1.0", "end").strip()
        if not question or not answer:
            messagebox.showwarning("Noch nicht vollständig", "Bitte fülle Frage und Antwort aus.", parent=self)
            return
        entry = {"category": category, "question": question, "answer": answer}
        if self.selected_id is not None and 0 <= self.selected_id < len(self.items):
            self.items[self.selected_id] = entry
        else:
            self.items.append(entry)
        self.selected_id = self.items.index(entry)
        self.refresh_list()
        self.refresh_preview()
        self.status_var.set("Eintrag gespeichert.")

    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        try:
            index = int(selected[0])
            entry = self.items[index]
        except (ValueError, IndexError):
            return
        self.selected_id = index
        self.category_var.set(entry["category"])
        self.question_var.set(entry["question"])
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", entry["answer"])

    def delete_entry(self) -> None:
        if self.selected_id is None or not 0 <= self.selected_id < len(self.items):
            messagebox.showinfo("Eintrag auswählen", "Wähle zuerst eine Frage in der Liste aus.", parent=self)
            return
        if messagebox.askyesno("Eintrag löschen", "Möchtest du diesen FAQ-Eintrag wirklich löschen?", parent=self):
            del self.items[self.selected_id]
            self.clear_form()
            self.refresh_list()
            self.refresh_preview()
            self.status_var.set("Eintrag gelöscht.")

    def refresh_list(self) -> None:
        query = self.search_var.get().strip().casefold() if hasattr(self, "search_var") else ""
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())
        for index, item in enumerate(self.items):
            haystack = " ".join(item.values()).casefold()
            if not query or query in haystack:
                self.tree.insert("", "end", iid=str(index), values=(item["category"], item["question"]))
        self.count_label.configure(text=f"{len(self.items)} Fragen")

    def refresh_preview(self) -> None:
        if not hasattr(self, "preview"):
            return
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for item in self.items:
            grouped[item["category"]].append(item)
        lines = ["FAQ-Vorschau", "─" * 24, ""]
        for category, entries in grouped.items():
            lines.extend((category, ""))
            for item in entries:
                lines.extend((f"• {item['question']}", item["answer"], ""))
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", "\n".join(lines) if self.items else "Noch keine Einträge vorhanden.")
        self.preview.configure(state="disabled")

    def apply_template(self) -> None:
        current = self.answer_text.get("1.0", "end").strip()
        if not current:
            messagebox.showinfo("Antwort zuerst ergänzen", "Schreibe zuerst deine Fakten oder Stichpunkte in das Antwortfeld. Die Vorlage formt sie anschließend aus.", parent=self)
            return
        template = ANSWER_TEMPLATES.get(self.template_var.get(), "{answer}")
        answer = template.format(answer=current)
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", answer)
        self.status_var.set("Antwortvorlage angewendet — bitte Fakten und Ton prüfen.")

    def copy_ai_prompt(self) -> None:
        question = self.question_var.get().strip()
        answer = self.answer_text.get("1.0", "end").strip()
        if not question:
            messagebox.showinfo("Frage fehlt", "Gib zuerst die FAQ-Frage ein, damit ein passender Prompt erstellt werden kann.", parent=self)
            return
        prompt = (
            "Du bist ein professioneller Kundenservice-Texter. Formuliere eine hilfreiche, klare und freundliche FAQ-Antwort auf Deutsch. "
            "Erfinde keine Fakten. Wenn Angaben fehlen, markiere sie mit [BITTE ERGÄNZEN]. Schreibe verständlich und konkret.\n\n"
            f"Kategorie: {self.category_var.get().strip() or 'Allgemein'}\n"
            f"Frage: {question}\n"
            f"Bekannte Fakten / Entwurf: {answer or '[hier Fakten ergänzen]'}\n\n"
            "Gib nur den fertigen Antworttext zurück."
        )
        self.clipboard_clear()
        self.clipboard_append(prompt)
        self.status_var.set("KI-Prompt in die Zwischenablage kopiert. In deinem bevorzugten KI-Dienst einfügen.")
        messagebox.showinfo("Prompt kopiert", "Der Prompt wurde kopiert. Füge ihn in ChatGPT oder einen anderen KI-Dienst ein und prüfe die Antwort vor der Veröffentlichung.", parent=self)

    def import_file(self) -> None:
        path = filedialog.askopenfilename(
            title="FAQ-Datei importieren",
            filetypes=[("CSV oder Excel", "*.csv *.xlsx *.xlsm"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xlsm"), ("Alle Dateien", "*.*")],
            parent=self,
        )
        if not path:
            return
        try:
            imported = self._read_spreadsheet(Path(path))
            if not imported:
                raise ValueError("Es wurden keine gültigen FAQ-Zeilen gefunden. Erwartet werden Spalten für Frage und Antwort.")
        except ImportError as exc:
            messagebox.showerror("Excel-Unterstützung fehlt", f"{exc}\n\nInstalliere sie mit: py -m pip install -r requirements-faq.txt", parent=self)
            return
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror("Import fehlgeschlagen", str(exc), parent=self)
            return
        self.items.extend(imported)
        self.refresh_list()
        self.refresh_preview()
        self.status_var.set(f"{len(imported)} Einträge aus {Path(path).name} importiert.")

    @staticmethod
    def _read_spreadsheet(path: Path) -> list[dict[str, str]]:
        if path.suffix.casefold() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                sample = file.read(4096)
                file.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
                except csv.Error:
                    dialect = csv.excel
                    dialect.delimiter = ";" if sample.count(";") > sample.count(",") else ","
                rows = list(csv.DictReader(file, dialect=dialect))
            return FAQStudio._normalize_rows(rows)
        if path.suffix.casefold() in {".xlsx", ".xlsm"}:
            try:
                from openpyxl import load_workbook
            except ImportError as exc:
                raise ImportError("Für Excel-Dateien wird das Paket openpyxl benötigt.") from exc
            workbook = load_workbook(path, read_only=True, data_only=True)
            try:
                sheet = workbook.active
                values = sheet.iter_rows(values_only=True)
                headers = next(values, None)
                if not headers:
                    return []
                rows = [dict(zip([clean_text(h) for h in headers], row)) for row in values]
                return FAQStudio._normalize_rows(rows)
            finally:
                workbook.close()
        raise ValueError("Bitte eine CSV-, XLSX- oder XLSM-Datei auswählen.")

    @staticmethod
    def _normalize_rows(rows: list[dict]) -> list[dict[str, str]]:
        imported = []
        for row in rows:
            normalized = {re.sub(r"[^a-z]", "", clean_text(key).casefold()): value for key, value in row.items() if key is not None}
            question = next((clean_text(normalized.get(key)) for key in ("frage", "question", "q", "title") if clean_text(normalized.get(key))), "")
            answer = next((clean_text(normalized.get(key)) for key in ("antwort", "answer", "a", "response") if clean_text(normalized.get(key))), "")
            category = next((clean_text(normalized.get(key)) for key in ("kategorie", "category", "bereich", "topic") if clean_text(normalized.get(key))), "Allgemein")
            if question and answer:
                imported.append({"category": category or "Allgemein", "question": question, "answer": answer})
        return imported

    def save_project(self) -> None:
        path = filedialog.asksaveasfilename(title="FAQ-Projekt speichern", defaultextension=".json", initialfile="mein_faq_projekt.json", filetypes=[("FAQ-Projekt (JSON)", "*.json")], parent=self)
        if not path:
            return
        try:
            Path(path).write_text(json.dumps({"format": "faq-studio", "version": 1, "items": self.items}, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status_var.set(f"Projekt gespeichert: {Path(path).name}")
        except OSError as exc:
            messagebox.showerror("Speichern fehlgeschlagen", str(exc), parent=self)

    def open_project(self) -> None:
        path = filedialog.askopenfilename(title="FAQ-Projekt öffnen", filetypes=[("FAQ-Projekt (JSON)", "*.json"), ("JSON", "*.json")], parent=self)
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            records = data.get("items", data) if isinstance(data, dict) else data
            if not isinstance(records, list):
                raise ValueError("Die Datei enthält keine FAQ-Liste.")
            items = self._normalize_rows(records)
            if not items:
                raise ValueError("Die Datei enthält keine gültigen Fragen und Antworten.")
        except (OSError, json.JSONDecodeError, ValueError, AttributeError) as exc:
            messagebox.showerror("Projekt konnte nicht geöffnet werden", str(exc), parent=self)
            return
        self.items = items
        self.clear_form()
        self.refresh_list()
        self.refresh_preview()
        self.status_var.set(f"Projekt geladen: {Path(path).name}")

    def export_menu(self) -> None:
        if not self.items:
            messagebox.showinfo("Noch keine FAQs", "Füge zuerst mindestens einen FAQ-Eintrag hinzu.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            title="FAQ exportieren", defaultextension=".html", initialfile=f"{safe_filename('faq')}.html",
            filetypes=[("Webseite (HTML)", "*.html"), ("Markdown", "*.md"), ("CSV", "*.csv"), ("JSON", "*.json")], parent=self,
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
                with destination.open("w", encoding="utf-8-sig", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["category", "question", "answer"], delimiter=";")
                    writer.writeheader()
                    writer.writerows(self.items)
                content = None
            elif suffix == ".json":
                content = json.dumps({"format": "faq-studio", "version": 1, "items": self.items}, ensure_ascii=False, indent=2)
            else:
                raise ValueError("Bitte wähle HTML, Markdown, CSV oder JSON als Dateiformat.")
            if content is not None:
                destination.write_text(content, encoding="utf-8")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export fehlgeschlagen", str(exc), parent=self)
            return
        self.status_var.set(f"Export fertig: {destination.name}")
        messagebox.showinfo("Export abgeschlossen", f"Deine FAQ wurde gespeichert:\n{destination}", parent=self)

    @staticmethod
    def _grouped(items: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for item in items:
            groups[item["category"]].append(item)
        return groups

    def _as_markdown(self) -> str:
        lines = ["# Häufig gestellte Fragen", ""]
        for category, entries in self._grouped(self.items).items():
            lines.extend((f"## {category}", ""))
            for item in entries:
                lines.extend((f"### {item['question']}", "", item["answer"], ""))
        return "\n".join(lines)

    def _as_html(self) -> str:
        sections = []
        for category, entries in self._grouped(self.items).items():
            cards = "\n".join(
                '<details class="faq-item"><summary>' + html.escape(item["question"]) + "</summary><p>" + html.escape(item["answer"]).replace("\n", "<br>\\n") + "</p></details>"
                for item in entries
            )
            sections.append(f"<section><h2>{html.escape(category)}</h2>{cards}</section>")
        return """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Häufig gestellte Fragen</title><style>
:root{color-scheme:light;--ink:#172033;--muted:#68748a;--line:#e4e9f2;--accent:#5267e8}
*{box-sizing:border-box}body{margin:0;padding:48px 20px;background:#f4f7fb;color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:auto;padding:clamp(24px,5vw,56px);background:#fff;border-radius:20px;box-shadow:0 12px 45px #17203312}h1{font-size:clamp(2rem,5vw,3rem);line-height:1.15;margin:0 0 32px}h2{font-size:1.3rem;margin:32px 0 12px;color:var(--accent)}
.faq-item{border:1px solid var(--line);border-radius:12px;margin:10px 0;padding:0 16px}.faq-item summary{cursor:pointer;list-style:none;padding:16px 28px 16px 0;font-weight:650;position:relative}.faq-item summary::-webkit-details-marker{display:none}.faq-item summary:after{content:"+";position:absolute;right:2px;color:var(--accent);font-size:1.3rem}.faq-item[open] summary:after{content:"−"}.faq-item p{margin:0;padding:0 0 18px;color:var(--muted);white-space:normal}
</style></head><body><main><h1>Häufig gestellte Fragen</h1>""" + "\n".join(sections) + "</main></body></html>"


if __name__ == "__main__":
    FAQStudio().mainloop()
