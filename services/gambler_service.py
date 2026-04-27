# services/gambler_service.py

from db.db import create_connection
from mysql.connector import Error

class GamblerService:
    def __init__(self):
        self.connection = create_connection()

    #  Gambler Profile Methods 
    def create_gambler(self, name, initial_balance, min_balance, win_threshold, loss_threshold):
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO gambler (name, initial_balance, current_balance, min_balance, win_threshold, loss_threshold)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (name, initial_balance, initial_balance, min_balance, win_threshold, loss_threshold)
            cursor.execute(query, values)
            self.connection.commit()
            print("Gambler created successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating gambler: {e}")

    def update_gambler(self, gambler_id, name=None, win_threshold=None, loss_threshold=None):
        try:
            cursor = self.connection.cursor()
            updates, values = [], []

            if name:
                updates.append("name = %s")
                values.append(name)
            if win_threshold:
                updates.append("win_threshold = %s")
                values.append(win_threshold)
            if loss_threshold:
                updates.append("loss_threshold = %s")
                values.append(loss_threshold)

            if not updates:
                print("No updates provided.")
                return

            query = f"UPDATE gambler SET {', '.join(updates)} WHERE gambler_id = %s"
            values.append(gambler_id)
            cursor.execute(query, tuple(values))
            self.connection.commit()
            print("Gambler updated successfully")
        except Error as e:
            print(f"Error updating gambler: {e}")

    def get_gambler_stats(self, gambler_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM gambler WHERE gambler_id = %s"
            cursor.execute(query, (gambler_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving gambler stats: {e}")

    def reset_gambler(self, gambler_id):
        try:
            cursor = self.connection.cursor()
            query = """
            UPDATE gambler
            SET current_balance = initial_balance,
                total_winnings = 0,
                total_bets = 0
            WHERE gambler_id = %s
            """
            cursor.execute(query, (gambler_id,))
            self.connection.commit()
            print("Preferences   reset successfully")
        except Error as e:
            print(f"Error resetting gambler: {e}")

    # --- Betting Preferences Methods ---
    def set_preferences(self, gambler_id, min_bet, max_bet, game_type, auto_play_enabled, session_limit):
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO betting_preferences (gambler_id, min_bet, max_bet, game_type, auto_play_enabled, session_limit)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (gambler_id, min_bet, max_bet, game_type, auto_play_enabled, session_limit)
            cursor.execute(query, values)
            self.connection.commit()
            print("Preferences set successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"Error setting preferences: {e}")

    def update_preferences(self, preference_id, min_bet=None, max_bet=None, game_type=None, auto_play_enabled=None, session_limit=None):
        try:
            cursor = self.connection.cursor()
            updates, values = [], []

            if min_bet is not None:
                updates.append("min_bet = %s")
                values.append(min_bet)
            if max_bet is not None:
                updates.append("max_bet = %s")
                values.append(max_bet)
            if game_type is not None:
                updates.append("game_type = %s")
                values.append(game_type)
            if auto_play_enabled is not None:
                updates.append("auto_play_enabled = %s")
                values.append(auto_play_enabled)
            if session_limit is not None:
                updates.append("session_limit = %s")
                values.append(session_limit)

            if not updates:
                print("No updates provided.")
                return

            query = f"UPDATE betting_preferences SET {', '.join(updates)} WHERE preference_id = %s"
            values.append(preference_id)
            cursor.execute(query, tuple(values))
            self.connection.commit()
            print("Preferences updated successfully")
        except Error as e:
            print(f"Error updating preferences: {e}")

    def get_preferences(self, gambler_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM betting_preferences WHERE gambler_id = %s"
            cursor.execute(query, (gambler_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving preferences: {e}")
