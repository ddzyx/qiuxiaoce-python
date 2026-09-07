# 快速上手指南

## 1. 初始化客户端

你可以通过环境变量 `QIUXIAOCE_API_KEY` 配置密钥，或者在初始化客户端时直接传入：

```python
from qiuxiaoce import QiuXiaoCeClient

# 自动读取环境变量 QIUXIAOCE_API_KEY
client = QiuXiaoCeClient()

# 或者直接显式传参
client = QiuXiaoCeClient(api_key="your_api_key_here")
```

> 💡 **提示**: 搜索球队/联赛、查看积分榜与射手榜为**免费接口**，不配置 Key 也能直接正常调用！

---

## 2. 常用代码示例

### 查询英超积分榜
```python
# 39 为英超 League ID
standings = client.get_standings(league_id=39)

for row in standings[:5]:
    print(f"第 {row['rank']} 名: {row['team_name']} - 积分: {row['points']}")
```

### 搜索俱乐部中文别名
```python
teams = client.search_teams("阿森纳")
if teams:
    print(f"球队 ID: {teams[0]['team_id']}, 英文: {teams[0]['name_en']}, 中文: {teams[0]['name_zh']}")
```

### 获取今日赛程与快讯
```python
digest = client.get_today_digest()
print(f"今日纳入分析比赛: {digest.get('total')} 场")
```

更多高级接口与全景数据包说明，请访问 [球小策官方主站](https://www.qiuxiaoce.com)。
