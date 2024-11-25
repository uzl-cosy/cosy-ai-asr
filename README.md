# Laboratorium AI ASR

![Python](https://img.shields.io/badge/Python-3.10.13-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Poetry](https://img.shields.io/badge/Build-Poetry-blue.svg)

**Laboratorium AI ASR** ist ein Python-Paket zur automatischen Spracherkennung (ASR). Es ermöglicht die präzise Transkription von .wav-Audiodateien und speichert die Ergebnisse in .json-Dateien. Das Paket nutzt [WhisperX](https://github.com/m-bain/whisperX) mit dem "medium" Whisper-Modell von OpenAI für hochwertige Ergebnisse.

## Inhaltsverzeichnis

- [Laboratorium AI ASR](#laboratorium-ai-asr)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Überblick](#überblick)
    - [Hauptmerkmale](#hauptmerkmale)
  - [Installation und Build](#installation-und-build)
  - [Nutzung](#nutzung)
    - [CLI-Verwendung mit Filedescriptoren](#cli-verwendung-mit-filedescriptoren)
      - [1. Modul starten und Modell laden](#1-modul-starten-und-modell-laden)
      - [2. Warten auf das "ready" Signal](#2-warten-auf-das-ready-signal)
      - [3. Dateien verarbeiten](#3-dateien-verarbeiten)
    - [Beispiel mit Shell-Skript](#beispiel-mit-shell-skript)
  - [Lizenz](#lizenz)

## Überblick

**Laboratorium AI ASR** bietet eine einfache Möglichkeit, Audioaufnahmen automatisch zu transkribieren. Es unterstützt verschiedene Whisper-Modelle und ermöglicht die Nutzung von CPU oder GPU zur Optimierung der Transkriptionsgeschwindigkeit und -genauigkeit.

### Hauptmerkmale

- **Automatische Spracherkennung (ASR):** Transkription von .wav-Dateien.
- **Modellvielfalt:** Unterstützung mehrerer Whisper-Modelle (tiny, base, small, medium, large-v1, large-v2, large-v3).
- **Hardware-Beschleunigung:** Nutzung von CPU oder GPU.
- **Flexible Konfiguration:** Anpassung von Gerät (DEVICE) und Berechnungstyp (COMPUTE_TYPE).

## Installation und Build

Dieses Paket wird mit [Poetry](https://python-poetry.org/) verwaltet. Folgen Sie diesen Schritten, um das Paket zu installieren und zu bauen:

1. **Repository klonen:**

   ```bash
   git clone https://github.com/yourusername/laboratorium-ai-asr.git
   cd laboratorium-ai-asr
   ```

2. **Abhängigkeiten installieren:**

   ```bash
   poetry install
   ```

3. **Virtuelle Umgebung aktivieren:**

   ```bash
   poetry shell
   ```

4. **Paket bauen:**

   ```bash
   poetry build
   ```

   Dieses Kommando erstellt die distributierbaren Dateien im dist/-Verzeichnis.

## Nutzung

Das Paket wird über die Kommandozeile (CLI) als dauerhaft laufendes Modul ausgeführt. Es ermöglicht die Transkription von .wav-Dateien und die Ausgabe in .json-Dateien mittels Filedescriptoren. Die Kommunikation erfolgt über eine Pipe, wobei das Modul "ready" sendet, sobald das Modell geladen ist und bereit zur Verarbeitung ist.

### CLI-Verwendung mit Filedescriptoren

#### 1. Modul starten und Modell laden

Starten Sie das ASR-Modul über die CLI. Das Modul lädt das Modell und signalisiert über den Filedescriptor, dass es bereit ist.

```bash
python -m laboratorium_ai_asr -f <FD>
```

**Parameter:**

- `-f, --fd`: Filedescriptor für die Pipe-Kommunikation.

**Beispiel:**

```bash
python -m laboratorium_ai_asr -f 3
```

#### 2. Warten auf das "ready" Signal

Nachdem das Modul gestartet wurde, lädt es das ASR-Modell. Sobald das Modell geladen ist, sendet das Modul das Signal "ready" über den angegebenen Filedescriptor.

#### 3. Dateien verarbeiten

Übergeben Sie die Pfade zur Eingabe- (.wav) und Ausgabe- (.json) Datei über die Pipe. Das Modul verarbeitet die Datei und sendet ein "done" Signal, sobald die Transkription abgeschlossen ist.

**Beispiel:**

```bash
echo "path/to/input.wav,path/to/output.json" >&3
```

**Beschreibung:**

- Das echo-Kommando sendet die Pfade zur Eingabe- und Ausgabedatei über den Filedescriptor 3.
- Das Modul empfängt die Pfade, transkribiert die .wav-Datei und speichert das Ergebnis in der .json-Datei.
- Nach Abschluss sendet das Modul ein "done" Signal über den Filedescriptor.

**Vollständiger Ablauf:**

1. **Starten Sie das ASR-Modul:**

   ```bash
   python -m laboratorium_ai_asr -f 3
   ```

2. **Senden Sie die Dateiwege zur Transkription:**

   ```bash
   echo "path/to/input.wav,path/to/output.json" >&3
   ```

3. **Wiederholen Sie Schritt 2 für weitere Dateien:**

   ```bash
   echo "path/to/another_input.wav,path/to/another_output.json" >&3
   ```

4. **Beenden des Moduls:**

   Senden Sie "exit,exit" über den Filedescriptor, um das Modul zu stoppen.

   ```bash
   echo "exit,exit" >&3
   ```

### Beispiel mit Shell-Skript

Hier ist ein Beispiel, wie Sie das ASR-Paket in einem Shell-Skript nutzen können:

```bash
#!/bin/bash

# Öffnen Sie einen Dateideskriptor (z.B. 3) für die Pipe-Kommunikation
exec 3<>/dev/null

# Starten Sie das ASR-Modul im Hintergrund und verbinden Sie den Filedescriptor
python -m laboratorium_ai_asr -f 3 &

# PID des ASR-Moduls speichern, um es später beenden zu können
ASR_PID=$!

# Warten Sie auf das "ready" Signal
read -u 3 signal
if [ "$signal" = "ready" ]; then
    echo "Modell ist bereit zur Verarbeitung."

    # Senden Sie die Eingabe- und Ausgabepfade
    echo "path/to/input.wav,path/to/output.json" >&3

    # Warten Sie auf das "done" Signal
    read -u 3 signal_done
    if [ "$signal_done" = "done" ]; then
        echo "Transkription abgeschlossen."
    fi

    # Weitere Transkriptionen können hier hinzugefügt werden
    echo "path/to/another_input.wav,path/to/another_output.json" >&3

    # Warten Sie erneut auf das "done" Signal
    read -u 3 signal_done
    if [ "$signal_done" = "done" ]; then
        echo "Weitere Transkription abgeschlossen."
    fi

    # Beenden Sie das ASR-Modul
    echo "exit,exit" >&3

    # Warten Sie, bis das ASR-Modul beendet ist
    wait $ASR_PID
fi

# Schließen Sie den Filedeskriptor
exec 3>&-
```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Details finden Sie in der [LICENSE](LICENSE)-Datei.
