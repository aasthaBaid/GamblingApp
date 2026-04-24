# services/winloss_service.py

from db.db import create_connection
from mysql.connector import Error
from decimal import Decimal

class WinLossService:
    def __init__(self):
        self.connection = create_connection()

    def calculate_winnings(self, bet_id, odds):
        """Calculate winnings based on bet odds"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT bet_amount, session_id FROM bet WHERE bet_id = %s", (bet_id,))
            bet = cursor.fetchone()
            if not bet:
                print("Bet not found")
                return None

            winnings = bet["bet_amount"] * Decimal(str(odds))
            print(f"Bet {bet_id} winnings = {winnings}")
            return winnings
        except Error as e:
            print(f"Error calculating winnings: {e}")
            return None

    def update_session_results(self, session_id):
        """Update session with total wins/losses"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT outcome, bet_amount FROM bet WHERE session_id = %s", (session_id,))
            bets = cursor.fetchall()

            total_wins = sum(b["bet_amount"] for b in bets if b["outcome"] == "WIN")
            total_losses = sum(b["bet_amount"] for b in bets if b["outcome"] == "LOSS")
            total_games = len(bets)

            query = """
            UPDATE session SET total_wins = %s, total_losses = %s, total_games = %s WHERE session_id = %s
            """
            cursor.execute(query, (total_wins, total_losses, total_games, session_id))
            self.connection.commit()
            print(f"Session {session_id} updated: Wins={total_wins}, Losses={total_losses}, Games={total_games}")
        except Error as e:
            print(f"Error updating session results: {e}")

    def track_streaks(self, session_id):
        """Track win/loss streaks for a session"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT outcome FROM bet WHERE session_id = %s ORDER BY placed_at", (session_id,))
            outcomes = [row["outcome"] for row in cursor.fetchall()]

            longest_win_streak = 0
            longest_loss_streak = 0
            current_win = 0
            current_loss = 0

            for outcome in outcomes:
                if outcome == "WIN":
                    current_win += 1
                    longest_win_streak = max(longest_win_streak, current_win)
                    current_loss = 0
                else:
                    current_loss += 1
                    longest_loss_streak = max(longest_loss_streak, current_loss)
                    current_win = 0

            return {
                "longest_win_streak": longest_win_streak,
                "longest_loss_streak": longest_loss_streak
            }
        except Error as e:
            print(f"Error tracking streaks: {e}")
            return None
