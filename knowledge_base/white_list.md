# 知识点白名单
# 出题的权威引用来源，禁止模型自由发挥

## Transformer / 注意力机制
- "Attention Is All You Need" (Vaswani et al. 2017)
- 缩放点积注意力：Q·K^T / sqrt(d_k)
- 多头注意力：h=8, d_k=d_v=d_model/h=64
- 位置编码：sin/cos 函数

## GPT 系列
- GPT-1: 117M参数，12层Transformer解码器
- GPT-2: 1.5B参数
- GPT-3: 175B参数，96层，d_model=12288
- GPT-4: 多模态，MoE架构（官方未公开具体参数）
- InstructGPT: 基于人类反馈的指令微调 (Ouyang et al. 2022)

## DeepSeek
- DeepSeek-R1: 671B参数，MoE架构，37B激活参数
- DeepSeek-V2: 236B参数，21B激活，Multi-head Latent Attention
- 开源MIT协议

## 微调技术
- LoRA: Hu et al. 2021，秩r=8-64，参数量减少10000x
- QLoRA: Dettmers et al. 2023，4-bit NF4量化+LoRA
- P-Tuning v2: Liu et al. 2022，连续提示微调
- AdaLoRA: 自适应秩分配

## RAG
- Lewis et al. 2020: Retrieval-Augmented Generation
- 标准流程：query→embedding→向量检索→(文档+query)→生成
- Chunk策略：256-512 tokens，重叠20%

## 推理优化
- KV Cache: 存储Key/Value矩阵，避免重复计算
- Flash Attention: Dao et al. 2022，IO感知的精确注意力
- vLLM: PagedAttention，KV缓存分页管理
- Continuous Batching: 动态批处理

## 模型压缩
- 量化：FP16→INT8→INT4，精度损失<1%
- 剪枝：结构化/非结构化
- 蒸馏：Hinton et al. 2015

## 数据库
- Redis: 内存KV数据库，单线程IO多路复用
- MySQL InnoDB: B+树索引，MVCC，redo/undo log
- Kafka: 分布式消息队列，分区+副本，顺序IO

## 分布式系统
- Raft: Ongaro & Ousterhout 2014，Leader选举+日志复制
- CAP定理: 一致性/可用性/分区容错性，三者不可兼得
- BASE: Basically Available, Soft state, Eventually consistent
