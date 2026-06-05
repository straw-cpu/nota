# nota

> Turn lectures, papers, and projects into structured, browsable HTML — as a coding agent skill.
>
> 📖 **中文版 (Chinese version)**: [README_CN.md](README_CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Agent skill](https://img.shields.io/badge/coding_agent-skill-7B2CBF.svg)

**This is a coding-agent skill, not a hosted service.** Works with Claude Code, Cursor, Codex CLI, OpenClaw, or any editor environment that supports skills. There is no cloud, no signup, no telemetry.

---

## What it does

mynotes packages knowledge into single-file HTML with MathJax formulas, syntax-highlighted code, folded proofs, and a sticky TOC — readable on any device, offline, no build step.

Four natural use cases:

| Use case | What you hand the agent | What you get |
|---|---|---|
| **Lecture notes** | PDF slides / handwritten scan | Structured HTML with theorems, proofs, examples |
| **Paper reading** | arXiv PDF | Section-by-section breakdown, key equations, Q&A blocks |
| **Project summary** | Your own notes / logs | Distilled writeup, methodology, results |
| **Academic poster** | Any of the above | Print-ready A1/A2 poster via `poster_print` template |

---

## Showcase

A real lecture note — *代数基础 Lecture 10: Hermitian 矩阵与正交投影* — generated end-to-end from a course PDF.

Covers: Courant-Fischer theorem · Hermitian矩阵特征值夹逼不等式 · Schur三角化 · 正规矩阵 · 正交投影矩阵，with full proofs in folded blocks and a two-level linked TOC.

→ [`examples/alg_lecture10-default.html`](examples/alg_lecture10-default.html)

---

## Skills

Five skills ship with this repo. Point your agent at the `skills/` directory:

| Skill | Trigger | What it does |
|---|---|---|
| `notes-new` | `/notes-new` | Create a new note from source material (PDF, text, or description) |
| `notes-update` | `/notes-update` | Add sections, Q&A blocks, or rewrite content in an existing note |
| `notes-theme` | `/notes-theme` | Switch color theme across one file or a whole directory |
| `notes-snapshot` | `/notes-snapshot` | Git-tag the current state for rollback |
| `notes-index` | `/notes-index` | Rebuild the browsable index page across all notes |

---

## Templates

Three production-ready templates:

| Template | Best for |
|---|---|
| `academic_lecture` | Multi-section lecture notes, cheat sheets — sticky TOC, callout blocks, code collapse |
| `minimal_slide` | Single-topic paper notes, lightweight reading records |
| `poster_print` | A1/A2 two-column print poster — MathJax, `@page` sizing for exact PDF output |

---

## Themes

| Theme | Status |
|---|---|
| `default` | Gray-red academic palette |
| `dark` | Dark background, red/blue accents |
| `solarized` | *Coming soon* |
| `custom` | Drop your own CSS variables |

---

## Quick start

```bash
# Clone into your agent's skill directory
git clone https://github.com/straw-cpu/nota ~/.claude/skills/nota

# Then, inside your agent:
/notes-new --template academic_lecture --title "My Lecture" --source lecture.pdf
```

The agent reads the source, builds a complete HTML with all theorems / proofs / examples, and saves it locally. No internet needed after clone.

---

## Structure

```
mynotes/
├── skills/
│   ├── notes-new/        ← create a note from source material
│   ├── notes-update/     ← edit / extend an existing note
│   ├── notes-theme/      ← switch themes
│   ├── notes-snapshot/   ← git-tag snapshots
│   └── notes-index/      ← rebuild index page
├── templates/
│   ├── academic_lecture.html
│   ├── minimal_slide.html
│   └── poster_print.html
├── themes/
│   ├── default.css
│   ├── dark.css
│   └── custom.css
├── tools/
│   ├── build_index.py    ← scan HTML, generate navigation page
│   └── theme_switch.py   ← batch theme replacement
└── examples/
    └── alg_lecture10.html
```

---

## Acknowledgements

HTML template structure and visual design reference two open-source projects:

- **[ARIS-in-AI-Offer](https://github.com/wanshuiyin/ARIS-in-AI-Offer)** — academic lecture template layout and CSS variable conventions
- **[posterly](https://github.com/Chenruishuo/posterly)** — poster print template and `@page` sizing approach

Both are MIT-licensed. mynotes adapts their visual style for a note-taking context; the skill workflows and content generation pipeline are independent.

---

## License

MIT. See [LICENSE](LICENSE).
