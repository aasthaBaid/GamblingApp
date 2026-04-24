# services/strategy_service.py

from db.db import create_connection
from mysql.connector import Error

class StrategyService:
    def __init__(self):
        self.connection = create_connection()

    def create_strategy(self, name, description):
        """Create a new betting strategy"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO strategy (name, description) VALUES (%s, %s)"
            cursor.execute(query, (name, description))
            self.connection.commit()
            strategy_id = cursor.lastrowid
            print(f"Strategy '{name}' created with ID {strategy_id}")
            return strategy_id
        except Error as e:
            print(f"Error creating strategy: {e}")
            return None

    def get_strategy(self, strategy_id):
        """Retrieve a strategy by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM strategy WHERE strategy_id = %s"
            cursor.execute(query, (strategy_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving strategy: {e}")
            return None

    def list_strategies(self):
        """List all strategies"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM strategy"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error listing strategies: {e}")
            return []

    def update_strategy(self, strategy_id, name=None, description=None):
        """Update strategy details"""
        try:
            cursor = self.connection.cursor()
            updates, values = [], []
            if name:
                updates.append("name = %s")
                values.append(name)
            if description:
                updates.append("description = %s")
                values.append(description)
            if not updates:
                print("No updates provided.")
                return
            query = f"UPDATE strategy SET {', '.join(updates)} WHERE strategy_id = %s"
            values.append(strategy_id)
            cursor.execute(query, tuple(values))
            self.connection.commit()
            print(f"Strategy {strategy_id} updated")
        except Error as e:
            print(f"Error updating strategy: {e}")
