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


# main.py

from services.bet_service import BetService

bet_service = BetService()

# Run 5 fixed bets of 50 units
bet_service.fixed_strategy(session_id=1, base_amount=50, num_bets=5, probability=0.5)

# Run 5 percentage bets (10% of stake)
bet_service.percentage_strategy(session_id=1, percentage=0.1, num_bets=5, probability=0.5)
# Run 5 Martingale bets starting at 20 units
bet_service.martingale_strategy(session_id=1, base_amount=20, num_bets=5, probability=0.5)
