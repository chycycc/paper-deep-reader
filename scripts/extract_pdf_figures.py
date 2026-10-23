#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从学术论文 PDF 中检索图注位置并高清裁剪原论文架构图/实验图 (基于 PyMuPDF / fitz)。

用法示例：
1. 扫描 PDF 中所有图注 (Figure / Fig. / 图) 所在的页码与坐标：
   python extract_pdf_figures.py --scan "paper.pdf"

2. 根据图注关键词自动定位并裁剪上方/同区域的架构图 (推荐)：
   python extract_pdf_figures.py --pdf "paper.pdf" --caption "Figure 2" --out "assets/L07_CASE_Fig2.png"

3. 按指定页码与归一化比例区域 [x0, y0, x1, y1] (范围 0.0~1.0) 或绝对坐标裁剪：
   python extract_pdf_figures.py --pdf "paper.pdf" --page 3 --bbox 0.05,0.06,0.95,0.48 --out "assets/L07_CASE_Fig2.png"
"""

import argparse
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] 未检测到 PyMuPDF (fitz)，请先执行: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


CAPTION_PATTERN = re.compile(
    r"^(?:Figure|Fig\.|FIG\.|图)\s*\d+(?!\s*(?:展示|显示|给出|说明|表明|描述|列举|对比|呈现|描绘|中|所示|可知|可见|shows|illustrates|depicts|presents|demonstrates))",
    re.IGNORECASE
)


def scan_captions(pdf_path: str):
    """扫描 PDF 中所有包含 Figure / Fig. / 图 的文本块及页面尺寸信息"""
    doc = fitz.open(pdf_path)
    print(f"=== PDF: {os.path.basename(pdf_path)} (共 {len(doc)} 页) ===")
    found = 0
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        w, h = page.rect.width, page.rect.height
        blocks = page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if block_type != 0:
                continue
            clean_text = " ".join(text.strip().split())
            if CAPTION_PATTERN.match(clean_text):
                found += 1
                rx0, ry0, rx1, ry1 = x0 / w, y0 / h, x1 / w, y1 / h
                print(
                    f"[Page {page_idx + 1}] "
                    f"Abs=({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}) "
                    f"Rel=({rx0:.3f},{ry0:.3f},{rx1:.3f},{ry1:.3f}) | "
                    f"{clean_text[:120]}"
                )
    if found == 0:
        print("未检索到标准图注开头的段落，请使用 --page 和 --bbox 手动指定裁剪区域。")
    doc.close()


def auto_crop_by_caption(pdf_path: str, caption_prefix: str, out_path: str, dpi: int = 300, pad: float = 10.0):
    """
    通过图注前缀（如 'Figure 2' 或 '图 1'）自动定位所在页，
    结合页面中的矢量绘图 (drawings) 与位图 (images) 边界框，自动裁剪出图注上方的完整图形。
    """
    doc = fitz.open(pdf_path)
    target_page = None
    caption_rect = None
    caption_text = ""

    # 提取图编号（如用户传入 'Figure 2' / 'Fig. 2' / '图 2' / '2'，均可统一匹配 Figure/Fig./图 + 编号）
    num_match = re.search(r"(\d+[a-zA-Z]?)\s*$", caption_prefix.strip())
    if num_match:
        fig_num = re.escape(num_match.group(1))
        pattern = re.compile(
            r"^\s*(?:Figure|Fig\.|FIG\.|图)\s*" + fig_num + r"(?!\s*(?:展示|显示|给出|说明|表明|描述|列举|对比|呈现|描绘|中|所示|可知|可见|shows|illustrates|depicts|presents|demonstrates))(?:[\s:\.\-—]|$)",
            re.IGNORECASE
        )
    else:
        norm_prefix = r"\s*".join(re.escape(p) for p in caption_prefix.strip().split())
        pattern = re.compile(r"^\s*" + norm_prefix + r"(?:[\s:\.\-—]|$)", re.IGNORECASE)

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        blocks = page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, _, block_type = b
            if block_type != 0:
                continue
            clean_text = " ".join(text.strip().split())
            if pattern.match(clean_text):
                target_page = page
                caption_rect = fitz.Rect(x0, y0, x1, y1)
                caption_text = clean_text
                # 检查紧邻下方是否有双语副图注 (如中文图注下方的 Fig. X)
                for b2 in blocks:
                    bx0, by0, bx1, by1, b2text, _, b2type = b2
                    if b2type == 0 and 0 <= by0 - y1 <= 25:
                        clean_b2 = " ".join(b2text.strip().split())
                        if CAPTION_PATTERN.match(clean_b2):
                            caption_rect |= fitz.Rect(bx0, by0, bx1, by1)
                break
        if target_page is not None:
            break

    if target_page is None:
        doc.close()
        raise ValueError(f"未在 PDF 中找到以 '{caption_prefix}' 开头的图注，请先运行 --scan 查看所有图注。")

    page_w, page_h = target_page.rect.width, target_page.rect.height
    # 判断该图是跨双栏宽图还是单栏图（跨过页面中线或宽度超过页面 52% 即为跨栏图）
    is_wide = (caption_rect.width > page_w * 0.52) or (
        caption_rect.x0 < page_w * 0.48 and caption_rect.x1 > page_w * 0.52
    )

    # 确定水平搜索范围
    if is_wide:
        search_x0 = page_w * 0.04
        search_x1 = page_w * 0.96
    else:
        # 单栏图：判断在左栏还是右栏
        if caption_rect.x0 < page_w * 0.48:
            search_x0 = page_w * 0.04
            search_x1 = min(caption_rect.x1 + 15, page_w * 0.52)
        else:
            search_x0 = max(caption_rect.x0 - 15, page_w * 0.48)
            search_x1 = page_w * 0.96

    # 查找图注上方最近的普通正文段落底部作为图形上界参考
    body_bottom_y = page_h * 0.05
    blocks = target_page.get_text("blocks")
    for b in blocks:
        bx0, by0, bx1, by1, btext, _, btype = b
        if btype != 0:
            continue
        # 水平方向有重叠，且在图注上方
        if bx1 > search_x0 + 10 and bx0 < search_x1 - 10 and by1 < caption_rect.y0 - 5:
            clean_b = " ".join(btext.strip().split())
            # 如果是一大段正文（字符数 > 140 且具有完整句子特征），视为正文段落边界
            if len(clean_b) > 140 and not CAPTION_PATTERN.match(clean_b):
                if by1 > body_bottom_y:
                    body_bottom_y = by1

    # 收集在 [body_bottom_y, caption_rect.y0] 之间的所有图像和矢量图形框
    candidate_rects = []
    for img_info in target_page.get_images(full=True):
        xref = img_info[0]
        for r in target_page.get_image_rects(xref):
            if r.x1 > search_x0 and r.x0 < search_x1 and r.y1 <= caption_rect.y0 + 15 and r.y0 >= body_bottom_y - 10:
                candidate_rects.append(r)

    for d in target_page.get_drawings():
        r = d.get("rect")
        if r and r.width > 2 and r.height > 2:
            # 排除全页边框
            if r.width > page_w * 0.95 and r.height > page_h * 0.90:
                continue
            if r.x1 > search_x0 and r.x0 < search_x1 and r.y1 <= caption_rect.y0 + 15 and r.y0 >= body_bottom_y - 10:
                candidate_rects.append(r)

    if candidate_rects:
        union_rect = candidate_rects[0]
        for r in candidate_rects[1:]:
            union_rect |= r
        # 同时纳入图内部的子标签文字块
        for b in blocks:
            bx0, by0, bx1, by1, _, _, btype = b
            if btype == 0 and bx1 > union_rect.x0 - 15 and bx0 < union_rect.x1 + 15:
                if by0 >= union_rect.y0 - 20 and by1 <= caption_rect.y0 + 5:
                    union_rect |= fitz.Rect(bx0, by0, bx1, by1)
        crop_rect = fitz.Rect(
            max(0, min(union_rect.x0, caption_rect.x0) - pad),
            max(0, union_rect.y0 - pad),
            min(page_w, max(union_rect.x1, caption_rect.x1) + pad),
            min(page_h, caption_rect.y1 + pad * 0.6),
        )
    else:
        # 兜底：取 body_bottom_y 到 caption_rect.y1
        crop_rect = fitz.Rect(
            max(0, search_x0 - pad),
            max(0, body_bottom_y + 4),
            min(page_w, search_x1 + pad),
            min(page_h, caption_rect.y1 + pad * 0.6),
        )

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    pix = target_page.get_pixmap(clip=crop_rect, dpi=dpi)
    pix.save(out_path)
    page_num = target_page.number + 1
    doc.close()
    print(f"[OK] 已裁剪第 {page_num} 页 ({caption_text[:60]}...) -> {out_path} ({pix.width}x{pix.height} px)")


def manual_crop(pdf_path: str, page_num: int, bbox_str: str, out_path: str, dpi: int = 300):
    """按页码与坐标框裁剪，若坐标均 <= 1.0 则视为相对页面宽高比例，否则视为绝对点坐标"""
    doc = fitz.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        doc.close()
        raise ValueError(f"页码超出范围: {page_num} (总页数 {len(doc)})")
    page = doc[page_num - 1]
    w, h = page.rect.width, page.rect.height
    vals = [float(v.strip()) for v in bbox_str.split(",")]
    if len(vals) != 4:
        doc.close()
        raise ValueError("--bbox 必须包含 4 个数值: x0,y0,x1,y1")
    x0, y0, x1, y1 = vals
    if max(vals) <= 1.0:
        x0, x1 = x0 * w, x1 * w
        y0, y1 = y0 * h, y1 * h
    clip_rect = fitz.Rect(x0, y0, x1, y1)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    pix = page.get_pixmap(clip=clip_rect, dpi=dpi)
    pix.save(out_path)
    doc.close()
    print(f"[OK] 已裁剪第 {page_num} 页指定区域 -> {out_path} ({pix.width}x{pix.height} px)")


def main():
    parser = argparse.ArgumentParser(description="从学术论文 PDF 中检索并高清裁剪架构图/实验图")
    parser.add_argument("--scan", metavar="PDF_PATH", help="扫描 PDF 中所有图注所在的页码与坐标")
    parser.add_argument("--pdf", metavar="PDF_PATH", help="要裁剪的 PDF 文件路径")
    parser.add_argument("--caption", metavar="PREFIX", help="按图注前缀自动裁剪 (例如 'Figure 2' 或 '图 1')")
    parser.add_argument("--page", type=int, help="手动裁剪的页码 (从 1 开始)")
    parser.add_argument("--bbox", help="手动裁剪的区域 x0,y0,x1,y1 (0~1 相对比例或绝对点坐标)")
    parser.add_argument("--out", metavar="OUT_PNG", help="输出 PNG 图片路径")
    parser.add_argument("--dpi", type=int, default=300, help="输出图片 DPI (默认 300)")

    args = parser.parse_args()
    if args.scan:
        scan_captions(args.scan)
    elif args.pdf and args.caption and args.out:
        auto_crop_by_caption(args.pdf, args.caption, args.out, dpi=args.dpi)
    elif args.pdf and args.page and args.bbox and args.out:
        manual_crop(args.pdf, args.page, args.bbox, args.out, dpi=args.dpi)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
