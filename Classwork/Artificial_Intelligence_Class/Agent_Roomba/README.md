# ToyBot Environment

A Python-based simulation environment for a toy-collecting robot agent using matplotlib visualization.

## Installation

### 1. Create a virtual environment

From the vscode terminal,

```bash
python -m venv .venv
```
Close the terminal and open it again. VSCode should recognize that the virtual environment is present and activate it for you. If it doesn't, then try closing and opening the project.

### 2. Install dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Project Structure

- `agent.py` - Base Agent class definition
- `environment.py` - Base Environment class
- `bedroom_env.py` - BedRoom environment class (extends Environment)
- `toybot.py` - ToyBot agent class (extends Agent)
- `main.py` - Main program that runs the simulation
- `requirements.txt` - Python package dependencies
- `README.md` - This file

## Dependencies

- **matplotlib** - Environment visualization with interactive plotting
- **numpy** - Numerical computing support
- Supporting libraries: contourpy, cycler, fonttools, kiwisolver, pillow, python-dateutil, pyparsing, six
