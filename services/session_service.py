# services/session_service.py

from db.db import create_connection
from mysql.connector import Error
from datetime import datetime

class SessionService:
    def __init__(self):
        self.connection = create_connection()

    def start_session(self, gambler_id, strategy_id, initial_balance, upper_limit, lower_limit, timeout=None):
        """Start a new gambling session"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO session (gambler_id, strategy_id, start_time, status, initial_balance, upper_limit, lower_limit, timeout, total_games, total_wins, total_losses)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0)
            """
            values = (gambler_id, strategy_id, datetime.now(), "ACTIVE", initial_balance, upper_limit, lower_limit, timeout)
            cursor.execute(query, values)
            self.connection.commit()
            session_id = cursor.lastrowid
            print(f"✅ Session {session_id} started for gambler {gambler_id}")
            return session_id
        except Error as e:
            print(f"Error starting session: {e}")
            return None

    def pause_session(self, session_id, reason="Manual"):
        """Pause an active session"""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE session SET status = %s WHERE session_id = %s"
            cursor.execute(query, ("PAUSED", session_id))
            self.connection.commit()
            print(f"⏸️ Session {session_id} paused ({reason})")
        except Error as e:
            print(f"Error pausing session: {e}")

    def resume_session(self, session_id):
        """Resume a paused session"""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE session SET status = %s WHERE session_id = %s"
            cursor.execute(query, ("ACTIVE", session_id))
            self.connection.commit()
            print(f"▶️ Session {session_id} resumed")
        except Error as e:
            print(f"Error resuming session: {e}")

    def end_session(self, session_id, reason="Manual"):
        """End a session (win/loss/manual)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            # Fetch balances
            cursor.execute("SELECT initial_balance, gambler_id, upper_limit, lower_limit FROM session WHERE session_id = %s", (session_id,))
            session = cursor.fetchone()
            if not session:
                print("❌ Session not found")
                return

            # Determine end reason
            cursor.execute("SELECT current_balance FROM gambler WHERE gambler_id = %s", (session["gambler_id"],))
            balance = cursor.fetchone()["current_balance"]

            if balance >= session["upper_limit"]:
                status = "ENDED_WIN"
                reason = "Upper limit reached"
            elif balance <= session["lower_limit"]:
                status = "ENDED_LOSS"
                reason = "Lower limit reached"
            else:
                status = "ENDED_MANUAL"

            query = """
            UPDATE session SET status = %s, end_time = %s, ending_balance = %s WHERE session_id = %s
            """
            cursor.execute(query, (status, datetime.now(), balance, session_id))
            self.connection.commit()
            print(f"✅ Session {session_id} ended ({reason}), final balance = {balance}")
        except Error as e:
            print(f"Error ending session: {e}")

    def get_session_summary(self, session_id):
        """Retrieve session stats"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM session WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving session summary: {e}")
