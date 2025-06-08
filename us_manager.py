import os
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import csv

# Directory dove vengono salvate le schede
US_DIR = "schede_us"
MANAGER_DIR = "manager"
os.makedirs(US_DIR, exist_ok=True)
os.makedirs(MANAGER_DIR, exist_ok=True)

# Percorsi file
PROG_MANAGER_PATH = os.path.join(US_DIR, "prog_manager.json")
TRANSLATION_PATH = os.path.join(MANAGER_DIR, "translations.json")

# Crea il file di traduzioni se non esiste
TRANSLATION_DEFAULT = {
  "it": {
    "project_params": "Parametri Progetto",
    "save": "Salva",
    "project_name": "Nome del progetto",
    "project_code": "Codice del progetto",
    "street": "Via",
    "city": "Comune",
    "province": "Provincia",
    "year": "Anno",
    "ente": "Ente responsabile",
    "ufficio": "Ufficio MiC competente",
    "main_title": "Gestione Schede US",
    "new_card": "Nuova scheda",
    "edit_card": "Modifica scheda",
    "delete_card": "Elimina scheda",
    "editor_matrix": "Editor Matrix",
    "export_csv": "Esporta CSV",
    "export_matrix": "Esporta Matrix",
    "tab1": "Anagrafica",
    "tab2": "Cosa contiene",
    "tab3": "Relazioni US",
    "tab4": "Osservazioni",
    "tab5": "Autore",
    "id": "ID",
    "nr_us": "Nr US",
    "area_struttura": "Area/struttura",
    "saggio": "Saggio",
    "settore": "Settore",
    "quadrato": "Quadrato",
    "criteri_distinzione": "Criteri di distinzione",
    "componenti_organici": "Componenti Organici",
    "componenti_inorganici": "Componenti Inorganici",
    "consistenza": "Consistenza (1-5)",
    "colore": "Colore",
    "misure": "Misure",
    "stato_conservazione": "Stato di conservazione",
    "copre": "Copre (US separate da virgola)",
    "uguale_a": "Uguale a (US separate da virgola)",
    "coperto_da": "Coperto da (US separate da virgola)",
    "si_lega_a": "Si lega a (US separate da virgola)",
    "gli_si_appoggia": "Gli si appoggia (US separate da virgola)",
    "si_appoggia_a": "Si appoggia a (US separate da virgola)",
    "taglia": "Taglia (US separate da virgola)",
    "tagliato_da": "Tagliato da (US separate da virgola)",
    "riempie": "Riempie (US separate da virgola)",
    "riempito_da": "Riempito da (US separate da virgola)",
    "descrizione": "Descrizione",
    "osservazioni": "Osservazioni",
    "interpretazioni": "Interpretazioni",
    "datazione": "Datazione",
    "elementi_datanti": "Elementi datanti",
    "data_rilevamento": "Data di rilevamento",
    "responsabile_compilazione": "Responsabile compilazione",
    "edit_title": "Modifica Scheda US",
    "new_title": "Nuova Scheda US"
  },
  "en": {
    "project_params": "Project Parameters",
    "save": "Save",
    "project_name": "Project Name",
    "project_code": "Project Code",
    "street": "Street",
    "city": "City",
    "province": "Province",
    "year": "Year",
    "ente": "Responsible Entity",
    "ufficio": "Competent MiC Office",
    "main_title": "US Sheet Manager",
    "new_card": "New Sheet",
    "edit_card": "Edit Sheet",
    "delete_card": "Delete Sheet",
    "editor_matrix": "Matrix Editor",
    "export_csv": "Export CSV",
    "export_matrix": "Export Matrix",
    "tab1": "Registry",
    "tab2": "Contents",
    "tab3": "US Relations",
    "tab4": "Notes",
    "tab5": "Author",
    "id": "ID",
    "nr_us": "US No.",
    "area_struttura": "Area/Structure",
    "saggio": "Trench",
    "settore": "Sector",
    "quadrato": "Square",
    "criteri_distinzione": "Distinction Criteria",
    "componenti_organici": "Organic Components",
    "componenti_inorganici": "Inorganic Components",
    "consistenza": "Consistency (1-5)",
    "colore": "Color",
    "misure": "Measures",
    "stato_conservazione": "Conservation State",
    "copre": "Covers (comma-separated US)",
    "uguale_a": "Equal to (comma-separated US)",
    "coperto_da": "Covered by (comma-separated US)",
    "si_lega_a": "Linked to (comma-separated US)",
    "gli_si_appoggia": "Supported by (comma-separated US)",
    "si_appoggia_a": "Supports (comma-separated US)",
    "taglia": "Cuts (comma-separated US)",
    "tagliato_da": "Cut by (comma-separated US)",
    "riempie": "Fills (comma-separated US)",
    "riempito_da": "Filled by (comma-separated US)",
    "descrizione": "Description",
    "osservazioni": "Notes",
    "interpretazioni": "Interpretations",
    "datazione": "Dating",
    "elementi_datanti": "Dating Elements",
    "data_rilevamento": "Survey Date",
    "responsabile_compilazione": "Compiled by",
    "edit_title": "Edit US Sheet",
    "new_title": "New US Sheet"
  },
  "de": {
    "project_params": "Projektparameter",
    "save": "Speichern",
    "project_name": "Projektname",
    "project_code": "Projektcode",
    "street": "Straße",
    "city": "Stadt",
    "province": "Bundesland",
    "year": "Jahr",
    "ente": "Verantwortliche Stelle",
    "ufficio": "Zuständiges MiC-Büro",
    "main_title": "US-Blattverwaltung",
    "new_card": "Neues Blatt",
    "edit_card": "Blatt bearbeiten",
    "delete_card": "Blatt löschen",
    "editor_matrix": "Matrix-Editor",
    "export_csv": "CSV exportieren",
    "export_matrix": "Matrix exportieren",
    "tab1": "Stammdaten",
    "tab2": "Inhalt",
    "tab3": "US-Beziehungen",
    "tab4": "Bemerkungen",
    "tab5": "Autor",
    "id": "ID",
    "nr_us": "US-Nr.",
    "area_struttura": "Bereich/Struktur",
    "saggio": "Schnitt",
    "settore": "Sektor",
    "quadrato": "Quadrat",
    "criteri_distinzione": "Unterscheidungskriterien",
    "componenti_organici": "Organische Komponenten",
    "componenti_inorganici": "Anorganische Komponenten",
    "consistenza": "Konsistenz (1-5)",
    "colore": "Farbe",
    "misure": "Maße",
    "stato_conservazione": "Erhaltungszustand",
    "copre": "Deckt ab (US, durch Komma getrennt)",
    "uguale_a": "Gleich wie (US, durch Komma getrennt)",
    "coperto_da": "Bedeckt von (US, durch Komma getrennt)",
    "si_lega_a": "Verbunden mit (US, durch Komma getrennt)",
    "gli_si_appoggia": "Gestützt von (US, durch Komma getrennt)",
    "si_appoggia_a": "Stützt (US, durch Komma getrennt)",
    "taglia": "Schneidet (US, durch Komma getrennt)",
    "tagliato_da": "Geschnitten von (US, durch Komma getrennt)",
    "riempie": "Füllt (US, durch Komma getrennt)",
    "riempito_da": "Gefüllt von (US, durch Komma getrennt)",
    "descrizione": "Beschreibung",
    "osservazioni": "Bemerkungen",
    "interpretazioni": "Interpretationen",
    "datazione": "Datierung",
    "elementi_datanti": "Datierende Elemente",
    "data_rilevamento": "Erhebungsdatum",
    "responsabile_compilazione": "Verantwortlicher",
    "edit_title": "US-Blatt bearbeiten",
    "new_title": "Neues US-Blatt"
  }
}

# Carica le traduzioni dal file esterno
if os.path.exists(TRANSLATION_PATH):
    with open(TRANSLATION_PATH, encoding="utf-8") as f:
        TRANSLATIONS = json.load(f)
else:
    TRANSLATIONS = TRANSLATION_DEFAULT

# Crea il file di traduzioni se non esiste
if not os.path.exists(TRANSLATION_PATH):
    with open(TRANSLATION_PATH, "w", encoding="utf-8") as f:
        json.dump(TRANSLATION_DEFAULT, f, indent=2, ensure_ascii=False)

# Funzione salva_scheda base
def salva_scheda(scheda):
    filename = f"US{scheda['id']}.json"
    filepath = os.path.join(US_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scheda, f, indent=2, ensure_ascii=False)

# Crea la root principale UNA SOLA VOLTA
root = tk.Tk()
root.withdraw()  # Nasconde la finestra principale finché non serve

# Variabili globali per finestre aperte
open_us_windows = {}
open_matrix_window = [None]

# Funzione per mostrare popup inserimento parametri progetto
def T(key, lingua=None):
    if lingua is None:
        # Prova a leggere lingua da prog_manager.json
        if os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
                prog_data = json.load(f)
            lingua = prog_data.get("lingua", "it")
        else:
            lingua = "it"
    return TRANSLATIONS.get(lingua, {}).get(key, key)

