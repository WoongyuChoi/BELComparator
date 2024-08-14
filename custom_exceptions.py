class MissingColumnsError(Exception):
    """필수 컬럼이 누락되었을 때 발생하는 예외"""
    pass

class InvalidBELValuesError(Exception):
    """잘못된 BEL 값이 입력되었을 때 발생하는 예외"""
    pass
