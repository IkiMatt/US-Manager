## US Manager
US Manager è uno strumento desktop con interfaccia grafica (GUI) sviluppato in Python/Tkinter per la gestione di schede stratigrafiche di Unità Stratigrafiche (US), schede diario di scavo e schede reperti. È pensato per supportare la documentazione di cantiere in ambito archeologico, sia su scavi stratigrafici che architettonici.

## Funzionalità principali
💾 Gestione progetti: crea un nuovo progetto archeologico e memorizza i metadati (ID, comune, anno, responsabili, ecc.).

📋 Schede US: crea, modifica e salva in JSON schede stratigrafiche dettagliate, comprensive di:

dati descrittivi (area, settore, materiali, consistenza…),

rapporti stratigrafici complessi e semplificati,

osservazioni, datazioni, e autore scheda,

campi personalizzati configurabili a piacere (es. stato di conservazione, indicatori di ritualità, ecc.).

🧱 Visualizzazione Matrice di Harris: visualizza i rapporti stratigrafici in una vista grafica con layout personalizzabile ed esportabile in SVG.

📖 Schede diario: diario giornaliero di cantiere con operatori, attività e US indagate.

🏺 Schede reperti: schede sintetiche di reperti mobili (singoli o sacchetti), con identificativo automatico e richiamo all’US di provenienza.

## Struttura delle cartelle
All'avvio, il programma crea automaticamente:

```yaml
Copia
Modifica
project_folder/
│
├── manager/               # Contiene i dati del progetto e la configurazione
│   ├── project.py
│   ├── custom_fields.json
│   └── su_layout.json
│
├── su_report/             # Contiene le schede US in formato JSON
│   └── US0001.json
│
├── diary_usm/             # Contiene le schede diario in formato JSON
│   └── 2025_07_15.json
│
├── finds_usm/             # Contiene le schede reperti
│   └── 0001.json
│
└── us_manager.py          # File principale
```
## Requisiti

Python 3.8+
Nessuna libreria esterna necessaria, solo standard library (tkinter, json, os, datetime, ecc.).

## Avvio del programma
Scarica us_manager.py nella tua cartella di progetto.

Esegui il programma con:

```bash
python us_manager.py
```
Alla prima esecuzione ti verrà chiesto di creare un nuovo progetto.

Inizia a compilare schede US, visualizzare la matrice, compilare schede diario o aggiungere reperti.

## Personalizzazione
I campi personalizzati possono essere aggiunti o rimossi dalla sezione apposita del programma.

Le relazioni stratigrafiche supportano sia l’inserimento manuale che la selezione da lista.

Il layout della matrice è salvabile e riutilizzabile.

## Esportazione
La matrice di Harris può essere esportata in formato SVG.

Le schede sono salvate in formato JSON leggibile e modificabile esternamente.

## Note
Il programma non richiede installazione.

Può essere eseguito anche da chi ha conoscenze minime di Python.

È pensato per un utilizzo offline e individuale sul campo.

```bash
@misc{curto2025usmanager,
  author = {Curto, Mattia},
  title = {US-manager},
  copyright = {All rights reserved},
  year = {2025},
  howpublished = {\url{https://github.com/IkiMatt/US-Manager/}}
}
```
---

## 🚀 Avvio rapido

```bash
git clone https://github.com/IkiMatt/US-Manager
cd US-manager
python us_manager.py