def mostra_popup_parametri():
    # Selezione lingua solo al primo avvio
    if os.path.exists(PROG_MANAGER_PATH):
        with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
            prog_data = json.load(f)
        lingua = prog_data.get('lingua', None)
    else:
        lingua = None
    if not lingua:
        # Popup selezione lingua
        lang_popup = tk.Toplevel(root)
        lang_popup.title("Seleziona lingua / Select language / Sprache wählen")
        lang_popup.grab_set()
        tk.Label(lang_popup, text="Seleziona la lingua / Select language / Sprache wählen:").pack(padx=20, pady=10)
        lang = tk.StringVar(value="it")
        def set_lang(l):
            lang.set(l)
            lang_popup.destroy()
        tk.Button(lang_popup, text="Italiano", width=15, command=lambda: set_lang("it")).pack(pady=5)
        tk.Button(lang_popup, text="English", width=15, command=lambda: set_lang("en")).pack(pady=5)
        tk.Button(lang_popup, text="Deutsch", width=15, command=lambda: set_lang("de")).pack(pady=5)
        lang_popup.transient()
        lang_popup.wait_window()
        lingua = lang.get()
        # Salva lingua in prog_manager.json
        if not os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, "w", encoding="utf-8") as f:
                json.dump({"lingua": lingua}, f, indent=4, ensure_ascii=False)
    # Popup inserimento parametri progetto
    popup = tk.Toplevel(root)
    popup.title(T("project_params", lingua))
    popup.grab_set()
    labels = [
        (T("project_name", lingua), "nome_progetto"),
        (T("project_code", lingua), "codice_progetto"),
        (T("street", lingua), "via"),
        (T("city", lingua), "comune"),
        (T("province", lingua), "provincia"),
        (T("year", lingua), "anno"),
        (T("ente", lingua), "ente_responsabile"),
        (T("ufficio", lingua), "ufficio_mic")
    ]
    entries = {}
    for i, (label, key) in enumerate(labels):
        tk.Label(popup, text=label).grid(row=i, column=0, sticky="e")
        entry = tk.Entry(popup, width=40)
        entry.grid(row=i, column=1)
        entries[key] = entry
    def salva_parametri():
        dati = {k: e.get() for k, e in entries.items()}
        dati["lingua"] = lingua
        with open(PROG_MANAGER_PATH, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)
        popup.destroy()
        avvia_gui_principale()
    btn_salva = tk.Button(popup, text=T("save", lingua), command=salva_parametri)
    btn_salva.grid(row=len(labels), column=1, pady=10)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)  # Disabilita chiusura X
    popup.transient()
    popup.wait_window()

# Variabile globale per elenco file
file_labels = []

def aggiorna_elenco(lingua=None):
    global file_labels, elenco
    if lingua is None:
        if os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
                prog_data = json.load(f)
            lingua = prog_data.get("lingua", "it")
        else:
            lingua = "it"
    elenco.delete(0, tk.END)
    file_labels = []
    for filename in sorted(os.listdir(US_DIR)):
        if filename.endswith(".json") and filename not in ("prog_manager.json", "positions.json"):
            filepath = os.path.join(US_DIR, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    dati = json.load(f)
                responsabile = dati.get("responsabile_compilazione", "-")
                data_ril = dati.get("data_rilevamento", "-")
                required_fields = [
                    "nr_us", "area_struttura", "saggio", "settore", "quadrato",
                    "criteri_distinzione", "componenti_organici", "componenti_inorganici",
                    "consistenza", "colore", "misure", "stato_conservazione",
                    "descrizione", "osservazioni", "interpretazioni", "datazione",
                    "elementi_datanti", "data_rilevamento", "responsabile_compilazione"
                ]
                complete = all(str(dati.get(f, "")).strip() for f in required_fields)
                stato = T("complete", lingua) if complete and "complete" in TRANSLATIONS[lingua] else ("COMPLETA" if complete else (T("partial", lingua) if "partial" in TRANSLATIONS[lingua] else "PARZIALE"))
                label = f"{filename} | {responsabile} | {data_ril} | {stato}"
                elenco.insert(tk.END, label)
                file_labels.append(filename)
                if not complete:
                    elenco.itemconfig(tk.END, {'fg': 'orange'})
                else:
                    elenco.itemconfig(tk.END, {'fg': 'green'})
            except Exception as e:
                elenco.insert(tk.END, filename)
                file_labels.append(filename)

def apri_editor_scheda(dati=None, lingua=None):
    if lingua is None:
        if os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
                prog_data = json.load(f)
            lingua = prog_data.get("lingua", "it")
        else:
            lingua = "it"
    us_id = None
    if dati and "id" in dati:
        us_id = str(dati["id"])
    if us_id and us_id in open_us_windows:
        try:
            open_us_windows[us_id].lift()
            open_us_windows[us_id].focus_force()
        except:
            pass
        return
    editor = tk.Toplevel(root)
    if us_id:
        open_us_windows[us_id] = editor
    def on_close():
        if us_id and us_id in open_us_windows:
            del open_us_windows[us_id]
        editor.destroy()
    editor.protocol("WM_DELETE_WINDOW", on_close)
    editor.title(T("edit_title", lingua) if dati else T("new_title", lingua))

    from tkinter import ttk
    notebook = ttk.Notebook(editor)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # --- TAB 1: Anagrafica ---
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text=T("tab1", lingua))
    row = 0
    tk.Label(tab1, text=T("id", lingua)).grid(row=row, column=0, sticky="e");
    label_id = tk.Label(tab1, text="")
    label_id.grid(row=row, column=1, sticky="w"); row+=1
    tk.Label(tab1, text=T("nr_us", lingua)).grid(row=row, column=0, sticky="e"); entry_nr_us = tk.Entry(tab1); entry_nr_us.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("area_struttura", lingua)).grid(row=row, column=0, sticky="e"); entry_area = tk.Entry(tab1); entry_area.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("saggio", lingua)).grid(row=row, column=0, sticky="e"); entry_saggio = tk.Entry(tab1); entry_saggio.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("settore", lingua)).grid(row=row, column=0, sticky="e"); entry_settore = tk.Entry(tab1); entry_settore.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("quadrato", lingua)).grid(row=row, column=0, sticky="e"); entry_quadrato = tk.Entry(tab1); entry_quadrato.grid(row=row, column=1); row+=1

    # --- TAB 2: Cosa contiene ---
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text=T("tab2", lingua))
    row = 0
    tk.Label(tab2, text=T("criteri_distinzione", lingua)).grid(row=row, column=0, sticky="e"); entry_criteri = tk.Entry(tab2); entry_criteri.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("componenti_organici", lingua)).grid(row=row, column=0, sticky="e"); entry_org = tk.Entry(tab2); entry_org.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("componenti_inorganici", lingua)).grid(row=row, column=0, sticky="e"); entry_inorg = tk.Entry(tab2); entry_inorg.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("consistenza", lingua)).grid(row=row, column=0, sticky="e"); entry_consistenza = ttk.Combobox(tab2, values=[1,2,3,4,5], width=3); entry_consistenza.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("colore", lingua)).grid(row=row, column=0, sticky="e"); entry_colore = tk.Entry(tab2); entry_colore.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("misure", lingua)).grid(row=row, column=0, sticky="e"); entry_misure = tk.Entry(tab2); entry_misure.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("stato_conservazione", lingua)).grid(row=row, column=0, sticky="e"); entry_stato = tk.Entry(tab2); entry_stato.grid(row=row, column=1); row+=1

    # --- TAB 3: Relazioni US ---
    tab3 = tk.Frame(notebook)
    notebook.add(tab3, text=T("tab3", lingua))
    row = 0
    tk.Label(tab3, text=T("copre", lingua)).grid(row=row, column=0, sticky="e"); entry_copre = tk.Entry(tab3); entry_copre.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("uguale_a", lingua)).grid(row=row, column=0, sticky="e"); entry_uguale_a = tk.Entry(tab3); entry_uguale_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("coperto_da", lingua)).grid(row=row, column=0, sticky="e"); entry_coperto_da = tk.Entry(tab3); entry_coperto_da.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("si_lega_a", lingua)).grid(row=row, column=0, sticky="e"); entry_si_lega_a = tk.Entry(tab3); entry_si_lega_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("gli_si_appoggia", lingua)).grid(row=row, column=0, sticky="e"); entry_gli_si_appoggia = tk.Entry(tab3); entry_gli_si_appoggia.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("si_appoggia_a", lingua)).grid(row=row, column=0, sticky="e"); entry_si_appoggia_a = tk.Entry(tab3); entry_si_appoggia_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("taglia", lingua)).grid(row=row, column=0, sticky="e"); entry_taglia = tk.Entry(tab3); entry_taglia.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("tagliato_da", lingua)).grid(row=row, column=0, sticky="e"); entry_tagliato_da = tk.Entry(tab3); entry_tagliato_da.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("riempie", lingua)).grid(row=row, column=0, sticky="e"); entry_riempie = tk.Entry(tab3); entry_riempie.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("riempito_da", lingua)).grid(row=row, column=0, sticky="e"); entry_riempito_da = tk.Entry(tab3); entry_riempito_da.grid(row=row, column=1); row+=1

    # --- TAB 4: Osservazioni ---
    tab4 = tk.Frame(notebook)
    notebook.add(tab4, text=T("tab4", lingua))
    row = 0
    tk.Label(tab4, text=T("descrizione", lingua)).grid(row=row, column=0, sticky="ne"); text_descrizione = tk.Text(tab4, width=40, height=3); text_descrizione.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("osservazioni", lingua)).grid(row=row, column=0, sticky="ne"); text_osservazioni = tk.Text(tab4, width=40, height=2); text_osservazioni.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("interpretazioni", lingua)).grid(row=row, column=0, sticky="ne"); text_interpretazioni = tk.Text(tab4, width=40, height=2); text_interpretazioni.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("datazione", lingua)).grid(row=row, column=0, sticky="e"); entry_datazione = tk.Entry(tab4); entry_datazione.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("elementi_datanti", lingua)).grid(row=row, column=0, sticky="e"); entry_elementi = tk.Entry(tab4); entry_elementi.grid(row=row, column=1); row+=1

    # --- TAB 5: Autore ---
    tab5 = tk.Frame(notebook)
    notebook.add(tab5, text=T("tab5", lingua))
    row = 0
    tk.Label(tab5, text=T("data_rilevamento", lingua)).grid(row=row, column=0, sticky="e"); entry_data_ril = tk.Entry(tab5); entry_data_ril.grid(row=row, column=1); row+=1
    tk.Label(tab5, text=T("responsabile_compilazione", lingua)).grid(row=row, column=0, sticky="e"); entry_responsabile = tk.Entry(tab5); entry_responsabile.grid(row=row, column=1); row+=1

    # Precompila i campi se modifica
    if dati:
        label_id.config(text=str(dati.get("id", "")))
        entry_nr_us.insert(0, str(dati.get("nr_us", "")))
        entry_area.insert(0, dati.get("area_struttura", ""))
        entry_saggio.insert(0, dati.get("saggio", ""))
        entry_settore.insert(0, dati.get("settore", ""))
        entry_quadrato.insert(0, dati.get("quadrato", ""))
        entry_criteri.insert(0, dati.get("criteri_distinzione", ""))
        entry_org.insert(0, dati.get("componenti_organici", ""))
        entry_inorg.insert(0, dati.get("componenti_inorganici", ""))
        entry_consistenza.set(dati.get("consistenza", ""))
        entry_colore.insert(0, dati.get("colore", ""))
        entry_misure.insert(0, dati.get("misure", ""))
        entry_stato.insert(0, dati.get("stato_conservazione", ""))
        entry_copre.insert(0, ",".join(str(n) for n in dati.get("copre", [])))
        entry_uguale_a.insert(0, ",".join(str(n) for n in dati.get("uguale_a", [])))
        entry_coperto_da.insert(0, ",".join(str(n) for n in dati.get("coperto_da", [])))
        entry_si_lega_a.insert(0, ",".join(str(n) for n in dati.get("si_lega_a", [])))
        entry_gli_si_appoggia.insert(0, ",".join(str(n) for n in dati.get("gli_si_appoggia", [])))
        entry_si_appoggia_a.insert(0, ",".join(str(n) for n in dati.get("si_appoggia_a", [])))
        entry_taglia.insert(0, ",".join(str(n) for n in dati.get("taglia", [])))
        entry_tagliato_da.insert(0, ",".join(str(n) for n in dati.get("tagliato_da", [])))
        entry_riempie.insert(0, ",".join(str(n) for n in dati.get("riempie", [])))
        entry_riempito_da.insert(0, ",".join(str(n) for n in dati.get("riempito_da", [])))
        text_descrizione.insert("1.0", dati.get("descrizione", ""))
        text_osservazioni.insert("1.0", dati.get("osservazioni", ""))
        text_interpretazioni.insert("1.0", dati.get("interpretazioni", ""))
        entry_datazione.insert(0, dati.get("datazione", ""))
        entry_elementi.insert(0, dati.get("elementi_datanti", ""))
        entry_data_ril.insert(0, dati.get("data_rilevamento", ""))
        entry_responsabile.insert(0, dati.get("responsabile_compilazione", ""))
    else:
        # Calcola nuovo ID automatico
        try:
            us_files = [f for f in os.listdir(US_DIR) if f.endswith('.json') and f != 'prog_manager.json']
            max_id = 0
            for f in us_files:
                with open(os.path.join(US_DIR, f), encoding="utf-8") as ff:
                    d = json.load(ff)
                    if "id" in d:
                        try:
                            max_id = max(max_id, int(d["id"]))
                        except:
                            pass
            nuovo_id = max_id + 1
        except:
            nuovo_id = 1
        label_id.config(text=str(nuovo_id))

    def salva():
        try:
            nr_us = int(entry_nr_us.get())
        except:
            messagebox.showerror(T("error", lingua) if "error" in TRANSLATIONS[lingua] else "Errore", T("invalid_us_number", lingua) if "invalid_us_number" in TRANSLATIONS[lingua] else "Numero US non valido.")
            return
        if dati:
            id_val = dati.get("id", label_id.cget("text"))
        else:
            id_val = label_id.cget("text")
        try:
            copre = [int(x.strip()) for x in entry_copre.get().split(",") if x.strip()]
            uguale_a = [int(x.strip()) for x in entry_uguale_a.get().split(",") if x.strip()]
            coperto_da = [int(x.strip()) for x in entry_coperto_da.get().split(",") if x.strip()]
            si_lega_a = [int(x.strip()) for x in entry_si_lega_a.get().split(",") if x.strip()]
            gli_si_appoggia = [int(x.strip()) for x in entry_gli_si_appoggia.get().split(",") if x.strip()]
            si_appoggia_a = [int(x.strip()) for x in entry_si_appoggia_a.get().split(",") if x.strip()]
            taglia = [int(x.strip()) for x in entry_taglia.get().split(",") if x.strip()]
            tagliato_da = [int(x.strip()) for x in entry_tagliato_da.get().split(",") if x.strip()]
            riempie = [int(x.strip()) for x in entry_riempie.get().split(",") if x.strip()]
            riempito_da = [int(x.strip()) for x in entry_riempito_da.get().split(",") if x.strip()]
        except:
            messagebox.showerror(T("error", lingua) if "error" in TRANSLATIONS[lingua] else "Errore", T("relations_must_be_numbers", lingua) if "relations_must_be_numbers" in TRANSLATIONS[lingua] else "Le relazioni devono essere numeri separati da virgole.")
            return
        scheda = {
            "id": id_val,
            "nr_us": nr_us,
            "area_struttura": entry_area.get(),
            "saggio": entry_saggio.get(),
            "settore": entry_settore.get(),
            "quadrato": entry_quadrato.get(),
            "criteri_distinzione": entry_criteri.get(),
            "componenti_organici": entry_org.get(),
            "componenti_inorganici": entry_inorg.get(),
            "consistenza": entry_consistenza.get(),
            "colore": entry_colore.get(),
            "misure": entry_misure.get(),
            "stato_conservazione": entry_stato.get(),
            "copre": copre,
            "uguale_a": uguale_a,
            "coperto_da": coperto_da,
            "si_lega_a": si_lega_a,
            "gli_si_appoggia": gli_si_appoggia,
            "si_appoggia_a": si_appoggia_a,
            "taglia": taglia,
            "tagliato_da": tagliato_da,
            "riempie": riempie,
            "riempito_da": riempito_da,
            "descrizione": text_descrizione.get("1.0", "end").strip(),
            "osservazioni": text_osservazioni.get("1.0", "end").strip(),
            "interpretazioni": text_interpretazioni.get("1.0", "end").strip(),
            "datazione": entry_datazione.get(),
            "elementi_datanti": entry_elementi.get(),
            "data_rilevamento": entry_data_ril.get(),
            "responsabile_compilazione": entry_responsabile.get()
        }
        salva_scheda(scheda)
        messagebox.showinfo(T("saved", lingua) if "saved" in TRANSLATIONS[lingua] else "Salvato", f"{T('card', lingua) if 'card' in TRANSLATIONS[lingua] else 'Scheda'} US[{nr_us}] {'aggiornata' if dati else 'creata'}.")
        aggiorna_elenco(lingua=lingua)
        editor.destroy()

    tk.Button(editor, text="💾 Salva", command=lambda: [salva(), on_close()]).pack(pady=10)

