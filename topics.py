#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interview-qa/topics.py
面试题主题池 - 仅保留AI/ML + 系统设计两个方向，每个10个主题
"""

TOPICS = {
    "ai_ml": [
        "Transformer 自注意力机制原理",
        "GPT 系列架构演进（GPT-1到GPT-4）",
        "RLHF 训练流程详解",
        "LoRA 微调原理与实现",
        "RAG 检索增强生成架构",
        "MoE 混合专家模型原理",
        "KV Cache 推理加速机制",
        "Precision 混合精度训练（FP16/BF16/INT8）",
        "Tokenizer 分词算法（BPE/WordPiece/SentencePiece）",
        "Embedding 文本向量化原理与应用",
    ],
    "system_design": [
        "1000QPS RAG知识库问答系统设计",
        "轻量级AI模型部署推理服务设计",
        "实时日志收集与分析系统设计",
        "分布式定时任务调度器设计",
        "短链接服务系统设计",
        "小型API网关设计（限流/鉴权/路由）",
        "配置中心服务设计（etcd/Consul）",
        "消息推送服务设计（WebSocket）",
        "用户行为数据采集管道设计",
        "小型搜索引擎设计（倒排索引）",
    ],
}
