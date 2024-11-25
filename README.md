# Laboratorium AI ASR

![Python](https://img.shields.io/badge/Python-3.10.13-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Poetry](https://img.shields.io/badge/Build-Poetry-blue.svg)

**Laboratorium AI ASR** is a Python package for automatic speech recognition (ASR). It enables precise transcription of .wav audio files and saves the results in .json files. The package uses [WhisperX](https://github.com/m-bain/whisperX) with OpenAI's "medium" Whisper model for high-quality results.

## Table of Contents

- [Laboratorium AI ASR](#laboratorium-ai-asr)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Key Features](#key-features)
  - [Installation and Build](#installation-and-build)
  - [Usage](#usage)
    - [CLI Usage with File Descriptors](#cli-usage-with-file-descriptors)
      - [1. Start Module and Load Model](#1-start-module-and-load-model)
      - [2. Wait for "ready" Signal](#2-wait-for-ready-signal)
      - [3. Process Files](#3-process-files)
    - [Example Shell Script](#example-shell-script)
  - [License](#license)

## Overview

**Laboratorium AI ASR** provides a simple way to automatically transcribe audio recordings. It supports various Whisper models and enables the use of CPU or GPU to optimize transcription speed and accuracy.

### Key Features

- **Automatic Speech Recognition (ASR):** Transcription of .wav files.
- **Model Variety:** Support for multiple Whisper models (tiny, base, small, medium, large-v1, large-v2, large-v3).
- **Hardware Acceleration:** CPU or GPU utilization.
- **Flexible Configuration:** Customization of device (DEVICE) and computation type (COMPUTE_TYPE).

## Installation and Build

This package is managed with [Poetry](https://python-poetry.org/). Follow these steps to install and build the package:

1. **Clone Repository:**

   ```bash
   git clone https://github.com/uzl-cosy/cosy-ai-asr.git
   cd laboratorium-ai-asr
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Activate Virtual Environment:**

   ```bash
   poetry shell
   ```

4. **Build Package:**

   ```bash
   poetry build
   ```

   This command creates the distributable files in the dist/ directory.

## Usage

The package runs as a persistent module through the command line interface (CLI). It enables transcription of .wav files and output to .json files using file descriptors. Communication occurs through a pipe, where the module sends "ready" once the model is loaded and ready for processing.

### CLI Usage with File Descriptors

#### 1. Start Module and Load Model

Start the ASR module via CLI. The module loads the model and signals through the file descriptor when it's ready.

```bash
python -m laboratorium_ai_asr -f <FD>
```

**Parameters:**

- `-f, --fd`: File descriptor for pipe communication.

**Example:**

```bash
python -m laboratorium_ai_asr -f 3
```

#### 2. Wait for "ready" Signal

After starting the module, it loads the ASR model. Once loaded, the module sends a "ready" signal through the specified file descriptor.

#### 3. Process Files

Pass the input (.wav) and output (.json) file paths through the pipe. The module processes the file and sends a "done" signal once transcription is complete.

**Example:**

```bash
echo "path/to/input.wav,path/to/output.json" >&3
```

**Description:**

- The echo command sends input and output file paths through file descriptor 3.
- The module receives the paths, transcribes the .wav file, and saves the result in the .json file.
- Upon completion, the module sends a "done" signal through the file descriptor.

**Complete Flow:**

1. **Start the ASR Module:**

   ```bash
   python -m laboratorium_ai_asr -f 3
   ```

2. **Send File Paths for Transcription:**

   ```bash
   echo "path/to/input.wav,path/to/output.json" >&3
   ```

3. **Repeat Step 2 for Additional Files:**

   ```bash
   echo "path/to/another_input.wav,path/to/another_output.json" >&3
   ```

### Example Shell Script

Here's an example of using the ASR package in a shell script:

```bash
#!/bin/bash

# Open a file descriptor (e.g., 3) for pipe communication
exec 3<>/dev/null

# Start the ASR module in background and connect the file descriptor
python -m laboratorium_ai_asr -f 3 &

# Store ASR module's PID for later termination
ASR_PID=$!

# Wait for "ready" signal
read -u 3 signal
if [ "$signal" = "ready" ]; then
      echo "Model is ready for processing."

      # Send input and output paths
      echo "path/to/input.wav,path/to/output.json" >&3

      # Wait for "done" signal
      read -u 3 signal_done
      if [ "$signal_done" = "done" ]; then
            echo "Transcription complete."
      fi

      # Additional transcriptions can be added here
      echo "path/to/another_input.wav,path/to/another_output.json" >&3

      # Wait for "done" signal again
      read -u 3 signal_done
      if [ "$signal_done" = "done" ]; then
            echo "Additional transcription complete."
      fi

      # Terminate the ASR module
      echo "exit,exit" >&3

      # Wait for ASR module to terminate
      wait $ASR_PID
fi

# Close the file descriptor
exec 3>&-
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