# Funzione per aprire una scheda per la modifica
# (deve essere visibile prima di avvia_gui_principale)
def apri_scheda_per_modifica(lingua=None):
    selezione = elenco.curselection()
    if not selezione:
        return
    idx = selezione[0]
    filename = file_labels[idx]
    filepath = os.path.join(US_DIR, filename)
    with open(filepath, encoding="utf-8") as f:
        dati = json.load(f)
    apri_editor_scheda(dati, lingua=lingua)

# Funzione per avviare la GUI principale
def avvia_gui_principale():
    global elenco
    # Carica dati progetto
    if os.path.exists(PROG_MANAGER_PATH):
        with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
            prog_data = json.load(f)
    else:
        prog_data = {}
    lingua = prog_data.get("lingua", "it")
    root.deiconify()  # Mostra la finestra principale
    root.title(prog_data.get("nome_progetto", T("main_title", lingua)))
    # Pulisci la finestra se già usata
    for widget in root.winfo_children():
        widget.destroy()
    # Imposta la finestra a schermo intero
    root.state('zoomed')
    # Titolo grande e bold
    titolo = prog_data.get("nome_progetto", T("main_title", lingua))
    label_titolo = tk.Label(root, text=titolo, font=("TkDefaultFont", 14, "bold"))
    label_titolo.pack(pady=(10, 2))

    # --- MENU VERTICALE A SINISTRA ---
    left_menu = tk.Frame(root)
    left_menu.pack(side="left", padx=(10,0), pady=10, fill="y")
    btn_plus = tk.Button(left_menu, text=T("new_card", lingua), width=18, height=2, command=lambda: apri_editor_scheda(lingua=lingua))
    btn_plus.pack(pady=(0, 10))
    btn_edit = tk.Button(left_menu, text=T("edit_card", lingua), width=18, height=2, command=lambda: apri_scheda_per_modifica(lingua=lingua))
    btn_edit.pack(pady=(0, 10))
    # Pulsante Cancella scheda
    def elimina_scheda():
        selezione = elenco.curselection()
        if not selezione:
            messagebox.showinfo(T("delete_card", lingua), T("select_card_to_delete", lingua) if "select_card_to_delete" in TRANSLATIONS[lingua] else "Seleziona una scheda da eliminare.")
            return
        idx = selezione[0]
        filename = file_labels[idx]
        risposta = messagebox.askyesno(T("confirm_delete", lingua) if "confirm_delete" in TRANSLATIONS[lingua] else "Conferma eliminazione", f"{T('delete_card', lingua)} {filename}?")
        if risposta:
            try:
                os.remove(os.path.join(US_DIR, filename))
                aggiorna_elenco()
                messagebox.showinfo(T("deleted", lingua) if "deleted" in TRANSLATIONS[lingua] else "Eliminata", f"{T('delete_card', lingua)} {filename} {T('deleted', lingua) if 'deleted' in TRANSLATIONS[lingua] else 'eliminata'}.")
            except Exception as e:
                messagebox.showerror(
                    T("error", lingua) if "error" in TRANSLATIONS[lingua] else "Errore",
                    f"{T('error_deleting', lingua) if 'error_deleting' in TRANSLATIONS[lingua] else 'Errore durante l\'eliminazione'}: {e}"
                )
    btn_delete = tk.Button(left_menu, text=T("delete_card", lingua), width=18, height=2, command=elimina_scheda)
    btn_delete.pack(pady=(0, 10))
    btn_editor_matrix = tk.Button(left_menu, text=T("editor_matrix", lingua), width=18, height=2, command=visualizza_harris_matrix)
    btn_editor_matrix.pack(pady=(0, 10))
    btn_export_csv2 = tk.Button(left_menu, text=T("export_csv", lingua), width=18, height=2, command=esporta_us_csv)
    btn_export_csv2.pack(pady=(0, 10))
    btn_export_matrix = tk.Button(left_menu, text=T("export_matrix", lingua), width=18, height=2, command=esporta_matrix_svg)
    btn_export_matrix.pack(pady=(0, 10))

    # --- DATI DI PROGETTO (frame verticale sotto i pulsanti) ---
    project_frame = tk.Frame(left_menu)
    project_frame.pack(pady=(30, 0), anchor="nw", fill="x")
    project_labels = [
        (T("project_code", lingua)+":", prog_data.get('codice_progetto', '')),
        (T("street", lingua)+":", prog_data.get('via', '')),
        (T("city", lingua)+":", prog_data.get('comune', '')),
        (T("province", lingua)+":", prog_data.get('provincia', '')),
        (T("year", lingua)+":", prog_data.get('anno', '')),
        (T("ente", lingua)+":", prog_data.get('ente_responsabile', '')),
        (T("ufficio", lingua)+":", prog_data.get('ufficio_mic', ''))
    ]
    for i, (label, value) in enumerate(project_labels):
        tk.Label(project_frame, text=label, anchor="w", font=("TkDefaultFont", 9, "bold"), width=20, justify="left").grid(row=i, column=0, sticky="w")
        tk.Label(project_frame, text=value, anchor="w", font=("TkDefaultFont", 9), width=22, justify="left", wraplength=180).grid(row=i, column=1, sticky="w")

    # --- FRAME CENTRALE: Matrix di Harris ---
    center_frame = tk.Frame(root)
    center_frame.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
    matrix_canvas = tk.Canvas(center_frame, bg="white")
    matrix_canvas.pack(fill="both", expand=True)

    # Pulsante refresh matrix sopra il canvas
    refresh_btn = tk.Button(center_frame, text="\u21bb", width=2, height=1, command=lambda: draw_matrix_on_canvas(matrix_canvas))
    refresh_btn.pack(anchor="ne", padx=2, pady=(0,2))

    # --- LISTA DELLE SCHEDE US ---
    elenco_frame = tk.Frame(root)
    elenco_frame.pack(pady=10, side="left", fill="y", padx=(30,0))
    elenco_scroll = tk.Scrollbar(elenco_frame, orient="vertical")
    elenco_scroll.pack(side="right", fill="y")
    elenco = tk.Listbox(elenco_frame, width=60, height=30, yscrollcommand=elenco_scroll.set)
    elenco.pack(side="left", fill="y")
    elenco_scroll.config(command=elenco.yview)

    aggiorna_elenco(lingua=lingua)

    # --- Disegna Matrix di Harris nella home ---
    def draw_matrix_on_canvas(canvas):
        # Carica tutte le schede dalla directory
        schede = []
        for filename in sorted(os.listdir(US_DIR)):
            if filename.endswith(".json") and filename != "prog_manager.json":
                filepath = os.path.join(US_DIR, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        if "nr_us" in data:
                            schede.append(data)
                except Exception as e:
                    pass
        if not schede:
            return
        nodes = {s['nr_us']: s for s in schede}
        edges_set = set()
        # Relazioni madre-figlia (madre -> figlia)
        madre_figlia = [
            ("copre", False), ("riempie", False), ("taglia", False), ("si_appoggia_a", False), ("si_lega_a", False)
        ]
        # Relazioni figlia-madre (invertite: madre <- figlia)
        figlia_madre = [
            ("coperto_da", True), ("riempito_da", True), ("tagliato_da", True), ("gli_si_appoggia", True)
        ]
        for s in schede:
            u = s['nr_us']
            for rel, inverti in madre_figlia:
                for v in s.get(rel, []):
                    if v in nodes:
                        edges_set.add((u, v))
            for rel, inverti in figlia_madre:
                for v in s.get(rel, []):
                    if v in nodes:
                        edges_set.add((v, u))
        edges = list(edges_set)
        uguale_edges = set()
        for s in schede:
            u = s['nr_us']
            for v in s.get("uguale_a", []):
                if v in nodes:
                    pair = tuple(sorted([u, v]))
                    uguale_edges.add(pair)
        levels = {n: 0 for n in nodes}
        changed = True
        while changed:
            changed = False
            for (u, v) in edges:
                if levels[v] < levels[u] + 1:
                    levels[v] = levels[u] + 1
                    changed = True
        levels_group = {}
        for n, lvl in levels.items():
            levels_group.setdefault(lvl, []).append(n)
        # RIMOSSO OGNI ORDINAMENTO NUMERICO: non ordinare i livelli numericamente
        # for lvl in levels_group:
        #     levels_group[lvl].sort()
        max_level = max(levels_group.keys())
        box_width = 80
        box_height = 40
        h_spacing = 40
        v_spacing = 80
        max_nodes_in_row = max(len(group) for group in levels_group.values())
        canvas_width = max_nodes_in_row * (box_width + h_spacing) + h_spacing
        canvas_height = (max_level + 1) * (box_height + v_spacing) + v_spacing
        # Aggiorna dimensione canvas
        canvas.config(scrollregion=(0,0,canvas_width,canvas_height))
        positions = {}
        # Carica posizioni personalizzate se esistono
        pos_path = os.path.join(US_DIR, "positions.json")
        custom_positions = {}
        if os.path.exists(pos_path):
            try:
                with open(pos_path, "r", encoding="utf-8") as f:
                    custom_positions = json.load(f)
            except Exception:
                custom_positions = {}
        for lvl in range(max_level + 1):
            if lvl in levels_group:
                nodes_in_level = levels_group[lvl]
                count = len(nodes_in_level)
                total_width = count * box_width + (count - 1) * h_spacing
                start_x = (canvas_width - total_width) / 2
                y = v_spacing + lvl * (box_height + v_spacing)
                for index, n in enumerate(nodes_in_level):
                    if str(n) in custom_positions:
                        x, y = custom_positions[str(n)]
                        positions[n] = (x, y, x + box_width, y + box_height)
                    else:
                        x = start_x + index * (box_width + h_spacing)
                        positions[n] = (x, y, x + box_width, y + box_height)
        # --- Disegno ---
        canvas.delete("all")
        # 1. Calcola i livelli dei nodi (gerarchia):
        #    - Ogni relazione (copre, riempie, taglia, ecc.) fa salire di livello il target
        #    - Il livello più basso (0) sono le US senza relazioni entranti
        # 2. Per ogni relazione, disegna una linea 1 a 1 tra le US, senza merge point
        # 3. Se una US ha più relazioni entranti, disegna le linee separatamente (no merge)
        # 4. Se una US ha più relazioni uscenti, disegna le linee separatamente
        # --- Calcolo merge point per relazioni convergenti ---
        # 1. Calcola per ogni US quante relazioni entranti ha
        incoming = {}
        for (u, v) in edges:
            incoming.setdefault(v, []).append(u)
        # 2. Disegna le relazioni con merge point solo dove necessario
        canvas.delete("all")
        handled = set()
        for target, sources in incoming.items():
            if len(sources) > 1 and target in positions:
                # Merge point: convergenza delle linee
                x3, y3, x4, y4 = positions[target]
                end_x = (x3 + x4) / 2
                end_y = y3
                merge_y = end_y - 30
                merge_x = end_x
                # Da ogni sorgente, linea verticale fino a merge_y, poi orizzontale fino al merge point
                for src in sources:
                    if src not in positions:
                        continue
                    x1, y1, x2, y2 = positions[src]
                    start_x = (x1 + x2) / 2
                    start_y = y2
                    canvas.create_line(start_x, start_y, start_x, merge_y, fill="black")
                    if abs(start_x - merge_x) > 2:
                        canvas.create_line(start_x, merge_y, merge_x, merge_y, fill="black")
                # Dal merge point, una sola linea verticale verso la US target
                canvas.create_line(merge_x, merge_y, end_x, end_y, fill="black")
                for src in sources:
                    handled.add((src, target))
        # 3. Tutte le altre relazioni (no merge point)
        for (u, v) in edges:
            if (u, v) in handled:
                continue
            if u in positions and v in positions:
                x1, y1, x2, y2 = positions[u]
                x3, y3, x4, y4 = positions[v]
                start_x = (x1 + x2) / 2
                start_y = y2
                end_x = (x3 + x4) / 2
                end_y = y3
                if abs(start_x - end_x) < 2:
                    canvas.create_line(start_x, start_y, end_x, end_y, fill="black")
                else:
                    mid_y = (start_y + end_y) / 2
                    canvas.create_line(start_x, start_y, start_x, mid_y, fill="black")
                    canvas.create_line(start_x, mid_y, end_x, mid_y, fill="black")
                    canvas.create_line(end_x, mid_y, end_x, end_y, fill="black")
        # Relazioni uguale_a (rosse tratteggiate)
        for (u, v) in uguale_edges:
            if u in positions and v in positions:
                cx_u = (positions[u][0] + positions[u][2]) / 2
                cy_u = (positions[u][1] + positions[u][3]) / 2
                cx_v = (positions[v][0] + positions[v][2]) / 2
                cy_v = (positions[v][1] + positions[v][3]) / 2
                canvas.create_line(cx_u, cy_u, cx_v, cy_v, dash=(4, 2), fill="red")
        for n, coords in positions.items():
            x1, y1, x2, y2 = coords
            canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"US {n}")

    # Navigazione e zoom
    matrix_canvas.bind('<Configure>', lambda e: draw_matrix_on_canvas(matrix_canvas))
    matrix_canvas.bind('<ButtonPress-1>', lambda e: setattr(matrix_canvas, '_drag_data', (e.x, e.y, matrix_canvas.xview()[0], matrix_canvas.yview()[0])))
    def on_drag(event):
        if hasattr(matrix_canvas, '_drag_data'):
            x, y, x0, y0 = matrix_canvas._drag_data
            dx = (x - event.x) / matrix_canvas.winfo_width()
            dy = (y - event.y) / matrix_canvas.winfo_height()
            matrix_canvas.xview_moveto(x0 + dx)
            matrix_canvas.yview_moveto(y0 + dy)
    matrix_canvas.bind('<B1-Motion>', on_drag)
    def on_mousewheel(event, canvas=matrix_canvas):
        # Zoom centrato sul mouse
        factor = 1.1 if event.delta > 0 else 0.9
        # Semplice zoom su tutto il canvas
        canvas.scale('all', event.x, event.y, factor, factor)

    def on_arrow(event):
        # Funzione placeholder: nessun offset gestito
        pass
    # Bind mouse wheel (Windows/Mac/Linux)
    matrix_canvas.bind("<MouseWheel>", lambda e: on_mousewheel(e, matrix_canvas))
    matrix_canvas.bind("<Button-4>", lambda e: on_mousewheel(type('event', (), {'delta': 120, 'x': e.x, 'y': e.y}), matrix_canvas))  # Linux scroll up
    matrix_canvas.bind("<Button-5>", lambda e: on_mousewheel(type('event', (), {'delta': -120, 'x': e.x, 'y': e.y}), matrix_canvas)) # Linux scroll down
    matrix_canvas.bind('<MouseWheel>', on_mousewheel)
    matrix_canvas.bind('<Button-4>', lambda e: on_mousewheel(type('event', (), {'delta': 120, 'x': e.x, 'y': e.y})))
    matrix_canvas.bind('<Button-5>', lambda e: on_mousewheel(type('event', (), {'delta': -120, 'x': e.x, 'y': e.y})))

    # Scrollbar per canvas
    x_scroll = tk.Scrollbar(center_frame, orient='horizontal', command=matrix_canvas.xview)
    y_scroll = tk.Scrollbar(center_frame, orient='vertical', command=matrix_canvas.yview)
    matrix_canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    x_scroll.pack(side='bottom', fill='x')
    y_scroll.pack(side='right', fill='y')

    # Aumenta la dimensione della finestra principale (ora a schermo intero)
    root.update()

    # Label "Made by Mattia Curto" in basso a sinistra
    label_credito = tk.Label(root, text=T("credit", lingua) if "credit" in TRANSLATIONS[lingua] else "Made by Mattia Curto", font=("TkDefaultFont", 9, "italic"), anchor="sw")
    label_credito.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-5)

