## Tool zur Modellierung eines Angriffspfades
Dieses Projekt ermöglicht die Verwaltung und Visualisierung von Angriffspfaden. Es bietet Funktionen zum Hinzufügen, Bearbeiten und Löschen von Nodes und Edges sowie zum Speichern und Laden von Projekten.

## Installation
1. Klonen Sie das Repository:
    ```bash
    git clone <repository-url>
    ```
2. Wechseln Sie in das Projektverzeichnis:
    ```bash
    cd <projektverzeichnis>
    ```
3. Installieren Sie die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```
4. Installieren Sie Graphviz:
     ```bash
    # Linux (Debian/Ubuntu)
    sudo apt install graphviz
   # Linux (Fedora, Rocky Linux, CentOS)
   sudo dnf install graphviz
   # Windows (choco)
   choco install graphviz
   # Windows (winget)
   winget install graphviz
   # macOS (port)
   sudo port install graphviz
   # macOS (brew)
   brew install graphviz
    ```
    Weitere Inforamtionen und Installer finden Sie auf der Webseite von [Graphviz](https://graphviz.org/download/).

## Nutzung
1. Starten Sie die Anwendung:
    ```bash
    python app.py
    ```
2. Öffnen Sie Ihren Webbrowser und gehen Sie auf `http://localhost:5000`, um auf die Weboberfläche zu gelangen.

## Dokumentation
Weitere Informationen zur Nutzung des Tools finden Sie in der [Dokumentation](https://github.com/udoschm/Entwicklung-eines-Tools-f-r-die-Modellierung-eines-Angriffspfades/blob/main/static/Benutzerdokumentation.pdf).
