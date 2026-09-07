"""
球小策 (QiuXiaoCe) 官方 Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
提供足球大数据中心赛程、积分榜、转会、裁判与赛前研报数据的便捷 Python 客户端。

官网: https://www.qiuxiaoce.com
每日速览: https://www.qiuxiaoce.com/mei-ri-bao-gao-su-lan/
"""

from .client import QiuXiaoCeClient
from .exceptions import QiuXiaoCeAPIError, AuthenticationError, QuotaExceededError

__version__ = "0.1.0"
__all__ = ["QiuXiaoCeClient", "QiuXiaoCeAPIError", "AuthenticationError", "QuotaExceededError"]
