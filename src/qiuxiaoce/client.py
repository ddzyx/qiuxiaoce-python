"""
球小策 (QiuXiaoCe) 官方 Python API 客户端
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
数据来源：球小策足球大数据与 AI 赛前研报中心

- 官方主站: https://www.qiuxiaoce.com
- 每日报告速览: https://www.qiuxiaoce.com/mei-ri-bao-gao-su-lan/
- 开发者控制台: https://www.qiuxiaoce.com/data-account/
- 数据文档: https://www.qiuxiaoce.com/data-docs/
"""

import os
from typing import Any, Dict, List, Optional
import requests

from .exceptions import AuthenticationError, QiuXiaoCeAPIError, QuotaExceededError

DEFAULT_BASE_URL = "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1"


class QiuXiaoCeClient:
    """
    球小策创作者开放 API 客户端。

    参数:
        api_key (str, 可选): 创作者 API 密钥。如果未显式提供，将自动读取环境变量 `QIUXIAOCE_API_KEY`。
        base_url (str, 可选): API 服务根地址，默认为官方生产接口地址。
        timeout (int, 可选): 网络请求超时时间（秒），默认 15 秒。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 15,
    ):
        self.api_key = api_key or os.getenv("QIUXIAOCE_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "QiuXiaoCe-Python-SDK/0.1.0",
            "Accept": "application/json",
        })
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self.session.request(method, url, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise QiuXiaoCeAPIError(f"网络连接异常: {e}") from e

        try:
            data = resp.json()
        except ValueError:
            raise QiuXiaoCeAPIError(f"服务端响应非标准 JSON: HTTP {resp.status_code} - {resp.text[:200]}")

        if resp.status_code == 401:
            code = data.get("code", "")
            if code == "missing_api_key":
                msg = "缺少 API Key。请免费领取: https://www.qiuxiaoce.com/data-account/ 或设置环境变量 QIUXIAOCE_API_KEY"
            else:
                msg = data.get("message") or "API Key 无效或已被吊销。"
            raise AuthenticationError(msg, status_code=401, response_data=data)
        if resp.status_code == 402:
            raise QuotaExceededError("点数余额不足，请前往球小策官网充值: https://www.qiuxiaoce.com/data-service/", status_code=402, response_data=data)

        if resp.status_code >= 400 or not data.get("success", True):
            msg = data.get("message") or data.get("note") or f"请求失败 (HTTP {resp.status_code})"
            raise QiuXiaoCeAPIError(msg, status_code=resp.status_code, response_data=data)

        return data

    # ---------------- 基础与配额 ----------------

    def get_quota(self) -> Dict[str, Any]:
        """查询当前账号剩余点数与套餐信息"""
        return self._request("GET", "/quota")

    # ---------------- 实体检索 ----------------

    def search_teams(self, query: str) -> List[Dict[str, Any]]:
        """按中文/英文/简称搜索球队并获取 Team ID"""
        res = self._request("GET", "/teams", params={"q": query})
        return res.get("data", [])

    def search_leagues(self, query: str) -> List[Dict[str, Any]]:
        """按名称/别名搜索赛事联赛并获取 League ID"""
        res = self._request("GET", "/leagues", params={"q": query})
        return res.get("data", [])

    def search_players(self, query: str) -> List[Dict[str, Any]]:
        """按球员姓名/别名搜索（至少 2 个字符）"""
        res = self._request("GET", "/players", params={"q": query})
        return res.get("data", [])

    def search_referees(self, query: str) -> List[Dict[str, Any]]:
        """搜索裁判英文名（如 Taylor）"""
        res = self._request("GET", "/referees", params={"q": query})
        return res.get("data", [])

    # ---------------- 赛程与今日快讯 ----------------

    def get_fixtures(
        self,
        date: Optional[str] = None,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        team_id: Optional[int] = None,
        last: Optional[int] = None,
        next_: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """查询比赛赛程（支持按日期、联赛、球队、近N场或未来N场过滤）"""
        params = {}
        if date:
            params["date"] = date
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if team_id:
            params["team"] = team_id
        if last:
            params["last"] = last
        if next_:
            params["next"] = next_
        res = self._request("GET", "/fixtures", params=params)
        return res.get("data", [])

    def get_today_digest(self) -> Dict[str, Any]:
        """获取今日重点赛事精选摘要及彩票场次对应关系"""
        return self._request("GET", "/today/digest")

    # ---------------- 联赛与积分榜 ----------------

    def get_standings(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛积分榜（支持历史赛季与最新赛季）"""
        params = {"league": league_id}
        if season:
            params["season"] = season
        res = self._request("GET", "/standings", params=params)
        return res.get("data", [])

    def get_topscorers(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛射手榜"""
        params = {}
        if season:
            params["season"] = season
        res = self._request("GET", f"/leagues/{league_id}/topscorers", params=params)
        return res.get("data", [])

    def get_topassists(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛助攻榜"""
        params = {}
        if season:
            params["season"] = season
        res = self._request("GET", f"/leagues/{league_id}/topassists", params=params)
        return res.get("data", [])

    # ---------------- 球队与对战 ----------------

    def get_team_form(self, team_id: int) -> Dict[str, Any]:
        """获取球队近期战绩形态与攻防均值"""
        return self._request("GET", f"/teams/{team_id}/form")

    def get_h2h(self, home_team_id: int, away_team_id: int) -> Dict[str, Any]:
        """查询两队历史交锋战绩（含双方球队档案与交锋汇总）"""
        return self._request("GET", "/h2h", params={"home_id": home_team_id, "away_id": away_team_id})

    # ---------------- 市场参考与专业分析 ----------------

    def get_quotes(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛胜平负/让球/进球数市场参考快照（合规口径）"""
        return self._request("GET", f"/fixtures/{fixture_id}/quotes")

    def get_quotes_history(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛市场参考走势时间序列"""
        return self._request("GET", f"/fixtures/{fixture_id}/quotes/history")

    def get_match_pack(self, fixture_id: int) -> Dict[str, Any]:
        """获取旗舰单场完整数据包（聚合基本面、攻防、伤停、xG、近期战绩与交锋）"""
        return self._request("GET", f"/match-pack/{fixture_id}")

    # ---------------- 转会/教练/裁判 ----------------

    def get_transfers(self, team_id: Optional[int] = None, player_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询球队转会汇总或球员转会历史（team_id / player_id 二选一）"""
        params = {}
        if team_id:
            params["team"] = team_id
        if player_id:
            params["player"] = player_id
        res = self._request("GET", "/transfers", params=params)
        return res.get("data", [])

    def get_coach(self, coach_id: int) -> Dict[str, Any]:
        """查询教练履历与执教历史"""
        return self._request("GET", f"/coaches/{coach_id}")

    def get_referee(self, referee_id: int) -> Dict[str, Any]:
        """查询裁判执法场次、黄红牌统计与近期执法战绩"""
        return self._request("GET", f"/referees/{referee_id}")

    # ---------------- 官方研报 ----------------

    def get_today_reports(self) -> List[Dict[str, Any]]:
        """获取今日官方深度研报列表"""
        res = self._request("GET", "/posts/today")
        return res.get("data", [])

    def get_report_detail(self, post_id: int) -> Dict[str, Any]:
        """获取单篇深度分析研报详情与结构化预测数据"""
        return self._request("GET", f"/posts/{post_id}")