def salva_scheda(scheda):
    # Carica parametri progetto e aggiungili alla scheda
    if os.path.exists(PROG_MANAGER_PATH):
        with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
            prog_data = json.load(f)
        scheda.update(prog_data)
    filename = f"US{scheda['nr_us']}.json"
    filepath = os.path.join(US_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scheda, f, indent=4, ensure_ascii=False)

# Funzione per aggiornare l'elenco delle schede
file_labels = []  # lista globale per mappare le righe della listbox ai file reali

def aggiorna_elenco(lingua=None):
    global file_labels, elenco
    if lingua is None:
        if os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
                prog_data = json.load(f)
            lingua = prog_data.get("lingua", "it")
        else:
            lingua = "it"
    elenco.delete(0, tk.END)
    file_labels = []
    for filename in sorted(os.listdir(US_DIR)):
        if filename.endswith(".json") and filename not in ("prog_manager.json", "positions.json"):
            filepath = os.path.join(US_DIR, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    dati = json.load(f)
                responsabile = dati.get("responsabile_compilazione", "-")
                data_ril = dati.get("data_rilevamento", "-")
                required_fields = [
                    "nr_us", "area_struttura", "saggio", "settore", "quadrato",
                    "criteri_distinzione", "componenti_organici", "componenti_inorganici",
                    "consistenza", "colore", "misure", "stato_conservazione",
                    "descrizione", "osservazioni", "interpretazioni", "datazione",
                    "elementi_datanti", "data_rilevamento", "responsabile_compilazione"
                ]
                complete = all(str(dati.get(f, "")).strip() for f in required_fields)
                stato = T("complete", lingua) if complete and "complete" in TRANSLATIONS[lingua] else ("COMPLETA" if complete else (T("partial", lingua) if "partial" in TRANSLATIONS[lingua] else "PARZIALE"))
                label = f"{filename} | {responsabile} | {data_ril} | {stato}"
                elenco.insert(tk.END, label)
                file_labels.append(filename)
                # Colorazione
                if not complete:
                    elenco.itemconfig(tk.END, {'fg': 'orange'})
                else:
                    elenco.itemconfig(tk.END, {'fg': 'green'})
            except Exception as e:
                elenco.insert(tk.END, filename)
                file_labels.append(filename)

# Funzione per aprire l'editor (creazione o modifica)
def apri_editor_scheda(dati=None, lingua=None):
    if lingua is None:
        if os.path.exists(PROG_MANAGER_PATH):
            with open(PROG_MANAGER_PATH, encoding="utf-8") as f:
                prog_data = json.load(f)
            lingua = prog_data.get("lingua", "it")
        else:
            lingua = "it"
    us_id = None
    if dati and "id" in dati:
        us_id = str(dati["id"])
    if us_id and us_id in open_us_windows:
        try:
            open_us_windows[us_id].lift()
            open_us_windows[us_id].focus_force()
        except:
            pass
        return
    editor = tk.Toplevel(root)
    if us_id:
        open_us_windows[us_id] = editor
    def on_close():
        if us_id and us_id in open_us_windows:
            del open_us_windows[us_id]
        editor.destroy()
    editor.protocol("WM_DELETE_WINDOW", on_close)
    editor.title(T("edit_title", lingua) if dati else T("new_title", lingua))

    from tkinter import ttk
    notebook = ttk.Notebook(editor)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # --- TAB 1: Anagrafica ---
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text=T("tab1", lingua))
    row = 0
    tk.Label(tab1, text=T("id", lingua)).grid(row=row, column=0, sticky="e");
    label_id = tk.Label(tab1, text="")
    label_id.grid(row=row, column=1, sticky="w"); row+=1
    tk.Label(tab1, text=T("nr_us", lingua)).grid(row=row, column=0, sticky="e"); entry_nr_us = tk.Entry(tab1); entry_nr_us.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("area_struttura", lingua)).grid(row=row, column=0, sticky="e"); entry_area = tk.Entry(tab1); entry_area.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("saggio", lingua)).grid(row=row, column=0, sticky="e"); entry_saggio = tk.Entry(tab1); entry_saggio.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("settore", lingua)).grid(row=row, column=0, sticky="e"); entry_settore = tk.Entry(tab1); entry_settore.grid(row=row, column=1); row+=1
    tk.Label(tab1, text=T("quadrato", lingua)).grid(row=row, column=0, sticky="e"); entry_quadrato = tk.Entry(tab1); entry_quadrato.grid(row=row, column=1); row+=1

    # --- TAB 2: Cosa contiene ---
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text=T("tab2", lingua))
    row = 0
    tk.Label(tab2, text=T("criteri_distinzione", lingua)).grid(row=row, column=0, sticky="e"); entry_criteri = tk.Entry(tab2); entry_criteri.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("componenti_organici", lingua)).grid(row=row, column=0, sticky="e"); entry_org = tk.Entry(tab2); entry_org.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("componenti_inorganici", lingua)).grid(row=row, column=0, sticky="e"); entry_inorg = tk.Entry(tab2); entry_inorg.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("consistenza", lingua)).grid(row=row, column=0, sticky="e"); entry_consistenza = ttk.Combobox(tab2, values=[1,2,3,4,5], width=3); entry_consistenza.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("colore", lingua)).grid(row=row, column=0, sticky="e"); entry_colore = tk.Entry(tab2); entry_colore.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("misure", lingua)).grid(row=row, column=0, sticky="e"); entry_misure = tk.Entry(tab2); entry_misure.grid(row=row, column=1); row+=1
    tk.Label(tab2, text=T("stato_conservazione", lingua)).grid(row=row, column=0, sticky="e"); entry_stato = tk.Entry(tab2); entry_stato.grid(row=row, column=1); row+=1

    # --- TAB 3: Relazioni US ---
    tab3 = tk.Frame(notebook)
    notebook.add(tab3, text=T("tab3", lingua))
    row = 0
    tk.Label(tab3, text=T("copre", lingua)).grid(row=row, column=0, sticky="e"); entry_copre = tk.Entry(tab3); entry_copre.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("uguale_a", lingua)).grid(row=row, column=0, sticky="e"); entry_uguale_a = tk.Entry(tab3); entry_uguale_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("coperto_da", lingua)).grid(row=row, column=0, sticky="e"); entry_coperto_da = tk.Entry(tab3); entry_coperto_da.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("si_lega_a", lingua)).grid(row=row, column=0, sticky="e"); entry_si_lega_a = tk.Entry(tab3); entry_si_lega_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("gli_si_appoggia", lingua)).grid(row=row, column=0, sticky="e"); entry_gli_si_appoggia = tk.Entry(tab3); entry_gli_si_appoggia.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("si_appoggia_a", lingua)).grid(row=row, column=0, sticky="e"); entry_si_appoggia_a = tk.Entry(tab3); entry_si_appoggia_a.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("taglia", lingua)).grid(row=row, column=0, sticky="e"); entry_taglia = tk.Entry(tab3); entry_taglia.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("tagliato_da", lingua)).grid(row=row, column=0, sticky="e"); entry_tagliato_da = tk.Entry(tab3); entry_tagliato_da.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("riempie", lingua)).grid(row=row, column=0, sticky="e"); entry_riempie = tk.Entry(tab3); entry_riempie.grid(row=row, column=1); row+=1
    tk.Label(tab3, text=T("riempito_da", lingua)).grid(row=row, column=0, sticky="e"); entry_riempito_da = tk.Entry(tab3); entry_riempito_da.grid(row=row, column=1); row+=1

    # --- TAB 4: Osservazioni ---
    tab4 = tk.Frame(notebook)
    notebook.add(tab4, text=T("tab4", lingua))
    row = 0
    tk.Label(tab4, text=T("descrizione", lingua)).grid(row=row, column=0, sticky="ne"); text_descrizione = tk.Text(tab4, width=40, height=3); text_descrizione.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("osservazioni", lingua)).grid(row=row, column=0, sticky="ne"); text_osservazioni = tk.Text(tab4, width=40, height=2); text_osservazioni.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("interpretazioni", lingua)).grid(row=row, column=0, sticky="ne"); text_interpretazioni = tk.Text(tab4, width=40, height=2); text_interpretazioni.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("datazione", lingua)).grid(row=row, column=0, sticky="e"); entry_datazione = tk.Entry(tab4); entry_datazione.grid(row=row, column=1); row+=1
    tk.Label(tab4, text=T("elementi_datanti", lingua)).grid(row=row, column=0, sticky="e"); entry_elementi = tk.Entry(tab4); entry_elementi.grid(row=row, column=1); row+=1

    # --- TAB 5: Autore ---
    tab5 = tk.Frame(notebook)
    notebook.add(tab5, text=T("tab5", lingua))
    row = 0
    tk.Label(tab5, text=T("data_rilevamento", lingua)).grid(row=row, column=0, sticky="e"); entry_data_ril = tk.Entry(tab5); entry_data_ril.grid(row=row, column=1); row+=1
    tk.Label(tab5, text=T("responsabile_compilazione", lingua)).grid(row=row, column=0, sticky="e"); entry_responsabile = tk.Entry(tab5); entry_responsabile.grid(row=row, column=1); row+=1

    # Precompila i campi se modifica
    if dati:
        label_id.config(text=str(dati.get("id", "")))
        entry_nr_us.insert(0, str(dati.get("nr_us", "")))
        entry_area.insert(0, dati.get("area_struttura", ""))
        entry_saggio.insert(0, dati.get("saggio", ""))
        entry_settore.insert(0, dati.get("settore", ""))
        entry_quadrato.insert(0, dati.get("quadrato", ""))
        entry_criteri.insert(0, dati.get("criteri_distinzione", ""))
        entry_org.insert(0, dati.get("componenti_organici", ""))
        entry_inorg.insert(0, dati.get("componenti_inorganici", ""))
        entry_consistenza.set(dati.get("consistenza", ""))
        entry_colore.insert(0, dati.get("colore", ""))
        entry_misure.insert(0, dati.get("misure", ""))
        entry_stato.insert(0, dati.get("stato_conservazione", ""))
        entry_copre.insert(0, ",".join(str(n) for n in dati.get("copre", [])))
        entry_uguale_a.insert(0, ",".join(str(n) for n in dati.get("uguale_a", [])))
        entry_coperto_da.insert(0, ",".join(str(n) for n in dati.get("coperto_da", [])))
        entry_si_lega_a.insert(0, ",".join(str(n) for n in dati.get("si_lega_a", [])))
        entry_gli_si_appoggia.insert(0, ",".join(str(n) for n in dati.get("gli_si_appoggia", [])))
        entry_si_appoggia_a.insert(0, ",".join(str(n) for n in dati.get("si_appoggia_a", [])))
        entry_taglia.insert(0, ",".join(str(n) for n in dati.get("taglia", [])))
        entry_tagliato_da.insert(0, ",".join(str(n) for n in dati.get("tagliato_da", [])))
        entry_riempie.insert(0, ",".join(str(n) for n in dati.get("riempie", [])))
        entry_riempito_da.insert(0, ",".join(str(n) for n in dati.get("riempito_da", [])))
        text_descrizione.insert("1.0", dati.get("descrizione", ""))
        text_osservazioni.insert("1.0", dati.get("osservazioni", ""))
        text_interpretazioni.insert("1.0", dati.get("interpretazioni", ""))
        entry_datazione.insert(0, dati.get("datazione", ""))
        entry_elementi.insert(0, dati.get("elementi_datanti", ""))
        entry_data_ril.insert(0, dati.get("data_rilevamento", ""))
        entry_responsabile.insert(0, dati.get("responsabile_compilazione", ""))
    else:
        # Calcola nuovo ID automatico
        try:
            us_files = [f for f in os.listdir(US_DIR) if f.endswith('.json') and f != 'prog_manager.json']
            max_id = 0
            for f in us_files:
                with open(os.path.join(US_DIR, f), encoding="utf-8") as ff:
                    d = json.load(ff)
                    if "id" in d:
                        try:
                            max_id = max(max_id, int(d["id"]))
                        except:
                            pass
            nuovo_id = max_id + 1
        except:
            nuovo_id = 1
        label_id.config(text=str(nuovo_id))

    def salva():
        try:
            nr_us = int(entry_nr_us.get())
        except:
            messagebox.showerror(T("error", lingua) if "error" in TRANSLATIONS[lingua] else "Errore", T("invalid_us_number", lingua) if "invalid_us_number" in TRANSLATIONS[lingua] else "Numero US non valido.")
            return
        if dati:
            id_val = dati.get("id", label_id.cget("text"))
        else:
            id_val = label_id.cget("text")
        try:
            copre = [int(x.strip()) for x in entry_copre.get().split(",") if x.strip()]
            uguale_a = [int(x.strip()) for x in entry_uguale_a.get().split(",") if x.strip()]
            coperto_da = [int(x.strip()) for x in entry_coperto_da.get().split(",") if x.strip()]
            si_lega_a = [int(x.strip()) for x in entry_si_lega_a.get().split(",") if x.strip()]
            gli_si_appoggia = [int(x.strip()) for x in entry_gli_si_appoggia.get().split(",") if x.strip()]
            si_appoggia_a = [int(x.strip()) for x in entry_si_appoggia_a.get().split(",") if x.strip()]
            taglia = [int(x.strip()) for x in entry_taglia.get().split(",") if x.strip()]
            tagliato_da = [int(x.strip()) for x in entry_tagliato_da.get().split(",") if x.strip()]
            riempie = [int(x.strip()) for x in entry_riempie.get().split(",") if x.strip()]
            riempito_da = [int(x.strip()) for x in entry_riempito_da.get().split(",") if x.strip()]
        except:
            messagebox.showerror(T("error", lingua) if "error" in TRANSLATIONS[lingua] else "Errore", T("relations_must_be_numbers", lingua) if "relations_must_be_numbers" in TRANSLATIONS[lingua] else "Le relazioni devono essere numeri separati da virgole.")
            return
        scheda = {
            "id": id_val,
            "nr_us": nr_us,
            "area_struttura": entry_area.get(),
            "saggio": entry_saggio.get(),
            "settore": entry_settore.get(),
            "quadrato": entry_quadrato.get(),
            "criteri_distinzione": entry_criteri.get(),
            "componenti_organici": entry_org.get(),
            "componenti_inorganici": entry_inorg.get(),
            "consistenza": entry_consistenza.get(),
            "colore": entry_colore.get(),
            "misure": entry_misure.get(),
            "stato_conservazione": entry_stato.get(),
            "copre": copre,
            "uguale_a": uguale_a,
            "coperto_da": coperto_da,
            "si_lega_a": si_lega_a,
            "gli_si_appoggia": gli_si_appoggia,
            "si_appoggia_a": si_appoggia_a,
            "taglia": taglia,
            "tagliato_da": tagliato_da,
            "riempie": riempie,
            "riempito_da": riempito_da,
            "descrizione": text_descrizione.get("1.0", "end").strip(),
            "osservazioni": text_osservazioni.get("1.0", "end").strip(),
            "interpretazioni": text_interpretazioni.get("1.0", "end").strip(),
            "datazione": entry_datazione.get(),
            "elementi_datanti": entry_elementi.get(),
            "data_rilevamento": entry_data_ril.get(),
            "responsabile_compilazione": entry_responsabile.get()
        }
        salva_scheda(scheda)
        messagebox.showinfo(T("saved", lingua) if "saved" in TRANSLATIONS[lingua] else "Salvato", f"{T('card', lingua) if 'card' in TRANSLATIONS[lingua] else 'Scheda'} US[{nr_us}] {'aggiornata' if dati else 'creata'}.")
        aggiorna_elenco(lingua=lingua)
        editor.destroy()

    tk.Button(editor, text="💾 Salva", command=lambda: [salva(), on_close()]).pack(pady=10)

