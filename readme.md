# Advanced Calculator Project

This project is an advanced calculator application built in Python, fulfilling the requirements of the midterm project. It features a command-line REPL interface, standard and advanced arithmetic operations, undo/redo functionality, calculation history, robust error handling, logging, and automated testing with CI/CD.

It demonstrates several software design patterns, including the **Factory**, **Memento**, and **Observer** patterns.

## Features ✨

-   **Core Operations**: Add, Subtract, Multiply, Divide
-   **Advanced Operations**: Power, Root, Modulus, Integer Division, Percentage, Absolute Difference
-   **REPL Interface**: A user-friendly command-line (Read-Eval-Print Loop) for interacting with the calculator.
-   **History Management**: View, clear, save, and load calculation history using `pandas`.
-   **Undo/Redo**: Uses the **Memento Pattern** to undo and redo calculations or history-modifying actions.
-   **Logging**: Logs all operations, errors, and system events to a file (`logs/app.log`).
-   **Auto-Save**: Uses the **Observer Pattern** to automatically save history to a CSV file after relevant actions (configurable via `.env`).
-   **Configuration**: All settings are managed externally via a `.env` file.
-   **Robust Error Handling**: Handles invalid inputs, mathematical errors (like division by zero), and file issues gracefully.
-   **Unit Testing**: Comprehensive test suite using `pytest` with over 90% code coverage enforced.
-   **CI/CD Pipeline**: Includes a GitHub Actions workflow to automatically run tests and check coverage on push/pull requests.
-   **Optional Feature 1: Color-Coded Outputs**: Uses `colorama` for a more readable and visually appealing command-line experience. 🎨
-   **Optional Feature 2: Dynamic Help Menu**: Uses a Decorator pattern to dynamically generate the help menu, ensuring it stays up-to-date as commands are added or removed. ❓

## Installation 🚀

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd project_root
    ```

2.  **Create and Activate a Virtual Environment**
    A virtual environment isolates project dependencies.

    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows (Command Prompt)
    python -m venv venv
    .\venv\Scripts\activate.bat

    # On Windows (PowerShell)
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    # If PowerShell script execution is disabled, run PowerShell as Admin and execute:
    # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
    Your terminal prompt should now start with `(venv)`.

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration Setup (`.env` file) ⚙️

Before running the application, you **must** create a configuration file named `.env` in the root directory (`project_root/`). Copy the example below and adjust the paths or settings if needed.


 --- Configuration for Advanced Calculator ---

# Base Directories (Relative paths are okay, they resolve from the project root)
CALCULATOR_LOG_DIR="logs"
CALCULATOR_HISTORY_DIR="data"

# History Settings
CALCULATOR_MAX_HISTORY_SIZE=20     # Max number of calculations to keep in memory
CALCULATOR_AUTO_SAVE="true"        # Enable/disable auto-saving history (true or false)

# Calculation Settings
CALCULATOR_PRECISION=4             # Number of decimal places for floating-point results
CALCULATOR_MAX_INPUT_VALUE=1000000000 # Maximum allowed numeric input value
CALCULATOR_DEFAULT_ENCODING="utf-8"  # Encoding for reading/writing history CSV

## Usage Guide ⌨️
To start the calculator's command-line interface (REPL), ensure your virtual environment is activated and run main.py from the project_root directory:
python main.py

## Available Commands
**Arithmetic Operations (require two numbers):**

**add <a> <b>**: Adds a and b.

**subtract <a> <b>**: Subtracts b from a.

**multiply <a> <b>**: Multiplies a and b.

**divide <a> <b>**: Divides a by b. (Error on division by zero)

**power <a> <b>**: Calculates a raised to the power of b.

**root <a> <b>**: Calculates the b-th root of a. (Error on even root of negative number)

**modulus <a> <b>**: Calculates a modulo b. (Error on modulus by zero)

**int_divide <a> <b>**: Performs integer division (a // b). (Error on division by zero)

**percent <a> <b>**: Calculates what percentage a is of b ((a / b) * 100). (Error if b is zero)

**abs_diff <a> <b>**: Calculates the absolute difference between a and b.

## History Management:

**h**istory**: Displays the current calculation history.

**clear**: Clears the calculation history (can be undone).

**undo**: Undoes the last calculation or history-modifying action (like clear or load).

**redo**: Redoes the last undone action.

## Persistence:

**save**: Manually saves the current history to the CSV file defined in .env (e.g., data/history.csv).

**load**: Loads the history from the CSV file, replacing the current history (can be undone).

## Other Commands:

**help**: Displays the list of available commands (dynamically generated).

**exit**: Exits the calculator application gracefully.

## Testing Instructions ✅
This project uses pytest for unit testing and pytest-cov for measuring code coverage. A pytest.ini file is included to configure test runs and ensure a separate test environment.

Activate Virtual Environment: Make sure your (venv) is active.

Run Tests: Navigate to the project_root directory and simply run:
pytest
The pytest.ini file automatically enables verbose output (-v), calculates coverage for the app directory (--cov=app), shows missing lines (--cov-report=term-missing), and enforces the 90% coverage requirement (--cov-fail-under=90).

If the tests complete without a "FAILED" message related to coverage, you have met the requirement.

Coverage Report: A detailed HTML coverage report can be generated if desired (requires pytest-cov):
pytest --cov=app --cov-report=html

## CI/CD Information (GitHub Actions) 🔄
A Continuous Integration (CI) workflow is defined in .github/workflows/python-app.yml. This workflow automatically runs on GitHub servers whenever code is pushed to the main branch or a pull request is opened against main.

Workflow Steps:

Checkout Code: Clones the repository code.

Set up Python: Configures the specified Python version.

Install Dependencies: Installs packages listed in requirements.txt using pip.

Run Tests & Check Coverage: Executes pytest using the configuration from pytest.ini (which includes --cov=app --cov-fail-under=90). If tests fail or coverage drops below 90%, the workflow run will fail, preventing merges of potentially broken code.

This ensures code quality and catches regressions automatically.