---
name: paper-deep-reader
description: Academic literature deep reading and structured note generation. Use when the user wants to read, analyze, and take comprehensive notes on one or multiple academic papers/PDFs, generate literature matrices, or build a research literature review based on a provided paper list.
---

# Paper Deep Reader (学术文献精读与结构化笔记)

本技能用于对学术文献（本地 PDF、文献检索目录、arXiv 论文）进行学术级深度精读，按统一规范生成带原文位置锚点的独立 Markdown 笔记，并产出跨文献横向对比矩阵与综述草稿。

---

## 一、 核心工程与学术原则 (Core Principles)

1. **上下文隔离与防衰减（关键）**：
   - 当待精读文献数量 $\ge 3$ 篇时，**严禁在主对话上下文中连续读取所有 PDF 全文**（会导致上下文膨胀、注意力衰减及后半程偷懒简写）。
   - **必须采用子代理隔离（`invoke_subagent`）或分步落盘机制**：每篇（或每 2 篇）派发独立子代理负责读取全文并直接写入对应的 `.md` 笔记文件；主代理仅维护进度表与核心元数据摘要。
2. **全文覆盖与防截断**：
   - 读取 PDF 时必须确保覆盖完整章节（Abstract $\rightarrow$ Intro $\rightarrow$ Method $\rightarrow$ Experiments/Tables $\rightarrow$ Limitations/Conclusion）。
   - 若单次 `read_file` 因长度限制被截断，必须通过分页参数（`StartLine`/`EndLine`）或调用本地 Python 脚本（`pymupdf` / `pypdf` / `pdfplumber`）完整提取正文与实验表格，**严禁仅凭摘要和引言编造方法与实验细节**。
3. **证据溯源锚点 (Provenance Anchors)**：
   - 笔记中的核心公式、架构设计、实验数据必须标注原文位置锚点（如 `[Sec 3.2, Eq. 5]`、`[Table 2, p. 6]`、`[Fig. 3]`），以便后续撰写论文时秒级回溯核对。
4. **忠实原文与诚实拒绝**：
   - 所有指标数据、Baseline 名称、超参数设置均以原文为准；若原文未提及某项数据（如未公布训练耗时或未开源代码），明确标注“原文未披露”，严禁脑补。

---

## 二、 单篇文献精读笔记标准模板 (Note Schema)

每篇文献独立保存为 `notes/{序号}_{第一作者或简称}_{年份}_{核心词}.md`，严格遵循以下结构：

