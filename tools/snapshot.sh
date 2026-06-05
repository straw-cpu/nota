#!/usr/bin/env bash
# snapshot.sh — 对 HTML 文件打 git tag checkpoint
# 用法：./snapshot.sh <文件> <tag描述>
# 示例：./snapshot.sh s4_LayerC_EKF.html before-ekf-rewrite

set -euo pipefail

# ── 参数检查 ────────────────────────────────────────────────────────────────
if [[ $# -lt 2 ]]; then
    echo "用法：$0 <文件路径> <tag描述>" >&2
    echo "示例：$0 s4_LayerC_EKF.html before-ekf-rewrite" >&2
    exit 1
fi

FILE="$1"
DESC="$2"

# ── 文件存在检查 ─────────────────────────────────────────────────────────────
if [[ ! -f "$FILE" ]]; then
    echo "错误：文件不存在：$FILE" >&2
    exit 1
fi

# ── 检查是否在 git 仓库内 ────────────────────────────────────────────────────
if ! git -C "$(dirname "$FILE")" rev-parse --git-dir > /dev/null 2>&1; then
    echo "错误：文件不在 git 仓库内：$FILE" >&2
    exit 1
fi

# ── 构造 tag 名 ───────────────────────────────────────────────────────────────
BASENAME="$(basename "$FILE")"
# 去掉 .html 后缀，转小写，空格换 -
SLUG="${BASENAME%.html}"
SLUG="${SLUG,,}"
SLUG="${SLUG// /-}"

DATE="$(date +%Y%m%d)"
TAG="notes/${SLUG}-${DESC}-${DATE}"

# ── git add + git tag（冲突时加 -b 后缀重试） ─────────────────────────────────
git add "$FILE"

if git tag "$TAG" 2>/dev/null; then
    echo "已打 tag：$TAG"
else
    TAG_RETRY="${TAG}-b"
    echo "警告：tag '$TAG' 已存在，改用 '$TAG_RETRY'" >&2
    git tag "$TAG_RETRY"
    echo "已打 tag：$TAG_RETRY"
fi
