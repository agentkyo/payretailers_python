class PayRetailersError(Exception):
    """Base exception for PayRetailers SDK."""
    def __init__(self, message, code=None, status_code=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(f"[{code}] {message}" if code else message)

class ValidationError(PayRetailersError):
    """Raised when validation of input parameters fails locally or at API level."""
    pass

class AuthenticationError(PayRetailersError):
    """Raised when authentication fails (HTTP 401)."""
    pass

class APIConnectionError(PayRetailersError):
    """Raised when connection to API fails."""
    pass

class TransactionCreationError(PayRetailersError):
    """Raised when transaction cannot be created."""
    pass

class PayoutCreationError(PayRetailersError):
    """Raised when payout cannot be created."""
    pass

# Mapping of specific API error codes to Exception classes
ERROR_CODE_MAP = {
    "001_VALIDATION_ERROR": ValidationError,
    "BLOCKED_BY_CUSTOMER_LIMIT_RULE": TransactionCreationError,
    "CUSTOMER_INVALID_AGE": ValidationError,
    "CUSTOMER_INVALID_ID": ValidationError,
    "INVALID_AMOUNT": ValidationError,
    "PAYMENT_METHOD_NOT_ALLOWED": TransactionCreationError,
    "TRANSACTION_MAX_AMOUNT": ValidationError,
    "TRANSACTION_MIN_AMOUNT": ValidationError,
    "TRANSACTION_INVALID_FIELD_COUNTRY": ValidationError,
    "TRANSACTION_INVALID_FIELD_CURRENCY": ValidationError,
    # Add more mappings as needed from documentation
}

def get_exception_for_code(code: str, message: str, status_code: int = None) -> PayRetailersError:
    """Factory function to return specific exception based on error code."""
    cls = ERROR_CODE_MAP.get(code, PayRetailersError)
    return cls(message, code=code, status_code=status_code)
