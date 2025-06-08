# US Manager

US Manager è un'applicazione Python per la gestione, la compilazione e l'esportazione di schede di Unità Stratigrafiche (US) in ambito archeologico. Supporta la gestione multilingua (italiano, inglese, tedesco), la visualizzazione delle relazioni tra US (matrix di Harris), l'esportazione dei dati e la personalizzazione dei progetti.

## Funzionalità principali
- Inserimento, modifica e cancellazione di schede US tramite interfaccia grafica (Tkinter)
- Salvataggio dei dati in formato JSON
- Visualizzazione grafica delle relazioni tra US (matrix di Harris)
- Esportazione dei dati in formato CSV e SVG
- Supporto multilingua per etichette, dati e interfaccia (IT/EN/DE)
- Salvataggio delle preferenze di lingua e progetto

## Requisiti
- Python 3.x
- Nessuna dipendenza esterna (solo librerie standard: tkinter, os, json, csv)

## Avvio
1. Avvia `us_manager.py` con Python 3.
2. Al primo avvio, inserisci i parametri del progetto.
3. Utilizza i pulsanti a sinistra per creare, modificare, eliminare o esportare le schede US.

## Struttura dei dati
- Tutte le schede sono salvate nella cartella `schede_us/` come file JSON.
- I parametri di progetto sono salvati in `schede_us/prog_manager.json`.

## Licenza
Vedi il file `LICENZA.txt`.

## Citazione accademica
Se utilizzi questo software per pubblicazioni, tesi o lavori accademici, è obbligatorio citare l'autore come segue:

> Curto, M. (2025). US Manager: software open source per la gestione delle Unità Stratigrafiche. https://github.com/mattiacurto

## Autore
Mattia Curto

---

# Gestione Schede US

## Descrizione
Software per la gestione di schede Unità Stratigrafiche (US) archeologiche tramite interfaccia grafica. Permette la creazione, modifica, esportazione e gestione di relazioni tra schede US.

## Avvio rapido
1. Assicurati di avere Python 3 installato.
2. Avvia il programma con:
   ```
   python us_manager.py
   ```
3. Segui le istruzioni a schermo per selezionare la lingua e inserire i parametri del progetto.

## Requisiti
- Python 3.x
- Modulo tkinter (incluso nella maggior parte delle installazioni Python)

## Funzionalità principali
- Gestione multilingua (italiano, inglese, tedesco)
- Creazione e modifica di schede US
- Esportazione CSV e Matrix
- Editor grafico delle relazioni tra US

---

# US Sheet Manager

## Description
Software for managing archaeological Stratigraphic Unit (US) sheets with a graphical interface. Allows creation, editing, export, and management of relationships between US sheets.

## Quick Start
1. Make sure you have Python 3 installed.
2. Start the program with:
   ```
   python us_manager.py
   ```
3. Follow the on-screen instructions to select language and enter project parameters.

## Requirements
- Python 3.x
- tkinter module (included in most Python installations)

## Main Features
- Multilanguage support (Italian, English, German)
- Create and edit US sheets
- Export to CSV and Matrix
- Graphical editor for US relationships

---

# US-Blattverwaltung

## Beschreibung
Software zur Verwaltung archäologischer Stratigrafie-Einheiten (US) mit grafischer Oberfläche. Ermöglicht das Erstellen, Bearbeiten, Exportieren und Verwalten von Beziehungen zwischen US-Blättern.

## Schnellstart
1. Stellen Sie sicher, dass Python 3 installiert ist.
2. Starten Sie das Programm mit:
   ```
   python us_manager.py
   ```
3. Folgen Sie den Anweisungen auf dem Bildschirm, um die Sprache zu wählen und Projektparameter einzugeben.

## Voraussetzungen
- Python 3.x
- tkinter-Modul (in den meisten Python-Installationen enthalten)

## Hauptfunktionen
- Mehrsprachige Unterstützung (Italienisch, Englisch, Deutsch)
- Erstellen und Bearbeiten von US-Blättern
- Export als CSV und Matrix
- Grafischer Editor für US-Beziehungen
