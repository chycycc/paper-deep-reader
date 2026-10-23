# paper-deep-reader

一个用于批量精读学术论文 PDF 并生成结构化 Markdown 笔记的 Agent Skill（适用于 Google Antigravity、Claude Code、Cursor）。

## 为什么写这个 Skill

直接把十几篇论文丢给大模型总结，通常会遇到几个很烦人的问题：

- **越读越水**：在一个对话里连续读三四篇长 PDF 后，上下文被塞满，后面的笔记开始偷工减料，甚至漏掉关键实验。
- **全是正确的废话**：生成的摘要看着通顺，但既没有具体的数学公式推导，也没有 Baseline 对比数据，写论文时还是得自己重新翻原文。
- **找不到原文出处**：笔记里记了个结论，过两周写 Related Work 想核对时，根本不知道这句结论来自原文的第几节、哪张表。
- **文件名对不上**：从知网、arXiv 或 Elsevier 批量下载的 PDF 文件名经常是编号或乱码，和手头的文献检索清单对不上号。

`paper-deep-reader` 的作用就是用一套硬性规则把这些环节卡死：读之前先核对文件清单；读的时候每篇单独开子代理（Subagent）隔离上下文，强制提取公式符号含义、实验表格数据和原文位置（如 `[Sec 3.2, Eq. 4]`）；全部读完后，汇总出一张横向对比表和一段能直接改改放进论文里的 Related Work 草稿。

## 安装

直接克隆到本地的 Skills 目录即可：

```bash
# Google Antigravity (Windows)
git clone https://github.com/chycycc/paper-deep-reader.git "$HOME/.gemini/config/skills/paper-deep-reader"

# macOS / Linux
git clone https://github.com/chycycc/paper-deep-reader.git ~/.gemini/config/skills/paper-deep-reader
```

如果你用的是 Claude Code 或 Cursor，把仓库里的 `SKILL.md` 放到对应的 skills 文件夹下即可。

## 怎么用

把待读的 PDF 放进同一个文件夹，开一个新对话，直接按平时说话的方式告诉 Agent 路径和你的文献清单就行。例如：

```text
用 paper-deep-reader 帮我精读 D:/papers/ 下的这 10 篇论文，笔记存到 D:/papers/notes/ 目录。

文献清单：
1. Attention Is All You Need
2. Deep Residual Learning for Image Recognition
3. ...

先帮我对一下本地 PDF 文件和清单能不能对应上，确认没问题后逐篇精读，最后生成一份横向对比总览。
```

如果担心详略程度不合心意，可以先让它“先读第一篇给我看看效果”，满意后再让它把剩下的批量跑完。

## 生成的笔记长什么样

每篇论文会单独生成一个 `.md` 文件（比如 `notes/01_Vaswani_2017_Transformer.md`），包含以下内容：

1. **基本信息与复现成本**：作者、发表年份、代码开源链接、所需算力评估，以及一句浓缩的“核心范式”（方便后续写综述直接引用）。
2. **背景与切入点**：之前的方法卡在哪里，这篇论文基于什么观察提出了新方案。
3. **方法细节与公式**：系统完整的数据流向、各模块设计动机、核心公式（附带每个符号/张量的维度和物理含义说明）以及损失函数。
4. **实验与消融分析**：在什么数据集上和哪些强 Baseline 做了对比（附具体指标表格）、消融实验证明哪个模块真正起作用、推理延迟与参数量。
5. **局限性与挑刺**：原文自述的限制，以及站在审稿人视角能挑出的毛病（比如假设过于理想、缺少某类对比基线、显存开销过大等）。
6. **对本课题的参考价值**：哪些设计能直接拿来用，写论文时怎么引用它。

所有单篇笔记写完后，会在同目录下额外生成一份 `00_文献横向对比与综述总览.md`，把这批论文的技术流派、解决的问题、核心模块、数据集指标和缺陷放在一张大表里对比，并附带一段串联好的文献综述草稿。

## License

MIT
