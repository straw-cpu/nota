# notes-split — PDF 按颗粒度拆分

`/notes-split` 是 `/notes-new` 的前置指令：把一个 PDF 按指定页数拆成若干小块，输出到 `splits/` 子目录，供后续逐块生成笔记使用。

## 用法

```
/notes-split <PDF路径> [--pages N] [--out <目录>] [--dry-run]
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `<PDF路径>` | 必须 | 源 PDF 的绝对或相对路径 |
| `--pages N` | `3` | 每块包含的页数（颗粒度）；必须为正整数 |
| `--out <目录>` | `<PDF同级目录>/splits/` | 输出目录；若不存在则自动创建 |
| `--dry-run` | 关闭 | 只打印将生成的分块计划，不写文件 |

## 工作流

### 第 1 步：解析参数

从用户输入提取：
- `PDF`：源文件路径（必须）；若不存在则报错退出
- `PAGES`：`--pages N`，默认 `3`；若提供的值非正整数则报错
- `OUT`：`--out <目录>`，默认为 `<PDF所在目录>/splits/`
- `DRY_RUN`：是否含 `--dry-run`

### 第 2 步：探测 PDF 总页数

用 Python 探测（优先 `pypdf`，fallback `PyPDF2`，再 fallback `pdfplumber`）：

```python
# /tmp/notes_split_probe.py
import sys

pdf_path = sys.argv[1]
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        import pdfplumber
        with pdfplumber.open(pdf_path) as p:
            print(len(p.pages))
        sys.exit(0)

r = PdfReader(pdf_path)
print(len(r.pages))
```

执行：`python3 /tmp/notes_split_probe.py "<PDF>"`
记录总页数为 `TOTAL`。

### 第 3 步：计算分块计划

```
part 数 = ceil(TOTAL / PAGES)
part_k 的页范围：[（k-1）*PAGES + 1, min(k*PAGES, TOTAL)]
输出文件名：part{k:02d}_p{start}-{end}.pdf
```

示例（TOTAL=24, PAGES=3）：
```
part01_p1-3.pdf
part02_p4-6.pdf
...
part08_p22-24.pdf
```

### 第 4 步：dry-run 模式

若 `--dry-run`：打印分块计划后退出：

```
PDF：<路径>（共 TOTAL 页）
颗粒度：PAGES 页/块，共 N 块

  part01_p1-3.pdf   → 第 1–3 页
  part02_p4-6.pdf   → 第 4–6 页
  ...

--dry-run 模式：未写入文件。运行不带 --dry-run 即可执行。
```

### 第 5 步：执行拆分

创建输出目录（若不存在）。

用 Python 执行拆分：

```python
# /tmp/notes_split_exec.py
import sys, os, math

pdf_path, out_dir, pages_per_part = sys.argv[1], sys.argv[2], int(sys.argv[3])

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfReader, PdfWriter

os.makedirs(out_dir, exist_ok=True)
reader = PdfReader(pdf_path)
total = len(reader.pages)
n_parts = math.ceil(total / pages_per_part)

for k in range(n_parts):
    start = k * pages_per_part          # 0-indexed
    end   = min(start + pages_per_part, total)
    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    fname = f"part{k+1:02d}_p{start+1}-{end}.pdf"
    out_path = os.path.join(out_dir, fname)
    with open(out_path, 'wb') as f:
        writer.write(f)
    print(f"  {fname}")

print(f"done  total={total}  parts={n_parts}")
```

执行：`python3 /tmp/notes_split_exec.py "<PDF>" "<OUT>" <PAGES>`

捕获输出，逐行解析文件名。

### 第 6 步：输出汇总

```
已拆分：<PDF文件名>（共 TOTAL 页，颗粒度 PAGES 页/块）
输出目录：<OUT>
生成文件：N 个
  ✓ part01_p1-3.pdf
  ✓ part02_p4-6.pdf
  ...

下一步：
  /notes-new <OUT>/part01_p1-3.pdf --template academic_lecture
  （或对整个目录批量生成：/notes-new <OUT>/ --template academic_lecture）
```

### 第 7 步：清理

```bash
rm -f /tmp/notes_split_probe.py /tmp/notes_split_exec.py
```

## 错误处理

| 情况 | 输出 |
|---|---|
| PDF 不存在 | `错误：文件不存在：<路径>` |
| `--pages` 非正整数 | `错误：--pages 必须为正整数（收到：<值>）` |
| pypdf / PyPDF2 / pdfplumber 均未安装 | `错误：需要 pypdf（pip install pypdf）` |
| 输出目录无写权限 | `错误：无法写入目录：<OUT>` |

## 与 notes-new 的衔接

```
/notes-split lecture.pdf --pages 3
→ splits/part01_p1-3.pdf ... part08_p22-24.pdf

/notes-new splits/part01_p1-3.pdf --template academic_lecture --title "Lecture 10 §1"
/notes-new splits/part02_p4-6.pdf --template academic_lecture --title "Lecture 10 §2"
...
```

或在 `notes-new` 中检测到目录时自动按拆分顺序批量处理。

## 依赖

- Python 3（`pypdf` 或 `PyPDF2`；均未安装时提示安装命令）
- 无其他外部依赖
