"""
球小策 (QiuXiaoCe) 官方 Python API 客户端 (v0.2.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
所属项目：球小策开源生态矩阵（open_source_matrix）
主要职责：提供球小策创作者开放平台（v2.25+）赛程、积分榜、球员高阶指标、
          单场事件/阵容/射门图、转会、裁判与研报数据的 Python 客户端。

- 官方主站: https://www.qiuxiaoce.com
- 开发者文档: https://qiuxiaoce.readthedocs.io/
- 每日报告速览: https://www.qiuxiaoce.com/mei-ri-bao-gao-su-lan/
- 开发者控制台: https://www.qiuxiaoce.com/data-account/
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
            "User-Agent": "QiuXiaoCe-Python-SDK/0.2.0",
            "Accept": "application/json",
        })
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送统一 HTTP 请求并处理认证、配额及业务错误"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
        try:
            resp = self.session.request(method, url, params=clean_params or None, timeout=self.timeout)
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

    # ---------------- 公开免 Key 端点 ----------------

    def get_public_today_fixtures(
        self,
        date: Optional[str] = None,
        league_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取公开今日纯技战术赛程列表（免 API Key，单次最多 60 场）"""
        params: Dict[str, Any] = {}
        if date:
            params["date"] = date
        if league_id is not None:
            params["league"] = league_id
        if status:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        res = self._request("GET", "/public/today-fixtures", params=params)
        return res.get("data", [])

    # ---------------- 实体检索与档案 ----------------

    def search_teams(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """按中文/英文/简称搜索球队并获取 Team ID（免 API Key）"""
        res = self._request("GET", "/teams", params={"q": query, "limit": limit, "offset": offset})
        return res.get("data", [])

    def get_team_profile(self, team_id: int) -> Dict[str, Any]:
        """获取球队基础档案、主场信息与联赛归属"""
        return self._request("GET", f"/teams/{team_id}")

    def get_team_fixtures(
        self,
        team_id: int,
        season: Optional[int] = None,
        last: Optional[int] = None,
        next_: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """获取指定球队的赛程与近期赛果（支持快照游标与分页）"""
        res = self._request(
            "GET",
            f"/teams/{team_id}/fixtures",
            params={
                "season": season,
                "last": last,
                "next": next_,
                "limit": limit,
                "offset": offset,
                "cursor": cursor,
            },
        )
        return res.get("data", [])

    def search_leagues(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """按名称/别名搜索赛事联赛并获取 League ID（免 API Key）"""
        res = self._request("GET", "/leagues", params={"q": query, "limit": limit, "offset": offset})
        return res.get("data", [])

    def get_league_fixtures(
        self,
        league_id: int,
        season: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """获取指定联赛的赛程与赛果列表"""
        res = self._request(
            "GET",
            f"/leagues/{league_id}/fixtures",
            params={"season": season, "limit": limit, "offset": offset, "cursor": cursor},
        )
        return res.get("data", [])

    def search_players(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """按球员姓名/别名搜索（至少 2 个字符）"""
        res = self._request("GET", "/players", params={"q": query, "limit": limit, "offset": offset})
        return res.get("data", [])

    def get_player_detail(self, player_id: int) -> Dict[str, Any]:
        """获取球员基础档案与当前效力俱乐部"""
        return self._request("GET", f"/players/{player_id}")

    def get_player_stats(self, player_id: int, season: Optional[int] = None) -> Dict[str, Any]:
        """获取球员分赛季基础技术统计"""
        return self._request("GET", f"/players/{player_id}/stats", params={"season": season})

    def get_player_advanced(self, player_id: int, season: Optional[int] = None) -> Dict[str, Any]:
        """获取球员高阶攻防指标（OTI / DII / GIM 等）"""
        return self._request("GET", f"/players/{player_id}/advanced", params={"season": season})

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
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """查询比赛赛程（支持按日期、联赛、球队、近N场、未来N场或分页过滤）"""
        params = {
            "date": date,
            "league": league_id,
            "season": season,
            "team": team_id,
            "last": last,
            "next": next_,
            "limit": limit,
            "offset": offset,
            "cursor": cursor,
        }
        res = self._request("GET", "/fixtures", params=params)
        return res.get("data", [])

    def get_today_digest(self) -> Dict[str, Any]:
        """获取今日重点赛事精选摘要及赛程对应关系"""
        return self._request("GET", "/today/digest")

    # ---------------- 单场事件、技术统计、阵容与射门图 ----------------

    def get_fixture_stats(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛主客队全场技术统计（控球、射门、角球、xG 等）"""
        return self._request("GET", f"/fixtures/{fixture_id}/stats")

    def get_fixture_events(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛进球、红黄牌、换人等时间轴事件"""
        return self._request("GET", f"/fixtures/{fixture_id}/events")

    def get_fixture_lineups(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛双方首发阵容、阵型与替补名单"""
        return self._request("GET", f"/fixtures/{fixture_id}/lineups")

    def get_fixture_shotmap(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛射门坐标与预期进球（xG）分布图数据"""
        return self._request("GET", f"/fixtures/{fixture_id}/shotmap")

    # ---------------- 联赛与积分榜（免 Key） ----------------

    def get_standings(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛积分榜（支持历史赛季与最新赛季，免 API Key）"""
        params: Dict[str, Any] = {"league": league_id}
        if season is not None:
            params["season"] = season
        res = self._request("GET", "/standings", params=params)
        return res.get("data", [])

    def get_topscorers(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛射手榜（免 API Key）"""
        res = self._request("GET", f"/leagues/{league_id}/topscorers", params={"season": season})
        return res.get("data", [])

    def get_topassists(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询指定联赛助攻榜（免 API Key）"""
        res = self._request("GET", f"/leagues/{league_id}/topassists", params={"season": season})
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
        """获取单场比赛市场参考快照（合规研究口径）"""
        return self._request("GET", f"/fixtures/{fixture_id}/quotes")

    def get_quotes_history(self, fixture_id: int) -> Dict[str, Any]:
        """获取单场比赛市场参考走势时间序列"""
        return self._request("GET", f"/fixtures/{fixture_id}/quotes/history")

    def get_match_pack(self, fixture_id: int) -> Dict[str, Any]:
        """获取旗舰单场完整数据包（聚合基本面、攻防、伤停、xG、球队排名、近期战绩与交锋）"""
        return self._request("GET", f"/match-pack/{fixture_id}")

    # ---------------- 转会/教练/裁判 ----------------

    def get_transfers(self, team_id: Optional[int] = None, player_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询球队转会汇总或球员转会历史（team_id / player_id 二选一）"""
        res = self._request("GET", "/transfers", params={"team": team_id, "player": player_id})
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
        """获取单篇深度分析研报详情与结构化研究数据"""
        return self._request("GET", f"/posts/{post_id}")
