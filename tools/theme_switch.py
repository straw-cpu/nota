#!/usr/bin/env python3
"""
theme_switch.py — 替换 HTML 文件的 :root CSS 主题变量

用法：
  python theme_switch.py <文件或目录> <主题名>
  python theme_switch.py s2.html dark
  python theme_switch.py ./notes/ solarized --dry-run
"""

import argparse
import glob
import os
import re
import sys


# ---------------------------------------------------------------------------
# 括号计数法：定位 :root { ... } 块的起止位置
# ---------------------------------------------------------------------------

def find_root_block(content: str, start_pos: int = 0):
    """
    从 start_pos 开始查找第一个 ':root' 块，返回 (block_start, block_end) 或 None。
    block_end 是紧跟在闭合 '}' 之后的位置（可直接用于切片）。
    """
    idx = content.find(":root", start_pos)
    if idx == -1:
        return None
    # 跳过 :root 后面的空白，找到第一个 '{'
    brace_start = content.find("{", idx)
    if brace_start == -1:
        return None
    depth = 0
    for i in range(brace_start, len(content)):
        ch = content[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return idx, i + 1  # 包含末尾 '}'
    return None  # 括号不匹配


# ---------------------------------------------------------------------------
# 主题 CSS 提取
# ---------------------------------------------------------------------------

def load_theme_root_block(themes_dir: str, theme_name: str) -> str:
    """
    读取 <themes_dir>/<theme_name>.css，返回 ':root { ... }' 块字符串。
    若文件不存在或不含有效块，抛出 ValueError。
    """
    css_path = os.path.join(themes_dir, f"{theme_name}.css")
    if not os.path.isfile(css_path):
        raise ValueError(f"主题文件不存在：{css_path}")

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # 去除纯注释后检查是否有实质内容
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL).strip()
    if not stripped:
        raise ValueError(f"主题文件内容为空（仅含注释）：{css_path}")

    result = find_root_block(css)
    if result is None:
        raise ValueError(f"主题文件中未找到 :root 块：{css_path}")

    start, end = result
    return css[start:end]


# ---------------------------------------------------------------------------
# 单文件处理
# ---------------------------------------------------------------------------

def process_file(html_path: str, new_root_block: str, theme_name: str, dry_run: bool) -> bool:
    """
    替换 html_path 中 <style> 标签内第一个 :root 块，
    同时更新 <meta name="mynotes:theme"> 的 content。
    返回是否成功修改。
    """
    try:
        with open(html_path, "r", encoding="utf-8", errors="replace") as f:
            original = f.read()
    except OSError as e:
        print(f"错误：无法读取 {html_path}：{e}", file=sys.stderr)
        return False

    content = original

    # 找 <style> 标签的范围，只在其内部替换 :root
    style_match = re.search(r"<style[^>]*>", content, re.IGNORECASE)
    if style_match is None:
        print(f"警告：{html_path} 中未找到 <style> 标签，跳过", file=sys.stderr)
        return False

    style_open_end = style_match.end()
    style_close = re.search(r"</style\s*>", content[style_open_end:], re.IGNORECASE)
    if style_close is None:
        print(f"警告：{html_path} 中 <style> 标签未闭合，跳过", file=sys.stderr)
        return False

    style_body_start = style_open_end
    style_body_end = style_open_end + style_close.start()

    # 在 style body 内定位 :root 块
    style_body = content[style_body_start:style_body_end]
    result = find_root_block(style_body)
    if result is None:
        print(f"警告：{html_path} 的 <style> 中未找到 :root 块，跳过", file=sys.stderr)
        return False

    rel_start, rel_end = result
    abs_start = style_body_start + rel_start
    abs_end = style_body_start + rel_end

    # 替换 :root 块
    content = content[:abs_start] + new_root_block + content[abs_end:]

    # 更新 <meta name="mynotes:theme" content="...">（若存在）
    def replace_theme_meta(m):
        before = m.group(1)  # name= 或 content= 在前的部分
        # 重建整个 meta 标签，只替换 content 值
        tag = m.group(0)
        tag = re.sub(
            r'(content=["\'])[^"\']*(["\'])',
            lambda cm: cm.group(1) + theme_name + cm.group(2),
            tag,
        )
        return tag

    content = re.sub(
        r'<meta\s+[^>]*name=["\']mynotes:theme["\'][^>]*>',
        lambda m: re.sub(
            r'(content=["\'])[^"\']*(["\'])',
            lambda cm: cm.group(1) + theme_name + cm.group(2),
            m.group(0),
        ),
        content,
        flags=re.IGNORECASE,
    )

    if content == original:
        print(f"无变化：{html_path}（已是该主题或 :root 内容相同）")
        return False

    if dry_run:
        print(f"[dry-run] 已切换：{html_path} → {theme_name}")
    else:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"已切换：{html_path} → {theme_name}")

    return True


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="替换 HTML 文件的 :root CSS 主题变量",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("target", help="目标 HTML 文件路径，或包含 HTML 文件的目录")
    parser.add_argument("theme", help="主题名称（对应 themes/<主题名>.css）")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印，不写入文件",
    )
    parser.add_argument(
        "--themes-dir",
        default="/root/cdm/ZBFB/tools/mynotes/themes/",
        help="主题 CSS 文件目录（默认：%(default)s）",
    )
    args = parser.parse_args()

    # 加载主题
    try:
        new_root_block = load_theme_root_block(args.themes_dir, args.theme)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)

    # 收集目标 HTML 文件
    target = os.path.abspath(args.target)
    if os.path.isfile(target):
        html_files = [target]
    elif os.path.isdir(target):
        html_files = sorted(glob.glob(os.path.join(target, "*.html")))
        if not html_files:
            print(f"警告：目录中未找到 HTML 文件：{target}", file=sys.stderr)
            sys.exit(0)
    else:
        print(f"错误：目标不存在：{target}", file=sys.stderr)
        sys.exit(1)

    # 处理每个文件
    changed = 0
    for html_path in html_files:
        if process_file(html_path, new_root_block, args.theme, args.dry_run):
            changed += 1

    suffix = "（dry-run，未实际写入）" if args.dry_run else ""
    print(f"\n共修改 {changed} 个文件{suffix}")


if __name__ == "__main__":
    main()
