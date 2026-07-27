# Markdown Notes Cheatsheet

A practical, copy-paste-friendly guide for writing clean notes in Markdown.

## 1) Quick Start

Use this tiny starter template for any note:

````markdown
# Title

## Summary
One short paragraph on what this note is about.

## Key Points
- Point 1
- Point 2
- Point 3

## Examples
```python
print("hello")
```

## Questions
- [ ] Question 1
- [ ] Question 2

## Next Actions
- [ ] Action 1
- [ ] Action 2
````

---

## 2) Core Markdown Syntax

### Headings

```markdown
# H1
## H2
### H3
#### H4
```

Tips:
- Use one `# H1` per file.
- Keep heading text short and descriptive.

### Paragraphs and line breaks

```markdown
This is paragraph one.

This is paragraph two.
```

Line breaks:
- Leave one blank line between paragraphs.
- For a hard line break, end line with two spaces.

### Emphasis

```markdown
*italic* or _italic_
**bold** or __bold__
***bold italic***
~~strikethrough~~
```

### Lists

Unordered:

```markdown
- Item A
- Item B
  - Sub-item B1
  - Sub-item B2
```

Ordered:

```markdown
1. First
2. Second
3. Third
```

Task lists:

```markdown
- [ ] Todo item
- [x] Done item
```

### Links

```markdown
[OpenAI](https://openai.com)
[Local File](../README.md)
```

### Images

```markdown
![Alt text](./images/example.png)
```

### Blockquotes

```markdown
> This is a quote.
>
> It can span multiple lines.
```

### Horizontal rule

```markdown
---
```

### Inline code

```markdown
Use `pip install` to install packages.
```

### Code blocks

Use fenced blocks and specify language when possible:

````markdown
```python
for i in range(3):
    print(i)
```
````

Common language tags:
- `python`
- `csharp`
- `cpp`
- `bash`
- `json`
- `yaml`
- `sql`
- `text`

### Tables

```markdown
| Topic | Status | Notes |
|------|--------|-------|
| Markdown basics | Done | Comfortable |
| Tables | In progress | Need more reps |
```

### Escaping special characters

If Markdown is formatting something you want as plain text, escape with `\`:

```markdown
\*not italic\*
\# not a heading
```

---

## 3) Note-Taking Patterns That Work

### Cornell-style notes (Markdown version)

```markdown
# Topic

## Cue Questions
- What problem does this solve?
- When should I use it?

## Notes
- Main concept
- Supporting details
- Example

## Summary
2-4 lines in your own words.
```

### Concept card

````markdown
## Concept: Dependency Injection

### What it is
Short definition.

### Why it exists
What pain point it solves.

### When to use
Concrete triggers.

### When not to use
Cost and tradeoffs.

### Example
```csharp
// short example
```
````

### Problem-solution log

```markdown
## Problem
What failed? Include exact error.

## Root cause
What was actually wrong.

## Fix
What changed.

## Prevention
How to avoid this next time.
```

---

## 4) Analog-First to Digital Distillation Template

Use this after writing on paper.

```markdown
# Session Distillation - YYYY-MM-DD

## Source
- Course/book/video:
- Sections covered:
- Time spent:

## Top 3 Concepts
1. 
2. 
3. 

## One Reusable Pattern
- Pattern:
- When to use:

## Questions I Still Have
- [ ] 
- [ ] 

## From-Memory Rebuild
- What I rebuilt:
- What I forgot:
- What I had to look up:

## Next Action (single)
- [ ] 
```

Rule:
- Do not transcribe everything.
- Distill what is reusable.

---

## 5) Course Note File Template

````markdown
# Course Name

## 1. Summary
### Predicted (before start)

### Actual (after section or module)

### Delta (what changed in your understanding)

## 2. Key Concepts
- [ ] Concept 1
- [ ] Concept 2

## 3. Code Patterns I Would Reuse
### Pattern Name
When to use:

```python
# snippet
```

## 4. Questions / Unresolved
- [ ] Question

## 5. Connections
- To other topics:
- To projects:

## 6. Session Log
| Date | Module | Time | Output |
|------|--------|------|--------|
|      |        |      |        |
````

---

## 6) Folder and File Naming Conventions

Good naming reduces search friction.

Recommended:
- `YYYY-MM-DD-topic.md`
- `python-oop-notes.md`
- `api-design-patterns.md`

Avoid:
- `notes.md` (too generic)
- `new notes final v2.md` (version chaos)

---

## 7) Writing Guidelines for Better Retention

- Write in your own words, not transcript style.
- Keep bullets short.
- Use examples for abstract ideas.
- Add one "when not to use" line for each major concept.
- Add one retrieval question per section.

Example retrieval question:

```markdown
Q: Why prefer composition over inheritance here?
A: 
```

---

## 8) Fast Formatting Reference

```markdown
# Heading 1
## Heading 2

**bold** *italic* ~~strike~~

- bullet
1. numbered
- [ ] task

`inline code`

> quote

[link](https://example.com)
![image](./img.png)

---

| A | B |
|---|---|
| 1 | 2 |
```

---

## 9) Common Mistakes

- Huge paragraphs with no headings.
- Copying slides verbatim.
- No examples.
- No unresolved questions.
- No follow-up action.

If a note has no decision, no example, and no next action, it is likely low value.

---

## 10) Weekly Review Template

```markdown
# Weekly Review - YYYY-MM-DD

## What I learned
- 

## What I can explain from memory
- 

## What is still fuzzy
- [ ] 

## What I built
- 

## Next week's focus
- [ ] 
```

---

## 11) Optional Extras (Supported in many editors)

Some Markdown flavors support callouts:

```markdown
> [!NOTE]
> This is a note callout.

> [!WARNING]
> This is a warning callout.
```

If callouts do not render in your tool, use regular blockquotes.

---

## 12) Plain-English Rulebook

- Capture quickly.
- Distill aggressively.
- Keep only reusable knowledge.
- Add one action before you close the file.

If you follow that, your notes become a system, not a pile.
