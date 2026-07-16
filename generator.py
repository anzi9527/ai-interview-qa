#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interview-qa/generator.py
AI 面试题生成引擎

流程：
1. 选主题（没做过的优先）
2. 1道概念简答 + 1道轻量化设计
3. DeepSeek 生成
4. 免费API交叉校验
5. 保存 + 更新索引

每日执行：早上08:00 cron
"""

import json
import os
import random
import re
import sys
import tempfile
import io

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

from config import (
    CATEGORIES, DIFFICULTIES, DAILY_TARGET,
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_BASE,
    REVIEW_API_KEY, REVIEW_MODEL, REVIEW_BASE, REVIEW_PROMPT,
    KNOWLEDGE_BASE_PROMPT,
    QUESTIONS_DIR, INDEX_FILE, STATE_FILE, OUTPUT_DIR,
)
from topics import TOPICS


# ─── 工具函数 ──────────────────────────────────────────

def call_deepseek(messages, max_tokens=4096, temperature=0.7) -> Optional[str]:
    """调用 DeepSeek API"""
    if not DEEPSEEK_API_KEY:
        print("  ❌ DEEPSEEK_API_KEY 未设置")
        return None

    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()

    try:
        req = Request(
            f"{DEEPSEEK_BASE}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ❌ DeepSeek API 错误: {e}")
        return None


def call_review_api(content: str) -> Optional[str]:
    """调用免费审核API做交叉校验"""
    if not REVIEW_API_KEY:
        print("  ⚠️  REVIEW_API_KEY 未设置，跳过交叉校验")
        return None

    prompt = REVIEW_PROMPT.format(content=content)

    payload = json.dumps({
        "model": REVIEW_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个严格的事实审核员。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.1,
    }).encode()

    try:
        req = Request(
            f"{REVIEW_BASE}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {REVIEW_API_KEY}"
            }
        )
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️  交叉校验API错误: {e}（跳过校验）")
        return None


def load_json(path):
    if path.exists():
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── 核心逻辑 ──────────────────────────────────────────

def load_index():
    data = load_json(INDEX_FILE)
    if "questions" not in data:
        data = {"questions": [], "total": 0, "by_category": {}, "by_difficulty": {}}
    return data


def save_index(index):
    save_json(INDEX_FILE, index)


def load_state():
    return load_json(STATE_FILE)


def save_state(state):
    save_json(STATE_FILE, state)


def pick_topics():
    """选今天要做的2个主题（1概念+1设计），已做过的跳过"""
    index = load_index()
    written = set()
    for q in index.get("questions", []):
        written.add((q["category"], q.get("topic", "")))

    picks = []
    for cat in ["ai_ml", "system_design"]:
        available = [t for t in TOPICS.get(cat, []) if (cat, t) not in written]
        if not available:
            # 所有主题做完了，轮回
            available = TOPICS.get(cat, [])
        picks.append((cat, random.choice(available)))

    return picks  # [(cat, topic), (cat, topic)]


def generate_question(category: str, topic: str, question_no: int) -> Optional[dict]:
    """生成一道题"""
    cat_config = CATEGORIES.get(category)
    if not cat_config:
        print(f"  ❌ 未知分类: {category}")
        return None

    difficulty = random.choice(DIFFICULTIES)
    print(f"\n📝 [{question_no}] {cat_config['emoji']} {topic}（{difficulty}）")

    # System prompt
    system_prompt = KNOWLEDGE_BASE_PROMPT + "\n\n你是一个专业的面试题库作者。严格遵循知识边界限制，不自我发挥。"

    # User prompt
    user_prompt = cat_config["prompt_template"].format(topic=topic, difficulty=difficulty)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Step 1: 生成
    content = call_deepseek(messages)
    if not content:
        return None

    # 清理 AI 前缀对话
    content = re.sub(r'^(好的|好的，|好的！|让我|我来|根据).*?\n', '', content, count=1)

    # Step 2: 交叉校验（如果有 REVIEW_API_KEY）
    review_result = call_review_api(content)
    if review_result:
        # 判断是否通过
        first_line = review_result.strip().split('\n')[0]
        if '不通过' in first_line or '需修改' in first_line:
            print(f"  ⚠️  交叉校验未通过，重新生成...")
            # 把审核结果作为反馈再生成一次
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": f"以上答案未通过事实审核。请根据以下审核意见修正：\n\n{review_result}\n\n严格按照知识点白名单来源重新回答。"
            })
            content = call_deepseek(messages, temperature=0.3)
            if not content:
                return None
            print(f"  ✅ 修正完成")
        else:
            print(f"  ✅ 交叉校验通过")

    date_str = datetime.now().strftime("%Y-%m-%d")

    return {
        "question_no": question_no,
        "title": topic,
        "category": category,
        "category_label": cat_config["label"],
        "difficulty": difficulty,
        "content": content,
        "generated_at": datetime.now().isoformat(),
        "date": date_str,
    }


def save_question(q: dict) -> Path:
    """保存题目到文件"""
    date_part = q["date"].replace("-", "")
    safe_title = re.sub(r'[^\w\-_]', '', q["title"][:30].replace(' ', '_'))
    filename = f"{date_part}_{q['question_no']:03d}_{q['category']}_{safe_title}.md"
    filepath = QUESTIONS_DIR / filename

    frontmatter = f"""---
title: "{q['title']}"
category: {q['category']}
difficulty: {q['difficulty']}
date: {q['date']}
question_no: {q['question_no']}
---

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + q['content'])

    print(f"  ✅ 已保存: {filepath.name}")
    return filepath


def update_index(q: dict, filepath: Path):
    index = load_index()

    index["questions"].append({
        "question_no": q["question_no"],
        "title": q["title"],
        "category": q["category"],
        "difficulty": q["difficulty"],
        "date": q["date"],
        "file": str(filepath.relative_to(OUTPUT_DIR)),
    })

    index["total"] = len(index["questions"])
    index["last_updated"] = datetime.now().isoformat()

    cat = q["category"]
    by_cat = index.get("by_category", {})
    by_cat[cat] = by_cat.get(cat, 0) + 1
    index["by_category"] = by_cat

    diff = q["difficulty"]
    by_diff = index.get("by_difficulty", {})
    by_diff[diff] = by_diff.get(diff, 0) + 1
    index["by_difficulty"] = by_diff

    save_index(index)


def generate_daily():
    """每日生成任务"""
    print(f"\n{'='*50}")
    print(f"📚 AI 面试题库 - 每日生成")
    print(f"{'='*50}\n")

    index = load_index()
    start_no = index["total"] + 1
    picks = pick_topics()
    generated = []

    for i, (cat, topic) in enumerate(picks):
        question_no = start_no + i
        q = generate_question(cat, topic, question_no)
        if q:
            filepath = save_question(q)
            update_index(q, filepath)
            generated.append(q)
        else:
            print(f"  ❌ 第 {question_no} 题生成失败")

    print(f"\n{'='*50}")
    print(f"✅ 今日生成完成！累计 {index['total']} 题")
    print(f"{'='*50}")

    return generated


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        index = load_index()
        print(f"📊 题库统计")
        print(f"   累计题目: {index.get('total', 0)}")
        print(f"   分类分布: {index.get('by_category', {})}")
        print(f"   难度分布: {index.get('by_difficulty', {})}")
        print(f"   最后更新: {index.get('last_updated', '—')}")
        return

    generate_daily()


if __name__ == "__main__":
    main()
