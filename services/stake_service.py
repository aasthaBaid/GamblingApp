# services/stake_service.py

from db.db import create_connection
from mysql.connector import Error

class StakeService:
    def __init__(self):
        self.connection = create_connection()
        # Track volatility in memory per session
        self.session_peak = {}
        self.session_low = {}

    def initialize_stake(self, gambler_id, session_id, amount, upper_limit, lower_limit):
        """Initialize starting stake with validation and boundaries"""
        try:
            cursor = self.connection.cursor()

            # Ensure session exists
            cursor.execute("SELECT session_id FROM session WHERE session_id = %s", (session_id,))
            if cursor.fetchone() is None:
                print(f"Session {session_id} does not exist. Create session first.")
                return

            # Update gambler balance
            cursor.execute("UPDATE gambler SET current_balance = %s WHERE gambler_id = %s", (amount, gambler_id))

            # Record transaction
            query = """
            INSERT INTO stake_transaction (gambler_id, session_id, type, amount, balance_after)
            VALUES (%s, %s, 'INITIAL_STAKE', %s, %s)
            """
            cursor.execute(query, (gambler_id, session_id, amount, amount))
            self.connection.commit()

            # Initialize volatility tracking
            self.session_peak[session_id] = amount
            self.session_low[session_id] = amount

            print("Stake initialized successfully")
        except Error as e:
            print(f"Error initializing stake: {e}")

    def record_transaction(self, gambler_id, session_id, bet_id, tx_type, amount, upper_limit=None, lower_limit=None):
        """Record stake change and validate boundaries"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Ensure session exists
            cursor.execute("SELECT session_id FROM session WHERE session_id = %s", (session_id,))
            if cursor.fetchone() is None:
                print(f"Session {session_id} does not exist. Create session first.")
                return

            # Get current balance
            cursor.execute("SELECT current_balance FROM gambler WHERE gambler_id = %s", (gambler_id,))
            balance = cursor.fetchone()["current_balance"]

            # Update balance depending on transaction type
            if tx_type in ("WIN", "DEPOSIT"):
                new_balance = balance + amount
            elif tx_type in ("LOSS", "BET_PLACED", "WITHDRAWAL"):
                new_balance = balance - amount
            elif tx_type in ("RESET", "INITIAL_STAKE"):
                new_balance = amount
            else:
                print("Invalid transaction type")
                return

            # Update gambler balance
            cursor.execute("UPDATE gambler SET current_balance = %s WHERE gambler_id = %s", (new_balance, gambler_id))

            # Insert transaction record
            query = """
            INSERT INTO stake_transaction (gambler_id, session_id, bet_id, type, amount, balance_after)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (gambler_id, session_id, bet_id, tx_type, amount, new_balance))
            self.connection.commit()

            # Track volatility
            self.session_peak[session_id] = max(self.session_peak.get(session_id, new_balance), new_balance)
            self.session_low[session_id] = min(self.session_low.get(session_id, new_balance), new_balance)

            # Boundary validation
            if upper_limit and new_balance >= upper_limit:
                print(f"Upper limit reached! Balance = {new_balance}")
            if lower_limit and new_balance <= lower_limit:
                print(f"Lower limit reached! Balance = {new_balance}")

            print(f"Transaction recorded: {tx_type}, new balance = {new_balance}")
            return new_balance
        except Error as e:
            print(f"Error recording transaction: {e}")

    def get_volatility(self, session_id):
        """Calculate volatility for a session"""
        peak = self.session_peak.get(session_id)
        low = self.session_low.get(session_id)
        if peak is None or low is None:
            return None
        volatility = ((peak - low) / peak) * 100 if peak > 0 else 0
        return {"peak": peak, "low": low, "volatility_percent": round(volatility, 2)}

    def get_stake_history(self, gambler_id, session_id=None):
        """Retrieve full stake history for gambler (optionally filtered by session)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if session_id:
                query = "SELECT * FROM stake_transaction WHERE gambler_id = %s AND session_id = %s ORDER BY created_at"
                cursor.execute(query, (gambler_id, session_id))
            else:
                query = "SELECT * FROM stake_transaction WHERE gambler_id = %s ORDER BY created_at"
                cursor.execute(query, (gambler_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving stake history: {e}")
