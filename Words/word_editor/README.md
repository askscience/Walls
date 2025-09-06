# Words - Word Editor

A minimal word editor application with a Rust (PyO3) core and a PySide6 GUI. The GUI and a real-time CLI communicate over a local TCP bridge so commands typed in the CLI instantly update the GUI.

## Project Layout

- `rust_core/`: Rust library compiled as a Python extension using PyO3 (`word_core`).
- `python_gui/`: PySide6 application and CLI.
  - `gui/custom_widgets.py`: icon helper that loads icons from `Walls/gui_core/utils/icons`.
  - `main.py`: GUI entry point; starts a TCP server for CLI commands.
  - `cli.py`: Real-time CLI that connects to the GUI server.

## Build the Rust core

You can build the PyO3 module using maturin (recommended) or `python -m pip install .` with a proper setup. For quick local development with maturin:

```bash
cd rust_core
maturin develop
```

This will produce an importable `word_core` module in your current Python environment.

## Run the GUI

```bash
cd <REPO_ROOT>/Words/word_editor
python python_gui/main.py
```

## Use the CLI (real-time)

With the GUI running:

```bash
cd <REPO_ROOT>/Words/word_editor
# Interactive REPL
python python_gui/cli.py

# Or send one-off commands
python python_gui/cli.py set_text "Hello from CLI!"
python python_gui/cli.py insert_text 0 "[PREFIX] "
python python_gui/cli.py open /path/to/file.txt
python python_gui/cli.py save /path/to/file.txt
```

Icons for toolbar are loaded from `Walls/gui_core/utils/icons` (e.g. `folder.svg`, `floppy-disk.svg`).