import logging
import os
import pandas as pd
from colorama import Fore, Style
from app.calculator_config import CalculatorConfig

# Base Observer class
class HistoryObserver:
    def update(self, calculation): 
        pass

# Logging observer for console + file logging
class LoggingObserver(HistoryObserver):
    def __init__(self, config: CalculatorConfig = None):
        if config is None:
            config = CalculatorConfig()  # Default config if none provided
        self.config = config
        os.makedirs(self.config.log_dir, exist_ok=True)
        log_file = os.path.join(self.config.log_dir, "calculator.log")

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            force=True
        )

    def update(self, calc):
        logging.info(f"{calc}")
        print(Fore.GREEN + f"[LOG] {calc}" + Style.RESET_ALL)

# Auto-save observer for saving history to CSV
class AutoSaveObserver(HistoryObserver):
    def __init__(self, calculator, history_file="history.csv"):
        self.calculator = calculator
        self.history_file = os.path.join(self.calculator.config.history_dir, history_file)
        os.makedirs(self.calculator.config.history_dir, exist_ok=True)

    def update(self, calc):
        self.save(self.calculator.history)

    def save(self, history):
        """Save full history to CSV"""
        if not history:
            return
        df = pd.DataFrame([{
            'operation': str(c.operation),
            'operand1': str(c.operand1),
            'operand2': str(c.operand2),
            'result': str(c.result),
            'timestamp': c.timestamp
        } for c in history])

        df.to_csv(self.history_file, index=False)

    def load(self):
        """Load history from CSV"""
        if os.path.exists(self.history_file):
            df = pd.read_csv(self.history_file)
            if df.empty:
                return []
            from app.calculation import Calculation
            return [
                Calculation.from_dict({
                    'operation': row['operation'],
                    'operand1': row['operand1'],
                    'operand2': row['operand2'],
                    'result': row['result'],
                    'timestamp': row['timestamp']
                }) for _, row in df.iterrows()
            ]
        return []
