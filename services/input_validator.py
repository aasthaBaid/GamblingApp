# services/input_validator.py

class ValidationException(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InputValidator:
    @staticmethod
    def validate_stake(amount):
        if amount is None or amount <= 0:
            raise ValidationException("Stake must be a positive number")

    @staticmethod
    def validate_bet_amount(amount, current_balance):
        if amount is None or amount <= 0:
            raise ValidationException("Bet amount must be positive")
        if amount > current_balance:
            raise ValidationException("Bet amount cannot exceed current balance")

    @staticmethod
    def validate_limits(initial_balance, upper_limit, lower_limit):
        if lower_limit >= initial_balance:
            raise ValidationException("Lower limit must be less than initial balance")
        if upper_limit <= initial_balance:
            raise ValidationException("Upper limit must be greater than initial balance")
        if lower_limit < 0:
            raise ValidationException("Lower limit cannot be negative")

    @staticmethod
    def validate_probability(probability):
        if probability < 0 or probability > 1:
            raise ValidationException("Probability must be between 0 and 1")

    @staticmethod
    def validate_strategy_name(name):
        if not name or len(name.strip()) == 0:
            raise ValidationException("Strategy name cannot be empty")
