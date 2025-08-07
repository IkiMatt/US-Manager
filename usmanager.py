import tkinter as tk
import os
from tkinter import simpledialog, messagebox, colorchooser, filedialog
from tkinter import ttk
import json
from tkinter import BooleanVar
import ast  # Per ast.literal_eval
import tkinter.font as tkFont  # Importa tkinter.font
import datetime
import math
import io
import subprocess # Per aprire file con il programma predefinito

# Prova a importare Pillow (PIL). Se non è installato, la funzione di esportazione PNG sarà disabilitata.
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
    # NOTA: Per l'esportazione PNG/JPG su Windows, potrebbe essere necessario specificare il percorso di Ghostscript
    # Ad esempio, da PIL 9.2.0 non è più necessario ma se si usano versioni precedenti:
    # from PIL import EpsImagePlugin
    # EpsImagePlugin.gs_windows_binary = r'C:\\Program Files\\gs\\\\gs10.03.1\\\\bin\\\\gswin64c'
except ImportError:
    PIL_AVAILABLE = False


# --- Funzioni di Utilità ---
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

        # Applica uno stile al frame
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

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
            ttk.Label(main_frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            if typ == "year":
                entry = ttk.Entry(main_frame, width=10)
                entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
                entry.config(validate="key", validatecommand=(self.register(self.validate_year), "%P"))
            else:
                entry = ttk.Entry(main_frame, width=30)
                entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            self.entries[label] = entry

        # Configura la colonna 1 per espandersi
        main_frame.grid_columnconfigure(1, weight=1)

        save_btn = ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save, style="Accent.TButton")
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=15)

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
        
        # Ensure self.custom_fields is a list
        if not isinstance(self.custom_fields, list):
            self.custom_fields = []

        self.create_widgets()
        self.populate_list()

    def create_widgets(self):
        # Frame principale con padding
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Nuovo Campo Personalizzato", padding="10")
        input_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(input_frame, text="Nome Campo:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.field_name_entry = ttk.Entry(input_frame, width=30)
        self.field_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.field_type_var = tk.StringVar()
        self.field_type_combobox = ttk.Combobox(input_frame, textvariable=self.field_type_var, 
                                                 values=["Testo", "Numerico", "Dropdown", "Checkbox"],
                                                 state="readonly", width=27)
        self.field_type_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.field_type_combobox.bind("<<ComboboxSelected>>", self._on_type_selected)

        self.dropdown_options_label = ttk.Label(input_frame, text="Opzioni (se Dropdown, separate da virgola):")
        self.dropdown_options_entry = ttk.Entry(input_frame, width=30)

        self.add_button = ttk.Button(input_frame, text="Aggiungi Campo", command=self.add_field, style="Accent.TButton")
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(main_frame, text="Campi Esistenti", padding="10")
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
        # Bind for selection to enable/disable delete button
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.delete_button = ttk.Button(main_frame, text="Elimina Campo Selezionato", command=self.delete_field, state="disabled", style="Danger.TButton")
        self.delete_button.pack(pady=10)
        
        self._on_type_selected()

    def on_tree_select(self, event=None):
        """Enable/disable delete button based on treeview selection."""
        if self.tree.selection():
            self.delete_button.config(state="normal")
        else:
            self.delete_button.config(state="disabled")

    def _on_type_selected(self, event=None):
        if self.field_type_var.get() == "Dropdown":
            self.dropdown_options_label.grid(row=3, column=0, padx=5, pady=2, sticky="e")
            self.dropdown_options_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
            self.add_button.grid(row=4, column=0, columnspan=2, pady=10)
        else:
            self.dropdown_options_label.grid_forget()
            self.dropdown_options_entry.grid_forget()
            self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

    def populate_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for field in self.custom_fields:
            name = field["name"]
            field_type = field["type"]
            self.tree.insert("", "end", values=(name, field_type))
        self.on_tree_select() # Update button state after populating

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
        
        # Refresh the main treeview to reflect potential changes in completeness tags
        self.app_instance.refresh_treeview()

class USCardDialog(tk.Toplevel):
    def __init__(self, master, project_data, existing_data=None):
        super().__init__(master)
        self.title("Nuova Scheda US" if existing_data is None else "Modifica Scheda US")
        self.resizable(False, False)
        self.project_data = project_data
        # Ensure existing_data is always a dictionary
        self.existing_data = existing_data if existing_data is not None else {}
        self.original_filename = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        tab1 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab1, text="Dati Iniziali")
        row = 0
        self.fields = {}
        ttk.Label(tab1, text="ID:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        display_id = str(self.existing_data.get("ID", get_next_id())) if self.existing_data else str(get_next_id())
        self.fields["ID"] = ttk.Label(tab1, text=display_id, font=("Arial", 10, "bold"))
        self.fields["ID"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        ttk.Label(tab1, text="Nome Progetto:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.fields["Nome Progetto"] = ttk.Label(tab1, text=project_data.get("nome_progetto", ""))
        self.fields["Nome Progetto"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        ttk.Label(tab1, text="ID Progetto:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.fields["ID Progetto"] = ttk.Label(tab1, text=project_data.get("id_progetto", ""))
        self.fields["ID Progetto"].grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        ttk.Label(tab1, text="Numero US:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.us_number_var = tk.StringVar()
        entry_us_num = ttk.Entry(tab1, textvariable=self.us_number_var)
        entry_us_num.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        entry_us_num.config(validate="key", validatecommand=(self.register(self.validate_integer_input), "%P"))
        row += 1
        ttk.Label(tab1, text="Tipo:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.type_var = tk.StringVar()
        type_options = ["SU", "SU Muraria", "SU Rivestimento", "SU Documentaria", "SU Virtuale strutturale", "SU Virtuale non strutturale"]
        ttk.Combobox(tab1, textvariable=self.type_var, values=type_options, state="readonly").grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        ttk.Label(tab1, text="Negativa:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.negative_var = BooleanVar()
        ttk.Checkbutton(tab1, variable=self.negative_var).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        ttk.Label(tab1, text="Area:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.area_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.area_var).grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        ttk.Label(tab1, text="Indagini archeologiche preliminari:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.prelim_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.prelim_var).grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        ttk.Label(tab1, text="Settore:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.sector_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.sector_var).grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        ttk.Label(tab1, text="Quadrato:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.square_var = tk.StringVar()
        ttk.Entry(tab1, textvariable=self.square_var).grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        tab1.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        tab2 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab2, text="Contenuto")
        row2 = 0
        ttk.Label(tab2, text="Criteri di distinzione:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.distinction_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.distinction_var).grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        row2 += 1
        ttk.Label(tab2, text="Componenti organiche:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.organic_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.organic_var).grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        row2 += 1
        ttk.Label(tab2, text="Componenti inorganiche:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.inorganic_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.inorganic_var).grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        row2 += 1
        ttk.Label(tab2, text="Consistenza:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.consistency_var = tk.StringVar()
        ttk.Combobox(tab2, textvariable=self.consistency_var, values=[str(i) for i in range(1,6)], state="readonly").grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        row2 += 1
        ttk.Label(tab2, text="Colore:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.color_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.color_var).grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        row2 += 1
        ttk.Label(tab2, text="Misure:").grid(row=row2, column=0, sticky="e", padx=5, pady=2)
        self.measures_var = tk.StringVar()
        ttk.Entry(tab2, textvariable=self.measures_var).grid(row=row2, column=1, padx=5, pady=2, sticky="ew")
        tab2.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        tab3 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab3, text="Rapporti")
        tab3.grid_columnconfigure(0, weight=1)
        tab3.grid_columnconfigure(1, weight=1)

        full_frame = ttk.LabelFrame(tab3, text="Rapporti Completi", padding="10")
        full_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        full_frame.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        full_fields = ["Copre (US separate da virgola)", "Coperto da (US separate da virgola)", "Uguale a (US separate da virgola)", "Si lega a (US separate da virgola)", "Si appoggia a (US separate da virgola)", "Taglia (US separate da virgola)", "Tagliato da (US separate da virgola)", "Riempie (US separate da virgola)", "Riempito da (US separate da virgola)"]
        self.full_relations_vars = {}
        for i, label in enumerate(full_fields):
            ttk.Label(full_frame, text=label).grid(row=i, column=0, sticky="e", padx=3, pady=2)
            var = tk.StringVar()
            ttk.Entry(full_frame, textvariable=var, width=30).grid(row=i, column=1, padx=3, pady=2, sticky="ew")
            self.full_relations_vars[label] = var
        
        simple_frame = ttk.LabelFrame(tab3, text="Rapporti Semplificati", padding="10")
        simple_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        simple_frame.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        simple_fields = [("Copre (US multiple)", "Copre"), ("Coperto da (US multiple)", "Coperto da")]
        self.simplified_relations_vars = {}
        for i, (label, key) in enumerate(simple_fields):
            ttk.Label(simple_frame, text=label).grid(row=i, column=0, sticky="e", padx=3, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(simple_frame, textvariable=var, width=28)
            entry.grid(row=i, column=1, padx=3, pady=2, sticky="ew")
            self.simplified_relations_vars[key] = var
            select_btn = ttk.Button(simple_frame, text="...", width=3, command=lambda v=var: self.open_su_selection_dialog(v))
            select_btn.grid(row=i, column=2, padx=(0, 3), pady=2, sticky="w")

        tab4 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab4, text="Osservazioni")
        tab4.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        ttk.Label(tab4, text="Descrizione:").grid(row=0, column=0, sticky="ne", padx=5, pady=2)
        self.description_text = tk.Text(tab4, height=2.5, width=40)
        self.description_text.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        row_obs = 1
        ttk.Label(tab4, text="Osservazioni:").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.observations_text = tk.Text(tab4, height=2.5, width=40)
        self.observations_text.grid(row=row_obs, column=1, padx=5, pady=2, sticky="ew")
        row_obs += 1
        ttk.Label(tab4, text="Interpretazioni:").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.interpretations_text = tk.Text(tab4, height=2.5, width=40)
        self.interpretations_text.grid(row=row_obs, column=1, padx=5, pady=2, sticky="ew")
        row_obs += 1
        ttk.Label(tab4, text="Contesto cronologico:").grid(row=row_obs, column=0, sticky="e", padx=5, pady=2)
        self.cronological_context_var = tk.StringVar()
        ttk.Entry(tab4, textvariable=self.cronological_context_var).grid(row=row_obs, column=1, padx=5, pady=2, sticky="ew")
        row_obs += 1
        ttk.Label(tab4, text="Datazione:").grid(row=row_obs, column=0, sticky="e", padx=5, pady=2)
        self.dating_var = tk.StringVar()
        ttk.Entry(tab4, textvariable=self.dating_var).grid(row=row_obs, column=1, padx=5, pady=2, sticky="ew")
        row_obs += 1
        ttk.Label(tab4, text="Elementi di datazione:").grid(row=row_obs, column=0, sticky="ne", padx=5, pady=2)
        self.dating_elements_text = tk.Text(tab4, height=2.5, width=40)
        self.dating_elements_text.grid(row=row_obs, column=1, padx=5, pady=2, sticky="ew")
        row_obs += 1

        tab5 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab5, text="Autore")
        tab5.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        row_tab5 = 0
        ttk.Label(tab5, text="Responsabile scientifico:").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.fields["Responsabile scientifico"] = ttk.Label(tab5, text=project_data.get("responsabile_scientifico", "")) # Corrected typo in key
        self.fields["Responsabile scientifico"].grid(row=row_tab5, column=1, sticky="w", padx=5, pady=2)
        row_tab5 += 1
        ttk.Label(tab5, text="Autore scheda:").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.report_author_var = tk.StringVar()
        ttk.Entry(tab5, textvariable=self.report_author_var).grid(row=row_tab5, column=1, padx=5, pady=2, sticky="ew")
        row_tab5 += 1
        ttk.Label(tab5, text="Data:").grid(row=row_tab5, column=0, sticky="e", padx=5, pady=2)
        self.date_var = tk.StringVar()
        ttk.Entry(tab5, textvariable=self.date_var).grid(row=row_tab5, column=1, padx=5, pady=2, sticky="ew")
        row_tab5 += 1

        # Nuovo Tab per le Foto
        tab6 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab6, text="Foto")
        tab6.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input
        row_photo = 0
        ttk.Label(tab6, text="Percorso Foto:").grid(row=row_photo, column=0, sticky="e", padx=5, pady=2)
        self.photo_path_var = tk.StringVar()
        self.photo_path_entry = ttk.Entry(tab6, textvariable=self.photo_path_var, width=40)
        self.photo_path_entry.grid(row=row_photo, column=1, padx=5, pady=2, sticky="ew")
        self.browse_photo_btn = ttk.Button(tab6, text="Sfoglia...", command=self.browse_photo)
        self.browse_photo_btn.grid(row=row_photo, column=2, padx=5, pady=2)
        row_photo += 1
        self.open_photo_btn = ttk.Button(tab6, text="Apri Foto", command=self.open_photo, state="disabled")
        self.open_photo_btn.grid(row=row_photo, column=1, columnspan=2, pady=5)
        # Bind per abilitare/disabilitare il pulsante "Apri Foto"
        self.photo_path_var.trace_add("write", self._update_open_photo_button_state)


        self.custom_fields_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.custom_fields_tab, text="Campi Personalizzati")
        self.custom_fields_tab.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input
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

        self.save_btn = ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save_card, style="Accent.TButton")
        self.save_btn.pack(pady=10)
        
        # Aggiorna lo stato del pulsante "Apri Foto" all'avvio
        self._update_open_photo_button_state()


    def validate_integer_input(self, value):
        return value.isdigit() or value == ""
        
    def _load_and_create_custom_fields(self):
        custom_fields_data = load_custom_fields()
        current_row = 0
        for field_def in custom_fields_data:
            field_name = field_def["name"]
            field_type = field_def["type"]
            ttk.Label(self.custom_fields_tab, text=field_name + ":").grid(row=current_row, column=0, sticky="e", padx=5, pady=2)
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
        
        dialog_frame = ttk.Frame(dialog, padding="10")
        dialog_frame.pack(fill="both", expand=True)

        ttk.Label(dialog_frame, text="Seleziona una o più US:").pack(pady=5)
        
        listbox_frame = ttk.Frame(dialog_frame)
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)

        listbox = tk.Listbox(listbox_frame, selectmode="multiple", exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        listbox.config(yscrollcommand=scrollbar.set)

        available_sus = list_su_reports(exclude_filename=self.original_filename)
        
        # Populate listbox and pre-select current values
        current_selection_list = [s.strip() for s in target_entry_var.get().split(',') if s.strip()]
        for i, su_display_name in enumerate(available_sus):
            listbox.insert(tk.END, su_display_name)
            if su_display_name in current_selection_list:
                listbox.selection_set(i)

        def on_ok():
            selected_indices = listbox.curselection()
            selected_sus = [listbox.get(i) for i in selected_indices]
            target_entry_var.set(", ".join(selected_sus))
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=on_ok, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side="left", padx=5)
        
        self.wait_window(dialog)

    def browse_photo(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona Immagine",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.photo_path_var.set(file_path)

    def open_photo(self):
        photo_path = self.photo_path_var.get()
        if photo_path and os.path.exists(photo_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(photo_path)
                elif os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', photo_path])
                else:  # Linux
                    subprocess.run(['xdg-open', photo_path])
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire la foto: {e}")
        else:
            messagebox.showwarning("Avviso", "Nessun percorso foto valido specificato o file non trovato.")

    def _update_open_photo_button_state(self, *args):
        if self.photo_path_var.get():
            self.open_photo_btn.config(state="normal")
        else:
            self.open_photo_btn.config(state="disabled")

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
            "Photo Path": self.photo_path_var.get(), # Salva il percorso della foto
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
        self.photo_path_var.set(data.get("Photo Path", "")) # Carica il percorso della foto
        custom_data_saved = data.get("Custom Fields", {})
        for field_name, var in self.custom_field_vars.items():
            if field_name in custom_data_saved:
                var.set(custom_data_saved[field_name])

class USCardViewerDialog(USCardDialog):
    """
    A non-editable viewer for US cards.
    Inherits from USCardDialog and disables all input fields.
    """
    def __init__(self, master, project_data, existing_data=None):
        super().__init__(master, project_data, existing_data)
        self.title("Visualizzazione Scheda US")
        
        # Disable all input widgets
        # Iterare su tutti i widget e disabilitarli, escludendo i Label
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame): # Notebook è un frame
                for tab_frame in widget.winfo_children(): # I tab sono frame
                    if isinstance(tab_frame, ttk.Frame):
                        for sub_widget in tab_frame.winfo_children():
                            if isinstance(sub_widget, (ttk.Entry, ttk.Combobox, ttk.Checkbutton, tk.Text, ttk.Button)):
                                try:
                                    sub_widget.config(state="disabled")
                                except tk.TclError: # Alcuni widget potrebbero non avere lo stato
                                    pass
            elif isinstance(widget, ttk.Button): # Il pulsante Salva principale
                widget.config(state="disabled")

        # Rimuovi o disabilita il pulsante salva (già fatto sopra, ma per sicurezza)
        if hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
            self.save_btn.destroy()

SU_LAYOUT_PATH = os.path.join("manager", "su_layout.json")

def load_su_layout():
    return load_json_file(SU_LAYOUT_PATH)

def save_su_layout(layout_data):
    os.makedirs("manager", exist_ok=True)
    save_json_file(SU_LAYOUT_PATH, layout_data)

class RelationViewerDialog(tk.Toplevel):
    def __init__(self, master, project_data):
        super().__init__(master)
        self.master_app = master  # Riferimento alla finestra principale
        self.project_data = project_data
        self.title("Matrix di Harris (Visualizzatore Migliorato)")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Dati
        self.all_su_data = self._load_all_su_data()
        self.su_layout_data = load_su_layout()
        self.tooltip = None
        self.tooltip_text = tk.StringVar()

        # Colori e stili
        self.COLORS = {
            "default": "#C6F4FA",
            "negative": "#FFCDD2",
            "muraria": "#E0E0E0",
            "virtuale": "#B2EBF2",
            "highlight": "red",
            "cycle_edge_color": "black", # Colore per le frecce dei cicli
            "normal_edge_color": "red"   # Colore per le frecce normali
        }

        # Variabili di stato
        self.selected_item = None
        self.start_x = None
        self.start_y = None
        self.current_su_tag = None

        self._create_widgets()
        self._apply_filters_and_redraw()

    def _create_widgets(self):
        # Frame principale con padding
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=5)

        # --- Filtri ---
        filter_frame = ttk.LabelFrame(top_frame, text="Filtri", padding="10")
        filter_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        ttk.Label(filter_frame, text="Tipo US:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.filter_type_var = tk.StringVar(value="Tutti")
        us_types = ["Tutti", "SU", "SU Muraria", "SU Rivestimento", "SU Documentaria", "SU Virtuale strutturale", "SU Virtuale non strutturale"]
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=us_types, state="readonly").grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Area:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.filter_area_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_area_var).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="Settore:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.filter_sector_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_sector_var).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Datazione:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.filter_dating_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_dating_var).grid(row=1, column=3, padx=5, pady=2)

        ttk.Button(filter_frame, text="Applica Filtri", command=self._apply_filters_and_redraw, style="Accent.TButton").grid(row=0, column=4, rowspan=2, padx=10, pady=5)
        ttk.Button(filter_frame, text="Resetta Filtri", command=self._reset_filters).grid(row=0, column=5, rowspan=2, padx=10, pady=5)

        # --- Canvas e Scrollbar ---
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightbackground="gray", highlightthickness=1) # Aggiungi bordo
        self.h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # --- Binding Eventi ---
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start) # Pan con tasto centrale
        self.canvas.bind("<B2-Motion>", self.on_pan_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom) # Zoom con rotellina
        self.canvas.bind("<Button-4>", self.on_zoom) # Zoom su Linux
        self.canvas.bind("<Button-5>", self.on_zoom)

        # --- Pulsanti Azione ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill="x", side="bottom")
        ttk.Button(button_frame, text="Salva Layout", command=self.save_current_layout).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Esporta SVG", command=self.export_svg).pack(side="left", padx=5)
        if PIL_AVAILABLE:
            ttk.Button(button_frame, text="Esporta PNG", command=lambda: self.export_image('png')).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Resetta Vista", command=self._apply_filters_and_redraw).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Controlla Coerenza", command=self.check_consistency).pack(side="left", padx=5)

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

    def _apply_filters_and_redraw(self):
        """Filtra i dati e ridisegna il canvas."""
        self.filtered_su_data = {}
        type_filter = self.filter_type_var.get()
        area_filter = self.filter_area_var.get().lower()
        sector_filter = self.filter_sector_var.get().lower()
        dating_filter = self.filter_dating_var.get().lower()

        for name, data in self.all_su_data.items():
            if type_filter != "Tutti" and data.get("Type") != type_filter:
                continue
            if area_filter and area_filter not in data.get("Area", "").lower():
                continue
            if sector_filter and sector_filter not in data.get("Sector", "").lower():
                continue
            if dating_filter and dating_filter not in data.get("Dating", "").lower():
                continue
            self.filtered_su_data[name] = data
        
        self._draw_relations()
    
    def _reset_filters(self):
        """Resetta i campi dei filtri e ridisegna."""
        self.filter_type_var.set("Tutti")
        self.filter_area_var.set("")
        self.filter_sector_var.set("")
        self.filter_dating_var.set("")
        self._apply_filters_and_redraw()

    def _get_node_color(self, su_data):
        """Restituisce il colore del nodo in base al tipo di US."""
        if su_data.get("Negative"):
            return self.COLORS["negative"]
        su_type = su_data.get("Type", "")
        if "Muraria" in su_type:
            return self.COLORS["muraria"]
        if "Virtuale" in su_type:
            return self.COLORS["virtuale"]
        return self.COLORS["default"]

    def _draw_legend(self):
        """Disegna la legenda fissa in basso a destra, non soggetta a zoom/pan."""
        self.canvas.delete("legend")  # Rimuove la vecchia legenda

        legend_width = 165
        legend_height = 100
        padding = 20

        # Usa le dimensioni del widget canvas, non le coordinate del mondo
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calcola la posizione in basso a destra in coordinate della finestra
        start_x_win = canvas_width - legend_width - padding
        start_y_win = canvas_height - legend_height - padding

        # Converte le coordinate della finestra in coordinate del canvas (mondo)
        # Questo assicura che la legenda si muova correttamente con il pan
        final_x = self.canvas.canvasx(start_x_win)
        final_y = self.canvas.canvasy(start_y_win)

        legend_items = {
            "US Negativa": self.COLORS["negative"],
            "US Muraria": self.COLORS["muraria"],
            "US Virtuale": self.COLORS["virtuale"],
            "Altra US": self.COLORS["default"],
        }
        box_size = 15
        
        # Disegna il contenitore della legenda
        self.canvas.create_rectangle(final_x - 5, final_y - 5,
                                     final_x + legend_width, final_y + legend_height,
                                     fill="white", outline="black", tags="legend")

        y = final_y
        for text, color in legend_items.items():
            self.canvas.create_rectangle(final_x, y, final_x + box_size, y + box_size, fill=color, outline="black", tags="legend")
            self.canvas.create_text(final_x + box_size + 5, y + box_size / 2, text=text, anchor="w", tags="legend", font=("Arial", 9))
            y += box_size + 5
        
        # Assicura che la legenda sia sempre in primo piano
        self.canvas.tag_raise("legend")

    def _sugiyama_layout(self, adj, reverse_adj, roots):
        """Implementazione semplificata dell'algoritmo di layout di Sugiyama."""
        # 1. Assegnazione livelli (Longest path layering)
        levels = {}
        queue = list(roots)
        for node in queue:
            levels[node] = 0
        
        visited_for_leveling = set(roots)
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            for v in adj.get(u, []):
                if v not in levels or levels[v] < levels[u] + 1:
                    levels[v] = levels[u] + 1
                    if v not in visited_for_leveling:
                        queue.append(v)
                        visited_for_leveling.add(v)

        # Gestione nodi non raggiungibili dalle radici
        for node in self.filtered_su_data:
            if node not in levels:
                levels[node] = 0 # Li mettiamo al livello 0

        max_level = max(levels.values()) if levels else 0
        nodes_by_level = [[] for _ in range(max_level + 1)]
        for node, level in levels.items():
            nodes_by_level[level].append(node)

        # 2. Riduzione incroci (Barycenter heuristic)
        # Inizializza le posizioni
        pos = {node: i for i, node in enumerate(nodes_by_level[0])}
        
        for _ in range(5): # Iterazioni per stabilizzare
            # Down-sweep
            for i in range(1, max_level + 1):
                barycenters = {}
                for u in nodes_by_level[i]:
                    parent_positions = [pos.get(p, 0) for p in reverse_adj.get(u, []) if p in pos]
                    barycenters[u] = sum(parent_positions) / len(parent_positions) if parent_positions else 0
                nodes_by_level[i].sort(key=lambda u: barycenters[u])
                for j, u in enumerate(nodes_by_level[i]):
                    pos[u] = j
            # Up-sweep
            for i in range(max_level - 1, -1, -1):
                barycenters = {}
                for u in nodes_by_level[i]:
                    child_positions = [pos.get(c, 0) for c in adj.get(u, []) if c in pos]
                    barycenters[u] = sum(child_positions) / len(child_positions) if child_positions else 0
                nodes_by_level[i].sort(key=lambda u: barycenters[u])
                for j, u in enumerate(nodes_by_level[i]):
                    pos[u] = j

        return nodes_by_level

    def _draw_relations(self):
        """Disegna l'intera matrice sul canvas."""
        self.canvas.delete("all")
        if not self.filtered_su_data:
            self.canvas.create_text(50, 50, anchor="nw", text="Nessuna scheda US trovata o corrispondente ai filtri.")
            return

        # Costruzione liste di adiacenza
        adj = {su: [] for su in self.filtered_su_data}
        reverse_adj = {su: [] for su in self.filtered_su_data}
        self.cycles = set()

        for su_name, su_data in self.filtered_su_data.items():
            relations = su_data.get("Simplified Relations", {})
            
            # "Copre" (A copre B, freccia da A a B)
            covers_str = relations.get("Copre", "").strip()
            if covers_str:
                for covered_su in [s.strip() for s in covers_str.split(',') if s.strip()]:
                    if covered_su in self.filtered_su_data:
                        adj[su_name].append(covered_su) # Freccia da su_name a covered_su
                        reverse_adj[covered_su].append(su_name)
                        # Controllo ciclo diretto
                        if su_name in adj.get(covered_su, []):
                            self.cycles.add(tuple(sorted((su_name, covered_su))))
            
            # "Coperto da" (A è coperto da B, freccia da B ad A)
            covered_by_str = relations.get("Coperto da", "").strip()
            if covered_by_str:
                for covering_su in [s.strip() for s in covered_by_str.split(',') if s.strip()]:
                    if covering_su in self.filtered_su_data:
                        adj[covering_su].append(su_name) # Freccia da covering_su a su_name
                        reverse_adj[su_name].append(covering_su)
                        # Controllo ciclo diretto
                        if su_name in adj.get(covering_su, []):
                            self.cycles.add(tuple(sorted((su_name, covering_su))))

        # Trova radici (nodi senza predecessori)
        roots = [su for su in self.filtered_su_data if not reverse_adj.get(su)]
        if not roots and self.filtered_su_data:
            # Fallback: usa tutti i nodi come possibili radici se ci sono cicli o componenti disconnesse
            roots = sorted(list(self.filtered_su_data.keys()))
        
        # Layout
        nodes_by_level = self._sugiyama_layout(adj, reverse_adj, roots)

        # Disegno nodi
        node_width, node_height, h_spacing, v_spacing, padding = 80, 40, 40, 60, 50
        max_level_width = max(len(level) for level in nodes_by_level) if nodes_by_level else 0
        canvas_width = max_level_width * (node_width + h_spacing) + 2 * padding
        
        node_positions = {}
        for level_idx, level_nodes in enumerate(nodes_by_level):
            level_width = len(level_nodes) * (node_width + h_spacing)
            start_x = (canvas_width - level_width) / 2
            y_pos = padding + level_idx * (node_height + v_spacing)
            for node_idx, su_name in enumerate(level_nodes):
                x_pos = start_x + node_idx * (node_width + h_spacing)
                node_positions[su_name] = (x_pos, y_pos)

        for su_name, pos in node_positions.items():
            x1, y1 = pos
            x2, y2 = x1 + node_width, y1 + node_height
            color = self._get_node_color(self.filtered_su_data[su_name])
            rect_tag = f"rect_{su_name}"
            text_tag = f"text_{su_name}"
            
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1.5, tags=(su_name, "su_node", rect_tag, "graph_element"))
            text = self.canvas.create_text(x1 + node_width / 2, y1 + node_height / 2, text=su_name, fill="black", font=("Arial", 10, "bold"), tags=(su_name, "su_node", text_tag, "graph_element"))
            
            # Binding per tooltip
            self.canvas.tag_bind(rect, "<Enter>", lambda e, s=su_name: self.show_tooltip(e, s))
            self.canvas.tag_bind(rect, "<Leave>", self.hide_tooltip)
            self.canvas.tag_bind(text, "<Enter>", lambda e, s=su_name: self.show_tooltip(e, s))
            self.canvas.tag_bind(text, "<Leave>", self.hide_tooltip)
        
        self.node_positions = node_positions
        self._draw_all_lines(adj)
        
        bbox = self.canvas.bbox("graph_element")
        if bbox:
            self.canvas.configure(scrollregion=(bbox[0] - 50, bbox[1] - 50, bbox[2] + 50, bbox[3] + 50))
        else:
            self.canvas.configure(scrollregion=(0,0,1200,800))
        
        self.after(100, self._draw_legend) # Disegna la legenda dopo un breve ritardo per assicurarsi che il canvas abbia le dimensioni corrette

    def _draw_all_lines(self, adj_list):
        """Disegna tutte le linee di relazione."""
        self.canvas.delete("relation_line")
        node_width, node_height = 80, 40
        
        for su_name, children in adj_list.items():
            if su_name not in self.node_positions: continue
            p_x, p_y = self.node_positions[su_name]
            
            for child_su_name in children:
                if child_su_name not in self.node_positions: continue
                c_x, c_y = self.node_positions[child_su_name]
                
                is_cycle = tuple(sorted((su_name, child_su_name))) in self.cycles
                
                # Inverti i colori e lo stile delle frecce
                line_color = self.COLORS["cycle_edge_color"] if is_cycle else self.COLORS["normal_edge_color"]
                line_dash = () if is_cycle else (5, 3) # Solida per cicli, tratteggiata per normale

                self.canvas.create_line(
                    p_x + node_width / 2, p_y + node_height,
                    c_x + node_width / 2, c_y,
                    arrow=tk.LAST, fill=line_color, width=1.5, dash=line_dash,
                    tags=("relation_line", f"line_{su_name}_{child_su_name}", "graph_element")
                )

    # --- Gestione Eventi Interazione ---

    def on_button_press(self, event):
        items = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if not items:
            self.selected_item = None
            return
        
        self.selected_item = items[-1] # Prendi l'elemento più in alto
        item_tags = self.canvas.gettags(self.selected_item)
        self.current_su_tag = next((tag for tag in item_tags if tag in self.filtered_su_data), None)

        if self.current_su_tag:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            rect_id = self.canvas.find_withtag(f"rect_{self.current_su_tag}")
            if rect_id:
                self.canvas.itemconfig(rect_id, outline=self.COLORS["highlight"], width=2.5)
            self.canvas.tag_raise(self.current_su_tag)

    def on_mouse_drag(self, event):
        if self.current_su_tag and self.start_x is not None:
            dx = self.canvas.canvasx(event.x) - self.start_x
            dy = self.canvas.canvasy(event.y) - self.start_y
            
            # Muovi tutti gli elementi del nodo
            self.canvas.move(self.current_su_tag, dx, dy)
            
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            
            # Aggiorna la posizione nel layout e ridisegna le linee
            rect_id = self.canvas.find_withtag(f"rect_{self.current_su_tag}")
            if rect_id:
                coords = self.canvas.coords(rect_id[0])
                self.node_positions[self.current_su_tag] = (coords[0], coords[1])
                # Ricostruisci adj list solo per ridisegnare linee
                adj = {su: [] for su in self.filtered_su_data}
                for su, su_data in self.filtered_su_data.items():
                    relations = su_data.get("Simplified Relations", {})
                    # Ripristinato la logica originale delle frecce
                    covers = [s.strip() for s in relations.get("Copre", "").split(',') if s.strip()]
                    covered_by = [s.strip() for s in relations.get("Coperto da", "").split(',') if s.strip()]
                    for c in covers:
                        if c in self.filtered_su_data: adj[su].append(c) # Freccia da su a c
                    for c in covered_by:
                        if c in self.filtered_su_data: adj[c].append(su) # Freccia da c a su

                self._draw_all_lines(adj)
            
            self.canvas.configure(scrollregion=self.canvas.bbox("graph_element"))

    def on_button_release(self, event):
        if self.current_su_tag:
            rect_id = self.canvas.find_withtag(f"rect_{self.current_su_tag}")
            if rect_id:
                self.canvas.itemconfig(rect_id, outline="black", width=1.5)
        self.selected_item = self.start_x = self.start_y = self.current_su_tag = None

    def on_double_click(self, event):
        items = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if not items: return
        
        item_tags = self.canvas.gettags(items[-1])
        su_name = next((tag for tag in item_tags if tag in self.all_su_data), None)
        
        if su_name:
            self.hide_tooltip()
            su_data = self.all_su_data.get(su_name)
            if su_data:
                dialog = USCardViewerDialog(self.master_app, self.project_data, existing_data=su_data) # Changed to ViewerDialog
                self.wait_window(dialog)
                # Ricarica i dati e ridisegna in caso di modifiche (se la modifica è avvenuta altrove)
                self.all_su_data = self._load_all_su_data()
                self._apply_filters_and_redraw()
                self.master_app.refresh_treeview()

    def on_pan_start(self, event): self.canvas.scan_mark(event.x, event.y)
    
    def on_pan_drag(self, event): 
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._draw_legend()
    
    def on_zoom(self, event):
        factor = 1.1 if event.num == 4 or event.delta > 0 else 0.9
        self.canvas.scale("graph_element", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("graph_element"))
        self._draw_legend()

    def show_tooltip(self, event, su_name):
        if self.tooltip:
            self.tooltip.destroy()

        su_data = self.all_su_data.get(su_name)
        if not su_data: return

        desc = su_data.get('Description', 'N/D')
        tooltip_content = (
            f"ID: {su_name}\n"
            f"Area: {su_data.get('Area', 'N/D')}\n"
            f"Settore: {su_data.get('Sector', 'N/D')}\n"
            f"Descrizione: {desc[:80]}{'...' if len(desc) > 80 else ''}"
        )
        
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
        label = ttk.Label(self.tooltip, text=tooltip_content, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength=300, font=("Arial", 9))
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    # --- Funzioni Aggiuntive ---

    def save_current_layout(self):
        """Salva le posizioni dei nodi visibili."""
        for su_name, pos in self.node_positions.items():
            self.su_layout_data[su_name] = pos # Salva le coordinate del vertice in alto a sx
        save_su_layout(self.su_layout_data)
        messagebox.showinfo("Layout Salvato", "Le posizioni correnti dei nodi visualizzati sono state salvate.")

    def check_consistency(self):
        """Controlla la coerenza dei rapporti 'Copre'/'Coperto da'."""
        inconsistencies = []
        for su_name, su_data in self.all_su_data.items():
            # Controlla 'Copre' (A copre B, quindi B è coperto da A)
            covers_list = [s.strip() for s in su_data.get("Simplified Relations", {}).get("Copre", "").split(',') if s.strip()]
            for covered_su in covers_list:
                if covered_su_data := self.all_su_data.get(covered_su):
                    their_covered_by = [s.strip() for s in covered_su_data.get("Simplified Relations", {}).get("Coperto da", "").split(',') if s.strip()]
                    if su_name not in their_covered_by:
                        inconsistencies.append(f"- {su_name} 'copre' {covered_su}, ma {covered_su} non è 'coperto da' {su_name}.")
            # Controlla 'Coperto da' (A è coperto da B, quindi B copre A)
            covered_by_list = [s.strip() for s in su_data.get("Simplified Relations", {}).get("Coperto da", "").split(',') if s.strip()]
            for covering_su in covered_by_list:
                if covering_su_data := self.all_su_data.get(covering_su):
                    their_covers = [s.strip() for s in covering_su_data.get("Simplified Relations", {}).get("Copre", "").split(',') if s.strip()]
                    if su_name not in their_covers:
                        inconsistencies.append(f"- {su_name} è 'coperto da' {covering_su}, ma {covering_su} non 'copre' {su_name}.")

        report = "Controllo Coerenza Rapporti:\n\n"
        if self.cycles:
            report += "Cicli Logici Rilevati (A-B e B-A):\n"
            for u, v in self.cycles:
                report += f"- {u} <--> {v}\n"
            report += "\n"
        
        if inconsistencies:
            report += "Incoerenze di Reciprocità Rilevate:\n"
            report += "\n".join(sorted(list(set(inconsistencies))))
        else:
            report += "Nessuna incoerenza di reciprocità trovata.\n"
        
        if not self.cycles and not inconsistencies:
            report = "Nessun ciclo logico o incoerenza di reciprocità rilevata."

        messagebox.showinfo("Report Coerenza", report)

    def export_svg(self):
        try:
            file_path = simpledialog.askstring("Esporta SVG", "Inserisci nome file (es. matrix.svg):", parent=self)
            if not file_path: return
            if not file_path.lower().endswith(".svg"): file_path += ".svg"
            
            bbox = self.canvas.bbox("graph_element") # Bbox solo degli elementi del grafo
            if not bbox:
                messagebox.showwarning("Esporta SVG", "Canvas vuoto, niente da esportare.")
                return
            
            x_min, y_min, x_max, y_max = bbox
            padding = 20
            # Aumenta l'altezza per fare spazio alla legenda sotto il grafo
            height_offset_for_legend = 150 # Spazio aggiuntivo per la legenda
            width, height = x_max - x_min + 2 * padding, y_max - y_min + 2 * padding + height_offset_for_legend
            
            svg_content = f'<svg width="{width}" height="{height}" viewBox="{x_min - padding} {y_min - padding} {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="Arial">\n'
            svg_content += f'<!-- Esportato il: {datetime.datetime.now().isoformat()} -->\n'
            svg_content += f'<!-- Progetto: {self.project_data.get("nome_progetto", "N/D")} -->\n'
            # Definisci due tipi di marker per le frecce (solida nera e tratteggiata rossa)
            svg_content += '<defs>\n'
            svg_content += '  <marker id="arrowhead_solid_black" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">\n'
            svg_content += '    <polygon points="0 0, 10 3.5, 0 7" fill="black" />\n'
            svg_content += '  </marker>\n'
            svg_content += '  <marker id="arrowhead_dashed_red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">\n'
            svg_content += '    <polygon points="0 0, 10 3.5, 0 7" fill="red" />\n'
            svg_content += '  </marker>\n'
            svg_content += '</defs>\n'
            
            # Logo (placeholder)
            logo_path = "logo.png" # CAMBIARE CON IL PERCORSO REALE DEL LOGO
            if os.path.exists(logo_path):
                 svg_content += f'<image href="{logo_path}" x="{x_min}" y="{y_max - 60}" height="60" width="150"/>\n'

            # Elementi del canvas con tag "graph_element"
            for item_id in self.canvas.find_withtag("graph_element"):
                item_type = self.canvas.type(item_id)
                coords = self.canvas.coords(item_id)
                
                if item_type == "rectangle":
                    svg_content += f'<rect x="{coords[0]}" y="{coords[1]}" width="{coords[2]-coords[0]}" height="{coords[3]-coords[1]}" fill="{self.canvas.itemcget(item_id, "fill")}" stroke="{self.canvas.itemcget(item_id, "outline")}" stroke-width="{self.canvas.itemcget(item_id, "width")}"/>\n'
                elif item_type == "text":
                    font = tkFont.Font(font=self.canvas.itemcget(item_id, "font"))
                    svg_content += f'<text x="{coords[0]}" y="{coords[1]}" text-anchor="middle" dominant-baseline="central" font-size="{font.actual("size")}px" fill="{self.canvas.itemcget(item_id, "fill")}" font-weight="{font.actual("weight")}">{self.canvas.itemcget(item_id, "text")}</text>\n'
                elif item_type == "line":
                    # Determina il colore e lo stile della linea per SVG
                    is_cycle_line = self.canvas.itemcget(item_id, "dash") == "" # Se è solida, è un ciclo
                    
                    stroke_color = "black" if is_cycle_line else "red"
                    dash_array = '' if is_cycle_line else 'stroke-dasharray="5, 3"'
                    marker_url = 'url(#arrowhead_solid_black)' if is_cycle_line else 'url(#arrowhead_dashed_red)'

                    svg_content += f'<line x1="{coords[0]}" y1="{coords[1]}" x2="{coords[2]}" y2="{coords[3]}" stroke="{stroke_color}" stroke-width="{self.canvas.itemcget(item_id, "width")}" marker-end="{marker_url}" {dash_array}/>\n'

            # Legenda in SVG (separata dal grafo)
            legend_items = {"US Negativa": self.COLORS["negative"], "US Muraria": self.COLORS["muraria"], "US Virtuale": self.COLORS["virtuale"], "Altra US": self.COLORS["default"]}
            l_box_size = 15
            l_padding = 5
            legend_width = 180
            legend_height = len(legend_items) * (l_box_size + l_padding) + l_padding

            # Posiziona la legenda sotto il grafo, allineata a sinistra
            lx = x_min # Allineata a sinistra del grafo
            ly = y_max + padding # Sotto il grafo, con un po' di padding

            svg_content += f'<g transform="translate({lx}, {ly})">\n'
            svg_content += f'<rect x="-{l_padding}" y="-{l_padding}" width="{legend_width}" height="{legend_height}" fill="white" stroke="black" />\n'
            current_y = 0
            for text, color in legend_items.items():
                svg_content += f'<rect x="0" y="{current_y}" width="{l_box_size}" height="{l_box_size}" fill="{color}" stroke="black"/>\n'
                svg_content += f'<text x="{l_box_size + l_padding}" y="{current_y + l_box_size/2}" dominant-baseline="central" font-size="12px">{text}</text>\n'
                current_y += l_box_size + l_padding
            svg_content += '</g>\n'

            svg_content += '</svg>'
            with open(file_path, "w", encoding="utf-8") as f: f.write(svg_content)
            messagebox.showinfo("Esportazione Riuscita", f"Matrice esportata in {file_path}")
        except Exception as e:
            messagebox.showerror("Errore Esportazione", f"Impossibile esportare SVG: {e}")

    def export_image(self, file_format='png'):
        if not PIL_AVAILABLE:
            messagebox.showerror("Errore", "La libreria Pillow (PIL) è necessaria per esportare in PNG/JPG.\nInstallala con: pip install Pillow")
            return
        
        try:
            file_path = simpledialog.askstring(f"Esporta {file_format.upper()}", f"Inserisci nome file (es. matrix.{file_format}):", parent=self)
            if not file_path: return
            if not file_path.lower().endswith(f".{file_format}"): file_path += f".{file_format}"

            # Salva il canvas come file PostScript in memoria
            ps = self.canvas.postscript(colormode='color')
            
            # Usa Pillow per convertire il PostScript in un'immagine
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            
            # Crea una nuova immagine con sfondo bianco
            final_img = Image.new("RGB", img.size, "white")
            final_img.paste(img, (0, 0), img)

            final_img.save(file_path, file_format)
            messagebox.showinfo("Esportazione Riuscita", f"Matrice esportata in {file_path}")

        except Exception as e:
            messagebox.showerror("Errore Esportazione", f"Impossibile esportare in {file_format.upper()}: {e}\n\nAssicurati che Ghostscript sia installato e accessibile nel PATH di sistema, specialmente su Windows.")

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
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input

        self.entries = {}
        row = 0
        ttk.Label(main_frame, text="Data (YYYY_MM_DD):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.date_var, width=40).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self.entries["Date"] = self.date_var; row += 1
        ttk.Label(main_frame, text="Giorno della settimana:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.day_of_week_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.day_of_week_var, values=["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"], state="readonly", width=38).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self.entries["Day of the week"] = self.day_of_week_var; row +=1
        for key, label_text in {"Operatori": "Operatori", "Indirizzo dei lavori in giornata": "Indirizzo Lavori"}.items():
            ttk.Label(main_frame, text=label_text + ":").grid(row=row, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=var, width=40).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
            self.entries[key] = var; row += 1
        ttk.Label(main_frame, text="US indagate:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        su_frame = ttk.Frame(main_frame); su_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        su_frame.grid_columnconfigure(0, weight=1) # Espandi l'entry
        self.su_indagate_var = tk.StringVar()
        ttk.Entry(su_frame, textvariable=self.su_indagate_var, width=30).grid(row=0, column=0, sticky="ew")
        ttk.Button(su_frame, text="...", width=3, command=self.open_su_selection_for_diary).grid(row=0, column=1, padx=(3,0))
        self.entries["SU indagate"] = self.su_indagate_var; row += 1
        ttk.Label(main_frame, text="Descrizione:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.description_text = tk.Text(main_frame, width=40, height=5); self.description_text.grid(row=row, column=1, sticky="ew", padx=5, pady=3); row += 1
        self.rinvenimenti_var = tk.BooleanVar()
        ttk.Label(main_frame, text="Rinvenimenti archeologici:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        ttk.Checkbutton(main_frame, variable=self.rinvenimenti_var).grid(row=row, column=1, sticky="w", padx=5, pady=3); row += 1
        ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save_diary, style="Accent.TButton").grid(row=row, column=0, columnspan=2, pady=15)

    def open_su_selection_for_diary(self):
        dialog = tk.Toplevel(self); dialog.title("Seleziona US Indagate"); dialog.geometry("300x400"); dialog.transient(self); dialog.grab_set()
        
        dialog_frame = ttk.Frame(dialog, padding="10")
        dialog_frame.pack(fill="both", expand=True)

        ttk.Label(dialog_frame, text="Seleziona una o più US:").pack(pady=5)
        
        listbox_frame = ttk.Frame(dialog_frame)
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)

        listbox = tk.Listbox(listbox_frame, selectmode="multiple", exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        listbox.config(yscrollcommand=scrollbar.set)

        available_sus = list_su_reports() # Already sorted by list_su_reports()
        
        # Populate listbox and pre-select current values
        current_selection_list = [s.strip() for s in self.su_indagate_var.get().split(',') if s.strip()]
        for i, su_name in enumerate(available_sus):
            listbox.insert(tk.END, su_name)
            if su_name in current_selection_list:
                listbox.selection_set(i)

        def on_ok():
            selected_indices = listbox.curselection()
            selected_sus = [listbox.get(i) for i in selected_indices]
            self.su_indagate_var.set(", ".join(selected_sus))
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=on_ok, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side="left", padx=5)
        
        self.wait_window(dialog)

    def populate_fields(self):
        # Ensure existing_data is a dictionary before using .get()
        if self.existing_data is None:
            self.existing_data = {}

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
        data = {"nome_progetto": self.project_data.get("nome_progetto", "N/A"), "id_progetto": self.project_data.get("id_progetto", "N/A"), "Descrizione": self.description_text.get("1.0", tk.END).strip(), "Rinvenimenti archeologici": self.rinvenimenti_var.get()}
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
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_rowconfigure(0, weight=1)
        
        left_frame = ttk.Frame(main_frame); left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10)); left_frame.grid_rowconfigure(1, weight=1)
        ttk.Label(left_frame, text="File Diario Disponibili:").grid(row=0, column=0, pady=5)
        
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew")
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(listbox_frame, width=30, selectbackground="#a6d9f7", selectforeground="black") # Aggiungi colori selezione
        self.file_listbox.grid(row=0, column=0, sticky="nsew")
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.file_listbox.yview); scrollbar.grid(row=0, column=1, sticky="ns"); self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        button_frame = ttk.Frame(left_frame); button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.new_btn = ttk.Button(button_frame, text="Nuovo", command=self.new_diary, style="Accent.TButton"); self.new_btn.pack(side="left", padx=2)
        self.edit_btn = ttk.Button(button_frame, text="Modifica", state="disabled", command=self.edit_diary); self.edit_btn.pack(side="left", padx=2)
        self.delete_btn = ttk.Button(button_frame, text="Elimina", state="disabled", command=self.delete_diary, style="Danger.TButton"); self.delete_btn.pack(side="left", padx=2)
        
        content_frame = ttk.Frame(main_frame); content_frame.grid(row=0, column=1, sticky="nsew"); content_frame.grid_rowconfigure(1, weight=1); content_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(content_frame, text="Contenuto File:").grid(row=0, column=0, pady=5, sticky="w")
        self.content_text = tk.Text(content_frame, wrap="word", state="disabled", font=("TkFixedFont", 10), background="#f0f0f0", relief="flat"); self.content_text.grid(row=1, column=0, sticky="nsew")
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
        self.existing_data = existing_data if existing_data is not None else {} # Ensure existing_data is a dict
        self.original_filename = original_filename
        
        self.create_widgets()
        if self.existing_data:
            self.populate_fields()
        else:
            self.id_var.set(get_next_find_id())
            self.date_var.set(datetime.date.today().strftime('%Y%m%d'))
            self.update_identifier()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(padx=15, pady=15, fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1) # Espandi la colonna degli input
        
        self.entries = {}
        row = 0

        ttk.Label(main_frame, text="ID Progressivo:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.id_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.id_var, font=("Arial", 10, "bold")).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text="Nome Progetto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(main_frame, text=self.project_data.get("nome_progetto", "N/A")).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        ttk.Label(main_frame, text="ID Progetto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.id_progetto_label = ttk.Label(main_frame, text=self.project_data.get("id_progetto", "N/A"))
        self.id_progetto_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.tipo_var, values=["Reperto Singolo", "Sacchetto"], state="readonly", width=38)
        tipo_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self.entries["Tipo"] = self.tipo_var
        row += 1

        ttk.Label(main_frame, text="Data (AAAAMMDD):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=40)
        date_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        date_entry.bind("<KeyRelease>", self.update_identifier)
        self.entries["Data"] = self.date_var
        row += 1

        ttk.Label(main_frame, text="Tipologia Reperto:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.tipologia_reperto_var = tk.StringVar()
        tipologie = ["ceramica", "concotto", "industria litica", "metallo", "ossa umane", "resti faunistici", "resti botanici", "carbone", "intonaco", "altro"]
        tipologia_combo = ttk.Combobox(main_frame, textvariable=self.tipologia_reperto_var, values=tipologie, state="readonly", width=38)
        tipologia_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
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
        nr_reperti_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self.entries["Nr Reperti"] = self.nr_reperti_var
        row += 1

        simple_fields = {"Nome area": "Nome Area", "Quadrato": "Quadrato", "Quadrante": "Quadrante"}
        for key, label_text in simple_fields.items():
            ttk.Label(main_frame, text=label_text + ":").grid(row=row, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=var, width=40).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
            self.entries[key] = var
            row += 1

        ttk.Label(main_frame, text="US di riferimento:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.us_var = tk.StringVar()
        us_options = list_su_reports()
        us_combo = ttk.Combobox(main_frame, textvariable=self.us_var, values=us_options, state="readonly", width=38)
        us_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        self.entries["US"] = self.us_var
        row += 1

        ttk.Label(main_frame, text="Descrizione:").grid(row=row, column=0, sticky="nw", padx=5, pady=3)
        self.description_text = tk.Text(main_frame, width=40, height=5)
        self.description_text.grid(row=row, column=1, sticky="ew", padx=5, pady=3)
        row += 1

        save_button = ttk.Button(main_frame, text="\U0001F4BE Salva", command=self.save_find, style="Accent.TButton")
        save_button.grid(row=row, column=0, columnspan=2, pady=15)

    def update_identifier(self, event=None):
        find_id = self.id_var.get()
        proj_id = self.project_data.get("id_progetto", "N/A")
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

        data = { "ID": find_id, "Nome Progetto": self.project_data.get("nome_progetto", "N/A"), "ID Progetto": self.project_data.get("id_progetto", "N/A"), "Identificativo Reperto": self.identifier_var.get(), "Descrizione": self.description_text.get("1.0", tk.END).strip() }
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
        main_frame = ttk.Frame(self, padding="15"); main_frame.pack(fill="both", expand=True)
        button_frame = ttk.Frame(main_frame); button_frame.pack(fill="x", pady=10)
        self.new_btn = ttk.Button(button_frame, text="Nuova Scheda Reperto", command=self.new_find, style="Accent.TButton"); self.new_btn.pack(side="left", padx=5)
        self.edit_btn = ttk.Button(button_frame, text="Modifica", state="disabled", command=self.edit_find); self.edit_btn.pack(side="left", padx=5)
        self.delete_btn = ttk.Button(button_frame, text="Cancella", state="disabled", command=self.delete_find, style="Danger.TButton"); self.delete_btn.pack(side="left", padx=5)
        
        tree_frame = ttk.Frame(main_frame); tree_frame.pack(fill="both", expand=True, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("ID", "Identificativo", "Data", "Tipo", "Tipologia", "US")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=120, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew") # Usa grid per Treeview
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); scrollbar.grid(row=0, column=1, sticky="ns"); self.tree.configure(yscrollcommand=scrollbar.set)
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

class ReportsDialog(tk.Toplevel):
    def __init__(self, master, project_data):
        super().__init__(master)
        self.title("Report Riassuntivo Schede US")
        self.geometry("600x500")
        self.resizable(True, True)
        self.project_data = project_data
        self.all_su_data = self._load_all_su_data()
        self.all_diary_data = self._load_all_diary_data()
        self.all_finds_data = self._load_all_finds_data()
        self.create_widgets()
        self.generate_report_content()

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

    def _load_all_diary_data(self):
        folder = "diary_usm"
        data = {}
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.lower().endswith(".json"):
                    filepath = os.path.join(folder, filename)
                    diary_data = load_json_file(filepath)
                    if diary_data:
                        data[os.path.splitext(filename)[0]] = diary_data
        return data

    def _load_all_finds_data(self):
        folder = "finds_usm"
        data = {}
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.lower().endswith(".json"):
                    filepath = os.path.join(folder, filename)
                    find_data = load_json_file(filepath)
                    if find_data:
                        data[os.path.splitext(filename)[0]] = find_data
        return data

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15"); main_frame.pack(fill="both", expand=True)
        self.report_text = tk.Text(main_frame, wrap="word", state="disabled", font=("Arial", 10), background="#f0f0f0", relief="flat")
        self.report_text.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.report_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.report_text.config(yscrollcommand=scrollbar.set)

    def generate_report_content(self):
        total_us = len(self.all_su_data)
        complete_us = 0
        incomplete_us = 0
        us_in_diary = set()
        us_with_finds = set()
        us_type_counts = {}
        all_dates = []

        for su_name, su_data in self.all_su_data.items():
            # Completezza
            desc = su_data.get("Description", "").strip()
            obs = su_data.get("Observations", "").strip()
            interp = su_data.get("Interpretations", "").strip()
            simp = su_data.get("Simplified Relations", {})
            is_incomplete = (not simp.get("Copre", "").strip() and not simp.get("Coperto da", "").strip()) or not desc or not obs or not interp
            
            if is_incomplete:
                incomplete_us += 1
            else:
                complete_us += 1

            # Tipo di US
            us_type = su_data.get("Type", "Sconosciuto")
            us_type_counts[us_type] = us_type_counts.get(us_type, 0) + 1

            # Date
            date_str = su_data.get("Date", "")
            if date_str:
                try:
                    # Assuming date format is YYYY-MM-DD or similar, try to parse
                    # This might need refinement based on actual date formats used
                    all_dates.append(datetime.datetime.strptime(date_str, '%Y-%m-%d'))
                except ValueError:
                    try:
                        all_dates.append(datetime.datetime.strptime(date_str, '%Y_%m_%d'))
                    except ValueError:
                        pass # Ignore unparseable dates

        # US nel diario
        for diary_name, diary_data in self.all_diary_data.items():
            su_indagate_str = str(diary_data.get("SU indagate", ""))
            for su_entry in su_indagate_str.split(','):
                # Extract only digits for comparison, then convert to string for lookup in all_su_data keys
                if (su_num_str := ''.join(filter(str.isdigit, su_entry.strip()))):
                    # Reconstruct the potential SU name (e.g., US1, USM2)
                    # This is a heuristic and might need to be more robust if SU naming is complex
                    for su_key in self.all_su_data.keys():
                        if su_key.endswith(su_num_str): # Check if the SU name ends with the number
                            us_in_diary.add(su_key)
                            break
        
        # US con reperti
        for find_name, find_data in self.all_finds_data.items():
            if (us_ref := find_data.get("US")):
                us_with_finds.add(us_ref)

        report_content = f"--- Report Riassuntivo Schede US ---\n\n"
        report_content += f"Dati Progetto: {self.project_data.get('nome_progetto', 'N/A')} (ID: {self.project_data.get('id_progetto', 'N/A')})\n\n"
        
        report_content += f"Totale Schede US: {total_us}\n"
        report_content += f"Schede US Complete: {complete_us}\n"
        report_content += f"Schede US Incomplete: {incomplete_us}\n"
        report_content += f"Schede US presenti nel Diario: {len(us_in_diary)}\n"
        report_content += f"Schede US con Reperti Associati: {len(us_with_finds)}\n\n"

        report_content += "Riepilogo per Tipo di US:\n"
        for us_type, count in sorted(us_type_counts.items()):
            report_content += f"- {us_type}: {count}\n"
        report_content += "\n"

        if all_dates:
            oldest_date = min(all_dates).strftime('%Y-%m-%d')
            most_recent_date = max(all_dates).strftime('%Y-%m-%d')
            report_content += f"Data Scheda US più Vecchia: {oldest_date}\n"
            report_content += f"Data Scheda US più Recente: {most_recent_date}\n"
        else:
            report_content += "Nessuna data trovata nelle schede US.\n"

        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", report_content)
        self.report_text.config(state="disabled")

class USManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USManager")
        self.geometry("950x700")
        self.resizable(True, True)

        # Configura lo stile ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam") # Puoi provare altri temi: "default", "alt", "classic", "vista", "xpnative", "aqua"

        # Stili personalizzati
        self.style.configure("TButton", font=("Arial", 10), padding=6, relief="flat")
        self.style.map("TButton", background=[("active", "#e0e0e0"), ("!disabled", "#f0f0f0")]) # Effetto al passaggio del mouse

        self.style.configure("Accent.TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#45a049")])

        self.style.configure("Danger.TButton", background="#f44336", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("Danger.TButton", background=[("active", "#da190b")])

        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TEntry", padding=3)
        self.style.configure("TCombobox", padding=3)
        self.style.configure("TCheckbutton", padding=3)
        self.style.configure("TNotebook.Tab", padding=[10, 5]) # Padding per i tab del notebook

        # Stili per Treeview
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e0e0e0")
        self.style.configure("Treeview", rowheight=25, font=("Arial", 9))
        self.style.map("Treeview", background=[("selected", "#a6d9f7")]) # Colore di selezione
        
        # Stili per completezza e diario
        self.style.configure("incomplete.Treeview", background="#FFCDD2") # Rosso chiaro
        self.style.configure("complete.Treeview", background="#C8E6C9")   # Verde chiaro
        # Nota: questi stili di background per le righe funzionano meglio con alcuni temi (es. 'clam')

        self.project_data = load_project_data()
        self.create_widgets()
        self.bind("<Return>", self.perform_search)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        project_info_frame = ttk.Frame(main_frame); project_info_frame.pack(fill="x", pady=5)
        ttk.Label(project_info_frame, text=self.project_data.get("nome_progetto", "N/A"), font=tkFont.Font(family="Arial", size=24, weight="bold")).pack(pady=2)
        ttk.Label(project_info_frame, text=self.project_data.get("id_progetto", "N/A"), font=tkFont.Font(family="Arial", size=18)).pack(pady=2)
        
        buttons_frame = ttk.Frame(main_frame); buttons_frame.pack(fill="x", pady=10)
        
        us_actions_frame = ttk.LabelFrame(buttons_frame, text="Azioni US", padding="10"); us_actions_frame.pack(side="left", padx=5, fill="y")
        ttk.Button(us_actions_frame, text="+ Nuova US", command=self.open_new_card, style="Accent.TButton").pack(side="left", padx=5, pady=5)
        self.edit_btn = ttk.Button(us_actions_frame, text="✏ Modifica US", command=self.edit_selected, state="disabled"); self.edit_btn.pack(side="left", padx=5, pady=5)
        self.delete_btn = ttk.Button(us_actions_frame, text="🗑 Cancella US", command=self.delete_selected, state="disabled", style="Danger.TButton"); self.delete_btn.pack(side="left", padx=5, pady=5)
        
        tools_frame = ttk.LabelFrame(buttons_frame, text="Strumenti", padding="10"); tools_frame.pack(side="left", padx=5, fill="y")
        ttk.Button(tools_frame, text="Matrix di Harris", command=self.open_relation_viewer).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Campi Personalizzati", command=self.open_custom_fields_dialog).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Gestione Diario", command=self.open_diary_viewer).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Gestione Reperti", command=self.open_finds_manager).pack(side="left", padx=5, pady=5)
        ttk.Button(tools_frame, text="Genera Report", command=self.open_reports_dialog).pack(side="left", padx=5, pady=5) # Nuovo pulsante Report
        
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)
        
        ttk.Label(main_frame, text="Schede US Esistenti", font=("Arial", 12, "bold")).pack(pady=5)
        
        tree_container_frame = ttk.Frame(main_frame)
        tree_container_frame.pack(fill="both", expand=True, padx=10)
        tree_container_frame.grid_columnconfigure(0, weight=1)
        tree_container_frame.grid_rowconfigure(0, weight=1)

        columns = ("SU", "Nr. Reperti", "Autore", "Data", "Completezza", "Nel diario")
        self.tree = ttk.Treeview(tree_container_frame, columns=columns, show="headings", height=15)
        
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
        
        self.tree.grid(row=0, column=0, sticky="nsew") # Usa grid per Treeview
        
        tree_scrollbar = ttk.Scrollbar(tree_container_frame, orient="vertical", command=self.tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.config(yscrollcommand=tree_scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.view_selected_us) # Bind double-click to view
        
        bottom_search_frame = ttk.Frame(main_frame); bottom_search_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        bottom_search_frame.grid_columnconfigure(0, weight=1) # Espandi l'entry di ricerca

        self.search_entry = ttk.Entry(bottom_search_frame, width=30); self.search_entry.grid(row=0, column=0, padx=5, sticky="ew")
        self.search_entry.bind("<Return>", self.perform_search)
        ttk.Button(bottom_search_frame, text="Cerca in Descrizione", command=self.perform_search, style="Accent.TButton").grid(row=0, column=1, padx=5)
        
        self.refresh_treeview()

    def on_tree_select(self, event):
        state = "normal" if self.tree.selection() else "disabled"
        self.edit_btn.config(state=state); self.delete_btn.config(state=state)
    
    def perform_search(self, event=None): self.refresh_treeview(search_query=self.search_entry.get().strip().lower())

    def open_new_card(self):
        dialog = USCardDialog(self, self.project_data); self.wait_window(dialog); self.refresh_treeview()

    def edit_selected(self):
        if not (selected := self.tree.selection()): return
        item_id = selected[0]
        item_data = self.tree.item(item_id)
        
        filename_to_load = None
        # Try to get the explicit iid (which should be the full filename)
        if 'iid' in item_data:
            filename_to_load = item_data['iid']
        else:
            # Fallback for older entries or if iid was not set correctly
            # Get the base name from the displayed values
            filename_base = item_data['values'][0] # This is 'US1', 'USM2', etc.
            
            # Search in the directory for a file matching this base name
            su_report_folder = "su_report"
            for f in os.listdir(su_report_folder):
                if os.path.splitext(f)[0] == filename_base and f.lower().endswith(".json"):
                    filename_to_load = f
                    break
        
        if not filename_to_load:
            messagebox.showerror("Errore", f"Impossibile trovare il file JSON corrispondente per l'elemento selezionato '{item_data['values'][0]}'.")
            return

        path = os.path.join("su_report", filename_to_load)
        if not os.path.exists(path):
            messagebox.showerror("Errore", f"File '{filename_to_load}' non trovato.")
            return
        if not (data := load_json_file(path)): return
        dialog = USCardDialog(self, self.project_data, existing_data=data); self.wait_window(dialog); self.refresh_treeview()

    def view_selected_us(self, event=None):
        if not (selected := self.tree.selection()): return
        item_id = selected[0]
        item_data = self.tree.item(item_id)
        
        filename_to_load = None
        if 'iid' in item_data:
            filename_to_load = item_data['iid']
        else:
            filename_base = item_data['values'][0]
            su_report_folder = "su_report"
            for f in os.listdir(su_report_folder):
                if os.path.splitext(f)[0] == filename_base and f.lower().endswith(".json"):
                    filename_to_load = f
                    break
        
        if not filename_to_load:
            messagebox.showerror("Errore", f"Impossibile trovare il file JSON corrispondente per l'elemento selezionato '{item_data['values'][0]}'.")
            return

        path = os.path.join("su_report", filename_to_load)
        if not os.path.exists(path):
            messagebox.showerror("Errore", f"File '{filename_to_load}' non trovato.")
            return
        if not (data := load_json_file(path)): return
        dialog = USCardViewerDialog(self, self.project_data, existing_data=data)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def delete_selected(self):
        if not (selected := self.tree.selection()): return
        item_id = selected[0]
        item_data = self.tree.item(item_id)

        filename_to_delete = None
        if 'iid' in item_data:
            filename_to_delete = item_data['iid']
        else:
            filename_base = item_data['values'][0]
            su_report_folder = "su_report"
            for f in os.listdir(su_report_folder):
                if os.path.splitext(f)[0] == filename_base and f.lower().endswith(".json"):
                    filename_to_delete = f
                    break

        if not filename_to_delete:
            messagebox.showerror("Errore", f"Impossibile trovare il file JSON corrispondente per l'elemento selezionato '{item_data['values'][0]}'.")
            return

        filename_display = item_data['values'][0] # Display name from values
        path = os.path.join("su_report", filename_to_delete)
        if not os.path.exists(path):
            messagebox.showerror("Errore", f"File '{filename_display}' non trovato.")
            return
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare '{filename_display}'?"):
            try: os.remove(path); messagebox.showinfo("Eliminato", f"{filename_display} eliminato."); self.refresh_treeview()
            except Exception as e: messagebox.showerror("Errore", f"Eliminazione fallita: {e}")

    def open_relation_viewer(self): 
        dialog = RelationViewerDialog(self, self.project_data)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def open_custom_fields_dialog(self): 
        # Pass self (the USManagerApp instance) to CustomFieldsDialog
        dialog = CustomFieldsDialog(self, self) 
        self.wait_window(dialog)

    def open_diary_viewer(self): dialog = DiaryViewerDialog(self); self.wait_window(dialog)
    def open_finds_manager(self):
        dialog = FindsManagerDialog(self, self.project_data); dialog.transient(self); dialog.grab_set(); self.wait_window(dialog)

    def open_reports_dialog(self): # Nuovo metodo per aprire il Report
        dialog = ReportsDialog(self, self.project_data)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

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
                        # Ensure 'SU indagate' is treated as a string before splitting
                        su_indagate_str = str(diary_data.get("SU indagate", ""))
                        for su_entry in su_indagate_str.split(','):
                            try:
                                # Extract only digits for comparison
                                if (su_num_str := ''.join(filter(str.isdigit, su_entry.strip()))):
                                    in_diary_sus.add(int(su_num_str))
                            except ValueError:
                                pass
        return in_diary_sus

    def refresh_treeview(self, search_query=None):
        for row in self.tree.get_children(): self.tree.delete(row)
        
        finds_count = self._get_finds_count_per_su()
        entries, in_diary_su_numbers = [], self._get_in_diary_su_numbers()
        
        for filename_with_ext in os.listdir("su_report"): # Iterate through actual files in directory
            if not filename_with_ext.lower().endswith(".json"):
                continue
            
            filename_base = os.path.splitext(filename_with_ext)[0] # Get filename without extension
            path = os.path.join("su_report", filename_with_ext)
            
            if data := load_json_file(path):
                desc = data.get("Description", "").strip(); obs = data.get("Observations", "").strip(); interp = data.get("Interpretations", "").strip()
                if search_query and search_query not in (desc + " " + obs + " " + interp).lower(): continue
                
                simp = data.get("Simplified Relations", {})
                is_incomplete = (not simp.get("Copre", "").strip() and not simp.get("Coperto da", "").strip()) or not desc or not obs or not interp
                su_number = data.get("SU number", 0)
                is_in_diary = su_number in in_diary_su_numbers
                num_reperti = finds_count.get(filename_base, 0) # Use filename_base for finds_count lookup

                entries.append((
                    su_number, 
                    filename_base, # Use base name for display
                    num_reperti,
                    data.get("Report author", ""), 
                    data.get("Date", ""), 
                    "Incompleta" if is_incomplete else "Completa", 
                    "Sì" if is_in_diary else "No", 
                    "incomplete" if is_incomplete else "complete", 
                    "in_diary_yes" if is_in_diary else "in_diary_no",
                    filename_with_ext # Store full filename as iid for easy access
                ))

        entries.sort(key=lambda x: x[0])
        
        for _, name, num_reperti, author, date, completeness, in_diary, comp_tag, diary_tag, full_filename in entries:
            tags = []
            if comp_tag == "incomplete": tags.append("incomplete")
            if diary_tag == "in_diary_yes": tags.append("in_diary_yes")
            else: tags.append("in_diary_no")
            # Pass full_filename as iid for easy retrieval in edit/delete
            self.tree.insert("", "end", values=(name, num_reperti, author, date, completeness, in_diary), tags=tags, iid=full_filename)

if __name__ == "__main__":
    if ensure_project_file():
        os.makedirs("su_report", exist_ok=True)
        os.makedirs("manager", exist_ok=True)
        os.makedirs("diary_usm", exist_ok=True)
        os.makedirs("finds_usm", exist_ok=True)
        os.makedirs("photos", exist_ok=True) # Crea la cartella 'photos'
        if not os.path.exists(CUSTOM_FIELDS_PATH):
            save_json_file(CUSTOM_FIELDS_PATH, [])
        app = USManagerApp()
        app.mainloop()
