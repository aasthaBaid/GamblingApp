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
            print(f"Session {session_id} started for gambler {gambler_id}")
            return session_id
        except Error as e:
            print(f"Error starting session: {e}")
            return None

    def get_session_status(self, session_id):
        """Retrieve session status"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT status FROM session WHERE session_id = %s", (session_id,))
            result = cursor.fetchone()
            return result["status"] if result else None
        except Error as e:
            print(f"Error retrieving session status: {e}")
            return None

    def pause_session(self, session_id, reason="Manual"):
        """Pause an ACTIVE session only"""
        try:
            # Check if session exists and is ACTIVE
            status = self.get_session_status(session_id)
            if status is None:
                print(f"Session {session_id} not found")
                return False
            elif status != "ACTIVE":
                print(f"Cannot pause session {session_id}: session is {status}, not ACTIVE")
                return False

            cursor = self.connection.cursor()
            query = "UPDATE session SET status = %s WHERE session_id = %s"
            cursor.execute(query, ("PAUSED", session_id))
            self.connection.commit()
            print(f"Session {session_id} paused ({reason})")
            return True
        except Error as e:
            print(f"Error pausing session: {e}")
            return False

    def resume_session(self, session_id):
        """Resume a PAUSED session only"""
        try:
            # Check if session exists and is PAUSED
            status = self.get_session_status(session_id)
            if status is None:
                print(f"Session {session_id} not found")
                return False
            elif status != "PAUSED":
                print(f"Cannot resume session {session_id}: session is {status}, not PAUSED")
                return False

            cursor = self.connection.cursor()
            query = "UPDATE session SET status = %s WHERE session_id = %s"
            cursor.execute(query, ("ACTIVE", session_id))
            self.connection.commit()
            print(f"Session {session_id} resumed")
            return True
        except Error as e:
            print(f"Error resuming session: {e}")
            return False

    def end_session(self, session_id, reason="Manual"):
        """End a session (ACTIVE or PAUSED only)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Check if session exists
            cursor.execute("SELECT status, gambler_id, upper_limit, lower_limit FROM session WHERE session_id = %s", (session_id,))
            session = cursor.fetchone()
            if not session:
                print(f"Session {session_id} not found")
                return False
            
            # Check if session can be ended (must be ACTIVE or PAUSED)
            if session["status"] not in ["ACTIVE", "PAUSED"]:
                print(f"Cannot end session {session_id}: session is already {session['status']}")
                return False

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
            print(f"Session {session_id} ended ({reason}), final balance = {balance}")
            return True
        except Error as e:
            print(f"Error ending session: {e}")
            return False

    def get_session_summary(self, session_id):
        """Retrieve session stats"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM session WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving session summary: {e}")
