"""Portfolio Assignment Sheet & Rubric Generator.

Gradio app for Rose State College AIML 2003/2013 final portfolio presentations.
Students fill out the form, Gemini customizes the rubric, and the app generates
a downloadable PDF assignment sheet.

Deploy on Hugging Face Spaces (CPU free tier). Set GEMINI_API_KEY as a Space secret.
"""

import gradio as gr

from rubric_generator import NLP_CLOS, CV_CLOS, CRITERIA, generate_rubric
from document_builder import build_docx

# ---------------------------------------------------------------------------
# Checkbox labels (numbered for clarity)
# ---------------------------------------------------------------------------

NLP_CHOICES = [f"{i + 1}. {clo}" for i, clo in enumerate(NLP_CLOS)]
CV_CHOICES = [f"{i + 1}. {clo}" for i, clo in enumerate(CV_CLOS)]


# ---------------------------------------------------------------------------
# Theme — matches course-styles.css color tokens
# ---------------------------------------------------------------------------

THEME = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#f7f9fc",
        c100="#d0e0f0",
        c200="#a8c4dc",
        c300="#7da8c8",
        c400="#528cb4",
        c500="#1a3a5c",
        c600="#163250",
        c700="#122a44",
        c800="#0e2238",
        c900="#0a1a2c",
        c950="#061220",
    ),
    neutral_hue=gr.themes.Color(
        c50="#f7f9fc",
        c100="#eef1f5",
        c200="#d0d7de",
        c300="#b0b8c2",
        c400="#8c95a0",
        c500="#656d76",
        c600="#4d545c",
        c700="#363c42",
        c800="#1f2328",
        c900="#14171a",
        c950="#0a0c0e",
    ),
    font=["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
)


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def update_visibility(presentation_type):
    """Show/hide CLO checkbox groups and update their labels to reflect minimums."""
    show_nlp = presentation_type in ("Standalone NLP", "Combined (NLP + CV)")
    show_cv = presentation_type in ("Standalone CV", "Combined (NLP + CV)")
    minimum = 2 if presentation_type == "Combined (NLP + CV)" else 4
    nlp_label = f"NLP Course Learning Outcomes (select at least {minimum})"
    cv_label = f"CV Course Learning Outcomes (select at least {minimum})"

    nlp_update = (gr.update(visible=True, label=nlp_label) if show_nlp
                  else gr.update(visible=False, value=[], label=nlp_label))
    cv_update = (gr.update(visible=True, label=cv_label) if show_cv
                 else gr.update(visible=False, value=[], label=cv_label))
    return nlp_update, cv_update


def _render_rubric_markdown(student_name, rubric):
    """Render the customized rubric as markdown for the preview pane."""
    level_labels = (("full", "Full Credit"), ("partial", "Partial Credit"),
                    ("minimal", "Minimal Credit"), ("none", "No Credit"))
    out = [f"### Rubric preview for {student_name}",
           "_100 points total — review before downloading._", ""]
    for criterion in CRITERIA:
        name = criterion["name"]
        descs = rubric.get(name, {})
        out.append(f"#### {name} &nbsp;<sub>({criterion['points']} pts)</sub>")
        for key, label in level_labels:
            out.append(f"- **{label}** — {descs.get(key, '—')}")
        out.append("")
    return "\n".join(out)


