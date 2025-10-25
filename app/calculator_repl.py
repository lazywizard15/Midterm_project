########################
# Advanced Calculator REPL
########################

from decimal import Decimal
import logging
import colorama

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.operations import OperationFactory
from app.history import LoggingObserver, AutoSaveObserver

colorama.init(autoreset=True)

def calculator_repl():
    """
    Command-line interface for the advanced calculator.

    Implements a REPL that continuously prompts the user for commands,
    processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(colorama.Fore.CYAN + "Welcome to Advanced Calculator. Type 'help' for commands.")

        while True:
            try:
                command = input(colorama.Fore.YELLOW + ">> ").lower().strip()

                # Exit command
                if command in ['exit', 'quit']:
                    try:
                        calc.save_history()
                        print(colorama.Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(colorama.Fore.RED + f"Warning: Could not save history: {e}")
                    print(colorama.Fore.CYAN + "Goodbye!")
                    break

                # Help menu
                elif command == 'help':
                    print(colorama.Fore.CYAN + "\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue

                # Show history
                elif command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(colorama.Fore.MAGENTA + "No calculations in history.")
                    else:
                        print(colorama.Fore.CYAN + "\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                # Clear history
                elif command == 'clear':
                    calc.clear_history()
                    print(colorama.Fore.GREEN + "History cleared.")
                    continue

                # Undo
                elif command == 'undo':
                    if calc.undo():
                        print(colorama.Fore.GREEN + "Operation undone.")
                    else:
                        print(colorama.Fore.YELLOW + "Nothing to undo.")
                    continue

                # Redo
                elif command == 'redo':
                    if calc.redo():
                        print(colorama.Fore.GREEN + "Operation redone.")
                    else:
                        print(colorama.Fore.YELLOW + "Nothing to redo.")
                    continue

                # Save history
                elif command == 'save':
                    try:
                        calc.save_history()
                        print(colorama.Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(colorama.Fore.RED + f"Error saving history: {e}")
                    continue

                # Load history
                elif command == 'load':
                    try:
                        calc.load_history()
                        print(colorama.Fore.GREEN + "History loaded successfully.")
                    except Exception as e:
                        print(colorama.Fore.RED + f"Error loading history: {e}")
                    continue

                # Perform operations
                elif command.split()[0] in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'int_divide', 'percent', 'abs_diff']:
                    parts = command.split()
                    if len(parts) != 3:
                        print(colorama.Fore.YELLOW + "Usage: operation operand1 operand2")
                        continue
                    op_name, a_str, b_str = parts
                    try:
                        a = float(a_str)
                        b = float(b_str)
                    except ValueError:
                        print(colorama.Fore.RED + "Operands must be numbers.")
                        continue

                    try:
                        result = calc.perform_operation(op_name, a, b)
                        if isinstance(result, Decimal):
                            result = result.normalize()
                        print(colorama.Fore.MAGENTA + f"Result: {result}")
                    except (ValidationError, OperationError) as e:
                        print(colorama.Fore.RED + f"Error: {e}")
                    except Exception as e:
                        print(colorama.Fore.RED + f"Unexpected error: {e}")
                    continue

                else:
                    print(colorama.Fore.YELLOW + f"Unknown command: '{command}'. Type 'help' for commands.")

            except KeyboardInterrupt:
                print(colorama.Fore.YELLOW + "\nOperation cancelled (Ctrl+C)")
                continue
            except EOFError:
                print(colorama.Fore.CYAN + "\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(colorama.Fore.RED + f"Error: {e}")
                continue

    except Exception as e:
        print(colorama.Fore.RED + f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise

if __name__ == "__main__":
    calculator_repl()
