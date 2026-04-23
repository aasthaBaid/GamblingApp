from services.gambler_service import GamblerService

service = GamblerService()

#create gambler
#gambler_id = service.create_gambler(
#     name="Alice",
#     initial_balance=1000,
#     min_balance=100,
#     win_threshold=2000,
#     loss_threshold=200
# )

# Set preferences
pref_id = service.set_preferences(
    gambler_id=1,
    min_bet=10,
    max_bet=200,
    game_type="Roulette",
    auto_play_enabled=True,
    session_limit=50
)


# Update gambler thresholds
service.update_gambler(gambler_id=1, win_threshold=2500)

# Retrieve stats
stats = service.get_gambler_stats(gambler_id=1)
print(stats)

# Reset gambler
#service.reset_gambler(gambler_id=1)