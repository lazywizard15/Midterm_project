"""
The Read-Eval-Print Loop (REPL) for the command-line interface.
Implements color output (Optional Feature) and dynamic help (Optional Feature).
"""
import sys
from typing import Callable, Dict, Optional

# --- DEBUG: Make sure colorama is imported ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True) # Initialize colorama
except ImportError:
    print("REPL Error: colorama not found!")
    sys.exit(1)
# --- END DEBUG ---

from app.calculator import Calculator
from app.calculator_config import ConfigLoader
from app.input_validators import InputHelper
from app.exceptions import CalculatorError

# --- Dynamic Help / Command Decorator ---
repl_commands: Dict[str, 'REPLCommand'] = {}

class REPLCommand:
    """A wrapper for REPL commands to store metadata for dynamic help."""
    def __init__(self, func: Callable, description: str, usage: Optional[str] = None):
        self.func = func
        self.description = description
        # Use function name as key, remove '_handler' suffix
        self.name = func.__name__.replace('_handler', '')
        self.usage = usage or self.name
        
def register_command(description: str, usage: Optional[str] = None):
    """Decorator to register a REPL command handler."""
    def decorator(func: Callable):
        cmd = REPLCommand(func, description, usage)
        repl_commands[cmd.name] = cmd
        return func
    return decorator

class REPL:
    """
    Manages the REPL, parsing input and calling the Calculator.
    Uses 'colorama' for color-coded output.
    """
    def __init__(self, calculator: Calculator, config: ConfigLoader):
        # init(autoreset=True) # Moved to top
        self.calculator = calculator
        self.config = config
        
        max_val = float(config.get_setting('CALCULATOR_MAX_INPUT_VALUE', 1e9))
        self.input_helper = InputHelper(max_value=max_val, min_value=-max_val)
        
        self.precision = int(config.get_setting('CALCULATOR_PRECISION', 4))
        
        self.is_running = True

    def _format_result(self, value: float) -> str:
        """Formats a numeric result according to precision rules."""
        if value.is_integer():
            return str(int(value))
        return f"{value:.{self.precision}f}"

    def run(self):
        """Starts the main REPL loop."""
        
        # --- DEBUG CHECKPOINT 10 ---
        print(f"{Fore.GREEN}--- CHECKPOINT 10: REPL.run() started. ---{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Welcome to the Advanced Calculator!{Style.RESET_ALL}")
        print(f"Type '{Fore.CYAN}help{Style.RESET_ALL}' for a list of commands.")
        
        while self.is_running:
            try:
                raw_input = input(f"{Fore.YELLOW}>>> {Style.RESET_ALL}").strip()
                if not raw_input:
                    continue
                
                command_name, operands = self.input_helper.parse_command_input(raw_input)
                
                handler = repl_commands.get(command_name)
                if handler:
                    handler.func(self, *operands)
                else:
                    print(f"{Fore.RED}Unknown command: '{command_name}'") # pragma: no cover

            except CalculatorError as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            except (EOFError, KeyboardInterrupt):
                self.is_running = False # pragma: no cover
            except Exception as e:
                print(f"{Fore.RED}An unexpected application error occurred: {e}{Style.RESET_ALL}")
                import logging # pragma: no cover
                logging.getLogger('app').critical(f"REPL Error: {e}", exc_info=True) # pragma: no cover

    # --- REPL Command Handlers ---
    
    def _handle_arithmetic(self, command_name: str, a: float, b: float):
        result = self.calculator.execute_command(command_name, a, b)
        formatted_result = self._format_result(result)
        print(f"{Fore.CYAN}Result: {formatted_result}{Style.RESET_ALL}")

    @register_command("Adds two numbers.", "add <a> <b>")
    def add(self, a: float, b: float):
        self._handle_arithmetic('add', a, b)

    @register_command("Subtracts the second number from the first.", "subtract <a> <b>")
    def subtract(self, a: float, b: float):
        self._handle_arithmetic('subtract', a, b)

    @register_command("Multiplies two numbers.", "multiply <a> <b>")
    def multiply(self, a: float, b: float):
        self._handle_arithmetic('multiply', a, b)

    @register_command("Divides the first number by the second.", "divide <a> <b>")
    def divide(self, a: float, b: float):
        self._handle_arithmetic('divide', a, b)

    @register_command("Raises <a> to the power of <b>.", "power <a> <b>")
    def power(self, a: float, b: float):
        self._handle_arithmetic('power', a, b)

    @register_command("Calculates the <b>-th root of <a>.", "root <a> <b>")
    def root(self, a: float, b: float):
        self._handle_arithmetic('root', a, b)

    @register_command("Calculates <a> modulo <b>.", "modulus <a> <b>")
    def modulus(self, a: float, b: float):
        self._handle_arithmetic('modulus', a, b)

    @register_command("Performs integer division of <a> by <b>.", "int_divide <a> <b>")
    def int_divide(self, a: float, b: float):
        self._handle_arithmetic('int_divide', a, b)

    @register_command("Calculates what percentage <a> is of <b>.", "percent <a> <b>")
    def percent(self, a: float, b: float):
        self._handle_arithmetic('percent', a, b)

    @register_command("Calculates the absolute difference between <a> and <b>.", "abs_diff <a> <b>")
    def abs_diff(self, a: float, b: float):
        self._handle_arithmetic('abs_diff', a, b)

    @register_command("Displays the calculation history.")
    def history(self):
        history = self.calculator.get_history()
        if not history:
            print(f"{Fore.MAGENTA}History is empty.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.MAGENTA}--- Calculation History ---{Style.RESET_ALL}")
        for record in history:
            print(f"{Fore.MAGENTA}  {record}{Style.RESET_ALL}")

    @register_command("Clears the entire calculation history.")
    def clear(self):
        self.calculator.clear_history()
        print(f"{Fore.GREEN}History cleared.{Style.RESET_ALL}")

    @register_command("Undoes the last calculation or action.")
    def undo(self):
        self.calculator.undo()
        print(f"{Fore.GREEN}Undo successful.{Style.RESET_ALL}")

    @register_command("Redoes the last undone action.")
    def redo(self):
        self.calculator.redo()
        print(f"{Fore.GREEN}Redo successful.{Style.RESET_ALL}")

    @register_command("Manually saves history to CSV.")
    def save(self):
        self.calculator.save_history()
        path = self.config.get_history_file_path()
        print(f"{Fore.GREEN}History saved to {path}{Style.RESET_ALL}")

    @register_command("Manually loads history from CSV.")
    def load(self):
        self.calculator.load_history()
        print(f"{Fore.GREEN}History loaded.{Style.RESET_ALL}")
        self.history()

    @register_command("Displays this help menu.")
    def help(self):
        print("{}{}--- Available Commands ---{}".format(Fore.GREEN, Style.BRIGHT, Style.RESET_ALL))
        
        # Find the longest usage string for nice alignment
        max_len = max(len(cmd.usage) for cmd in repl_commands.values()) + 2  # Add 2 for padding
        
        # Iterate over the dynamically registered commands
        for cmd in sorted(repl_commands.values(), key=lambda c: c.name):
            # Create the padded usage string
            usage_str = "{}{:<{width}}{}".format(Fore.CYAN, cmd.usage, Style.RESET_ALL, width=max_len)
            description = cmd.description
            print("  {} : {}".format(usage_str, description))

    @register_command("Exits the application.")
    def exit(self):
        self.is_running = False