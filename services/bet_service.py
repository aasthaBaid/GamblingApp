# services/bet_service.py

import random
from decimal import Decimal
from db.db import create_connection
from mysql.connector import Error
from services.input_validator import InputValidator , ValidationException
from services.stake_service import StakeService


class BetService:
    def __init__(self):
        self.connection = create_connection()
        self.stake_service = StakeService()

    def create_bet(self, session_id, bet_amount, bet_number, probability, strategy_applied, stake_before):
        """Place a bet and determine outcome"""
        try:
            if stake_before <= 0:
                print(f"Cannot place bet: balance ({stake_before}) is zero or negative")
                return None, None, stake_before 
            InputValidator.validate_bet_amount(bet_amount, stake_before)
            InputValidator.validate_probability(probability)

            cursor = self.connection.cursor(dictionary=True)

            # Fetch session limits
            cursor.execute("SELECT lower_limit, upper_limit FROM session WHERE session_id = %s", (session_id,))
            session = cursor.fetchone()
            if not session:
                print("Session not found")
                return None, None, stake_before
            
            lower_limit = session["lower_limit"]
            upper_limit = session["upper_limit"]

            # Check if current balance is already below lower limit
            if stake_before <= lower_limit:
                print(f"Cannot place bet: balance ({stake_before}) is at or below lower limit ({lower_limit})")
                return None, None, stake_before

            # Determine outcome (win/loss)
            outcome = "WIN" if random.random() <= probability else "LOSS"
            stake_after = stake_before + bet_amount if outcome == "WIN" else stake_before - bet_amount

            # Check if bet would breach lower limit
            if stake_after < lower_limit:
                print(f"Cannot place bet: resulting balance ({stake_after}) would breach lower limit ({lower_limit})")
                return None, None, stake_before

            # Insert bet record
            query = """
            INSERT INTO bet (session_id, bet_amount, bet_number, probability, strategy_applied, outcome, stake_before, stake_after)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (session_id, bet_amount, bet_number, probability, strategy_applied, outcome, stake_before, stake_after)
            cursor.execute(query, values)
            self.connection.commit()
            bet_id = cursor.lastrowid

            # Record stake transaction
            tx_type = "WIN" if outcome == "WIN" else "LOSS"
            self.stake_service.record_transaction(
                gambler_id=self.get_gambler_id(session_id),
                session_id=session_id,
                bet_id=bet_id,
                tx_type=tx_type,
                amount=bet_amount
            )

            # Check if session should end (hit limits)
            if stake_after >= upper_limit:
                print(f"Upper limit ({upper_limit}) reached! Session should be ended.")
                self._end_session_auto(session_id, "Upper limit reached")
            elif stake_after <= lower_limit:
                print(f"Lower limit ({lower_limit}) reached! Session should be ended.")
                self._end_session_auto(session_id, "Lower limit reached")

            print(f"Bet {bet_id} created: {outcome}, new stake = {stake_after}")
            return bet_id, outcome, stake_after

        except ValidationException as ve:
            print(f"Validation failed: {ve.message}")
            return None, None, stake_before  
        except Error as e:
            print(f"Error creating bet: {e}")
            return None, None, None
    
    def _end_session_auto(self, session_id, reason):
        """Auto-end session when limits are reached"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT gambler_id FROM session WHERE session_id = %s", (session_id,))
            session = cursor.fetchone()
            if not session:
                return
            
            cursor.execute("SELECT current_balance FROM gambler WHERE gambler_id = %s", (session["gambler_id"],))
            balance = cursor.fetchone()["current_balance"]
            
            status = "ENDED_WIN" if balance >= 0 else "ENDED_LOSS"
            from datetime import datetime
            query = "UPDATE session SET status = %s, end_time = %s, ending_balance = %s WHERE session_id = %s"
            cursor.execute(query, (status, datetime.now(), balance, session_id))
            self.connection.commit()
        except Error as e:
            print(f"Error auto-ending session: {e}")      
        

    def get_gambler_id(self, session_id):
        """Helper to fetch gambler_id from session"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT gambler_id FROM session WHERE session_id = %s", (session_id,))
        result = cursor.fetchone()
        return result["gambler_id"] if result else None

    # --- Strategy Implementations ---
    def fixed_strategy(self, session_id, base_amount, num_bets, probability):
        """Always bet the same amount"""
        stake = self.get_current_stake(session_id)
        for i in range(1, num_bets+1):
            self.create_bet(session_id, base_amount, i, probability, "Fixed", stake)
            stake = self.get_current_stake(session_id)

    def percentage_strategy(self, session_id, percentage, num_bets, probability):
        """Bet a percentage of current stake"""
        stake = self.get_current_stake(session_id)
        for i in range(1, num_bets+1):
            # Ensure both operands are Decimal
            bet_amount = Decimal(stake) * Decimal(str(percentage))
            self.create_bet(session_id, bet_amount, i, probability, "Percentage", stake)
            stake = self.get_current_stake(session_id)

    def martingale_strategy(self, session_id, base_amount, num_bets, probability):
        """Double bet after each loss, reset after win"""
        stake = self.get_current_stake(session_id)
        bet_amount = base_amount
        for i in range(1, num_bets+1):
            bet_id, outcome, stake = self.create_bet(session_id, bet_amount, i, probability, "Martingale", stake)
            if outcome == "LOSS":
                bet_amount *= 2
            else:
                bet_amount = base_amount

    # Helper
    def get_current_stake(self, session_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT g.current_balance 
            FROM gambler g 
            JOIN session s ON g.gambler_id = s.gambler_id 
            WHERE s.session_id = %s
        """, (session_id,))
        result = cursor.fetchone()
        return result["current_balance"] if result else 0
