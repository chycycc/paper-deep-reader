# paper-reader

一个面向学术文献阅读与综述整理的 Agent Skill（适用于 Google Antigravity、Claude Code、Cursor），支持 **`skim`（泛读梳理）** 与 **`deep`（深度精读）** 两种模式，并自带从 PDF 原文裁剪高清模型架构图的脚本。

## 为什么做这个 Skill

平时用大模型读论文、写开题或学位论文综述，最容易踩四个坑：

1. **连读几篇后越写越水**：在一个对话里连续塞进好几篇长 PDF，后面几篇因为上下文爆满开始偷工减料，漏掉实验表和公式细节。
2. **乱画 Mermaid 流程图**：让 AI 画模型架构图，它往往往节点里塞满公式和长句子，连线交叉成一团乱麻，根本没法看，不如直接把原论文里的架构图高清截出来。
3. **局限性乱扣帽子**：AI 很喜欢把“整理者自己的对比分析”或者“原文没做过的实验边界”直接写成“原作者的缺陷”，写进综述里很容易出现事实性偏差。
4. **泛读和精读混为一谈**：几十篇参考/储备文献只需要梳理题录、方法概括、适用边界和汇总底表；而核心的十来篇基线论文才需要逐节抠公式、核对训练与推理差异。

`paper-reader` 把文献处理拆成了 **`skim`（泛读）** 和 **`deep`（精读）** 两条路线，并定死了一条学术底线：任何时候总结论文局限，都必须明确区分 **「作者自述」**、**「覆盖边界」** 和 **「方法分析」**。

## 目录结构

```text
paper-reader/
├── SKILL.md                        # 双模式（skim + deep）规则与输出模板
├── README.md                       # 使用说明
└── scripts/
    └── extract_pdf_figures.py      # 基于 PyMuPDF 的原论文架构图定位与高清裁剪脚本
```

## 安装

克隆到本地 Skills 目录，并确保 Python 环境装有 `pymupdf`（用于精读时从 PDF 裁剪原图）：

```bash
pip install pymupdf

# Google Antigravity (Windows)
git clone https://github.com/chycycc/paper-reader.git "$HOME/.gemini/config/skills/paper-reader"

# macOS / Linux
git clone https://github.com/chycycc/paper-reader.git ~/.gemini/config/skills/paper-reader
```

*(注：即使暂未将 GitHub 仓库改名，旧地址也会自动重定向或可按实际仓库地址克隆)*

## 两种模式怎么用

### 1. 泛读梳理模式 (`skim`)

适合处理重点参考、扩展储备或整批入库文献（比如 20~40 篇），一次性产出两份材料：
- **清单式分类详情**：按研究主题分类，每篇包含完整题录、DOI、本地 PDF 链接、中文技术概述、使用方向、**适用边界（不能外推的红线）**及中英文检索式。
- **结构化文献信息汇总表**：横向底表（`编号 | 作者（年份）论文题目 | 发表期刊/会议 | 研究方法 | 核心观点 | 研究局限性 | 对本课题的启示`），四项正文默认控制在 120–200 字符，局限性强制标注来源。

调用示例：
```text
用 paper-reader 的 skim 模式，帮我把 D:/论文库/02_重点参考 下的这 20 篇 PDF 整理成「文献清单分类详情」和「结构化文献信息汇总表」，输出到 D:/论文库/04_筛选成果/。
```

### 2. 重度精读模式 (`deep`)

适合需要深度复现、作为核心 Baseline 或方法近邻的论文（比如 5~10 篇）。每篇由独立子代理（Subagent）隔离上下文精读全文，单独输出一份 `L编号_简称_精读笔记.md`：
- **不画杂乱 Mermaid 图**：自动调用 `scripts/extract_pdf_figures.py` 从 PDF 原文裁剪模型架构图（如 `Figure 2` / `图 2`）存入 `assets/` 并嵌入笔记，搭配分步列表讲清张量流向。
- **抠细节与防脑补**：完整列出核心公式并解释每个符号与张量的维度；专门核查**训练期与推理期差异**（比如训练时是否用了真实回复做后验、测试时是否喂了伪真值标签）；摘录主实验与消融实验完整数据表。
- **横向机制对标**：全部读完后生成 `00_精读核心文献横向对比.md`，用流派演进表、全维度对比表和专项机制对标表把这批核心论文的架构、监督信号、损失函数与本课题研究点逐项对齐（注：此处仅做核心文献的方法对标，不以精读子集越界替代全库范围的文献综述）。

调用示例：
```text
用 paper-reader 的 deep 模式精读 D:/论文库/01_精读核心 下的 10 篇论文，笔记存到 D:/论文库/03_阅读笔记/01_单篇文献笔记/。
文献清单参考 D:/论文库/文献清单与检索体系.md。先核对本地 PDF 和清单的对应关系，确认无误后逐篇精读并截取原文架构图，最后生成精读核心文献的横向机制对比表。
```

## 单独使用 PDF 截图脚本

`scripts/extract_pdf_figures.py` 也可以在命令行单独调用，支持中英文论文图注识别：

```bash
# 1. 扫描 PDF 中所有图注所在的页码与坐标
python scripts/extract_pdf_figures.py --scan "paper.pdf"

# 2. 按图注自动裁剪上方的架构图（支持传 "Figure 2"、"Fig. 2"、"图 2" 或纯数字 "2"）
python scripts/extract_pdf_figures.py --pdf "paper.pdf" --caption "Figure 2" --out "assets/CASE_Fig2.png"

# 3. 手动指定页码和相对比例坐标 [x0,y0,x1,y1] 裁剪
python scripts/extract_pdf_figures.py --pdf "paper.pdf" --page 3 --bbox 0.05,0.06,0.95,0.35 --out "assets/CASE_Fig2.png"
```

## License

MIT
