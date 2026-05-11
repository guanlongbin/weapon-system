"""
每日新闻抓取脚本
使用 Tavily 搜索最近24小时新闻，DeepSeek 生成中文摘要
按日期累积，每天追加不覆盖
运行：python3 fetch_news.py
环境变量：DEEPSEEK_API_KEY, TAVILY_API_KEY
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
TAVILY_URL = "https://api.tavily.com/search"

MISSILES_FILE = "missiles.json"
OUTPUT_FILE = "news-cache.json"
MAX_DAYS = 14  # 最多保留 14 天的历史

CST = timezone(timedelta(hours=8))


def tavily_search(weapon_name: str) -> list[dict]:
    """用 Tavily 搜索武器最近24小时的新闻"""
    today = datetime.now().strftime("%Y-%m-%d")
    query = f"{weapon_name} 最新动态 战争 2026"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
        "max_results": 5,
        "days": 1,  # 只搜最近24小时
        "include_domains": [],
        "exclude_domains": []
    }
    try:
        resp = requests.post(TAVILY_URL, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "date": r.get("published_date", ""),
                "snippet": r.get("content", "")[:300]
            }
            for r in results
        ]
    except Exception as e:
        print(f"  Tavily 搜索失败 [{weapon_name}]: {e}")
        return []


def deepseek_summarize(weapon_name: str, news_list: list[dict]) -> str:
    """用 DeepSeek 对搜索结果生成简短中文摘要"""
    if not news_list:
        return ""

    news_text = "\n".join([
        f"- {n['title']}：{n['snippet']}"
        for n in news_list if n.get("title")
    ])

    prompt = f"""以下是关于武器"{weapon_name}"的最新搜索结果（最近24小时）：

{news_text}

请根据上述内容，用2-3句话（不超过150字）总结该武器的最新动态，要求：
1. 语言简洁客观，不要加入主观评价
2. 聚焦最新的使用情况、技术进展或战场表现
3. 如果信息不足，就返回"暂无最新动态"
4. 直接返回摘要文字，不要任何前缀或标签"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.3
    }
    try:
        resp = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  DeepSeek 摘要失败 [{weapon_name}]: {e}")
        return ""


def load_existing_cache() -> dict:
    """读取已有的 news-cache.json"""
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            # 兼容旧格式：items[name] 从对象转为数组
            for name, val in list(cache.get("items", {}).items()):
                if isinstance(val, dict) and "summary" in val:
                    # 旧格式 {summary, news} -> 数组 [{date, summary, news}]
                    cache["items"][name] = [{
                        "date": cache.get("updated_at", "").split(" ")[0],
                        "summary": val.get("summary", ""),
                        "news": val.get("news", [])
                    }]
            return cache
    except (FileNotFoundError, json.JSONDecodeError):
        return {"updated_at": "", "items": {}}


def main():
    if not DEEPSEEK_API_KEY or not TAVILY_API_KEY:
        print("错误：请设置 DEEPSEEK_API_KEY 和 TAVILY_API_KEY 环境变量")
        exit(1)

    with open(MISSILES_FILE, "r", encoding="utf-8") as f:
        missiles = json.load(f)

    names = list({m.get("武器类别", "").split("\n")[0].strip() for m in missiles if m.get("武器类别")})
    print(f"共 {len(names)} 个武器，开始抓取...")

    today_str = datetime.now(CST).strftime("%Y-%m-%d")
    cache = load_existing_cache()
    cache["updated_at"] = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

    for i, name in enumerate(names, 1):
        print(f"[{i}/{len(names)}] {name}")

        news_list = tavily_search(name)
        print(f"  找到 {len(news_list)} 条新闻")

        summary = deepseek_summarize(name, news_list) if news_list else "暂无最新动态"

        top_news = [
            {"title": n["title"], "url": n["url"], "date": n.get("date", "")}
            for n in news_list[:3]
        ]

        entry = {
            "date": today_str,
            "summary": summary,
            "news": top_news
        }

        # 累积：今天的新条目放到最前面，保留最近 MAX_DAYS 天
        history = cache.get("items", {}).get(name, [])
        # 如果今天已经有条目，替换它
        history = [e for e in history if e.get("date") != today_str]
        history.insert(0, entry)
        history = history[:MAX_DAYS]

        cache.setdefault("items", {})[name] = history

        if i < len(names):
            time.sleep(1.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"\n完成！已写入 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
