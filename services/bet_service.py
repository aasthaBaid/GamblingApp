# services/bet_service.py

import random
from decimal import Decimal
from db.db import create_connection
from mysql.connector import Error
from services.stake_service import StakeService

class BetService:
    def __init__(self):
        self.connection = create_connection()
        self.stake_service = StakeService()

    def create_bet(self, session_id, bet_amount, bet_number, probability, strategy_applied, stake_before):
        """Place a bet and determine outcome"""
        try:
            cursor = self.connection.cursor()

            # Determine outcome (win/loss)
            outcome = "WIN" if random.random() <= probability else "LOSS"
            stake_after = stake_before + bet_amount if outcome == "WIN" else stake_before - bet_amount

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

            print(f"✅ Bet {bet_id} created: {outcome}, new stake = {stake_after}")
            return bet_id, outcome, stake_after
        except Error as e:
            print(f"Error creating bet: {e}")
            return None, None, None

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
