import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

PROJECTS = {
    "Sitemap XML Generator": {
        "script": "app.py",
        "version": "3.11",
        "path": ""
    },
    "Sitemap Submission Tool": {
        "script": "app.py",
        "version": "3.11",
        "path": ""
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
    from tkinter import filedialog
    project = project_var.get()
    if not project:
        messagebox.showerror("Fehler", "Bitte ein Projekt auswählen.")
        return
    
    folder_path = filedialog.askdirectory(title=f"Ordner für '{project}' auswählen")
    if folder_path:
        PROJECTS[project]["path"] = folder_path
        path_label.config(text=f"Pfad: {folder_path}")


def on_project_change(*args):
    project = project_var.get()
    if project and PROJECTS[project]["path"]:
        path_label.config(text=f"Pfad: {PROJECTS[project]['path']}")
    else:
        path_label.config(text="Pfad: Noch nicht konfiguriert")


root = tk.Tk()
root.title("Python Project Launcher")
root.geometry("600x300")
root.resizable(False, False)

# Hauptrahmen
main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

# Titel
title = ttk.Label(main, text="Python Projekt Launcher", font=("Segoe UI", 14, "bold"))
title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

# Projekt-Auswahl
project_label = ttk.Label(main, text="Projekt auswählen:", font=("Segoe UI", 11, "bold"))
project_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

project_var = tk.StringVar()
project_combo = ttk.Combobox(main, textvariable=project_var, values=list(PROJECTS.keys()), state="readonly", width=50)
project_combo.grid(row=2, column=0, columnspan=2, sticky="w")
project_combo.bind("<<ComboboxSelected>>", on_project_change)

# Pfad-Anzeige
path_label = ttk.Label(main, text="Pfad: Noch nicht konfiguriert", font=("Segoe UI", 9), foreground="gray")
path_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

# Browse-Button
browse_btn = ttk.Button(main, text="Pfad konfigurieren", command=browse_project_path)
browse_btn.grid(row=4, column=0, sticky="w", pady=(8, 15))

# Python-Version
version_label = ttk.Label(main, text="Python-Version auswählen:", font=("Segoe UI", 11, "bold"))
version_label.grid(row=5, column=0, sticky="w", pady=(0, 5))

version_var = tk.StringVar(value="3.11")
version_combo = ttk.Combobox(main, textvariable=version_var, values=VERSIONS, state="readonly", width=15)
version_combo.grid(row=6, column=0, sticky="w")

# Start-Button
start_btn = ttk.Button(main, text="Projekt starten", command=run_project)
start_btn.grid(row=7, column=0, sticky="w", pady=(20, 0))

# Info-Text
info = ttk.Label(main, text="Hinweis: Wähle erst das Projekt, konfiguriere den Pfad, wähle die Python-Version und starte dann.", 
                 font=("Segoe UI", 9), foreground="blue", wraplength=550, justify="left")
info.grid(row=8, column=0, columnspan=2, sticky="w", pady=(15, 0))

root.mainloop()
