import sys
from pathlib import Path
from colorama import Fore, Style
from app.calculator_config import ConfigLoader
from app.logger import setup_logging
from app.operations import CommandFactory
from app.history import History
from app.calculator import Calculator
from app.observers import LoggingObserver, AutoSaveObserver
from app.repl import REPL
from app.exceptions import ConfigError

def main():
    """Initializes and runs the calculator application."""
    try:
        # 1. Load Configuration
        project_root = Path(__file__).parent
        config = ConfigLoader(dotenv_path=project_root / '.env')

        # 2. Setup Logging
        logger = setup_logging(config)
        logger.info("Application starting...")

        # 3. Setup Core Components
        command_factory = CommandFactory()
        history = History(config)
        calculator = Calculator(command_factory, history)

        # 4. Register Observers (Observer Pattern)
        logging_observer = LoggingObserver(logger)
        auto_save_observer = AutoSaveObserver(history) # Give it the history manager

        calculator.attach(logging_observer)
        if config.get_setting('CALCULATOR_AUTO_SAVE', 'false').lower() == 'true':
            calculator.attach(auto_save_observer)
            logger.info("Auto-save observer registered.")
        
        # 5. Start the REPL
        repl = REPL(calculator, config)
        repl.run()

    except ConfigError as e:
        print(f"{Fore.RED}Configuration Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}An unexpected critical error occurred: {e}{Style.RESET_ALL}", file=sys.stderr)
        if 'logger' in locals():
            locals()['logger'].critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)

    if 'logger' in locals():
        logger.info("Application shutting down gracefully.")
    print(f"\n{Fore.CYAN}Thank you for using the Advanced Calculator!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()