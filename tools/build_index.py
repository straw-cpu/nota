#!/usr/bin/env python3
"""
build_index.py — 扫描目录，重建 index.html 笔记导航页

用法：
  python build_index.py <目录>                  # 扫描目录，输出 index.html
  python build_index.py <目录> -o <输出路径>    # 指定输出文件
  python build_index.py <目录> --dry-run        # 只打印，不写文件
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path


def extract_meta(html_content: str) -> dict:
    """从 HTML 内容中提取元数据，仅用正则，不依赖 BeautifulSoup。"""
    result = {
        "title": None,
        "description": None,
        "template": None,
        "modified_at": None,
    }

    # <title>...</title>
    m = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
    if m:
        result["title"] = re.sub(r"\s+", " ", m.group(1)).strip()

    # <meta name="description" content="...">
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
        html_content, re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
            html_content, re.IGNORECASE,
        )
    if m:
        result["description"] = m.group(1).strip()

    # <meta name="mynotes:template" content="...">
    m = re.search(
        r'<meta\s+name=["\']mynotes:template["\']\s+content=["\']([^"\']*)["\']',
        html_content, re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']mynotes:template["\']',
            html_content, re.IGNORECASE,
        )
    if m:
        result["template"] = m.group(1).strip()

    # <meta name="mynotes:modified-at" content="...">
    m = re.search(
        r'<meta\s+name=["\']mynotes:modified-at["\']\s+content=["\']([^"\']*)["\']',
        html_content, re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']mynotes:modified-at["\']',
            html_content, re.IGNORECASE,
        )
    if m:
        result["modified_at"] = m.group(1).strip()

    return result


def build_rows(directory: str) -> list:
    """扫描目录，收集每个 HTML 文件的元数据，返回行列表（按文件名排序）。"""
    pattern = os.path.join(directory, "*.html")
    files = sorted(glob.glob(pattern))
    rows = []
    for fpath in files:
        fname = os.path.basename(fpath)
        if fname.lower() == "index.html":
            continue
        size_kb = os.path.getsize(fpath) / 1024
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            print(f"警告：无法读取 {fpath}：{e}", file=sys.stderr)
            content = ""
        meta = extract_meta(content)
        rows.append({
            "filename": fname,
            "title": meta["title"] or "—",
            "description": meta["description"] or "—",
            "template": meta["template"] or "—",
            "modified_at": meta["modified_at"] or "—",
            "size_kb": f"{size_kb:.1f} KB",
        })
    return rows


def render_html(rows: list, page_title: str) -> str:
    """渲染 index.html，AI-Offer academic 风格。"""
    row_html_parts = []
    for r in rows:
        desc = r["description"]
        if desc != "—" and len(desc) > 80:
            desc = desc[:77] + "…"
        row_html_parts.append(
            f'    <tr>\n'
            f'      <td><a href="{r["filename"]}">{r["filename"]}</a></td>\n'
            f'      <td>{r["title"]}</td>\n'
            f'      <td class="desc">{desc}</td>\n'
            f'      <td>{r["template"]}</td>\n'
            f'      <td>{r["modified_at"]}</td>\n'
            f'      <td class="size">{r["size_kb"]}</td>\n'
            f'    </tr>'
        )
    rows_html = "\n".join(row_html_parts)
    count = len(rows)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <style>
    :root {{
      --primary: #1a4a8c;
      --accent:  #b8390e;
      --bg:      #fdfcf7;
      --surface: #f4f1e8;
      --border:  #d6cfc0;
      --text:    #2c2c2c;
      --muted:   #6b6560;
      --radius:  4px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, serif;
      background: var(--bg);
      color: var(--text);
      padding: 2rem 1rem;
      line-height: 1.6;
    }}

    header {{
      max-width: 900px;
      margin: 0 auto 2rem;
      border-bottom: 2px solid var(--primary);
      padding-bottom: 0.75rem;
    }}

    header h1 {{
      font-size: 1.8rem;
      color: var(--primary);
      letter-spacing: 0.03em;
    }}

    header p.subtitle {{
      color: var(--muted);
      font-size: 0.9rem;
      margin-top: 0.3rem;
    }}

    .wrapper {{
      max-width: 900px;
      margin: 0 auto;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }}

    thead tr {{
      background: var(--primary);
      color: #fff;
    }}

    thead th {{
      padding: 0.6rem 0.8rem;
      text-align: left;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}

    tbody tr {{
      border-bottom: 1px solid var(--border);
      transition: background 0.15s;
    }}

    tbody tr:nth-child(even) {{ background: var(--surface); }}
    tbody tr:hover {{ background: #ece8da; }}

    tbody td {{
      padding: 0.55rem 0.8rem;
      vertical-align: top;
    }}

    tbody td a {{
      color: var(--primary);
      text-decoration: none;
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 0.88rem;
    }}

    tbody td a:hover {{
      color: var(--accent);
      text-decoration: underline;
    }}

    td.desc {{
      color: var(--muted);
      font-size: 0.87rem;
      max-width: 260px;
    }}

    td.size {{
      color: var(--muted);
      font-size: 0.85rem;
      white-space: nowrap;
    }}

    footer {{
      max-width: 900px;
      margin: 1.5rem auto 0;
      text-align: right;
      font-size: 0.82rem;
      color: var(--muted);
    }}

    footer span.accent {{ color: var(--accent); font-weight: 600; }}
  </style>
</head>
<body>
  <header>
    <h1>{page_title}</h1>
    <p class="subtitle">共 {count} 个笔记文件 · 由 build_index.py 自动生成</p>
  </header>

  <div class="wrapper">
    <table>
      <thead>
        <tr>
          <th>文件名</th>
          <th>标题</th>
          <th>描述</th>
          <th>模板</th>
          <th>修改时间</th>
          <th>大小</th>
        </tr>
      </thead>
      <tbody>
{rows_html}
      </tbody>
    </table>
  </div>

  <footer>
    <span class="accent">{count}</span> entries · build_index.py
  </footer>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="扫描目录，重建 index.html 笔记导航页",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("dir", help="要扫描的目录路径")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出文件路径（默认：<dir>/index.html）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印生成内容，不写入文件",
    )
    parser.add_argument(
        "--title",
        default="笔记索引",
        help="页面标题（默认：笔记索引）",
    )
    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    if not os.path.isdir(target_dir):
        print(f"错误：目录不存在：{target_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or os.path.join(target_dir, "index.html")
    output_path = os.path.abspath(output_path)

    rows = build_rows(target_dir)
    html = render_html(rows, args.title)

    if args.dry_run:
        print(html)
        print(f"\n[dry-run] 将写入：{output_path}（共 {len(rows)} 个条目）", file=sys.stderr)
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"已生成：{output_path}（共 {len(rows)} 个条目）")


if __name__ == "__main__":
    main()
