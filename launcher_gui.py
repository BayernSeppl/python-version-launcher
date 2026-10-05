import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

VERSIONS = ["3.8", "3.11", "3.14"]


def run_script():
    version = version_var.get()
    script_path = script_entry.get().strip()

    if not script_path:
        messagebox.showerror("Fehler", "Bitte einen Script-Pfad eingeben.")
        return

    if not os.path.exists(script_path):
        messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_path}")
        return

    try:
        command = ["py", f"-{version}", script_path]
        subprocess.Popen(command)
        root.destroy()
    except Exception as exc:
        messagebox.showerror("Fehler", f"Start fehlgeschlagen: {exc}")


def browse_file():
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(
        title="Python-Datei auswählen",
        filetypes=[("Python Files", "*.py"), ("Alle Dateien", "*.*")]
    )
    if file_path:
        script_entry.delete(0, tk.END)
        script_entry.insert(0, file_path)


root = tk.Tk()
root.title("Python Version Launcher")
root.geometry("520x220")
root.resizable(False, False)

main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

label = ttk.Label(main, text="Python-Version auswählen:", font=("Segoe UI", 11, "bold"))
label.grid(row=0, column=0, sticky="w", pady=(0, 8))

version_var = tk.StringVar(value="3.11")
version_combo = ttk.Combobox(main, textvariable=version_var, values=VERSIONS, state="readonly", width=15)
version_combo.grid(row=1, column=0, sticky="w")

script_label = ttk.Label(main, text="Pfad zur Python-Datei:", font=("Segoe UI", 10, "bold"))
script_label.grid(row=2, column=0, sticky="w", pady=(15, 5))

script_entry = ttk.Entry(main, width=52)
script_entry.grid(row=3, column=0, sticky="w")

browse_btn = ttk.Button(main, text="Durchsuchen", command=browse_file)
browse_btn.grid(row=3, column=1, padx=(10, 0), sticky="w")

start_btn = ttk.Button(main, text="Programm starten", command=run_script)
start_btn.grid(row=4, column=0, pady=(20, 0), sticky="w")

root.mainloop()
