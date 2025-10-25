"""
REPL (Read-Eval-Print Loop) interface for the calculator.
"""
from app.calculator import Calculator
from app.operations import OperationFactory
from app.history import LoggingObserver, AutoSaveObserver
from app.exceptions import ValidationError, OperationError


def calculator_repl():
    """Run the calculator REPL."""
    calculator = Calculator()
    
    # Add observers
    calculator.add_observer(LoggingObserver())
    calculator.add_observer(AutoSaveObserver(calculator))
    
    print("Welcome to Advanced Calculator. Type 'help' for commands.")
    
    # Try to load history
    try:
        calculator.load_history()
    except Exception as e:
        print(f"Warning: Could not load history: {str(e)}")
    
    while True:
        try:
            user_input = input("\n> ").strip().lower()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input == 'exit' or user_input == 'quit':
                try:
                    calculator.save_history()
                    print("History saved successfully.")
                except Exception as e:
                    print(f"Warning: Could not save history: {str(e)}")
                print("Goodbye!")
                break
            
            elif user_input == 'help':
                print_help()
            
            elif user_input == 'history':
                show_history(calculator)
            
            elif user_input == 'clear':
                calculator.clear_history()
                print("History cleared.")
            
            elif user_input == 'undo':
                if calculator.undo():
                    print("Undo successful.")
                else:
                    print("Nothing to undo.")
            
            elif user_input == 'redo':
                if calculator.redo():
                    print("Redo successful.")
                else:
                    print("Nothing to redo.")
            
            elif user_input == 'operations':
                print("\nAvailable operations:")
                ops = OperationFactory.get_available_operations()
                unique_ops = sorted(set(ops))
                for op in unique_ops:
                    print(f"  - {op}")
            
            else:
                # Try to parse as operation
                parts = user_input.split()
                
                if len(parts) == 3:
                    operation_name, operand1, operand2 = parts
                    process_calculation(calculator, operation_name, operand1, operand2)
                elif len(parts) == 1:
                    # Single operation name, prompt for operands
                    operation_name = parts[0]
                    try:
                        OperationFactory.create_operation(operation_name)
                        operand1 = input("Enter first operand: ").strip()
                        operand2 = input("Enter second operand: ").strip()
                        process_calculation(calculator, operation_name, operand1, operand2)
                    except ValidationError:
                        print("Usage: operation operand1 operand2")
                        print("Example: add 5 3")
                        print("Type 'help' for more commands.")
                else:
                    print("Usage: operation operand1 operand2")
                    print("Example: add 5 3")
                    print("Type 'help' for more commands.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit.")
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print("  <operation> <num1> <num2> - Perform calculation")
    print("  help - Show this help message")
    print("  operations - List available operations")
    print("  history - Show calculation history")
    print("  clear - Clear calculation history")
    print("  undo - Undo the last calculation")
    print("  redo - Redo the last undone calculation")
    print("  exit/quit - Exit the calculator")
    print("\nExample: add 5 3")


def show_history(calculator: Calculator):
    """Display calculation history."""
    history = calculator.get_history()
    if not history:
        print("No calculations in history.")
        return
    
    print("\nCalculation History:")
    for i, calc in enumerate(history, 1):
        print(f"  {i}. {calc.operand1} {calc.operation} {calc.operand2} = {calc.result}")


def process_calculation(calculator: Calculator, operation_name: str, operand1: str, operand2: str):
    """
    Process a calculation.
    
    Args:
        calculator (Calculator): The calculator instance.
        operation_name (str): Name of the operation.
        operand1 (str): First operand.
        operand2 (str): Second operand.
    """
    try:
        operation = OperationFactory.create_operation(operation_name)
        calculator.set_operation(operation)
        result = calculator.perform_operation(operand1, operand2)
        print(f"\nResult: {result}")
    except ValidationError as e:
        print(f"Validation Error: {str(e)}")
    except OperationError as e:
        print(f"Operation Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    calculator_repl()