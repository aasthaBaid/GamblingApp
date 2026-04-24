# from services.gambler_service import GamblerService

# service = GamblerService()

# #create gambler
# #gambler_id = service.create_gambler(
# #     name="Alice",
# #     initial_balance=1000,
# #     min_balance=100,
# #     win_threshold=2000,
# #     loss_threshold=200
# # )

# # Set preferences
# pref_id = service.set_preferences(
#     gambler_id=1,
#     min_bet=10,
#     max_bet=200,
#     game_type="Roulette",
#     auto_play_enabled=True,
#     session_limit=50
# )


# # Update gambler thresholds
# service.update_gambler(gambler_id=1, win_threshold=2500)

# # Retrieve stats
# stats = service.get_gambler_stats(gambler_id=1)
# print(stats)

# Reset gambler
#service.reset_gambler(gambler_id=1)



# from services.bet_service import BetService

# bet_service = BetService()

# # Run 5 fixed bets of 50 units
# bet_service.fixed_strategy(session_id=1, base_amount=50, num_bets=5, probability=0.5)

# # Run 5 percentage bets (10% of stake)
# bet_service.percentage_strategy(session_id=1, percentage=0.1, num_bets=5, probability=0.5)
# # Run 5 Martingale bets starting at 20 units
# bet_service.martingale_strategy(session_id=1, base_amount=20, num_bets=5, probability=0.5)


# main.py

# from services.session_service import SessionService

# session_service = SessionService()

# # Start a new session
# session_id = session_service.start_session(
#     gambler_id=1,
#     strategy_id=1,
#     initial_balance=1000,
#     upper_limit=2000,
#     lower_limit=200,
#     timeout=60
# )

# # Pause and resume
# session_service.pause_session(session_id, reason="Break")
# session_service.resume_session(session_id)

# # End session
# session_service.end_session(session_id)

# # Get summary
# summary = session_service.get_session_summary(session_id)
# print(summary)


# main.py

# from services.winloss_service import WinLossService

# winloss_service = WinLossService()

# # Calculate winnings for a bet with odds 2.0
# winloss_service.calculate_winnings(bet_id=12, odds=2.0)

# # Update session results
# winloss_service.update_session_results(session_id=1)

# # Track streaks
# streaks = winloss_service.track_streaks(session_id=1)
# print(streaks)


# main.py

from services.gambler_service import GamblerService
from services.session_service import SessionService
from services.stake_service import StakeService
from services.bet_service import BetService
from services.winloss_service import WinLossService

def main():
    gambler_service = GamblerService()
    session_service = SessionService()
    stake_service = StakeService()
    bet_service = BetService()
    winloss_service = WinLossService()

    # --- UC1: Create gamblers ---
    alice_id = gambler_service.create_gambler("Alice", 1000, 100, 2000, 200)
    bob_id   = gambler_service.create_gambler("Bob", 1500, 200, 3000, 300)

    # --- UC4: Start sessions (assumes strategy_id=1 exists in DB) ---
    alice_session = session_service.start_session(alice_id, strategy_id=1,
                                                  initial_balance=1000,
                                                  upper_limit=2000,
                                                  lower_limit=200)
    bob_session   = session_service.start_session(bob_id, strategy_id=1,
                                                  initial_balance=1500,
                                                  upper_limit=3000,
                                                  lower_limit=300)

    # --- UC2: Initialize stake ---
    stake_service.initialize_stake(alice_id, alice_session, 1000, upper_limit=2000, lower_limit=200)
    stake_service.initialize_stake(bob_id, bob_session, 1500, upper_limit=3000, lower_limit=300)

    # --- UC3: Place bets with strategies ---
    bet_service.fixed_strategy(session_id=alice_session, base_amount=50, num_bets=3, probability=0.5)
    bet_service.martingale_strategy(session_id=bob_session, base_amount=20, num_bets=3, probability=0.5)

    # --- UC5: Calculate results ---
    winloss_service.update_session_results(alice_session)
    winloss_service.update_session_results(bob_session)

    print("Alice streaks:", winloss_service.track_streaks(alice_session))
    print("Bob streaks:", winloss_service.track_streaks(bob_session))

    # End sessions
    session_service.end_session(alice_session)
    session_service.end_session(bob_session)

    # Show summaries
    print("Alice summary:", session_service.get_session_summary(alice_session))
    print("Bob summary:", session_service.get_session_summary(bob_session))

if __name__ == "__main__":
    main()

