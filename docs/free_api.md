# 免费接口清单

为方便广大足球数据分析爱好者与开发者，[球小策（qiuxiaoce.com）](https://www.qiuxiaoce.com) 开放了以下**赛事维度只读接口**完全免密钥调用：

| 接口名称 | 方法 | 说明 |
| :--- | :--- | :--- |
| **今日公开赛程** | `client.get_public_today_fixtures(...)` | 获取当日纯技战术赛程列表（最多 60 场） |
| **球队中英文搜索** | `client.search_teams(q)` | 支持中文名、英文名、常见昵称模糊检索，返回规范 ID |
| **联赛搜索** | `client.search_leagues(q)` | 搜索英超、西甲、欧冠等联赛 ID 与中英文名称 |
| **联赛实时积分榜** | `client.get_standings(league_id, season)` | 完整主客场战绩、进失球与积分数据 |
| **联赛射手榜** | `client.get_topscorers(league_id)` | 联赛球员进球榜单 |
| **联赛助攻榜** | `client.get_topassists(league_id)` | 联赛球员助攻榜单 |

---

## 调用限制说明

- **限频规则**: 单 IP 每分钟默认允许 30 次调用（超出返回 HTTP 429）。
- **更高权限与深度数据**: 单场 200+ 维全景数据包 (Match Pack)、市场参考走势、伤停损失与 AI 赛前深度研报需持有 API Key。
- **获取专属密钥**: 可前往 [球小策开发者控制台](https://www.qiuxiaoce.com/data-account/) 免费领取 500 点体验金。