# Funzione per aprire scheda in modifica
def apri_scheda_per_modifica(lingua=None):
    global elenco, file_labels
    selezione = elenco.curselection()
    if not selezione:
        return
    idx = selezione[0]
    filename = file_labels[idx]
    filepath = os.path.join(US_DIR, filename)
    with open(filepath, encoding="utf-8") as f:
        dati = json.load(f)
    apri_editor_scheda(dati, lingua=lingua)

# Funzione per visualizzare il matrix di Harris
def visualizza_harris_matrix():
    if open_matrix_window[0] is not None and open_matrix_window[0].winfo_exists():
        open_matrix_window[0].lift()
        open_matrix_window[0].focus_force()
        return
    # Carica tutte le schede dalla directory
    schede = []
    for filename in sorted(os.listdir(US_DIR)):
        if filename.endswith(".json") and filename != "prog_manager.json":
            filepath = os.path.join(US_DIR, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                    if "nr_us" in data:
                        schede.append(data)
            except Exception as e:
                print(f"Errore leggendo {filename}: {e}")
    if not schede:
        messagebox.showinfo("Matrix di Harris", "Nessuna scheda disponibile per visualizzare la matrix.")
        return

    # Crea un dizionario di nodi basato su nr_us
    nodes = {s['nr_us']: s for s in schede}

    # Costruisce le relazioni SOLO come indicato in "copre" e "coperto_da" (no duplicati, no simmetrie)
    edges_set = set()
    for s in schede:
        u = s['nr_us']
        # Relazioni dirette: u copre v
        for v in s.get("copre", []):
            if v in nodes:
                edges_set.add((u, v))
        # Relazioni dirette: u è coperto da v (quindi v -> u)
        for v in s.get("coperto_da", []):
            if v in nodes:
                edges_set.add((v, u))
        for v in s.get("si_lega_a", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("gli_si_appoggia", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("si_appoggia_a", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("taglia", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("tagliato_da", []):
            if v in nodes:
                edges_set.add((v, u))
        for v in s.get("riempie", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("riempito_da", []):
            if v in nodes:
                edges_set.add((v, u))
    edges = list(edges_set)
    uguale_edges = set()
    for s in schede:
        u = s['nr_us']
        for v in s.get("uguale_a", []):
            if v in nodes:
                pair = tuple(sorted([u, v]))
                uguale_edges.add(pair)
    levels = {n: 0 for n in nodes}
    changed = True
    while changed:
        changed = False
        for (u, v) in edges:
            if levels[v] < levels[u] + 1:
                levels[v] = levels[u] + 1
                changed = True
    levels_group = {}
    for n, lvl in levels.items():
        levels_group.setdefault(lvl, []).append(n)
    # RIMOSSO OGNI ORDINAMENTO NUMERICO: non ordinare i livelli numericamente
    # for lvl in levels_group:
    #     levels_group[lvl].sort()
    max_level = max(levels_group.keys())
    box_width = 80
    box_height = 40
    h_spacing = 40
    v_spacing = 80
    max_nodes_in_row = max(len(group) for group in levels_group.values())
    canvas_width = int(max_nodes_in_row * (box_width + h_spacing) + h_spacing)
    canvas_height = int((max_level + 1) * (box_height + v_spacing) + v_spacing)
    editor_win = tk.Toplevel(root)
    editor_win.title("Editor Matrix di Harris")
    editor_win.geometry(f"{canvas_width+40}x{canvas_height+40}")
    # Sostituisco il canvas con una struttura con barre di scorrimento
    canvas_frame = tk.Frame(editor_win)
    canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)
    x_scroll = tk.Scrollbar(canvas_frame, orient='horizontal')
    y_scroll = tk.Scrollbar(canvas_frame, orient='vertical')
    canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg="white",
                      xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set,
                      scrollregion=(0,0,canvas_width,canvas_height))
    canvas.grid(row=0, column=0, sticky="nsew")
    x_scroll.config(command=canvas.xview)
    y_scroll.config(command=canvas.yview)
    x_scroll.grid(row=1, column=0, sticky="ew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)
    # --- Calcolo posizioni dei nodi (positions) ---
    levels_group = {}
    for n, lvl in levels.items():
        levels_group.setdefault(lvl, []).append(n)
    max_level = max(levels_group.keys())
    box_width = 80
    box_height = 40
    h_spacing = 40
    v_spacing = 80
    max_nodes_in_row = max(len(group) for group in levels_group.values())
    canvas_width = int(max_nodes_in_row * (box_width + h_spacing) + h_spacing)
    canvas_height = int((max_level + 1) * (box_height + v_spacing) + v_spacing)
    positions = {}
    # Carica posizioni personalizzate se esistono
    pos_path = os.path.join(US_DIR, "positions.json")
    custom_positions = {}
    if os.path.exists(pos_path):
        try:
            with open(pos_path, "r", encoding="utf-8") as f:
                custom_positions = json.load(f)
        except Exception:
            custom_positions = {}
    for lvl in range(max_level + 1):
        if lvl in levels_group:
            nodes_in_level = levels_group[lvl]
            count = len(nodes_in_level)
            total_width = count * box_width + (count - 1) * h_spacing
            start_x = (canvas_width - total_width) / 2
            y = v_spacing + lvl * (box_height + v_spacing)
            for index, n in enumerate(nodes_in_level):
                if str(n) in custom_positions:
                    x, y_custom = custom_positions[str(n)]
                    positions[n] = (x, y_custom, x + box_width, y_custom + box_height)
                else:
                    x = start_x + index * (box_width + h_spacing)
                    positions[n] = (x, y, x + box_width, y + box_height)

    # --- Disegno archi ---
    incoming = {}
    for (u, v) in edges:
        incoming.setdefault(v, []).append(u)
    handled = set()
    for target, sources in incoming.items():
        if len(sources) > 1 and target in positions:
            x3, y3, x4, y4 = positions[target]
            end_x = (x3 + x4) / 2
            end_y = y3
            merge_y = end_y - 30
            merge_x = end_x
            for src in sources:
                if src not in positions:
                    continue
                x1, y1, x2, y2 = positions[src]
                start_x = (x1 + x2) / 2
                start_y = y2
                canvas.create_line(start_x, start_y, start_x, merge_y, fill="black")
                if abs(start_x - merge_x) > 2:
                    canvas.create_line(start_x, merge_y, merge_x, merge_y, fill="black")
            canvas.create_line(merge_x, merge_y, end_x, end_y, fill="black")
            for src in sources:
                handled.add((src, target))
    for (u, v) in edges:
        if (u, v) in handled:
            continue
        if u in positions and v in positions:
            x1, y1, x2, y2 = positions[u]
            x3, y3, x4, y4 = positions[v]
            start_x = (x1 + x2) / 2
            start_y = y2
            end_x = (x3 + x4) / 2
            end_y = y3
            if abs(start_x - end_x) < 2:
                canvas.create_line(start_x, start_y, end_x, end_y, fill="black")
            else:
                mid_y = (start_y + end_y) / 2
                canvas.create_line(start_x, start_y, start_x, mid_y, fill="black")
                canvas.create_line(start_x, mid_y, end_x, mid_y, fill="black")
                canvas.create_line(end_x, mid_y, end_x, end_y, fill="black")
    for (u, v) in uguale_edges:
        if u in positions and v in positions:
            cx_u = (positions[u][0] + positions[u][2]) / 2
            cy_u = (positions[u][1] + positions[u][3]) / 2
            cx_v = (positions[v][0] + positions[v][2]) / 2
            cy_v = (positions[v][1] + positions[v][3]) / 2
            canvas.create_line(cx_u, cy_u, cx_v, cy_v, dash=(4, 2), fill="red")
    node_ids = {}
    for n, coords in positions.items():
        x1, y1, x2, y2 = coords
        rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", tags=f"us_{n}")
        text_id = canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"US {n}", tags=f"us_{n}")
        node_ids[n] = (rect_id, text_id)
    dragging = {"node": None, "offset": (0,0)}
    def on_press(event):
        for n, (rect_id, text_id) in node_ids.items():
            x1, y1, x2, y2 = positions[n]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                dragging["node"] = n
                dragging["offset"] = (event.x - x1, event.y - y1)
                break
    def on_motion(event):
        n = dragging["node"]
        if n is not None:
            dx, dy = dragging["offset"]

            x = event.x - dx
            y = event.y - dy
           

            # Snap alla griglia durante il drag
            x_snap = round(x / GRID_SIZE) * GRID_SIZE
            y_snap = round(y / GRID_SIZE) * GRID_SIZE
            # Limiti canvas
            min_x = 0
            min_y = 0
            max_x = int(canvas['width']) - box_width if 'width' in canvas.keys() else canvas.winfo_width() - box_width
            max_y = int(canvas['height']) - box_height if 'height' in canvas.keys() else canvas.winfo_height() - box_height
            x_snap = max(min_x, min(x_snap, max_x))
            y_snap = max(min_y, min(y_snap, max_y))
            positions[n] = (x_snap, y_snap, x_snap + box_width, y_snap + box_height)
            canvas.coords(node_ids[n][0], x_snap, y_snap, x_snap + box_width, y_snap + box_height)
            canvas.coords(node_ids[n][1], x_snap + box_width/2, y_snap + box_height/2)

    def on_release(event):
        n = dragging["node"]
        if n is not None:
            to_save = {str(k): [positions[k][0], positions[k][1]] for k in positions}
            with open(pos_path, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2)
        dragging["node"] = None
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_motion)
    canvas.bind("<ButtonRelease-1>", on_release)
    tk.Label(editor_win, text="Trascina i nodi US per modificare la disposizione. Le posizioni vengono salvate automaticamente.").pack()
    GRID_SIZE = 30  # dimensione griglia per snap (definito anche sopra, qui serve per la griglia visiva)
    # Disegna la griglia sul canvas per aiutare lo snap
    def draw_grid():
        canvas.delete('grid')
        step = GRID_SIZE
        w = int(canvas['width']) if 'width' in canvas.keys() else canvas.winfo_width()
        h = int(canvas['height']) if 'height' in canvas.keys() else canvas.winfo_height()
        for x in range(0, w, step):
            canvas.create_line(x, 0, x, h, fill='#e0e0e0', tags='grid')
        for y in range(0, h, step):
            canvas.create_line(0, y, w, y, fill='#e0e0e0', tags='grid')
    # Ridisegna la griglia quando il canvas cambia dimensione
    canvas.bind('<Configure>', lambda e: draw_grid())
    draw_grid()

# Esportazione CSV solo delle schede filtrate
# Sostituisci la funzione esporta_us_csv con una che esporta solo le schede attualmente visibili
import csv

def esporta_us_csv():
    if not file_labels:
        messagebox.showinfo("Esporta CSV", "Nessuna scheda US da esportare.")
        return
    all_data = []
    for filename in file_labels:
        with open(os.path.join(US_DIR, filename), encoding="utf-8") as f:
            data = json.load(f)
            all_data.append(data)
    all_keys = set()
    for d in all_data:
        all_keys.update(d.keys())
    all_keys = sorted(all_keys)
    from tkinter import filedialog
    save_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Esporta le schede US filtrate in CSV"
    )
    if not save_path:
        return
    with open(save_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, delimiter=';')
        writer.writeheader()
        for d in all_data:
            d2 = {k: (", ".join(map(str, v)) if isinstance(v, list) else v) for k, v in d.items()}
            writer.writerow(d2)
    messagebox.showinfo("Esporta CSV", f"Esportazione completata in:\n{save_path}")

def esporta_matrix_svg():
    # Carica tutte le schede dalla directory
    schede = []
    for filename in sorted(os.listdir(US_DIR)):
        if filename.endswith(".json") and filename != "prog_manager.json":
            filepath = os.path.join(US_DIR, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                    if "nr_us" in data:
                        schede.append(data)
            except Exception as e:
                pass
    if not schede:
        messagebox.showinfo("Esporta Matrix", "Nessuna scheda disponibile per esportare la matrix.")
        return
    nodes = {s['nr_us']: s for s in schede}
    edges_set = set()
    for s in schede:
        u = s['nr_us']
        for v in s.get("copre", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("coperto_da", []):
            if v in nodes:
                edges_set.add((v, u))
        for v in s.get("si_lega_a", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("gli_si_appoggia", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("si_appoggia_a", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("taglia", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("tagliato_da", []):
            if v in nodes:
                edges_set.add((v, u))
        for v in s.get("riempie", []):
            if v in nodes:
                edges_set.add((u, v))
        for v in s.get("riempito_da", []):
            if v in nodes:
                edges_set.add((v, u))
    edges = list(edges_set)
    uguale_edges = set()
    for s in schede:
        u = s['nr_us']
        for v in s.get("uguale_a", []):
            if v in nodes:
                pair = tuple(sorted([u, v]))
                uguale_edges.add(pair)
    levels = {n: 0 for n in nodes}
    changed = True
    while changed:
        changed = False
        for (u, v) in edges:
            if levels[v] < levels[u] + 1:
                levels[v] = levels[u] + 1
                changed = True
    levels_group = {}
    for n, lvl in levels.items():
        levels_group.setdefault(lvl, []).append(n)
    # RIMOSSO OGNI ORDINAMENTO NUMERICO: non ordinare i livelli numericamente
    # for lvl in levels_group:
    #     levels_group[lvl].sort()
    max_level = max(levels_group.keys())
    box_width = 80
    box_height = 40
    h_spacing = 40
    v_spacing = 80
    max_nodes_in_row = max(len(group) for group in levels_group.values())
    canvas_width = int(max_nodes_in_row * (box_width + h_spacing) + h_spacing)
    canvas_height = int((max_level + 1) * (box_height + v_spacing) + v_spacing)

    # --- Calcolo posizioni dei nodi (positions) ---
    positions = {}
    # Carica posizioni personalizzate se esistono
    pos_path = os.path.join(US_DIR, "positions.json")
    custom_positions = {}
    if os.path.exists(pos_path):
        try:
            with open(pos_path, "r", encoding="utf-8") as f:
                custom_positions = json.load(f)
        except Exception:
            custom_positions = {}
    for lvl in range(max_level + 1):
        if lvl in levels_group:
            nodes_in_level = levels_group[lvl]
            count = len(nodes_in_level)
            total_width = count * box_width + (count - 1) * h_spacing
            start_x = (canvas_width - total_width) / 2
            y = v_spacing + lvl * (box_height + v_spacing)
            for index, n in enumerate(nodes_in_level):
                if str(n) in custom_positions:
                    x, y_custom = custom_positions[str(n)]
                    positions[n] = (x, y_custom, x + box_width, y_custom + box_height)
                else:
                    x = start_x + index * (box_width + h_spacing)
                    positions[n] = (x, y, x + box_width, y + box_height)

    from tkinter import filedialog
    save_path = filedialog.asksaveasfilename(
        defaultextension=".svg",
        filetypes=[("SVG files", "*.svg")],
        title="Esporta Matrix di Harris in SVG"
    )
    if not save_path:
        return
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}">')
    # --- Disegno: ogni relazione è sempre 1 a 1, ma con merge point per convergenze ---
    handled = set()
    incoming = {}
    for (u, v) in edges:
        incoming.setdefault(v, []).append(u)
    for target, sources in incoming.items():
        if len(sources) > 1 and target in positions:
            x3, y3, x4, y4 = positions[target]
            end_x = (x3 + x4) / 2
            end_y = y3
            merge_y = end_y - 30
            merge_x = end_x
            for src in sources:
                if src not in positions:
                    continue
                x1, y1, x2, y2 = positions[src]
                start_x = (x1 + x2) / 2
                start_y = y2
                svg.append(f'<line x1="{start_x}" y1="{start_y}" x2="{start_x}" y2="{merge_y}" stroke="black"/>')
                if abs(start_x - merge_x) > 2:
                    svg.append(f'<line x1="{start_x}" y1="{merge_y}" x2="{merge_x}" y2="{merge_y}" stroke="black"/>')
            svg.append(f'<line x1="{merge_x}" y1="{merge_y}" x2="{end_x}" y2="{end_y}" stroke="black"/>')
            for src in sources:
                handled.add((src, target))
    for (u, v) in edges:
        if (u, v) in handled:
            continue
        if u in positions and v in positions:
            x1, y1, x2, y2 = positions[u]
            x3, y3, x4, y4 = positions[v]
            start_x = (x1 + x2) / 2
            start_y = y2
            end_x = (x3 + x4) / 2
            end_y = y3
            if abs(start_x - end_x) < 2:
                svg.append(f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" stroke="black"/>')
            else:
                mid_y = (start_y + end_y) / 2
                svg.append(f'<line x1="{start_x}" y1="{start_y}" x2="{start_x}" y2="{mid_y}" stroke="black"/>')
                svg.append(f'<line x1="{start_x}" y1="{mid_y}" x2="{end_x}" y2="{mid_y}" stroke="black"/>')
                svg.append(f'<line x1="{end_x}" y1="{mid_y}" x2="{end_x}" y2="{end_y}" stroke="black"/>')
    for (u, v) in uguale_edges:
        if u in positions and v in positions:
            cx_u = (positions[u][0] + positions[u][2]) / 2
            cy_u = (positions[u][1] + positions[u][3]) / 2
            cx_v = (positions[v][0] + positions[v][2]) / 2
            cy_v = (positions[v][1] + positions[v][3]) / 2
            svg.append(f'<line x1="{cx_u}" y1="{cy_u}" x2="{cx_v}" y2="{cy_v}" stroke="red" stroke-dasharray="4,2"/>')
    for n, coords in positions.items():
        x1, y1, x2, y2 = coords
        svg.append(f'<rect x="{x1}" y="{y1}" width="{box_width}" height="{box_height}" fill="white" stroke="black"/>')
        svg.append(f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 + 5}" font-size="16" text-anchor="middle" fill="black">US {n}</text>')
    svg.append('</svg>')
    with open(save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    messagebox.showinfo("Esporta Matrix", f"Matrix esportata in SVG:\n{save_path}")

# AVVIO: controlla presenza parametri progetto
def main():
    if not os.path.exists(PROG_MANAGER_PATH):
        mostra_popup_parametri()
    else:
        avvia_gui_principale()
    root.mainloop()

if __name__ == "__main__":
    main()
