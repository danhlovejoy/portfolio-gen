# Portfolio Assignment Generator — Spec

**Rose State College | AIML 2003 / AIML 2013 | Spring 2026**
Gradio app deployed on Hugging Face Spaces (CPU free tier).

---

## Purpose

Students fill out a form describing their final portfolio presentation. The app validates their selections, calls Gemini 2.5 Flash to generate a customized rubric, and produces a downloadable DOCX assignment sheet. The instructor reviews the DOCX, edits if needed, signs it, and returns it as the student's contract for the final presentation.

---

## Architecture

```
┌─────────────┐      ┌────────────────────┐      ┌──────────────────┐
│  Gradio UI  │ ──►  │  rubric_generator  │ ──►  │ document_builder │
│  (app.py)   │      │  (Gemini 2.5 Flash)│      │  (python-docx)   │
└─────────────┘      └────────────────────┘      └──────────────────┘
       │                       │                          │
   Form input          JSON rubric data           DOCX file output
```

### Files

| File | Role |
|------|------|
| `app.py` | Gradio Blocks UI, validation, event wiring |
| `rubric_generator.py` | CLO data, rubric criteria, Gemini prompt, fallback descriptions |
| `document_builder.py` | DOCX generation with python-docx (portrait assignment sheet + landscape rubric) |
| `requirements.txt` | `gradio`, `google-genai`, `python-docx` |

---

## Data Model

### Course Learning Outcomes (CLOs)

**NLP (AIML 2003) — 6 CLOs:**

1. Manipulate text as numerical data by explaining the process of tokenization and the creation of word embeddings.
2. Engineer effective prompts using structured techniques (few-shot, chain-of-thought) to control LLM output behavior and format.
3. Implement core NLP tasks including classification, summarization, and sentiment analysis using hosted LLM APIs.
4. Construct a Retrieval-Augmented Generation (RAG) pipeline that connects an LLM to an external knowledge base.
5. Orchestrate simple AI agents that utilize basic tools (like a calculator or search) to complete multi-step tasks.
6. Evaluate LLM performance by identifying hallucinations and applying frameworks for bias and safety auditing.

**CV (AIML 2013) — 6 CLOs:**

1. Represent and transform digital images as multidimensional NumPy arrays to perform image manipulation of any kind.
2. Apply spatial filters and kernels to extract low-level features like edges and textures from raw image data.
3. Deploy pre-trained deep learning models (such as ResNet or YOLO) to perform image classification and real-time object detection.
4. Calculate and interpret model metrics including accuracy, precision, and recall, using confusion matrices to identify specific failure modes.
5. Implement visual similarity search by extracting feature vectors (embeddings) from images and calculating distance in a vector space.
6. Audit vision systems for demographic bias, proposing mitigation strategies for ethical issues in facial recognition and surveillance.

### Rubric Criteria

| Criterion | Points | What it measures |
|-----------|--------|------------------|
| CLO Coverage | 30 | Does the project demonstrate the selected CLOs with visible evidence? |
| Working Application | 25 | Does the application run during the presentation? |
| Project Scope | 20 | Is the project appropriately ambitious and well-scoped? |
| Presentation & Understanding | 25 | Is the presentation clear and well-timed? Can the student answer questions? |

**Total: 100 points.**

### Scoring Levels

Each criterion is scored across four levels:

- **Full Credit** — criterion fully met
- **Partial Credit** — mostly met, minor gaps
- **Minimal Credit** — significant gaps
- **No Credit** — criterion not met

---

## Presentation Types

| Type | CLO Minimum | Checkbox Groups Shown |
|------|-------------|----------------------|
| Standalone NLP | 4 NLP CLOs | NLP only |
| Standalone CV | 4 CV CLOs | CV only |
| Combined (NLP + CV) | 2 NLP + 2 CV CLOs | Both |

---

## UI Flow

### Form Inputs

1. **Student Name** — text field, required
2. **Presentation Type** — radio buttons: Standalone NLP, Standalone CV, Combined (NLP + CV)
3. **NLP CLOs** — checkbox group, visible when type includes NLP
4. **CV CLOs** — checkbox group, visible when type includes CV
5. **Project Description** — multiline text, required ("What are you building? What problem does it solve? What data or APIs does it use?")
6. **Contingency Plan** — multiline text, required ("If your idea turns out to be too ambitious, what will you cut and still meet the CLO requirements?")
7. **Generate** button → validates → calls Gemini → builds DOCX → returns file download

### Validation Rules

- Name, description, and contingency must be non-empty.
- Standalone NLP/CV: at least 4 CLOs selected from the relevant course.
- Combined: at least 2 NLP CLOs and at least 2 CV CLOs.
- When presentation type changes, hidden checkbox groups are cleared.

---

## Gemini Integration

**Model:** `gemini-2.5-flash`
**Auth:** `GEMINI_API_KEY` environment variable (set as HF Space secret)
**Response format:** `application/json` (structured output mode)

### Prompt Strategy

The prompt provides:
- Presentation type and duration (8--10 minutes)
- Student's project description (quoted)
- Selected CLOs (listed by course, numbered)
- The four criteria with point values
- Rules: 1--2 sentences per description, second person ("Your project..."), project-specific not generic, four distinct levels