```markdown
# [序号] 论文原标题 (英文/中文对照)

## 0. 元数据与复现性卡片 (Metadata & Reproducibility)
- **作者与机构**：Authors & Affiliations
- **发表期刊/会议与年份**：Venue & Year（注明 CCF 等级 / 中科院分区，若已知）
- **文件映射**：`本地 PDF 文件名` ↔ `检索目录条目编号`
- **开源代码/数据**：[GitHub 链接 / 未开源]
- **复现成本评估**：算力需求（GPU 型号与卡时）、数据集是否公开、工程实现难度（低/中/高）
- **一句话核心范式（可用于 Related Work 引用）**：
  > 针对 **[具体场景下的核心痛点]**，本文提出了 **[方法/模型名称]**，通过 **[核心机制 A]** 与 **[核心机制 B]** 解决了 **[传统方法的某个缺陷]**，在 **[核心数据集]** 上实现了 **[关键指标提升数据]**。

---

## 1. 研究背景与核心科学问题 (Motivation & Problem Statement)
- **领域背景与任务定义**：本文具体解决什么输入到输出的映射问题？`[Sec 1]`
- **现有方案的根本瓶颈 (Pain Points)**：
  - 路线 A 的缺陷：...
  - 路线 B 的缺陷：...
- **本文切入点与核心假设 (Core Hypothesis)**：作者观察到了什么反直觉现象或先验规律？为何认为新方案能打破瓶颈？

## 2. 核心贡献清单 (Contributions)
1. **理论/概念层面**：...
2. **方法/架构层面**：...
3. **实验/应用层面**：...

## 3. 方法论与技术细节深度拆解 (Methodology)
- **整体数据流与系统 Pipeline**：
  （使用文字或 Mermaid 流程图清晰描绘：输入张量/数据 $\rightarrow$ 模块 1 $\rightarrow$ 模块 2 $\rightarrow$ 输出与损失计算）`[Fig. X]`
- **核心模块逐一剖析**：
  - **模块一：[名称]** `[Sec X.X]`
    - 设计动机：为什么要加这个模块？
    - 数学表达与公式推导：写出关键公式（LaTeX 格式），并**逐一解释公式中每个符号/张量的维度与物理含义** `[Eq. X]`。
  - **模块二：[名称]** `[Sec X.X]`
    - 核心机制、算法伪代码逻辑或注意力/特征交互细节。
- **训练目标与优化策略**：
  - 总损失函数构成（如 $\mathcal{L}_{total} = \mathcal{L}_1 + \lambda \mathcal{L}_2$）及超参数敏感度 `[Eq. Y]`。
  - 训练与推理阶段是否存在差异？

## 4. 实验设计与关键证据审计 (Experiments & Evidence)
- **实验设置 (Setup)** `[Sec X.1]`：
  - **数据集**：名称、规模、划分方式。
  - **评价指标 (Metrics)**：具体指标名称及高低优劣方向（$\uparrow$ / $\downarrow$）。
  - **关键超参数与硬件**：Batch size、学习率、优化器、GPU 型号。
- **主实验结果 (Main Results)** `[Table X]`：
  - 对比了哪些强力 Baseline（SOTA 方法）？
  - 核心定量结果摘录（构建 Markdown 小表格，列出最重要的 2~3 个对比行与本文结果，标出提升幅度 $\Delta$）。
- **消融实验深度分析 (Ablation Study)** `[Table Y]`：
  - 去掉模块 A 后性能下降多少？去掉模块 B 后下降多少？
  - **关键结论**：消融实验证明了哪个组件才是真正的性能贡献主力？
- **可视化与定性分析 / 效率对比**：推理延迟（Latency）、参数量（Params）、FLOPs 对比 `[Table Z / Fig. Z]`。

## 5. 局限性与审稿人视角批判 (Critical Review & Limitations)
- **作者自述的局限性** `[Sec Conclusion/Limitations]`：...
- **审稿人视角挑刺（潜在漏洞与边界条件）**：
  - **假设脆弱性**：该方法依赖的先验假设在什么极端场景（Corner Cases）下会失效？
  - **实验公平性存疑**：是否漏掉了某类重要 Baseline？是否在特定数据集上才有效？
  - **代价与副作用**：精度提升是否以成倍增加训练开销或推理延迟为代价？

## 6. 对本课题的启示与联结点 (Actionable Takeaways)
- **可直接复用的组件/技巧**：（如某个特定的 Loss、数据增强方式、评估指标）
- **可作为我们论文的 Baseline / 引用定位**：在撰写引言或相关工作时，应将其归为哪一类代表作？如何指出其不足以引出我们的工作？
- **潜在改进方向 (Future Work Ideas)**：如果将本文的 [机制 X] 替换为 [机制 Y]，或迁移到我们的场景中，会有什么效果？
```

---

## 三、 批量精读标准执行工作流 (Batch SOP)

当用户提供 **PDF 文件夹 + 文献检索目录（如 10 篇）** 时，严格按以下 4 个阶段执行：

### 阶段 1：目录核验与映射对齐 (Alignment & Manifest)
1. 读取用户提供的“文献检索目录”，并扫描本地 PDF 文件夹。
2. 将目录条目与本地 PDF 文件进行精确匹配（处理文件名缩写、乱码或编号不一致问题）。
3. 在笔记输出目录生成或展示对照清单；若发现缺失 PDF 或无法匹配的条目，立即向用户报告。

### 阶段 2：首篇标杆校准或并行精读 (Execution)
- **若用户要求先看效果**：先完整精读第 1 篇并生成 `notes/01_xxx.md`，请用户确认深度与侧重点。
- **若用户要求全量执行**：
  - 利用 `invoke_subagent` 分批派发阅读任务（或逐篇读取并立刻落盘释放上下文）；
  - 每篇严格执行 **全文提取 $\rightarrow$ 核对图表公式 $\rightarrow$ 按模板写入 `notes/0X_xxx.md`**；
  - 检查生成的 `.md` 文件字数与完整性（单篇深度笔记通常应在 1500~3000 字以上，包含完整公式与实验表格数据）。

### 阶段 3：跨文献横向对比与综合 (Synthesis Matrix)
所有单篇笔记落盘后，读取全部笔记的核心卡片，在输出目录生成 **`00_文献横向对比与综述总览.md`**，必须包含：
1. **研究流派与技术演进图**（使用 Mermaid `flowchart TD` 绘制这批文献的技术传承与分支关系）。
2. **10 篇文献全维度对比矩阵表**：
   | 编号与简称 | 发表年份/出处 | 所属技术流派 | 解决的核心痛点 | 核心方法/模块 | 实验数据集与关键指标 | 核心局限性 | 开源状态 |
3. **共性规律与领域空白总结**：
   - 这批文献共同验证了什么结论？
   - 还有哪些共性痛点至今未被完美解决（即用户课题的潜在切入点）？
4. **可直接用于论文的 Related Work 综述草稿**：
   - 按照学术论文 `Related Work` 的行文逻辑（分流派演进 $\rightarrow$ 代表作剖析 $\rightarrow$ 现有方法局限总结），将这批文献串联写成一段有理有据、带引用占位的学术综述段落。
