# PDFReflow.ai – Working Rules (Beginner Friendly)

## Goal
Help me ship the MVP fast with small, safe steps.

## Allowed Automation (with limits)
- You may run: `git status`, `git diff`, and ONE of: `rg`/`grep` with a narrow keyword.
- You may read at most 3 files per task (ask before reading more).
- Do NOT run `ls -R`, `find`, `tree`, or `git log --all`.
- Do NOT scan the whole repo.

## Before Editing
1) Say what you plan to change (max 5 bullet points).
2) Ask which file(s) to open if you are unsure.

## Output Format
- Prefer unified diff.
- Keep explanations short (max 6 lines).
- If unsure, ask 1-2 clarifying questions only.

## Code Style
- Python 3.11
- Prefer small functions, minimal refactors
- Avoid new dependencies unless necessary

## OCR (P0)
- `layout_analyzer` must output:
  [{"text": str, "bbox": [x0,y0,x1,y1], "conf": float}]
- Ignore empty text
- Keep it working on a single page first

## Debugging
- Prefer smallest reproducible command.
- If command output is huge, show only the error trace / failing assertion.

## Task Memory
- When a task is done or stuck, update `plan.md`:
  - status (Done/Blocked)
  - modified files
  - next step (1 line)
