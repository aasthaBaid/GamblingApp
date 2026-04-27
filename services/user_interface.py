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
        print("--- Gambler Management ---")
        print("1. Create Gambler")
        print("2. View Gambler Stats")
        print("3. Update Gambler (name, thresholds)")
        print("4. Set Betting Preferences")
        print("5. Update Betting Preferences")
        print("6. View Betting Preferences")
        print("7. Reset Gambler")
        print("\n--- Session & Betting ---")
        print("8. Start Session")
        print("9. Place Bets")
        print("10. Pause/Resume Session")
        print("11. End Session")
        print("\n--- Reports ---")
        print("12. View Gambler Report")
        print("13. Exit")

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
                    print(f"✅ Gambler {name} created with ID {gambler_id}")
                except ValidationException as e:
                    print(f"Validation error: {e.message}")

            elif choice == "2":
                gambler_id = int(input("Enter gambler ID: "))
                stats = self.gambler_service.get_gambler_stats(gambler_id)
                if stats:
                    print("\n=== Gambler Stats ===")
                    print(f"Name: {stats['name']}")
                    print(f"Initial Balance: ${stats['initial_balance']}")
                    print(f"Current Balance: ${stats['current_balance']}")
                    print(f"Min Balance: ${stats['min_balance']}")
                    print(f"Win Threshold: ${stats['win_threshold']}")
                    print(f"Loss Threshold: ${stats['loss_threshold']}")
                    print(f"Total Winnings: ${stats['total_winnings']}")
                    print(f"Total Bets: {stats['total_bets']}")
                else:
                    print("❌ Gambler not found")


            elif choice == "3":
                gambler_id = int(input("Enter gambler ID: "))
                name = input("Enter new name (or press Enter to skip): ").strip()
                win_threshold = input("Enter new win threshold (or press Enter to skip): ").strip()
                loss_threshold = input("Enter new loss threshold (or press Enter to skip): ").strip()
                try:
                    self.gambler_service.update_gambler(
                        gambler_id,
                        name=name if name else None,
                        win_threshold=Decimal(win_threshold) if win_threshold else None,
                        loss_threshold=Decimal(loss_threshold) if loss_threshold else None
                    )
                    print("✅ Gambler updated successfully")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "4":
                gambler_id = int(input("Enter gambler ID: "))
                min_bet = Decimal(input("Min bet amount: "))
                max_bet = Decimal(input("Max bet amount: "))
                game_type = input("Game type (e.g., Roulette, Blackjack): ")
                auto_play = input("Auto-play enabled? (y/n): ").lower() == 'y'
                session_limit = int(input("Session limit: "))
                try:
                    pref_id = self.gambler_service.set_preferences(gambler_id, min_bet, max_bet, game_type, auto_play, session_limit)
                    print(f"✅ Betting preferences set (ID: {pref_id})")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "5":
                preference_id = int(input("Enter preference ID: "))
                min_bet = input("New min bet (or press Enter to skip): ").strip()
                max_bet = input("New max bet (or press Enter to skip): ").strip()
                game_type = input("New game type (or press Enter to skip): ").strip()
                auto_play = input("Auto-play enabled? (y/n/skip): ").strip().lower()
                session_limit = input("New session limit (or press Enter to skip): ").strip()
                try:
                    self.gambler_service.update_preferences(
                        preference_id,
                        min_bet=Decimal(min_bet) if min_bet else None,
                        max_bet=Decimal(max_bet) if max_bet else None,
                        game_type=game_type if game_type else None,
                        auto_play_enabled=True if auto_play == 'y' else (False if auto_play == 'n' else None),
                        session_limit=int(session_limit) if session_limit else None
                    )
                    print("✅ Betting preferences updated")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "6":
                gambler_id = int(input("Enter gambler ID: "))
                prefs = self.gambler_service.get_preferences(gambler_id)
                if prefs:
                    print("\n=== Betting Preferences ===")
                    print(f"Min Bet: ${prefs['min_bet']}")
                    print(f"Max Bet: ${prefs['max_bet']}")
                    print(f"Game Type: {prefs['game_type']}")
                    print(f"Auto-play Enabled: {prefs['auto_play_enabled']}")
                    print(f"Session Limit: {prefs['session_limit']}")
                else:
                    print("❌ No preferences found for this gambler")

            elif choice == "7":
                gambler_id = int(input("Enter gambler ID: "))
                confirm = input("Are you sure you want to reset this gambler? (y/n): ").lower()
                if confirm == 'y':
                    self.gambler_service.reset_gambler(gambler_id)
                    print("✅ Gambler reset successfully")
                else:
                    print("Reset cancelled")

            elif choice == "8":
                gambler_id = int(input("Enter gambler ID: "))
                strategy_id = int(input("Enter strategy ID: "))
                initial_balance = Decimal(input("Initial balance: "))
                upper_limit = Decimal(input("Upper limit: "))
                lower_limit = Decimal(input("Lower limit: "))
                session_id = self.session_service.start_session(gambler_id, strategy_id, initial_balance, upper_limit, lower_limit)
                if session_id:
                    print(f"✅ Session {session_id} started")

            elif choice == "9":
                session_id = int(input("Enter session ID: "))
                status = self.session_service.get_session_status(session_id)
                if status != "ACTIVE":
                    print(f"❌ Cannot place bets: session is {status}, not ACTIVE")
                else:
                    base_amount = Decimal(input("Bet amount: "))
                    num_bets = int(input("Number of bets: "))
                    probability = float(input("Win probability (0–1): "))
                    try:
                        InputValidator.validate_probability(probability)
                        self.bet_service.fixed_strategy(session_id, base_amount, num_bets, probability)
                    except ValidationException as e:
                        print(f"Validation error: {e.message}")

            elif choice == "10":
                session_id = int(input("Enter session ID: "))
                status = self.session_service.get_session_status(session_id)
                if status is None:
                    print(f"❌ Session {session_id} not found")
                elif status == "ACTIVE":
                    self.session_service.pause_session(session_id, "User action")
                elif status == "PAUSED":
                    self.session_service.resume_session(session_id)
                else:
                    print(f"❌ Cannot pause/resume: session is {status}")

            elif choice == "11":
                session_id = int(input("Enter session ID: "))
                self.session_service.end_session(session_id)

            elif choice == "12":
                gambler_id = int(input("Enter gambler ID: "))
                report = self.report_service.gambler_report(gambler_id)
                print("\n=== Gambler Report ===")
                for s in report["sessions"]:
                    print(f"Session {s['session_id']} | Status: {s['status']} | "
                          f"Initial: ${s['initial_balance']} | Ending: ${s['ending_balance']} | "
                          f"Wins: ${s['total_wins']} | Losses: ${s['total_losses']}")
                print(f"\nTotal Games: {report['total_games']} | Total Wins: ${report['total_wins']} | Total Losses: ${report['total_losses']}")

            elif choice == "13":
                print("Exiting Gambling App. Goodbye.")
                break

            else:
                print("❌ Invalid choice, please try again.")
