import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

PROJECTS = {
    "Sitemap XML Generator": {
        "script": "app.py",
        "path": "",
        "default_version": "3.11"
    },
    "Sitemap Submission Tool": {
        "script": "app.py",
        "path": "",
        "default_version": "3.11"
    }
}

VERSIONS = ["3.8", "3.11", "3.14"]

def run_project():
    project = project_var.get()
    if not project:
        messagebox.showerror("Fehler", "Bitte ein Projekt auswählen.")
        return

    project_info = PROJECTS[project]
    version = version_var.get()
    project_path = project_info["path"]

    if not project_path or not os.path.exists(project_path):
        messagebox.showerror("Fehler", f"Pfad für '{project}' nicht konfiguriert oder nicht vorhanden.")
        return

    script_full_path = os.path.join(project_path, project_info["script"])
    if not os.path.exists(script_full_path):
        messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_full_path}")
        return

    try:
        command = ["py", f"-{version}", script_full_path]
        subprocess.Popen(command, cwd=project_path)
        root.destroy()
    except Exception as exc:
        messagebox.showerror("Fehler", f"Start fehlgeschlagen: {exc}")

def browse_project_path():
    project = project_var.get()
    if not project:
        messagebox.showerror("Fehler", "Bitte zuerst ein Projekt auswählen.")
        return

    folder_path = filedialog.askdirectory(title=f"Ordner für '{project}' auswählen")
    if folder_path:
        PROJECTS[project]["path"] = folder_path
        path_label.config(text=f"Pfad: {folder_path}")

def on_project_change(*args):
    project = project_var.get()
    if project:
        info = PROJECTS[project]
        if info["path"]:
            path_label.config(text=f"Pfad: {info['path']}")
        else:
            path_label.config(text="Pfad: Noch nicht konfiguriert")
        version_var.set(info["default_version"])
    else:
        path_label.config(text="Pfad: Noch nicht konfiguriert")

root = tk.Tk()
root.title("Projekt Launcher mit Python-Version Auswahl")
root.geometry("620x330")
root.resizable(False, False)

main = ttk.Frame(root, padding=18)
main.pack(fill="both", expand=True)

header = ttk.Label(main, text="Projekt Launcher", font=("Segoe UI", 14, "bold"))
header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

project_label = ttk.Label(main, text="Projekt auswählen:", font=("Segoe UI", 10, "bold"))
project_label.grid(row=1, column=0, sticky="w")

project_var = tk.StringVar()
project_combo = ttk.Combobox(main, textvariable=project_var, values=list(PROJECTS.keys()), state="readonly", width=55)
project_combo.grid(row=2, column=0, columnspan=2, sticky="w")
project_combo.bind("<<ComboboxSelected>>", on_project_change)

path_label = ttk.Label(main, text="Pfad: Noch nicht konfiguriert", foreground="gray")
path_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

browse_btn = ttk.Button(main, text="Ordner auswählen", command=browse_project_path)
browse_btn.grid(row=4, column=0, sticky="w", pady=(8, 15))

version_label = ttk.Label(main, text="Python-Version:", font=("Segoe UI", 10, "bold"))
version_label.grid(row=5, column=0, sticky="w")

version_var = tk.StringVar(value="3.11")
version_combo = ttk.Combobox(main, textvariable=version_var, values=VERSIONS, state="readonly", width=12)
version_combo.grid(row=6, column=0, sticky="w")

start_btn = ttk.Button(main, text="Projekt starten", command=run_project)
start_btn.grid(row=7, column=0, sticky="w", pady=(22, 0))

info = ttk.Label(
    main,
    text="Hinweis: Für die Sitemap-Tools ist meist Python 3.11 die richtige Wahl.\nFür alte Programme kann 3.8 nötig sein, für neue Programme ggf. 3.14.",
    foreground="blue",
    wraplength=560,
    justify="left"
)
info.grid(row=8, column=0, columnspan=2, sticky="w", pady=(15, 0))

root.mainloop()
