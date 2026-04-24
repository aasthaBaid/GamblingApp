# services/report_service.py

from db.db import create_connection
from mysql.connector import Error

class ReportService:
    def __init__(self):
        self.connection = create_connection()

    def gambler_report(self, gambler_id):
        """Generate a report for a gambler across all sessions"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT s.session_id, s.start_time, s.end_time, s.status,
                   s.initial_balance, s.ending_balance, s.total_games,
                   s.total_wins, s.total_losses
            FROM session s
            WHERE s.gambler_id = %s
            ORDER BY s.start_time
            """
            cursor.execute(query, (gambler_id,))
            sessions = cursor.fetchall()

            report = {
                "gambler_id": gambler_id,
                "sessions": sessions,
                "total_sessions": len(sessions),
                "total_games": sum(s["total_games"] for s in sessions),
                "total_wins": sum(s["total_wins"] for s in sessions),
                "total_losses": sum(s["total_losses"] for s in sessions),
            }
            return report
        except Error as e:
            print(f"Error generating gambler report: {e}")
            return None

    def session_report(self, session_id):
        """Detailed report for a single session"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT b.bet_id, b.bet_amount, b.bet_number, b.probability,
                   b.strategy_applied, b.stake_before, b.stake_after, b.outcome
            FROM bet b
            WHERE b.session_id = %s
            ORDER BY b.placed_at
            """
            cursor.execute(query, (session_id,))
            bets = cursor.fetchall()

            summary = {
                "session_id": session_id,
                "total_bets": len(bets),
                "wins": sum(1 for b in bets if b["outcome"] == "WIN"),
                "losses": sum(1 for b in bets if b["outcome"] == "LOSS"),
                "final_stake": bets[-1]["stake_after"] if bets else None,
                "bets": bets
            }
            return summary
        except Error as e:
            print(f"Error generating session report: {e}")
            return None

    def overall_report(self):
        """Aggregate report across all gamblers and sessions"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT COUNT(*) AS total_sessions,
                   SUM(total_games) AS total_games,
                   SUM(total_wins) AS total_wins,
                   SUM(total_losses) AS total_losses
            FROM session
            """
            cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"Error generating overall report: {e}")
            return None
