#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interview-qa/repo_manager.py
GitHub 仓库管理
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(os.environ.get("REPO_DIR", str(Path.home() / "repos" / "ai-interview-qa")))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "anzi9527/ai-interview-qa"
QUESTIONS_SRC = Path(__file__).parent / "output" / "questions"
INDEX_SRC = Path(__file__).parent / "output" / "index.json"


def load_index():
    if INDEX_SRC.exists():
        try:
            with open(INDEX_SRC, encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"total": 0, "questions": []}


def ensure_repo():
    if REPO_DIR.exists():
        return True
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN 未设置")
        return False
    REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    r = subprocess.run(["git", "clone", repo_url, str(REPO_DIR)],
                      capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"❌ clone 失败: {r.stderr[:200]}")
        return False
    return True


def generate_readme():
    index = load_index()
    total = index.get("total", 0)
    by_cat = index.get("by_category", {})
    last_updated = index.get("last_updated", "—")[:10]

    cat_emojis = {"ai_ml": "🤖", "system_design": "🏗️"}
    cat_labels = {"ai_ml": "AI/ML", "system_design": "系统设计"}

    stats_rows = ""
    for cat in ["ai_ml", "system_design"]:
        e = cat_emojis.get(cat, "📌")
        l = cat_labels.get(cat, cat)
        c = by_cat.get(cat, 0)
        stats_rows += f"| {e} {l} | {c} |\n"

    recent = ""
    for q in index.get("questions", [])[-6:]:
        e = cat_emojis.get(q.get("category", ""), "📌")
        recent += f"- [{q.get('difficulty','')}] {e} {q['title']} ({q.get('date','')})\n"

    return f"""# 🎯 AI 面试题库

> AI 每日自动生成的面试题库 —— 聚焦 AI/ML 和轻量化系统设计两个方向。
> 每个答案都经过双API交叉校验以保证准确性。

[![每日更新](https://img.shields.io/badge/每日更新-🔄-brightgreen)]()
[![MIT License](https://img.shields.io/badge/license-MIT-blue)]()

## 📊 统计

- **累计题目**: {total} 道
- **覆盖方向**: {', '.join(cat_labels.values())}
- **最后更新**: {last_updated}

### 题目分布

| 分类 | 数量 |
|------|------|
{stats_rows}

### 🔥 最近题目

{recent}

## 📁 结构

```
questions/     ← 面试题（Markdown）
index.json     ← 完整索引
```

## 🚀 使用

直接在 [questions/](questions/) 目录浏览或搜索。

## 📝 来源声明

本仓库所有题目由 AI（DeepSeek）生成，经过通义千问交叉事实校验后发布。如发现错误，欢迎提 Issue。

---

*由 AI 智能体 小玲 自动维护*
"""


def sync():
    if not ensure_repo():
        return False

    import shutil

    # 复制 questions
    dest_dir = REPO_DIR / "questions"
    dest_dir.mkdir(parents=True, exist_ok=True)

    for f in QUESTIONS_SRC.glob("*.md"):
        shutil.copy2(f, dest_dir / f.name)

    # 复制 index
    if INDEX_SRC.exists():
        shutil.copy2(INDEX_SRC, REPO_DIR / "index.json")

    # 生成 README
    readme = generate_readme()
    (REPO_DIR / "README.md").write_text(readme, encoding='utf-8')

    # git
    try:
        subprocess.run(["git", "config", "user.name", "openclaw-bot"],
                      cwd=REPO_DIR, capture_output=True, timeout=10)
        subprocess.run(["git", "config", "user.email", "bot@openclaw.ai"],
                      cwd=REPO_DIR, capture_output=True, timeout=10)
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, capture_output=True, timeout=10)

        r = subprocess.run(["git", "commit", "-m", f"每日更新 {datetime.now().strftime('%Y-%m-%d')}"],
                          cwd=REPO_DIR, capture_output=True, text=True, timeout=10)

        if "nothing to commit" in r.stdout:
            print("📭 无新内容")
            return True

        pr = subprocess.run(["git", "push"], cwd=REPO_DIR,
                           capture_output=True, text=True, timeout=30)
        if pr.returncode == 0:
            print(f"✅ 已推送: {GITHUB_REPO}")
            return True
        else:
            print(f"❌ push 失败: {pr.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ git 操作异常: {e}")
        return False


def status():
    index = load_index()
    print(f"📊 题库: {index.get('total', 0)} 题")
    print(f"   分类: {index.get('by_category', {})}")
    print(f"   难度: {index.get('by_difficulty', {})}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "push":
        sync()
    else:
        status()
        print(f"\n用法: python repo_manager.py push")