### Fallback

If `GEMINI_API_KEY` is missing or the API call fails, the app uses generic fallback descriptions defined in `rubric_generator.py`. These are functional but not customized to the student's project.

### Validation

The returned JSON is validated for structure: all four criterion names present, each with all four scoring levels. Any structural mismatch triggers fallback.

---

## DOCX Output

The generated document has two sections:

### Page 1 — Assignment Sheet (Portrait, US Letter)

- **Header:** "Rose State College | [Course Label]" (centered, 9pt, gray)
- **Title:** "Final Portfolio Presentation" (20pt, bold, primary color)
- **Subtitle:** "Custom Assignment Sheet" (12pt, muted)
- **Student Info Table:** 2×4 grid with light background — Student name, presentation type, date (Tuesday, May 12, 2026), duration (8--10 minutes)
- **Selected CLOs:** Listed by course with numbering, indented. Combined presentations show subheadings for each course.
- **Project Description:** Student's text
- **Contingency Plan:** Student's text
- **Signature Lines:** Instructor approval + date (light gray lines)
- **Footer:** "Generated [date] | Instructor: Dan Lovejoy" (centered, 8pt, italic, light gray)

### Page 2 — Rubric (Landscape)

- **Title:** "Rubric: [Student Name]" (16pt, bold, primary)
- **Subtitle:** "100 points total | Each criterion scored Full / Partial / Minimal / No Credit"
- **Rubric Table:** 5 columns (Criterion + 4 scoring levels), header row with dark fill and white text, alternating row shading, 8--9pt text
- Same header/footer as page 1

---

## Design Tokens

The app and DOCX share the course visual identity. These values come from `course-styles.css`:

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#1a3a5c` | Headings, labels, table headers, DOCX title |
| `--primary-light` | `#2e5a88` | Gradient endpoints |
| `--accent` | `#2e7d32` | Section heading underlines, tip boxes |
| `--light-bg` | `#f7f9fc` | Card backgrounds, alternating table rows |
| `--border` | `#d0d7de` | Table borders, card borders |
| `--text` | `#1f2328` | Body text |
| `--muted` | `#656d76` | Secondary text, subtitles, footer |
| `--warn-bg` | `#fff3e0` | Warning callout background |
| `--warn-border` | `#e65100` | Warning callout border |
| `--due-bg` | `#fce4ec` | Due-date banner background |
| `--due-text` | `#c62828` | Due-date banner text |

### DOCX Color Mapping

| DOCX constant | Hex | Maps to |
|---------------|-----|---------|
| `PRIMARY` | `#1a3a5c` | `--primary` |
| `ACCENT` | `#2e7d32` | `--accent` |
| `MUTED` | `#646464` | `--muted` (approx) |
| `HEADER_FILL` | `#1A3A5C` | `--primary` (table header bg) |
| `LIGHT_FILL` | `#F7F9FC` | `--light-bg` (alternating rows) |
| `WHITE_FILL` | `#FFFFFF` | White (alternating rows) |
| Border color | `#D0D7DE` | `--border` |

### Typography

- **Font stack:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Body text:** 0.95rem / 10pt in DOCX
- **Max content width:** 820px (Gradio default is wider; the DOCX is constrained by page margins)

### Gradio Theme

The app uses `gr.themes.Soft()` as a base. To match the course identity more closely, apply these overrides:

```python
theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#f7f9fc",    # --light-bg
        c100="#d0e0f0",   # --primary-faded
        c200="#a8c4dc",
        c300="#7da8c8",
        c400="#528cb4",
        c500="#1a3a5c",   # --primary
        c600="#163250",
        c700="#122a44",
        c800="#0e2238",
        c900="#0a1a2c",
        c950="#061220",
    ),
    neutral_hue=gr.themes.Color(
        c50="#f7f9fc",
        c100="#eef1f5",
        c200="#d0d7de",   # --border
        c300="#b0b8c2",
        c400="#8c95a0",
        c500="#656d76",   # --muted
        c600="#4d545c",
        c700="#363c42",
        c800="#1f2328",   # --text
        c900="#14171a",
        c950="#0a0c0e",
    ),
    font=["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
)
```

---

## Deployment

### Platform

Hugging Face Spaces, SDK: Gradio, Hardware: CPU Basic (free tier).

### Space Structure

```
portfolio-generator/
├── app.py
├── rubric_generator.py
├── document_builder.py
└── requirements.txt
```

### Secrets

Set `GEMINI_API_KEY` in the Space settings under Repository secrets. The app reads it via `os.environ.get("GEMINI_API_KEY")`.

### Deploy Steps

1. Create a new Space on huggingface.co (SDK: Gradio, hardware: CPU Basic).
2. Add `GEMINI_API_KEY` as a Space secret.
3. Push the four files to the Space repo.
4. The Space auto-builds and deploys.

---

## Open Items

- [x] Update `google-generativeai` to `google.genai` (current package shows deprecation warnings)
- [x] Apply custom Gradio theme (currently using `gr.themes.Soft()` without overrides)
- [x] Add a preview pane so students can see the rubric before downloading
- [ ] Test with real student submissions during class
