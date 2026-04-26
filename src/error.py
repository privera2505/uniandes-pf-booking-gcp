class InvalidDateRangeException(Exception):
    """Exception Raised when the check-in date is later than the check-out date"""
    pass

class BookingDateValidationException(Exception):
    """Exception raised when the check-in date is lower than today"""
    pass

class RoomNotExist(Exception):
    """Exception raise when the room not exist."""
    pass

class UserNotExist(Exception):
    """Exception raise when the user not exist."""
    pass

class RoomAlreadyBooked(Exception):
    """Exception raise when the room is already booked"""
    pass

class MaxGuestsExceededException(Exception):
    """Exception raise when the max guest exceed."""
    pass

class RateNotAvailableException(Exception):
    """Exception raise when the rate is not available"""
    pass

class ReservationDuplicated(Exception):
    """Exception raise when the Revation was duplicated"""
    pass