def generate(name, presentation_type, nlp_selected, cv_selected, description, contingency):
    """Validate inputs, generate rubric via Gemini, build PDF."""

    # --- Validation ---
    if not name or not name.strip():
        raise gr.Error("Please enter your name.")
    if not description or not description.strip():
        raise gr.Error("Please describe your project.")
    if not contingency or not contingency.strip():
        raise gr.Error("Please describe your contingency plan — what will you cut if your idea is too ambitious?")

    # Parse selected CLO indices
    nlp_indices = [NLP_CHOICES.index(s) for s in (nlp_selected or [])]
    cv_indices = [CV_CHOICES.index(s) for s in (cv_selected or [])]

    # Enforce CLO minimums
    if presentation_type == "Standalone NLP":
        if len(nlp_indices) < 4:
            raise gr.Error(f"Standalone NLP requires at least 4 CLOs. You selected {len(nlp_indices)}.")
    elif presentation_type == "Standalone CV":
        if len(cv_indices) < 4:
            raise gr.Error(f"Standalone CV requires at least 4 CLOs. You selected {len(cv_indices)}.")
    elif presentation_type == "Combined (NLP + CV)":
        errors = []
        if len(nlp_indices) < 2:
            errors.append(f"at least 2 NLP CLOs (you selected {len(nlp_indices)})")
        if len(cv_indices) < 2:
            errors.append(f"at least 2 CV CLOs (you selected {len(cv_indices)})")
        if errors:
            raise gr.Error(f"Combined presentation requires {' and '.join(errors)}.")

    # --- Generate rubric ---
    rubric = generate_rubric(nlp_indices, cv_indices, description.strip(), presentation_type)

    # --- Build DOCX ---
    filepath = build_docx(
        student_name=name.strip(),
        presentation_type=presentation_type,
        selected_nlp_indices=nlp_indices,
        selected_cv_indices=cv_indices,
        project_description=description.strip(),
        contingency=contingency.strip(),
        rubric_data=rubric,
    )

    return filepath, _render_rubric_markdown(name.strip(), rubric)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Portfolio Assignment Generator",
) as demo:

    gr.Markdown(
        "# Final Portfolio Assignment Generator\n"
        "**Rose State College  |  AIML 2003 / AIML 2013  |  Spring 2026**\n\n"
        "Fill out the form below, then click **Generate** to download your "
        "custom assignment sheet and rubric."
    )

    with gr.Group():
        with gr.Row():
            name_input = gr.Textbox(
                label="Student Name",
                placeholder="First Last",
                scale=1,
            )
            type_input = gr.Radio(
                choices=["Standalone NLP", "Standalone CV", "Combined (NLP + CV)"],
                label="Presentation Type",
                value="Standalone NLP",
                scale=2,
            )

    nlp_group = gr.CheckboxGroup(
        choices=NLP_CHOICES,
        label="NLP Course Learning Outcomes (select at least 4)",
        visible=True,
    )
    cv_group = gr.CheckboxGroup(
        choices=CV_CHOICES,
        label="CV Course Learning Outcomes (select at least 4)",
        visible=True,
    )

    description_input = gr.Textbox(
        label="Project Description",
        placeholder="What are you building? What problem does it solve? What data or APIs does it use?",
        lines=4,
    )
    contingency_input = gr.Textbox(
        label="Contingency Plan",
        placeholder="If your idea turns out to be too ambitious, what will you cut and still meet the CLO requirements?",
        lines=3,
    )

    generate_btn = gr.Button("Generate Assignment Sheet", variant="primary", size="lg")
    output_file = gr.File(label="Your Assignment Sheet (DOCX)")
    rubric_preview = gr.Markdown(visible=False)

    # --- Wiring ---
    type_input.change(
        update_visibility,
        inputs=type_input,
        outputs=[nlp_group, cv_group],
    )

    # Apply correct initial hidden state on page load (default is Standalone NLP,
    # so CV group should be hidden). Both groups are rendered visible=True at
    # build time so Gradio 6.x materializes them in the DOM and can later toggle.
    demo.load(
        update_visibility,
        inputs=type_input,
        outputs=[nlp_group, cv_group],
    )

    def _generate_and_show(*args):
        filepath, md = generate(*args)
        return filepath, gr.update(value=md, visible=True)

    generate_btn.click(
        _generate_and_show,
        inputs=[name_input, type_input, nlp_group, cv_group, description_input, contingency_input],
        outputs=[output_file, rubric_preview],
    )


if __name__ == "__main__":
    demo.launch(theme=THEME)
