"""
球小策 SDK 异常类定义
"""

class QiuXiaoCeAPIError(Exception):
    """球小策 API 基础异常"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(QiuXiaoCeAPIError):
    """密钥未提供或无效"""
    pass


class QuotaExceededError(QiuXiaoCeAPIError):
    """点数余额不足"""
    pass
