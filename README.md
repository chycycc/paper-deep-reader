# Paper Deep Reader (`paper-deep-reader`)

面向 AI 编程助手与科研 Agent（Antigravity / Claude Code / Cursor）的**学术文献批量精读与结构化笔记生成 Skill**。

针对科研人员在阅读多篇 PDF 文献时常见的**“AI 摘要流于表面”、“多篇连续阅读导致上下文膨胀与注意力衰减”、“缺少原文公式/表格位置溯源”**以及**“笔记难以直接转化为论文 Related Work”**四大痛点设计。

---

## 核心特性

1. **子代理上下文隔离（防衰减机制）**
   - 当批量精读 $\ge 3$ 篇文献时，强制通过子代理（Subagent）或分步落盘机制隔离每篇 PDF 的全文上下文，确保第 10 篇与第 1 篇的精读深度完全一致。
2. **全文防截断与公式级拆解**
   - 强制覆盖 `Abstract -> Introduction -> Methodology -> Experiments -> Limitations` 全流程；
   - 核心数学公式（LaTeX）要求逐一拆解每个符号/张量的维度与物理含义。
3. **原文证据溯源锚点（Provenance Anchors）**
   - 所有关键方法、公式与实验对比数据均标注原文位置（如 `[Sec 3.2, Eq. 5]`、`[Table 2, p. 6]`），写论文核对引文时可秒级回溯。
4. **前置目录核验与映射对齐**
   - 自动将用户的“文献检索目录”与本地 PDF 文件进行对齐核验，提前排查乱码文件名或缺失文献。
5. **一键生成横向对比矩阵与 Related Work 草稿**
   - 批量精读完成后，自动汇总生成《00_文献横向对比与综述总览.md》，包含 Mermaid 技术演进图、10 篇文献全维度对比表格，以及可直接用于论文的 `Related Work` 综述段落。

---

## 目录结构

```text
paper-deep-reader/
├── SKILL.md     # Skill 核心指令规范与精读模板定义
└── README.md    # 项目说明与使用指南
```

---

## 安装方式

将本仓库克隆至您的 Agent Skills 目录中：

### Google Antigravity
```bash
git clone https://github.com/chycycc/paper-deep-reader.git ~/.gemini/config/skills/paper-deep-reader
```
*(Windows 路径：`C:\Users\<用户名>\.gemini\config\skills\paper-deep-reader`)*

### Claude Code / Cursor
将 `SKILL.md` 复制或软链接至对应工具的全局/工作区 Skills 目录即可。

---

## 使用指南（Prompt 模板）

准备好存放 PDF 的文件夹与文献检索清单后，在对话中发送以下指令：

```markdown
请使用 paper-deep-reader 技能，帮我精读以下学术文献并生成深度笔记：

【PDF 存放目录】：D:/papers/
【笔记输出目录】：D:/papers/notes/

【文献检索清单】：
1. [论文标题或文件名 1]
2. [论文标题或文件名 2]
...

【执行要求】：
1. 先核对本地 PDF 与清单的映射关系；
2. 严格按照 paper-deep-reader 模板逐篇精读全文，提取公式符号定义、实验对比表格与原文位置锚点；
3. 每篇独立输出至 notes/{序号}_{简称}.md；
4. 全部完成后生成《00_文献横向对比与综述总览.md》。
```

---

## 单篇笔记输出章节概览

每篇文献生成的 `.md` 笔记包含以下标准模块：
- `0. 元数据与复现性卡片`（含开源代码链接、算力需求评估、一句话核心范式）
- `1. 研究背景与核心科学问题`（现有路线瓶颈、本文核心假设）
- `2. 核心贡献清单`（理论 / 方法 / 实验三层贡献）
- `3. 方法论与技术细节深度拆解`（Pipeline 图解、核心模块、LaTeX 公式与符号维度释义、损失函数）
- `4. 实验设计与关键证据审计`（数据集、强 Baseline 对比表、消融实验贡献度分析、推理效率）
- `5. 局限性与审稿人视角批判`（假设脆弱性、实验盲区、计算代价）
- `6. 对本课题的启示与联结点`（可复用组件、引用定位、未来改进方向）

---

## License

MIT License
