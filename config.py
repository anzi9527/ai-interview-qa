#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interview-qa/config.py
面试题库配置中心

出题规则（基于豆包分析结论）：
- 每日2题：1道LLM概念简答 + 1道轻量化系统设计
- 禁止开放式超大架构设计题（幻觉率61-66%）
- 启用双API交叉校验控错
"""

import os
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
QUESTIONS_DIR = OUTPUT_DIR / "questions"
INDEX_FILE = OUTPUT_DIR / "index.json"
STATE_FILE = OUTPUT_DIR / "generation_state.json"
KB_DIR = BASE_DIR / "knowledge_base"

# 只保留2个赛道（砍掉8分类）
CATEGORIES = {
    "ai_ml": {
        "label": "AI/ML",
        "emoji": "🤖",
        "type": "concept",  # 概念简答，低幻觉
        "prompt_template": """你是一个资深AI面试官，请出一道AI/ML概念简答题。

题目方向：{topic}
难度：{difficulty}

规则：
1. 只能基于业界公认的标准知识点出题
2. 禁止自定义参数、虚构论文、未公开的架构方案
3. 答案必须有明确出处（官方文档、经典论文、权威博客）
4. 概念简答题，不需要设计系统

格式：
# ❓ 题目
（简短的题目描述）

## ✅ 标准答案
（基于权威来源的答案，附参考来源）

## 💡 面试官追问
- 追问1：（及答案要点）
- 追问2：（及答案要点）

## 📚 参考来源
（列出引用来源）

难度：{difficulty} | 分类：AI/ML"""
    },
    "system_design": {
        "label": "轻量化系统设计",
        "emoji": "🏗️",
        "type": "design",  # 受限场景设计，中等幻觉
        "prompt_template": """你是一个资深系统设计面试官，请出一道轻量化系统设计题。

题目方向：{topic}
难度：{difficulty}

规则（硬性约束）：
1. QPS限制：不超过10,000 QPS
2. 组件限制：最多5个核心组件
3. 只使用业界成熟方案（Redis/MySQL/Kafka/gRPC等）
4. 禁止自定义架构名称、虚构性能数据
5. 不讨论百万级并发、不讨论跨机房部署

格式：
# ❓ 题目
（简单描述需求场景，限100字）

## 🏗️ 架构方案
（组件选择 + 数据流，限200字）

## ✅ 关键设计决策
（3个核心选择及理由）

## 💡 面试官追问
- 追问1：（及答案要点）
- 追问2：（及答案要点）

## 📚 参考来源
（列出引用来源）

难度：{difficulty} | 分类：轻量化系统设计"""
    },
}

DIFFICULTIES = ["初级", "中级", "高级"]

# 每日产出（基于15分钟人力校验能力）
DAILY_TARGET = 2  # 1道概念 + 1道设计

# 知识点白名单（手工维护，仅收录权威来源的知识点）
KNOWLEDGE_BASE_PROMPT = """
参考知识点来源（出题必须基于以下来源，禁止自由发挥）：
1. Transformer架构：Attention Is All You Need (Vaswani et al. 2017)
2. GPT系列：OpenAI GPT-1/2/3/4技术报告
3. DeepSeek：DeepSeek-R1技术报告 (2025)
4. RAG：Lewis et al. 2020 (Retrieval-Augmented Generation)
5. LoRA：Hu et al. 2021 (LoRA: Low-Rank Adaptation)
6. RLHF：InstructGPT论文 (Ouyang et al. 2022)
7. Redis：Redis官方文档
8. MySQL InnoDB：MySQL官方文档
9. Kafka：Kafka官方设计文档
10. gRPC：gRPC官方文档
11. Docker & K8s：Docker/K8s官方文档
12. 分布式共识：Raft论文 (Ongaro & Ousterhout 2014)
"""

# API配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE = "https://api.deepseek.com"

# 交叉校验API（免费额度）
REVIEW_API_KEY = os.environ.get("REVIEW_API_KEY", "")  # 通义千问或智谱
REVIEW_MODEL = "qwen-turbo"  # 通义千问免费版
REVIEW_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
REVIEW_PROMPT = """你是一个严格的事实审核员。请逐条审核以下面试题的知识点是否准确。

规则：
1. 核对每个知识点是否和行业公认标准一致
2. 标记"可信/需要核实/错误"三级
3. 如果发现错误，指出具体错在哪
4. 只做事实审核，不做内容评价

题目内容：
{content}

输出格式：
## 审核结果

总评：通过/需修改/不通过

| 知识点 | 判断 | 说明 |
|--------|------|------|
| ... | ... | ... |

### 需要修改的条目
（如果有的话，逐条列出）

### 参考修正
（如果需要修改，给出正确的表述）"""
