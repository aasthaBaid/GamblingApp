from db.db import create_connection
from mysql.connector import Error

# bet_id (PK)
# session_id (FK)
# bet_amount
# bet_number
# probability
# strategy_applied
# stake_before
# stake_after
# placed_at


class BetService():

    def __init__(self):
        self.connection = create_connection()

    def create_bet(self, session_id, bet_amount, bet_number, probability, strategy_applied, stake_before, stake_after):
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO bet (session_id, bet_amount, bet_number, probability, strategy_applied, stake_before, stake_after)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (session_id, bet_amount, bet_number, probability, strategy_applied, stake_before, stake_after)
            cursor.execute(query, values)
            self.connection.commit()
            print("Bet created successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating bet: {e}")
            return None
        
    def get_bet(self, bet_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM bet WHERE bet_id = %s"
            cursor.execute(query, (bet_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving bet: {e}")
            return None
    
    def get_bets_by_session(self, session_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM bet WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving bets for session: {e}")
            return None
