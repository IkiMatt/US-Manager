import tkinter as tk
import os
from tkinter import simpledialog, messagebox
from tkinter import ttk
import json
from tkinter import BooleanVar
import ast # Per ast.literal_eval
import tkinter.font as tkFont # Importa tkinter.font
import datetime

# --- Helper Functions ---
def load_json_file(filepath):
    """Carica un file JSON in modo sicuro."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            messagebox.showerror("Errore JSON", f"Il file {os.path.basename(filepath)} è corrotto: {e}")
            return {}
        except Exception as e:
            messagebox.showerror("Errore di Lettura", f"Errore durante la lettura di {os.path.basename(filepath)}: {e}")
            return {}
    return {}

def save_json_file(filepath, data):
    """Salva i dati in un file JSON in modo sicuro."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Errore di Scrittura", f"Errore durante il salvataggio di {os.path.basename(filepath)}: {e}")

class ProjectDialog(tk.Toplevel):
    def __init__(self, master, on_save):
        super().__init__(master)
        self.title("Nuovo Progetto")
        self.resizable(False, False)
        self.on_save = on_save

        fields = [
            ("Nome Progetto", "text"),
            ("ID Progetto", "text"),
            ("Via", "text"),
            ("Comune", "text"),
            ("Anno di inizio", "year"),
            ("Archeologo progettista", "text"),
            ("Direttore Lavori", "text"),
            ("Responsabile scientifico", "text"),
            ("Ente responsabile", "text"),
            ("Organo ministeriale territoriale", "text"),
        ]
        self.entries = {}

        for i, (label, typ) in enumerate(fields):
            tk.Label(self, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=3)
            if typ == "year":
                entry = ttk.Entry(self, width=10)
                entry.grid(row=i, column=1, padx=5, pady=3)
                entry.config(validate="key", validatecommand=(self.register(self.validate_year), "%P"))
            else:
                entry = ttk.Entry(self, width=30)
                entry.grid(row=i, column=1, padx=5, pady=3)
            self.entries[label] = entry

        save_btn = ttk.Button(self, text="\U0001F4BE Salva", command=self.save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def validate_year(self, value):
        return value.isdigit() and (len(value) <= 4)

    def save(self):
        data = {label: entry.get().strip() for label, entry in self.entries.items()}
        if not all(data.values()):
            messagebox.showerror("Errore", "Compila tutti i campi.")
            return
        self.on_save(data)
        self.destroy()

def ensure_project_file():
    project_path = os.path.join("manager", "project.py")
    root = tk.Tk()
    root.withdraw()
    project_created = False
    if not os.path.exists(project_path):
        def save_project(data):
            nonlocal project_created
            os.makedirs("manager", exist_ok=True)
            with open(project_path, "w", encoding="utf-8") as f:
                for k, v in data.items():
                    f.write(f"{k.replace(' ', '_').lower()} = {repr(v)}\n")
            messagebox.showinfo("Salvato", "Dati del progetto salvati.")
            project_created = True
        d = ProjectDialog(root, save_project)
        root.wait_window(d)
    else:
        project_created = True
    root.destroy()
    return project_created

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        try:
            x, y, _, cy = self.widget.bbox("insert")
        except Exception:
            x, y, cy = 0, 0, 0
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=4)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def load_project_data():
    project_path = os.path.join("manager", "project.py")
    data = {}
    if os.path.exists(project_path):
        with open(project_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    try:
                        data[k.strip()] = ast.literal_eval(v.strip())
                    except (ValueError, SyntaxError):
                        data[k.strip()] = v.strip()
    return data

def get_next_id():
    folder = "su_report"
    if not os.path.exists(folder):
        return 1
    files = [f for f in os.listdir(folder) if f.lower().endswith(".json")]
    return len(files) + 1

def list_su_reports(exclude_filename=None):
    folder = "su_report"
    if not os.path.exists(folder):
        return []
    files = [f for f in os.listdir(folder) if f.lower().endswith(".json")]
    if exclude_filename:
        files = [f for f in files if f != exclude_filename]
    return sorted([os.path.splitext(f)[0] for f in files])

CUSTOM_FIELDS_PATH = os.path.join("manager", "custom_fields.json")

def load_custom_fields():
    return load_json_file(CUSTOM_FIELDS_PATH)

def save_custom_fields(fields_data):
    os.makedirs("manager", exist_ok=True)
    save_json_file(CUSTOM_FIELDS_PATH, fields_data)

class CustomFieldsDialog(tk.Toplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.title("Configura Campi Personalizzati")
        self.resizable(False, False)
        self.app_instance = app_instance
        self.custom_fields = load_custom_fields()
        
        self.create_widgets()
        self.populate_list()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self, text="Nuovo Campo Personalizzato")
        input_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(input_frame, text="Nome Campo:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.field_name_entry = ttk.Entry(input_frame, width=30)
        self.field_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(input_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.field_type_var = tk.StringVar()
        self.field_type_combobox = ttk.Combobox(input_frame, textvariable=self.field_type_var, 
                                                 values=["Testo", "Numerico", "Dropdown", "Checkbox"],
                                                 state="readonly", width=27)
        self.field_type_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.field_type_combobox.bind("<<ComboboxSelected>>", self._on_type_selected)

        self.dropdown_options_label = tk.Label(input_frame, text="Opzioni (se Dropdown, separate da virgola):")
        self.dropdown_options_entry = ttk.Entry(input_frame, width=30)

        self.add_button = ttk.Button(input_frame, text="Aggiungi Campo", command=self.add_field)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=5)

        list_frame = ttk.LabelFrame(self, text="Campi Esistenti")
        list_frame.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("Nome Campo", "Tipo")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.delete_button = ttk.Button(self, text="Elimina Campo Selezionato", command=self.delete_field)
        self.delete_button.pack(pady=5)
        
        self._on_type_selected()

    def _on_type_selected(self, event=None):
        if self.field_type_var.get() == "Dropdown":
            self.dropdown_options_label.grid(row=3, column=0, padx=5, pady=2, sticky="e")
            self.dropdown_options_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
            self.add_button.grid(row=4, column=0, columnspan=2, pady=5)
        else:
            self.dropdown_options_label.grid_forget()
            self.dropdown_options_entry.grid_forget()
            self.add_button.grid(row=2, column=0, columnspan=2, pady=5)

    def populate_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for field in self.custom_fields:
            name = field["name"]
            field_type = field["type"]
            self.tree.insert("", "end", values=(name, field_type))

    def add_field(self):
        name = self.field_name_entry.get().strip()
        field_type = self.field_type_var.get()
        options = []

        if not name or not field_type:
            messagebox.showerror("Errore", "Nome e tipo del campo sono obbligatori.")
            return
        
        if any(f["name"] == name for f in self.custom_fields):
            messagebox.showerror("Errore", "Un campo con questo nome esiste già.")
            return

        if field_type == "Dropdown":
            options_str = self.dropdown_options_entry.get().strip()
            if not options_str:
                messagebox.showerror("Errore", "Le opzioni sono obbligatorie per il tipo Dropdown.")
                return
            options = [opt.strip() for opt in options_str.split(',') if opt.strip()]

        new_field = {"name": name, "type": field_type}
        if options:
            new_field["options"] = options

        self.custom_fields.append(new_field)
        save_custom_fields(self.custom_fields)
        self.populate_list()
        self.field_name_entry.delete(0, tk.END)
        self.field_type_var.set("")
        self.dropdown_options_entry.delete(0, tk.END)
        messagebox.showinfo("Successo", f"Campo '{name}' aggiunto.")

    def delete_field(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un campo da eliminare.")
            return

        item_values = self.tree.item(selected_item[0], "values")
        field_name_to_delete = item_values[0]

        confirm = messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare il campo '{field_name_to_delete}'? Questa azione non elimina i dati già salvati nelle schede esistenti, ma il campo non sarà più modificabile.")
        if confirm:
            self.custom_fields = [f for f in self.custom_fields if f["name"] != field_name_to_delete]
            save_custom_fields(self.custom_fields)
            self.populate_list()
            messagebox.showinfo("Successo", f"Campo '{field_name_to_delete}' eliminato.")
        
        self.app_instance.refresh_treeview()

class USCardDialog(tk.Toplevel):
    def __init__(self, master, project_data, existing_data=None):
        super().__init__(master)
        self.title("Nuova Scheda US" if existing_data is None else "Modifica Scheda US")
        self.resizable(False, False)
        self.project_data = project_data
        self.existing_data = existing_data
        self.original_filename = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="Dati Iniziali")
        row = 0
        self.fields = {}
        tk.Label(tab1, text="ID").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        display_id = str(existing_data.get("ID", get_next_id())) if existing_data else str(get_next_id())
        self.fields["ID"] = tk.Label(tab1, text=display_id)
        self.fields["ID"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Nome Progetto").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.fields["Nome Progetto"] = tk.Label(tab1, text=project_data.get("project_name", ""))
        self.fields["Nome Progetto"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="ID Progetto").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.fields["ID Progetto"] = tk.Label(tab1, text=project_data.get("project_id", ""))
        self.fields["ID Progetto"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Numero US").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.us_number_var = tk.StringVar()
        entry_us_num = ttk.Entry(tab1, textvariable=self.us_number_var)
        entry_us_num.grid(row=row, column=1, padx=5, pady=2)
        entry_us_num.config(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))
        row += 1
        tk.Label(tab1, text="Tipo").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.type_var = tk.StringVar()
        type_options = ["SU", "SU Muraria", "SU Rivestimento", "SU Documentaria", "SU Virtuale strutturale", "SU Virtuale non strutturale"]
        ttk.Combobox(tab1, textvariable=self.type_var, values=type_options, state="readonly").grid(row=row, column=1, padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Negativa").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.negative_var = BooleanVar()
        ttk.Checkbutton(tab1, variable=self.negative_var).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Area").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.area_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.area_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Indagini archeologiche preliminari").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.prelim_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.prelim_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Settore").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.sector_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.sector_var).grid(row=row, column=1, padx=5, pady=2)
        row += 1
        tk.Label(tab1, text="Quadrato").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.square_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.square_var).grid(row=row, column=1, padx=5, pady=2)

        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="Contenuto")
        row2 = 0
        tk.Label(tab2, text="Criteri di distinzione").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.distinction_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.distinction_var).grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1
        tk.Label(tab2, text="Componenti organiche").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.organic_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.organic_var).grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1
        tk.Label(tab2, text="Componenti inorganiche").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.inorganic_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.inorganic_var).grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1
        tk.Label(tab2, text="Consistenza").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.consistency_var = tk.StringVar()
        ttk.Combobox(tab2, textvariable=self.consistency_var, values=[str(i) for i in range(1,6)], state="readonly").grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1
        tk.Label(tab2, text="Colore").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.color_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.color_var).grid(row=row2, column=1, padx=5, pady=2)
        row2 += 1
        tk.Label(tab2, text="Misure").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.measures_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.measures_var).grid(row=row2, column=1, padx=5, pady=2)

        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="Rapporti")
        full_frame = ttk.LabelFrame(tab3, text="Rapporti Completi")
        full_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        full_fields = ["Copre (US separate da virgola)", "Coperto da (US separate da virgola)", "Uguale a (US separate da virgola)", "Si lega a (US separate da virgola)", "Si appoggia a (US separate da virgola)", "Taglia (US separate da virgola)", "Tagliato da (US separate da virgola)", "Riempie (US separate da virgola)", "Riempito da (US separate da virgola)"]
        self.full_relations_vars = {}
        for i, label in enumerate(full_fields):
            tk.Label(full_frame, text=label).grid(row=i, column=0, sticky="e", padx=3, pady=2)
            var = tk.StringVar()
            ttk.Entry(full_frame, textvariable=var, width=30).grid(row=i, column=1, padx=3, pady=2)
            self.full_relations_vars[label] = var
        simple_frame = ttk.LabelFrame(tab3, text="Rapporti Semplificati")
        simple_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        simple_fields = [("Copre (US multiple)", "Copre"), ("Coperto da (US multiple)", "Coperto da")]
        self.simplified_relations_vars = {}
        for i, (label, key) in enumerate(simple_fields):
            tk.Label(simple_frame, text=label).grid(row=i, column=0, sticky="e", padx=3, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(simple_frame, textvariable=var, width=28)
            entry.grid(row=i, column=1, padx=3, pady=2, sticky="ew")
            self.simplified_relations_vars[key] = var
            select_btn = ttk.Button(simple_frame, text="...", width=3, command=lambda v=var: self.open_su_selection_dialog(v))
            select_btn.grid(row=i, column=2, padx=(0, 3), pady=2, sticky="w")

        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="Osservazioni")
        tk.Label(tab4, text="Descrizione").grid(row=0, column=0, sticky="ne", padx=5, pady=2)
        self.description_text = tk.Text(tab4, height=2.5, width=40)
        self.description_text.grid(row=0, column=1, padx=5, pady=2)
        row_obs = 1
        tk.Label(tab4, text="Osservazioni").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.observations_text = tk.Text(tab4, height=2.5, width=40)
        self.observations_text.grid(row=row_obs, column=1, padx=5, pady=2)
        row_obs += 1
        tk.Label(tab4, text="Interpretazioni").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.interpretations_text = tk.Text(tab4, height=2.5, width=40)
        self.interpretations_text.grid(row=row_obs, column=1, padx=5, pady=2)
        row_obs += 1
        tk.Label(tab4, text="Contesto cronologico").grid(row=row_obs, column=0, sticky="e", padx=5, pady=2)
        self.cronological_context_var = tk.StringVar()
        ttk.Entry(tab4, textvariable=self.cronological_context_var).grid(row=row_obs, column=1, padx=5, pady=2)
        row_obs += 1
        tk.Label(tab4, text="Datazione").grid(row=row_obs, column=0, sticky="e", padx=5, pady=2)
        self.dating_var = tk.StringVar()
        ttk.Entry(tab4, textvariable=self.dating_var).grid(row=row_obs, column=1, padx=5, pady=2)
        row_obs += 1
        tk.Label(tab4, text="Elementi di datazione").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.dating_elements_text = tk.Text(tab4, height=2.5, width=40)
        self.dating_elements_text.grid(row=row_obs, column=1, padx=5, pady=2)
        row_obs += 1

        tab5 = ttk.Frame(self.notebook)
        self.notebook.add(tab5, text="Autore")
        row_tab5 = 0
        tk.Label(tab5, text="Responsabile scientifico").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.fields["Responsabile scientifico"] = tk.Label(tab5, text=project_data.get("scientific_manager", ""))
        self.fields["Responsabile scientifico"].grid(row=row_tab5, column=1, sticky="w", padx=5, pady=2)
        row_tab5 += 1
        tk.Label(tab5, text="Autore scheda").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.report_author_var = tk.StringVar()
        ttk.Entry(tab5, textvariable=self.report_author_var).grid(row=row_tab5, column=1, padx=5, pady=2)
        row_tab5 += 1
        tk.Label(tab5, text="Data").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.date_var = tk.StringVar()
        ttk.Entry(tab5, textvariable=self.date_var).grid(row=row_tab5, column=1, padx=5, pady=2)
        row_tab5 += 1

        self.custom_fields_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_fields_tab, text="Campi Personalizzati")
        self.custom_field_vars = {}
        self._load_and_create_custom_fields()

        if self.existing_data:
            self.populate_fields()
            type_map_reverse = {"": "SU", "M": "SU Muraria", "R": "SU Rivestimento", "D": "SU Documentaria", "V_s": "SU Virtuale strutturale", "V_n": "SU Virtuale non strutturale"}
            us_num = self.existing_data.get("SU number")
            us_type = self.existing_data.get("Type")
            negative = self.existing_data.get("Negative", False)
            type_code_rev = ""
            for code, name in type_map_reverse.items():
                if name == us_type:
                    type_code_rev = code
                    break
            negative_code_rev = "-" if negative else ""
            self.original_filename = f"US{type_code_rev}{negative_code_rev}{us_num}.json"

        save_btn = ttk.Button(self, text="\U0001F4BE Salva", command=self.save_card)
        save_btn.grid(row=1, column=0, pady=10)

    def validate_integer_input(self, value):
        return value.isdigit() or value == ""
        
    def _load_and_create_custom_fields(self):
        custom_fields_data = load_custom_fields()
        current_row = 0
        for field_def in custom_fields_data:
            field_name = field_def["name"]
            field_type = field_def["type"]
            tk.Label(self.custom_fields_tab, text=field_name + ":").grid(row=current_row, column=0, sticky="e", padx=5, pady=2)
            if field_type == "Testo":
                var = tk.StringVar()
                ttk.Entry(self.custom_fields_tab, textvariable=var, width=30).grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
                self.custom_field_vars[field_name] = var
            elif field_type == "Numerico":
                var = tk.StringVar()
                entry = ttk.Entry(self.custom_fields_tab, textvariable=var, width=30)
                entry.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
                entry.config(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))
                self.custom_field_vars[field_name] = var
            elif field_type == "Dropdown":
                var = tk.StringVar()
                options = field_def.get("options", [])
                ttk.Combobox(self.custom_fields_tab, textvariable=var, values=options, state="readonly", width=27).grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
                self.custom_field_vars[field_name] = var
            elif field_type == "Checkbox":
                var = BooleanVar()
                ttk.Checkbutton(self.custom_fields_tab, variable=var).grid(row=current_row, column=1, padx=5, pady=2, sticky="w")
                self.custom_field_vars[field_name] = var
            current_row += 1

    def open_su_selection_dialog(self, target_entry_var):
        dialog = tk.Toplevel(self)
        dialog.title("Seleziona US")
        dialog.transient(self)
        dialog.grab_set()
        available_sus = list_su_reports(exclude_filename=self.original_filename)
        available_sus_display = sorted([os.path.splitext(f)[0] for f in available_sus])
        current_selection_list = [s.strip() for s in target_entry_var.get().split(',') if s.strip()]
        self.su_checkbox_vars = {}
        row_num = 0
        for su_display_name in available_sus_display:
            var = tk.BooleanVar()
            if su_display_name in current_selection_list:
                var.set(True)
            ttk.Checkbutton(dialog, text=su_display_name, variable=var).grid(row=row_num, column=0, sticky="w", padx=5, pady=2)
            self.su_checkbox_vars[su_display_name] = var
            row_num += 1
        def on_ok():
            selected_sus = [su_name for su_name, var in self.su_checkbox_vars.items() if var.get()]
            target_entry_var.set(", ".join(selected_sus))
            dialog.destroy()
        ttk.Button(dialog, text="OK", command=on_ok).grid(row=row_num, column=0, pady=10)
        ttk.Button(dialog, text="Annulla", command=dialog.destroy).grid(row=row_num, column=1, pady=10)
        self.wait_window(dialog)

    def save_card(self):
        us_num_val = self.us_number_var.get()
        if not us_num_val.isdigit():
            messagebox.showerror("Errore", "Il numero US deve essere un intero.")
            return
        if not self.type_var.get():
            messagebox.showerror("Errore", "Il tipo è obbligatorio.")
            return
        custom_fields_data = load_custom_fields()
        for field_def in custom_fields_data:
            if field_def["type"] == "Numerico":
                field_name = field_def["name"]
                var = self.custom_field_vars.get(field_name)
                if var and var.get() and not var.get().isdigit():
                    messagebox.showerror("Errore di input", f"Il campo '{field_name}' deve essere un numero intero.")
                    return
        type_map = {"SU": "", "SU Muraria": "M", "SU Rivestimento": "R", "SU Documentaria": "D", "SU Virtuale strutturale": "V_s", "SU Virtuale non strutturale": "V_n"}
        type_code = type_map.get(self.type_var.get(), "")
        negative_code = "-" if self.negative_var.get() else ""
        us_number = self.us_number_var.get()
        new_filename = f"US{type_code}{negative_code}{us_number}.json"
        new_filepath = os.path.join("su_report", new_filename)
        data = {
            "ID": int(self.fields["ID"].cget("text")),
            "Nome Progetto": self.fields["Nome Progetto"].cget("text"),
            "ID Progetto": self.fields["ID Progetto"].cget("text"),
            "SU number": int(us_number),
            "Type": self.type_var.get(),
            "Negative": self.negative_var.get(),
            "Area": self.area_var.get(),
            "Preliminary archaeological investigations": self.prelim_var.get(),
            "Sector": self.sector_var.get(),
            "Square": self.square_var.get(),
            "Distinction criteria": self.distinction_var.get(),
            "Organic components": self.organic_var.get(),
            "Inorganic components": self.inorganic_var.get(),
            "Consistency": self.consistency_var.get(),
            "Color": self.color_var.get(),
            "Measures": self.measures_var.get(),
            "Full Relations": {k: v.get() for k, v in self.full_relations_vars.items()},
            "Simplified Relations": {k: v.get() for k, v in self.simplified_relations_vars.items()},
            "Description": self.description_text.get("1.0", tk.END).strip(),
            "Observations": self.observations_text.get("1.0", tk.END).strip(),
            "Interpretations": self.interpretations_text.get("1.0", tk.END).strip(),
            "Cronological context": self.cronological_context_var.get(),
            "Dating": self.dating_var.get(),
            "Dating elements": self.dating_elements_text.get("1.0", tk.END).strip(),
            "Scientific manager": self.fields["Responsabile scientifico"].cget("text"),
            "Report author": self.report_author_var.get(),
            "Date": self.date_var.get(),
            "Custom Fields": {k: v.get() for k, v in self.custom_field_vars.items()}
        }
        os.makedirs("su_report", exist_ok=True)
        if self.existing_data and self.original_filename:
            old_filepath = os.path.join("su_report", self.original_filename)
            if old_filepath != new_filepath:
                if os.path.exists(new_filepath):
                    messagebox.showerror("Errore", f"Un file con il nuovo nome '{new_filename}' esiste già. Scegli un numero SU o un tipo diverso, o elimina il file esistente.")
                    return
                try:
                    os.remove(old_filepath)
                except Exception as e:
                    messagebox.showerror("Errore", f"Impossibile eliminare il vecchio file {self.original_filename}: {e}")
                    return
            save_json_file(new_filepath, data)
            messagebox.showinfo("Salvato", f"Scheda US aggiornata come {new_filename}")
        else:
            if os.path.exists(new_filepath):
                messagebox.showerror("Errore", f"Un file con il nome '{new_filename}' esiste già. Scegli un numero SU o un tipo diverso.")
                return
            save_json_file(new_filepath, data)
            messagebox.showinfo("Salvato", f"Scheda US salvata come {new_filename}")
        self.destroy()

    def populate_fields(self):
        data = self.existing_data
        self.us_number_var.set(data.get("SU number", ""))
        self.type_var.set(data.get("Type", ""))
        self.negative_var.set(data.get("Negative", False))
        self.area_var.set(data.get("Area", ""))
        self.prelim_var.set(data.get("Preliminary archaeological investigations", ""))
        self.sector_var.set(data.get("Sector", ""))
        self.square_var.set(data.get("Square", ""))
        self.distinction_var.set(data.get("Distinction criteria", ""))
        self.organic_var.set(data.get("Organic components", ""))
        self.inorganic_var.set(data.get("Inorganic components", ""))
        self.consistency_var.set(data.get("Consistency", ""))
        self.color_var.set(data.get("Color", ""))
        self.measures_var.set(data.get("Measures", ""))
        for k, var in self.full_relations_vars.items():
            var.set(data.get("Full Relations", {}).get(k, ""))
        for k, var in self.simplified_relations_vars.items():
            var.set(data.get("Simplified Relations", {}).get(k, ""))
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", data.get("Description", "").strip())
        self.observations_text.delete("1.0", tk.END)
        self.observations_text.insert("1.0", data.get("Observations", "").strip())
        self.interpretations_text.delete("1.0", tk.END)
        self.interpretations_text.insert("1.0", data.get("Interpretations", "").strip())
        self.cronological_context_var.set(data.get("Cronological context", ""))
        self.dating_var.set(data.get("Dating", ""))
        self.dating_elements_text.delete("1.0", tk.END)
        self.dating_elements_text.insert("1.0", data.get("Dating elements", "").strip())
        self.report_author_var.set(data.get("Report author", ""))
        self.date_var.set(data.get("Date", ""))
        custom_data_saved = data.get("Custom Fields", {})
        for field_name, var in self.custom_field_vars.items():
            if field_name in custom_data_saved:
                var.set(custom_data_saved[field_name])

