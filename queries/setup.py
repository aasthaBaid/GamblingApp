# queries/setup.py

from mysql.connector import Error
from db.db import create_connection


def drop_tables():
    """Drop all tables in the correct order (reverse of foreign key dependencies)"""
    connection = create_connection()
    cursor = connection.cursor()
    
    tables_to_drop = [
        "bet_history",
        "stake_transaction",
        "bet",
        "session",
        "betting_preferences",
        "strategy",
        "gambler"
    ]
    
    try:
        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        connection.commit()
        print("✅ All tables dropped successfully")
    except Error as e:
        print(f"Error dropping tables: {e}")
    finally:
        cursor.close()
        connection.close()


def create_tables():
    connection = create_connection()
    cursor = connection.cursor()

    # SQL statements for each table
    tables = {}

    tables["GAMBLER"] = """
    CREATE TABLE IF NOT EXISTS gambler (
        gambler_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        initial_balance DECIMAL(10,2) NOT NULL,
        current_balance DECIMAL(10,2) NOT NULL,
        total_winnings DECIMAL(10,2) DEFAULT 0,
        total_bets INT DEFAULT 0,
        min_balance DECIMAL(10,2),
        win_threshold DECIMAL(10,2),
        loss_threshold DECIMAL(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    tables["BETTING_PREFERENCES"] = """
    CREATE TABLE IF NOT EXISTS betting_preferences (
        preference_id INT AUTO_INCREMENT PRIMARY KEY,
        gambler_id INT,
        min_bet DECIMAL(10,2),
        max_bet DECIMAL(10,2),
        game_type VARCHAR(50),
        auto_play_enabled BOOLEAN DEFAULT FALSE,
        session_limit INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (gambler_id) REFERENCES gambler(gambler_id)
    );
    """

    tables["STRATEGY"] = """
    CREATE TABLE IF NOT EXISTS strategy (
        strategy_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        description TEXT
    );
    """

    tables["SESSION"] = """
    CREATE TABLE IF NOT EXISTS session (
        session_id INT AUTO_INCREMENT PRIMARY KEY,
        gambler_id INT,
        strategy_id INT,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP NULL,
        status VARCHAR(20),
        initial_balance DECIMAL(10,2),
        ending_balance DECIMAL(10,2),
        upper_limit DECIMAL(10,2),
        lower_limit DECIMAL(10,2),
        timeout INT,
        total_games INT DEFAULT 0,
        total_wins INT DEFAULT 0,
        total_losses INT DEFAULT 0,
        FOREIGN KEY (gambler_id) REFERENCES gambler(gambler_id),
        FOREIGN KEY (strategy_id) REFERENCES strategy(strategy_id)
    );
    """

    tables["BET"] = """
    CREATE TABLE IF NOT EXISTS bet (
        bet_id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT,
        bet_amount DECIMAL(10,2),
        bet_number INT,
        probability FLOAT,
        strategy_applied VARCHAR(50),
        outcome ENUM('WIN','LOSS') NOT NULL,
        stake_before DECIMAL(10,2),
        stake_after DECIMAL(10,2),
        placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES session(session_id)
    );
    """

    tables["BET_HISTORY"] = """
    CREATE TABLE IF NOT EXISTS bet_history (
        history_id INT AUTO_INCREMENT PRIMARY KEY,
        bet_id INT,
        result ENUM('WIN','LOSS') NOT NULL,
        win_amount DECIMAL(10,2),
        loss_amount DECIMAL(10,2),
        net_change DECIMAL(10,2),
        odds VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bet_id) REFERENCES bet(bet_id)
    );
    """

    tables["STAKE_TRANSACTION"] = """
    CREATE TABLE IF NOT EXISTS stake_transaction (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        gambler_id INT,
        session_id INT,
        bet_id INT NULL,
        type ENUM('INITIAL_STAKE','BET_PLACED','WIN','LOSS','DEPOSIT','WITHDRAWAL','RESET') NOT NULL,
        amount DECIMAL(10,2),
        balance_after DECIMAL(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (gambler_id) REFERENCES gambler(gambler_id),
        FOREIGN KEY (session_id) REFERENCES session(session_id),
        FOREIGN KEY (bet_id) REFERENCES bet(bet_id)
    );
    """

    # Execute all table creation queries
    for name, query in tables.items():
        try:
            cursor.execute(query)
            print(f"Table {name} created successfully.")
        except Error as e:
            print(f"Error creating {name}: {e}")

    cursor.close()
    connection.close()


def seed_strategies():
    """Insert default betting strategies into the strategy table"""
    connection = create_connection()
    cursor = connection.cursor()

    strategies = [
        ("Fixed", "Bet a fixed amount every round"),
        ("Percentage", "Bet a percentage of current stake"),
        ("Martingale", "Double bet after each loss, reset after win"),
    ]

    try:
        for name, description in strategies:
            # Check if strategy already exists
            cursor.execute("SELECT COUNT(*) FROM strategy WHERE name = %s", (name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO strategy (name, description) VALUES (%s, %s)",
                    (name, description)
                )
        connection.commit()
        print("✅ Default strategies seeded successfully")
    except Error as e:
        print(f"Error seeding strategies: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    drop_tables()
    create_tables()
    seed_strategies()
