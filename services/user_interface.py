# services/user_interface.py

from decimal import Decimal
from services.gambler_service import GamblerService
from services.session_service import SessionService
from services.stake_service import StakeService
from services.bet_service import BetService
from services.winloss_service import WinLossService
from services.report_service import ReportService
from services.input_validator import ValidationException, InputValidator

class UserInterface:
    def __init__(self):
        self.gambler_service = GamblerService()
        self.session_service = SessionService()
        self.stake_service = StakeService()
        self.bet_service = BetService()
        self.winloss_service = WinLossService()
        self.report_service = ReportService()

    def display_menu(self):
        print("\n=== Gambling App Menu ===")
        print("1. Create Gambler")
        print("2. Start Session")
        print("3. Place Bets")
        print("4. End Session")
        print("5. View Gambler Report")
        print("6. Exit")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Select an option: ")

            if choice == "1":
                name = input("Enter gambler name: ")
                initial_balance = Decimal(input("Initial balance: "))
                min_balance = Decimal(input("Minimum balance: "))
                upper_limit = Decimal(input("Upper limit: "))
                lower_limit = Decimal(input("Lower limit: "))
                try:
                    InputValidator.validate_stake(initial_balance)
                    InputValidator.validate_limits(initial_balance, upper_limit, lower_limit)
                    gambler_id = self.gambler_service.create_gambler(name, initial_balance, min_balance, upper_limit, lower_limit)
                    print(f"Gambler {name} created with ID {gambler_id}")
                except ValidationException as e:
                    print(f"Validation error: {e.message}")

            elif choice == "2":
                gambler_id = int(input("Enter gambler ID: "))
                strategy_id = int(input("Enter strategy ID: "))
                initial_balance = Decimal(input("Initial balance: "))
                upper_limit = Decimal(input("Upper limit: "))
                lower_limit = Decimal(input("Lower limit: "))
                session_id = self.session_service.start_session(gambler_id, strategy_id, initial_balance, upper_limit, lower_limit)
                print(f"Session {session_id} started")

            elif choice == "3":
                session_id = int(input("Enter session ID: "))
                base_amount = Decimal(input("Bet amount: "))
                num_bets = int(input("Number of bets: "))
                probability = float(input("Win probability (0–1): "))
                try:
                    InputValidator.validate_probability(probability)
                    self.bet_service.fixed_strategy(session_id, base_amount, num_bets, probability)
                except ValidationException as e:
                    print(f"Validation error: {e.message}")

            elif choice == "4":
                session_id = int(input("Enter session ID: "))
                self.session_service.end_session(session_id)

            elif choice == "5":
                gambler_id = int(input("Enter gambler ID: "))
                report = self.report_service.gambler_report(gambler_id)
                print("\n=== Gambler Report ===")
                for s in report["sessions"]:
                    print(f"Session {s['session_id']} | Status: {s['status']} | "
                          f"Initial: {s['initial_balance']} | Ending: {s['ending_balance']} | "
                          f"Wins: {s['total_wins']} | Losses: {s['total_losses']}")
                print(f"Total Games: {report['total_games']} | Total Wins: {report['total_wins']} | Total Losses: {report['total_losses']}")

            elif choice == "6":
                print("Exiting Gambling App. Goodbye.")
                break

            else:
                print("Invalid choice, please try again.")
