"""
球小策 Python SDK 快速上手示例
"""

import os
from qiuxiaoce import QiuXiaoCeClient

# 1. 初始化客户端
# 自动读取环境变量 QIUXIAOCE_API_KEY，也可以显式传参: client = QiuXiaoCeClient(api_key="your_key")
client = QiuXiaoCeClient()

def main():
    print("=== 1. 查询账号点数 ===")
    try:
        quota = client.get_quota()
        print(f"当前可用点数: {quota.get('data', {}).get('points_balance')}")
    except Exception as e:
        print(f"查询失败: {e}")

    print("\n=== 2. 搜索球队 (阿森纳) ===")
    teams = client.search_teams("阿森纳")
    for t in teams[:3]:
        print(f"[{t.get('id')}] {t.get('name')} ({t.get('country')})")

    print("\n=== 3. 查询英超积分榜 ===")
    try:
        standings = client.get_standings(league_id=39)  # 39 为英超 League ID
        for row in standings[:5]:
            print(f"第 {row.get('rank')} 名: {row.get('team_name')} - 积分: {row.get('points')}")
    except Exception as e:
        print(f"获取积分榜失败: {e}")

    print("\n=== 4. 获取今日摘要快讯 ===")
    try:
        digest = client.get_today_digest()
        print(f"今日比赛总数: {digest.get('data', {}).get('total_fixtures')}")
    except Exception as e:
        print(f"获取快讯失败: {e}")

if __name__ == "__main__":
    main()