SU_LAYOUT_PATH = os.path.join("manager", "su_layout.json")

def load_su_layout():
    return load_json_file(SU_LAYOUT_PATH)

def save_su_layout(layout_data):
    os.makedirs("manager", exist_ok=True)
    save_json_file(SU_LAYOUT_PATH, layout_data)

class RelationViewerDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Matrix di Harris (Visualizzatore)")
        self.geometry("800x600")
        self.resizable(True, True)
        self.all_su_data = self._load_all_su_data()
        self.su_layout_data = load_su_layout()
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(main_frame, bg="white")
        self.h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.selected_item = None
        self.start_x = None
        self.start_y = None
        self.current_su_tag = None
        self._draw_relations()
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5, fill="x", side="bottom")
        ttk.Button(button_frame, text="Salva Layout", command=self.save_current_layout).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Esporta SVG", command=self.export_svg).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Resetta Vista", command=self._draw_relations).pack(side="left", padx=5)

    def _load_all_su_data(self):
        folder = "su_report"
        data = {}
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.lower().endswith(".json"):
                    filepath = os.path.join(folder, filename)
                    su_data = load_json_file(filepath)
                    if su_data:
                        data[os.path.splitext(filename)[0]] = su_data
        return data
    
    def _get_su_display_name(self, su_name):
        return su_name

    def _draw_relations(self):
        self.canvas.delete("all")
        if not self.all_su_data:
            self.canvas.create_text(50, 50, anchor="nw", text="Nessuna scheda US trovata.")
            return
        adj_list = {su: [] for su in self.all_su_data.keys()}
        reverse_adj_list = {su: [] for su in self.all_su_data.keys()}
        for su_name, su_data in self.all_su_data.items():
            simplified_relations = su_data.get("Simplified Relations", {})
            covers_str = simplified_relations.get("Covers", "").strip()
            if covers_str:
                for covered_su in [s.strip() for s in covers_str.split(',') if s.strip()]:
                    if covered_su in self.all_su_data:
                        adj_list[su_name].append(covered_su)
                        reverse_adj_list[covered_su].append(su_name)
            covered_by_str = simplified_relations.get("Covered by", "").strip()
            if covered_by_str:
                for covering_su in [s.strip() for s in covered_by_str.split(',') if s.strip()]:
                    if covering_su in self.all_su_data:
                        adj_list[covering_su].append(su_name)
                        reverse_adj_list[su_name].append(covering_su)
        root_sus = [su for su in self.all_su_data.keys() if not reverse_adj_list[su]]
        if not root_sus and self.all_su_data:
            root_sus = list(self.all_su_data.keys())
            messagebox.showwarning("Attenzione", "Nessuna US radice trovata. Visualizzazione di tutte le unità. La matrice potrebbe essere incompleta o contenere cicli.")
        root_sus.sort(key=lambda x: self.all_su_data[x].get("SU number", 0))
        levels = {}
        queue = []
        for root_su in root_sus:
            if root_su not in levels:
                levels[root_su] = 0
                queue.append(root_su)
        max_level = 0
        head = 0
        while head < len(queue):
            current_su = queue[head]
            head += 1
            max_level = max(max_level, levels.get(current_su, 0))
            for neighbor_su in adj_list.get(current_su, []):
                if neighbor_su not in levels or levels[neighbor_su] < levels[current_su] + 1:
                    levels[neighbor_su] = levels[current_su] + 1
                    queue.append(neighbor_su)
        sus_by_level = {i: [] for i in range(max_level + 1)}
        for su_name, level in levels.items():
            sus_by_level[level].append(su_name)
        for level_num in sus_by_level:
            sus_by_level[level_num].sort(key=lambda x: self.all_su_data[x].get("SU number", 0))
        node_width, node_height, horizontal_spacing, vertical_spacing, padding = 80, 40, 30, 60, 100
        for level_num in range(max_level + 1):
            sus_in_level = sus_by_level.get(level_num, [])
            level_content_width = len(sus_in_level) * (node_width + horizontal_spacing) - horizontal_spacing
            start_x = padding - (level_content_width / 2)
            y_pos = padding + (max_level - level_num) * (node_height + vertical_spacing) + node_height / 2
            current_x = start_x + node_width / 2
            for su_name in sus_in_level:
                if su_name not in self.su_layout_data or len(self.su_layout_data.get(su_name, [])) != 2:
                    self.su_layout_data[su_name] = [current_x - node_width/2, y_pos - node_height/2]
                current_x += (node_width + horizontal_spacing)
        for su_name, pos in self.su_layout_data.items():
            if su_name not in self.all_su_data: continue
            x1, y1 = pos
            x2, y2 = x1 + node_width, y1 + node_height
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#C6F4FA", outline="black", width=1, tags=(su_name, "su_rect"))
            self.canvas.create_text(x1 + node_width / 2, y1 + node_height / 2, text=self._get_su_display_name(su_name), fill="black", font=("Arial", 10, "bold"), tags=(su_name, "su_text"))
        self._redraw_all_lines()
        bbox = self.canvas.bbox("all")
        self.canvas.configure(scrollregion=(bbox[0] - 50, bbox[1] - 50, bbox[2] + 50, bbox[3] + 50) if bbox else (0,0,800,600))

    def on_button_press(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)[0]
        item_tags = self.canvas.gettags(self.selected_item)
        self.current_su_tag = next((tag for tag in item_tags if tag.startswith("US")), None)
        if self.current_su_tag:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            self.canvas.itemconfig(self.canvas.find_withtag(self.current_su_tag + "&&su_rect"), outline="red", width=2)
            self.canvas.tag_raise(self.current_su_tag)

    def on_mouse_drag(self, event):
        if self.current_su_tag:
            dx = self.canvas.canvasx(event.x) - self.start_x
            dy = self.canvas.canvasy(event.y) - self.start_y
            for item_id in self.canvas.find_withtag(self.current_su_tag):
                self.canvas.move(item_id, dx, dy)
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            coords = self.canvas.coords(self.canvas.find_withtag(self.current_su_tag + "&&su_rect"))
            self.su_layout_data[self.current_su_tag] = [coords[0], coords[1]]
            self._redraw_all_lines()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_button_release(self, event):
        if self.current_su_tag:
            self.canvas.itemconfig(self.canvas.find_withtag(self.current_su_tag + "&&su_rect"), outline="black", width=1)
            self.selected_item = self.start_x = self.start_y = self.current_su_tag = None

    def _redraw_all_lines(self):
        self.canvas.delete("relation_line")
        node_width, node_height = 80, 40
        adj_list = {su: [] for su in self.all_su_data.keys()}
        for su_name, su_data in self.all_su_data.items():
            simplified_relations = su_data.get("Simplified Relations", {})
            if covers_str := simplified_relations.get("Covers", "").strip():
                for covered_su in [s.strip() for s in covers_str.split(',') if s.strip()]:
                    if covered_su in self.all_su_data:
                        adj_list[su_name].append(covered_su)
            if covered_by_str := simplified_relations.get("Covered by", "").strip():
                for covering_su in [s.strip() for s in covered_by_str.split(',') if s.strip()]:
                    if covering_su in self.all_su_data:
                        adj_list[covering_su].append(su_name)
        for su_name, children in adj_list.items():
            if su_name not in self.su_layout_data: continue
            p_x_tl, p_y_tl = self.su_layout_data[su_name]
            for child_su_name in children:
                if child_su_name in self.su_layout_data:
                    c_x_tl, c_y_tl = self.su_layout_data[child_su_name]
                    self.canvas.create_line(p_x_tl + node_width / 2, p_y_tl + node_height, c_x_tl + node_width / 2, c_y_tl, arrow=tk.LAST, fill="black", width=1.5, tags=("relation_line", f"line_{su_name}_{child_su_name}"))

    def on_pan_start(self, event): self.canvas.scan_mark(event.x, event.y)
    def on_pan_drag(self, event): self.canvas.scan_dragto(event.x, event.y, gain=1)
    def on_zoom(self, event):
        factor = 1.1 if event.num == 4 or event.delta > 0 else 0.9 if event.num == 5 or event.delta < 0 else 0
        if factor:
            self.canvas.scale("all", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def save_current_layout(self):
        save_su_layout(self.su_layout_data)
        messagebox.showinfo("Layout Salvato", "Le posizioni correnti del layout sono state salvate.")

    def export_svg(self):
        try:
            file_path = simpledialog.askstring("Esporta SVG", "Inserisci nome file (es. matrix.svg):", parent=self)
            if not file_path: return
            if not file_path.lower().endswith(".svg"): file_path += ".svg"
            bbox = self.canvas.bbox("all")
            if not bbox:
                messagebox.showwarning("Esporta SVG", "Canvas vuoto, niente da esportare.")
                return
            x_min, y_min, x_max, y_max = bbox
            width, height = x_max - x_min + 20, y_max - y_min + 20
            svg_content = f'<svg width="{width}" height="{height}" viewBox="{x_min-10} {y_min-10} {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
            svg_content += '<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="black" /></marker></defs>\n'
            for item_id in self.canvas.find_all():
                item_type = self.canvas.type(item_id)
                coords = self.canvas.coords(item_id)
                if item_type == "rectangle":
                    svg_content += f'<rect x="{coords[0]}" y="{coords[1]}" width="{coords[2]-coords[0]}" height="{coords[3]-coords[1]}" fill="{self.canvas.itemcget(item_id, "fill")}" stroke="{self.canvas.itemcget(item_id, "outline")}" stroke-width="{self.canvas.itemcget(item_id, "width")}"/>\n'
                elif item_type == "text":
                    font = tkFont.Font(font=self.canvas.itemcget(item_id, "font"))
                    svg_content += f'<text x="{coords[0]}" y="{coords[1]}" text-anchor="middle" dominant-baseline="central" font-family="{font.actual("family")}" font-size="{font.actual("size")}px" fill="{self.canvas.itemcget(item_id, "fill")}" font-weight="{font.actual("weight")}">{self.canvas.itemcget(item_id, "text")}</text>\n'
                elif item_type == "line" and "relation_line" in self.canvas.gettags(item_id) and len(coords) == 4:
                    svg_content += f'<line x1="{coords[0]}" y1="{coords[1]}" x2="{coords[2]}" y2="{coords[3]}" stroke="{self.canvas.itemcget(item_id, "fill")}" stroke-width="{self.canvas.itemcget(item_id, "width")}" marker-end="url(#arrowhead)"/>\n'
            svg_content += '</svg>'
            with open(file_path, "w", encoding="utf-8") as f: f.write(svg_content)
            messagebox.showinfo("Esportazione Riuscita", f"Matrice esportata in {file_path}")
        except Exception as e:
            messagebox.showerror("Errore Esportazione", f"Impossibile esportare SVG: {e}")

class DiaryEditDialog(tk.Toplevel):
    def __init__(self, master, project_data, existing_data=None, original_filename=None):
        super().__init__(master)
        self.title("Nuova Scheda Diario" if existing_data is None else "Modifica Scheda Diario")
        self.resizable(False, False)
        self.project_data = project_data
        self.existing_data = existing_data
        self.original_filename = original_filename
        self.create_widgets()
        if self.existing_data: self.populate_fields()
        else: self.date_var.set(datetime.date.today().strftime('%Y_%m_%d'))

    def create_widgets(self):
        main_frame = ttk.Frame(self); main_frame.pack(padx=10, pady=10)
        self.entries = {}
        row = 0
        ttk.Label(main_frame, text="Data (YYYY_MM_DD)").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.date_var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.entries["Date"] = self.date_var; row += 1
        ttk.Label(main_frame, text="Giorno della settimana").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.day_of_week_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.day_of_week_var, values=["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"], state="readonly", width=38).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.entries["Day of the week"] = self.day_of_week_var; row +=1
        for key, label_text in {"Operatori": "Operatori", "Indirizzo dei lavori in giornata": "Indirizzo Lavori"}.items():
            ttk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=3)
            self.entries[key] = var; row += 1
        ttk.Label(main_frame, text="US indagate").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        su_frame = ttk.Frame(main_frame); su_frame.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.su_indagate_var = tk.StringVar()
        ttk.Entry(su_frame, textvariable=self.su_indagate_var, width=30).pack(side="left")
        ttk.Button(su_frame, text="...", width=3, command=self.open_su_selection_for_diary).pack(side="left", padx=(3,0))
        self.entries["SU indagate"] = self.su_indagate_var; row += 1
        ttk.Label(main_frame, text="Descrizione").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.description_text = tk.Text(main_frame, width=40, height=5); self.description_text.grid(row=row, column=1, sticky="w", padx=5, pady=3); row += 1
        self.rinvenimenti_var = tk.BooleanVar()
        ttk.Label(main_frame, text="Rinvenimenti archeologici").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        ttk.Checkbutton(main_frame, variable=self.rinvenimenti_var).grid(row=row, column=1, sticky="w", padx=5, pady=3); row += 1
        ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save_diary).grid(row=row, column=0, columnspan=2, pady=10)

    def open_su_selection_for_diary(self):
        dialog = tk.Toplevel(self); dialog.title("Seleziona US Indagate"); dialog.geometry("300x400"); dialog.transient(self); dialog.grab_set()
        ttk.Label(dialog, text="Seleziona una o più US:").pack(pady=5)
        listbox = tk.Listbox(dialog, selectmode="multiple", exportselection=False); listbox.pack(fill="both", expand=True, padx=10, pady=5)
        available_sus = sorted([os.path.splitext(f)[0] for f in list_su_reports()])
        for su_name in available_sus: listbox.insert(tk.END, su_name)
        for i, su_name in enumerate(available_sus):
            if su_name in [s.strip() for s in self.su_indagate_var.get().split(',') if s.strip()]: listbox.selection_set(i)
        def on_ok():
            self.su_indagate_var.set(", ".join([listbox.get(i) for i in listbox.curselection()])); dialog.destroy()
        btn_frame = ttk.Frame(dialog); btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side="left", padx=5)
        self.wait_window(dialog)

    def populate_fields(self):
        for key, var in self.entries.items(): var.set(self.existing_data.get(key, ""))
        self.description_text.delete("1.0", tk.END); self.description_text.insert("1.0", self.existing_data.get("Descrizione", ""))
        self.rinvenimenti_var.set(self.existing_data.get("Rinvenimenti archeologici", False))

    def validate_date(self, date_str):
        try: datetime.datetime.strptime(date_str, '%Y_%m_%d'); return True
        except ValueError: return False

    def save_diary(self):
        date_str = self.date_var.get()
        if not self.validate_date(date_str):
            messagebox.showerror("Data non valida", "La data deve essere in formato YYYY_MM_DD (es. 2025_07_08).")
            return
        new_filename = f"{date_str}.json"
        diary_folder = "diary_usm"
        new_filepath = os.path.join(diary_folder, new_filename)
        if self.original_filename is None and os.path.exists(new_filepath):
            messagebox.showerror("File Esistente", f"Una scheda diario per questa data ({date_str}) esiste già.")
            return
        if self.original_filename and new_filename != self.original_filename and os.path.exists(new_filepath):
            messagebox.showerror("File Esistente", f"Impossibile rinominare in {new_filename} perché un file con quel nome esiste già.")
            return
        data = {"project_name": self.project_data.get("project_name", "N/A"), "project_id": self.project_data.get("project_id", "N/A"), "Descrizione": self.description_text.get("1.0", tk.END).strip(), "Rinvenimenti archeologici": self.rinvenimenti_var.get()}
        for key, var in self.entries.items(): data[key] = var.get()
        save_json_file(new_filepath, data)
        if self.original_filename and new_filename != self.original_filename:
            os.remove(os.path.join(diary_folder, self.original_filename))
        messagebox.showinfo("Successo", f"Scheda diario '{new_filename}' salvata.")
        self.destroy()

class DiaryViewerDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gestore Diario USM")
        self.geometry("750x500")
        self.resizable(True, True)
        self.master = master
        self.diary_folder = "diary_usm"
        os.makedirs(self.diary_folder, exist_ok=True)
        self.create_widgets()
        self.load_diary_files()

    def create_widgets(self):
        main_frame = ttk.Frame(self); main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_rowconfigure(0, weight=1)
        left_frame = ttk.Frame(main_frame); left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 5)); left_frame.grid_rowconfigure(1, weight=1)
        tk.Label(left_frame, text="File Diario Disponibili:").grid(row=0, column=0, pady=5)
        self.file_listbox = tk.Listbox(left_frame, width=30); self.file_listbox.grid(row=1, column=0, sticky="ns")
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.file_listbox.yview); scrollbar.grid(row=1, column=1, sticky="ns"); self.file_listbox.config(yscrollcommand=scrollbar.set)
        button_frame = ttk.Frame(left_frame); button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.new_btn = ttk.Button(button_frame, text="Nuovo", command=self.new_diary); self.new_btn.pack(side="left", padx=2)
        self.edit_btn = ttk.Button(button_frame, text="Modifica", state="disabled", command=self.edit_diary); self.edit_btn.pack(side="left", padx=2)
        self.delete_btn = ttk.Button(button_frame, text="Elimina", state="disabled", command=self.delete_diary); self.delete_btn.pack(side="left", padx=2)
        content_frame = ttk.Frame(main_frame); content_frame.grid(row=0, column=1, sticky="nsew"); content_frame.grid_rowconfigure(1, weight=1); content_frame.grid_columnconfigure(0, weight=1)
        tk.Label(content_frame, text="Contenuto File:").grid(row=0, column=0, pady=5, sticky="w")
        self.content_text = tk.Text(content_frame, wrap="word", state="disabled"); self.content_text.grid(row=1, column=0, sticky="nsew")
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_text.yview); content_scrollbar.grid(row=1, column=1, sticky="ns"); self.content_text.config(yscrollcommand=content_scrollbar.set)

    def on_file_select(self, event=None):
        state = "normal" if self.file_listbox.curselection() else "disabled"
        self.edit_btn.config(state=state); self.delete_btn.config(state=state)
        if state == "normal": self.display_selected_file()
        else: self.content_text.config(state="normal"); self.content_text.delete("1.0", tk.END); self.content_text.config(state="disabled")

    def load_diary_files(self):
        self.file_listbox.delete(0, tk.END)
        try:
            for f in sorted([f for f in os.listdir(self.diary_folder) if f.lower().endswith(".json")], reverse=True): self.file_listbox.insert(tk.END, f)
        except FileNotFoundError: pass
        self.on_file_select()

    def display_selected_file(self):
        if not (selected_index := self.file_listbox.curselection()): return
        filename = self.file_listbox.get(selected_index[0])
        data = load_json_file(os.path.join(self.diary_folder, filename))
        self.content_text.config(state="normal"); self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", json.dumps(data, indent=4, ensure_ascii=False) if data else "Errore nel caricamento del file o file vuoto.")
        self.content_text.config(state="disabled")

    def new_diary(self):
        dialog = DiaryEditDialog(self, project_data=self.master.project_data)
        self.wait_window(dialog); self.load_diary_files(); self.master.refresh_treeview()

    def edit_diary(self):
        if not (selected_index := self.file_listbox.curselection()): return
        filename = self.file_listbox.get(selected_index[0])
        if not (existing_data := load_json_file(os.path.join(self.diary_folder, filename))): return
        dialog = DiaryEditDialog(self, project_data=self.master.project_data, existing_data=existing_data, original_filename=filename)
        self.wait_window(dialog); self.load_diary_files(); self.master.refresh_treeview()

    def delete_diary(self):
        if not (selected_index := self.file_listbox.curselection()): return
        filename = self.file_listbox.get(selected_index[0])
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare permanentemente '{filename}'?"):
            try:
                os.remove(os.path.join(self.diary_folder, filename))
                messagebox.showinfo("Eliminato", f"'{filename}' è stato eliminato.")
                self.load_diary_files(); self.master.refresh_treeview()
            except Exception as e: messagebox.showerror("Errore", f"Impossibile eliminare il file: {e}")

# --- Finds Management (NUOVA SEZIONE) ---

FINDS_FOLDER = "finds_usm"

def get_next_find_id():
    """Genera il prossimo ID progressivo per un reperto (es. 0001)."""
    os.makedirs(FINDS_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(FINDS_FOLDER) if f.lower().endswith(".json")]
    if not files:
        return "0001"
    
    max_id = 0
    for f in files:
        try:
            # L'ID è il nome del file senza estensione
            current_id = int(os.path.splitext(f)[0])
            if current_id > max_id:
                max_id = current_id
        except (ValueError, IndexError):
            continue # Ignora file con nomi non validi
            
    next_id = max_id + 1
    if next_id > 9999:
        messagebox.showwarning("Attenzione", "ID reperto ha superato 9999.")
        return str(next_id)
        
    return f"{next_id:04d}"

class FindEditDialog(tk.Toplevel):
    """Dialogo per la creazione e modifica di una scheda reperto."""
    def __init__(self, master, project_data, existing_data=None, original_filename=None):
        super().__init__(master)
        self.title("Nuova Scheda Reperto" if existing_data is None else "Modifica Scheda Reperto")
        self.resizable(False, False)
        self.project_data = project_data
        self.existing_data = existing_data
        self.original_filename = original_filename
        
        self.create_widgets()
        if self.existing_data:
            self.populate_fields()
        else:
            self.id_var.set(get_next_find_id())
            self.date_var.set(datetime.date.today().strftime('%Y%m%d'))
            self.update_identifier()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=15, pady=15)
        
        self.entries = {}
        row = 0

        ttk.Label(main_frame, text="ID Progressivo:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.id_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.id_var, font=("Arial", 10, "bold")).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text="Nome Progetto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(main_frame, text=self.project_data.get("project_name", "N/A")).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        ttk.Label(main_frame, text="ID Progetto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.project_id_label = ttk.Label(main_frame, text=self.project_data.get("project_id", "N/A"))
        self.project_id_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.tipo_var, values=["Reperto Singolo", "Sacchetto"], state="readonly", width=38)
        tipo_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.entries["Tipo"] = self.tipo_var
        row += 1

        ttk.Label(main_frame, text="Data (AAAAMMDD):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=40)
        date_entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        date_entry.bind("<KeyRelease>", self.update_identifier)
        self.entries["Data"] = self.date_var
        row += 1

        ttk.Label(main_frame, text="Tipologia Reperto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.tipologia_reperto_var = tk.StringVar()
        tipologie = ["ceramica", "concotto", "industria litica", "metallo", "ossa umane", "resti faunistici", "resti botanici", "carbone", "intonaco", "altro"]
        tipologia_combo = ttk.Combobox(main_frame, textvariable=self.tipologia_reperto_var, values=tipologie, state="readonly", width=38)
        tipologia_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        tipologia_combo.bind("<<ComboboxSelected>>", self.update_identifier)
        self.entries["Tipologia Reperto"] = self.tipologia_reperto_var
        row += 1

        ttk.Label(main_frame, text="Identificativo:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.identifier_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.identifier_var, foreground="blue", wraplength=300).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text="Nr. Reperti:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.nr_reperti_var = tk.StringVar()
        nr_reperti_entry = ttk.Entry(main_frame, textvariable=self.nr_reperti_var, width=40)
        nr_reperti_entry.config(validate="key", validatecommand=(self.register(lambda v: v.isdigit() or v == ""), "%P"))
        nr_reperti_entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.entries["Nr Reperti"] = self.nr_reperti_var
        row += 1

        simple_fields = {"Nome area": "Nome Area", "Quadrato": "Quadrato", "Quadrante": "Quadrante"}
        for key, label_text in simple_fields.items():
            ttk.Label(main_frame, text=label_text + ":").grid(row=row, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=3)
            self.entries[key] = var
            row += 1

        ttk.Label(main_frame, text="US di riferimento:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.us_var = tk.StringVar()
        us_options = list_su_reports()
        us_combo = ttk.Combobox(main_frame, textvariable=self.us_var, values=us_options, state="readonly", width=38)
        us_combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.entries["US"] = self.us_var
        row += 1

        ttk.Label(main_frame, text="Descrizione:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.description_text = tk.Text(main_frame, width=40, height=5)
        self.description_text.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        save_button = ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save_find)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

    def update_identifier(self, event=None):
        find_id = self.id_var.get()
        proj_id = self.project_data.get("project_id", "N/A")
        date = self.date_var.get()
        find_type = self.tipologia_reperto_var.get().replace(" ", "-")
        self.identifier_var.set(f"{find_id}_{proj_id}_{date}_{find_type}" if find_id and proj_id and date and find_type else "...")

    def populate_fields(self):
        self.id_var.set(self.existing_data.get("ID", ""))
        for key, var in self.entries.items():
            var.set(self.existing_data.get(key, ""))
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", self.existing_data.get("Descrizione", ""))
        self.update_identifier()

    def save_find(self):
        if not self.tipo_var.get() or not self.date_var.get() or not self.tipologia_reperto_var.get():
            messagebox.showerror("Errore", "I campi 'Tipo', 'Data' e 'Tipologia Reperto' sono obbligatori.")
            return
        
        find_id = self.id_var.get()
        new_filename = f"{find_id}.json"
        filepath = os.path.join(FINDS_FOLDER, new_filename)

        if self.original_filename is None and os.path.exists(filepath):
            messagebox.showerror("Errore", f"Un reperto con ID {find_id} esiste già.")
            return

        data = { "ID": find_id, "Nome Progetto": self.project_data.get("project_name", "N/A"), "ID Progetto": self.project_data.get("project_id", "N/A"), "Identificativo Reperto": self.identifier_var.get(), "Descrizione": self.description_text.get("1.0", tk.END).strip() }
        for key, var in self.entries.items():
            data[key] = var.get()
        
        save_json_file(filepath, data)
        messagebox.showinfo("Successo", f"Scheda reperto '{new_filename}' salvata.")
        self.destroy()

class FindsManagerDialog(tk.Toplevel):
    def __init__(self, master, project_data):
        super().__init__(master)
        self.title("Gestione Reperti")
        self.geometry("800x600")
        self.resizable(True, True)
        self.master = master
        self.project_data = project_data
        os.makedirs(FINDS_FOLDER, exist_ok=True)
        self.create_widgets()
        self.load_finds_files()

    def create_widgets(self):
        main_frame = ttk.Frame(self); main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        button_frame = ttk.Frame(main_frame); button_frame.pack(fill="x", pady=5)
        self.new_btn = ttk.Button(button_frame, text="Nuova Scheda Reperto", command=self.new_find); self.new_btn.pack(side="left", padx=5)
        self.edit_btn = ttk.Button(button_frame, text="Modifica", state="disabled", command=self.edit_find); self.edit_btn.pack(side="left", padx=5)
        self.delete_btn = ttk.Button(button_frame, text="Cancella", state="disabled", command=self.delete_find); self.delete_btn.pack(side="left", padx=5)
        tree_frame = ttk.Frame(main_frame); tree_frame.pack(fill="both", expand=True, pady=5)
        columns = ("ID", "Identificativo", "Data", "Tipo", "Tipologia", "US")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=120, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); scrollbar.pack(side="right", fill="y"); self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event=None):
        state = "normal" if self.tree.selection() else "disabled"
        self.edit_btn.config(state=state); self.delete_btn.config(state=state)

    def load_finds_files(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        files = [f for f in os.listdir(FINDS_FOLDER) if f.lower().endswith(".json")]
        entries = []
        for filename in files:
            if data := load_json_file(os.path.join(FINDS_FOLDER, filename)):
                entries.append((data.get("ID", ""), data.get("Identificativo Reperto", ""), data.get("Data", ""), data.get("Tipo", ""), data.get("Tipologia Reperto", ""), data.get("US", ""), filename))
        entries.sort(key=lambda x: x[0])
        for entry in entries: self.tree.insert("", "end", values=entry[:-1], iid=entry[-1])
        self.on_tree_select()

    def new_find(self):
        dialog = FindEditDialog(self, project_data=self.project_data); self.wait_window(dialog); self.load_finds_files()

    def edit_find(self):
        if not (selected_item_id := self.tree.selection()): return
        filename = selected_item_id[0]
        if existing_data := load_json_file(os.path.join(FINDS_FOLDER, filename)):
            dialog = FindEditDialog(self, project_data=self.project_data, existing_data=existing_data, original_filename=filename)
            self.wait_window(dialog); self.load_finds_files()

    def delete_find(self):
        if not (selected_item_id := self.tree.selection()): return
        filename = selected_item_id[0]
        if messagebox.askyesno("Conferma Cancellazione", f"Sei sicuro di voler eliminare definitivamente '{filename}'?"):
            try: os.remove(os.path.join(FINDS_FOLDER, filename)); messagebox.showinfo("Cancellato", f"'{filename}' è stato cancellato."); self.load_finds_files()
            except Exception as e: messagebox.showerror("Errore", f"Impossibile cancellare il file: {e}")

class USManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USManager")
        self.geometry("950x700")
        self.resizable(True, True)
        style = ttk.Style(self); style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("incomplete", foreground="red"); style.configure("complete", foreground="green")
        style.map("in_diary_yes", background=[("!selected", "#C8E6C9")]); style.map("in_diary_no", background=[("!selected", "#FFCDD2")])
        self.project_data = load_project_data()
        self.create_widgets()
        self.bind("<Return>", self.perform_search)

    def create_widgets(self):
        project_info_frame = tk.Frame(self); project_info_frame.pack(fill="x", pady=5)
        tk.Label(project_info_frame, text=self.project_data.get("project_name", "N/A"), font=tkFont.Font(family="Arial", size=24, weight="bold")).pack(pady=2)
        tk.Label(project_info_frame, text=self.project_data.get("project_id", "N/A"), font=tkFont.Font(family="Arial", size=18)).pack(pady=2)
        buttons_frame = tk.Frame(self); buttons_frame.pack(fill="x", pady=10, padx=5)
        us_actions_frame = ttk.LabelFrame(buttons_frame, text="Azioni US"); us_actions_frame.pack(side="left", padx=5, fill="y")
        ttk.Button(us_actions_frame, text="+ Nuova US", command=self.open_new_card).pack(side="left", padx=5, pady=5)
        self.edit_btn = ttk.Button(us_actions_frame, text="✏ Modifica US", command=self.edit_selected, state="disabled"); self.edit_btn.pack(side="left", padx=5, pady=5)
        self.delete_btn = ttk.Button(us_actions_frame, text="🗑 Cancella US", command=self.delete_selected, state="disabled"); self.delete_btn.pack(side="left", padx=5, pady=5)
        tools_frame = ttk.LabelFrame(buttons_frame, text="Strumenti"); tools_frame.pack(side="left", padx=5, fill="y")
        ttk.Button(tools_frame, text="Matrix di Harris", command=self.open_relation_viewer).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Campi Personalizzati", command=self.open_custom_fields_dialog).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Gestione Diario", command=self.open_diary_viewer).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Gestione Reperti", command=self.open_finds_manager).pack(side="left", padx=5, pady=5)
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=5)
        tk.Label(self, text="Schede US Esistenti").pack()
        
        columns = ("SU", "Nr. Reperti", "Autore", "Data", "Completezza", "Nel diario")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        self.tree.heading("SU", text="SU")
        self.tree.heading("Nr. Reperti", text="Nr. Reperti")
        self.tree.heading("Autore", text="Autore")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Completezza", text="Completezza")
        self.tree.heading("Nel diario", text="Nel diario")
        
        self.tree.column("SU", anchor="center", width=120)
        self.tree.column("Nr. Reperti", anchor="center", width=80)
        self.tree.column("Autore", anchor="center", width=150)
        self.tree.column("Data", anchor="center", width=100)
        self.tree.column("Completezza", anchor="center", width=100)
        self.tree.column("Nel diario", anchor="center", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        bottom_search_frame = tk.Frame(self); bottom_search_frame.pack(side="bottom", fill="x", pady=10)
        self.search_entry = ttk.Entry(bottom_search_frame, width=30); self.search_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)
        ttk.Button(bottom_search_frame, text="Cerca in Descrizione", command=self.perform_search).pack(side="left", padx=5)
        self.refresh_treeview()

    def on_tree_select(self, event):
        state = "normal" if self.tree.selection() else "disabled"
        self.edit_btn.config(state=state); self.delete_btn.config(state=state)
    
    def perform_search(self, event=None): self.refresh_treeview(search_query=self.search_entry.get().strip().lower())

    def open_new_card(self):
        dialog = USCardDialog(self, self.project_data); self.wait_window(dialog); self.refresh_treeview()

    def edit_selected(self):
        if not (selected := self.tree.selection()): return
        filename = self.tree.item(selected[0])["values"][0] + ".json"
        path = os.path.join("su_report", filename)
        if not os.path.exists(path):
            messagebox.showerror("Errore", f"File '{filename}' non trovato.")
            return
        if not (data := load_json_file(path)): return
        dialog = USCardDialog(self, self.project_data, existing_data=data); self.wait_window(dialog); self.refresh_treeview()

    def delete_selected(self):
        if not (selected := self.tree.selection()): return
        filename_display = self.tree.item(selected[0])["values"][0]
        filename = filename_display + ".json"
        path = os.path.join("su_report", filename)
        if not os.path.exists(path):
            messagebox.showerror("Errore", f"File '{filename_display}' non trovato.")
            return
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare '{filename_display}'?"):
            try: os.remove(path); messagebox.showinfo("Eliminato", f"{filename_display} eliminato."); self.refresh_treeview()
            except Exception as e: messagebox.showerror("Errore", f"Eliminazione fallita: {e}")

    def open_relation_viewer(self): dialog = RelationViewerDialog(self); self.wait_window(dialog)
    def open_custom_fields_dialog(self): dialog = CustomFieldsDialog(self, self); self.wait_window(dialog)
    def open_diary_viewer(self): dialog = DiaryViewerDialog(self); self.wait_window(dialog)
    def open_finds_manager(self):
        dialog = FindsManagerDialog(self, self.project_data); dialog.transient(self); dialog.grab_set(); self.wait_window(dialog)

    def _get_finds_count_per_su(self):
        """Calcola il numero totale di reperti per ogni US."""
        su_finds_count = {}
        if not os.path.exists(FINDS_FOLDER):
            return su_finds_count
        
        for filename in os.listdir(FINDS_FOLDER):
            if filename.lower().endswith(".json"):
                find_data = load_json_file(os.path.join(FINDS_FOLDER, filename))
                if find_data and (us_name := find_data.get("US")):
                    try:
                        num_items = int(find_data.get("Nr Reperti", 1))
                    except (ValueError, TypeError):
                        num_items = 1
                    
                    su_finds_count[us_name] = su_finds_count.get(us_name, 0) + num_items
        return su_finds_count

    def _get_in_diary_su_numbers(self):
        diary_folder, in_diary_sus = "diary_usm", set()
        if os.path.exists(diary_folder):
            for filename in os.listdir(diary_folder):
                if filename.lower().endswith(".json"):
                    if (diary_data := load_json_file(os.path.join(diary_folder, filename))) and "SU indagate" in diary_data:
                        for su_entry in diary_data["SU indagate"].split(','):
                            try:
                                if (su_num_str := ''.join(filter(str.isdigit, su_entry.strip()))): in_diary_sus.add(int(su_num_str))
                            except ValueError: pass
        return in_diary_sus

    def refresh_treeview(self, search_query=None):
        for row in self.tree.get_children(): self.tree.delete(row)
        
        finds_count = self._get_finds_count_per_su()
        entries, in_diary_su_numbers = [], self._get_in_diary_su_numbers()
        
        for filename in list_su_reports():
            path = os.path.join("su_report", filename + ".json")
            if data := load_json_file(path):
                desc = data.get("Description", "").strip(); obs = data.get("Observations", "").strip(); interp = data.get("Interpretations", "").strip()
                if search_query and search_query not in (desc + " " + obs + " " + interp).lower(): continue
                
                simp = data.get("Simplified Relations", {})
                is_incomplete = (not simp.get("Covers", "").strip() and not simp.get("Covered by", "").strip()) or not desc or not obs or not interp
                su_number = data.get("SU number", 0)
                is_in_diary = su_number in in_diary_su_numbers
                num_reperti = finds_count.get(filename, 0)

                entries.append((
                    su_number, 
                    filename, 
                    num_reperti,
                    data.get("Report author", ""), 
                    data.get("Date", ""), 
                    "Incompleta" if is_incomplete else "Completa", 
                    "Sì" if is_in_diary else "No", 
                    "incomplete" if is_incomplete else "complete", 
                    "in_diary_yes" if is_in_diary else "in_diary_no"
                ))

        entries.sort(key=lambda x: x[0])
        
        for _, name, num_reperti, author, date, completeness, in_diary, comp_tag, diary_tag in entries:
            self.tree.insert("", "end", values=(name, num_reperti, author, date, completeness, in_diary), tags=(comp_tag, diary_tag))

if __name__ == "__main__":
    if ensure_project_file():
        os.makedirs("su_report", exist_ok=True)
        os.makedirs("manager", exist_ok=True)
        os.makedirs("diary_usm", exist_ok=True)
        os.makedirs("finds_usm", exist_ok=True)
        if not os.path.exists(CUSTOM_FIELDS_PATH):
            save_json_file(CUSTOM_FIELDS_PATH, [])
        app = USManagerApp()
        app.mainloop()
