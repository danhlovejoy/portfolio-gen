"""Rubric customization via Gemini 2.0 Flash with template fallback."""

import json
import os

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# CLO data
# ---------------------------------------------------------------------------

NLP_CLOS = [
    "Manipulate text as numerical data by explaining the process of tokenization and the creation of word embeddings.",
    "Engineer effective prompts using structured techniques (few-shot, chain-of-thought) to control LLM output behavior and format.",
    "Implement core NLP tasks including classification, summarization, and sentiment analysis using hosted LLM APIs.",
    "Construct a Retrieval-Augmented Generation (RAG) pipeline that connects an LLM to an external knowledge base.",
    "Orchestrate simple AI agents that utilize basic tools (like a calculator or search) to complete multi-step tasks.",
    "Evaluate LLM performance by identifying hallucinations and applying frameworks for bias and safety auditing.",
]

CV_CLOS = [
    "Represent and transform digital images as multidimensional NumPy arrays to perform image manipulation of any kind.",
    "Apply spatial filters and kernels to extract low-level features like edges and textures from raw image data.",
    "Deploy pre-trained deep learning models (such as ResNet or YOLO) to perform image classification and real-time object detection.",
    "Calculate and interpret model metrics including accuracy, precision, and recall, using confusion matrices to identify specific failure modes.",
    "Implement visual similarity search by extracting feature vectors (embeddings) from images and calculating distance in a vector space.",
    "Audit vision systems for demographic bias, proposing mitigation strategies for ethical issues in facial recognition and surveillance.",
]

# ---------------------------------------------------------------------------
# Rubric criteria (fixed names and points; descriptions are customized)
# ---------------------------------------------------------------------------

CRITERIA = [
    {"name": "CLO Coverage", "points": 30},
    {"name": "Working Application", "points": 25},
    {"name": "Project Scope", "points": 20},
    {"name": "Presentation & Understanding", "points": 25},
]

# ---------------------------------------------------------------------------
# Fallback descriptions (used when Gemini is unavailable)
# ---------------------------------------------------------------------------

FALLBACK = {
    "CLO Coverage": {
        "full": "The project clearly demonstrates all selected CLOs with specific, visible evidence in the code and presentation.",
        "partial": "Most selected CLOs are demonstrated, but one or two lack clear evidence or are only superficially addressed.",
        "minimal": "Fewer than half the selected CLOs are convincingly demonstrated. Evidence is vague or missing for several.",
        "none": "The project does not meaningfully demonstrate the selected CLOs.",
    },
    "Working Application": {
        "full": "The application runs without errors during the presentation. The audience sees it execute and produce correct results.",
        "partial": "The application mostly runs but encounters a minor error or requires a workaround during the presentation.",
        "minimal": "The application fails to run or produces significant errors. The student shows static outputs instead of live execution.",
        "none": "No working application is demonstrated.",
    },
    "Project Scope": {
        "full": "The project is appropriately ambitious -- challenging enough to demonstrate real learning, scoped well enough to complete. The contingency plan was realistic.",
        "partial": "The scope is reasonable but slightly too narrow or too broad. The contingency plan exists but was not well thought through.",
        "minimal": "The project is either trivially simple or far too ambitious with no realistic path to completion.",
        "none": "The project scope shows no evidence of planning or consideration of feasibility.",
    },
    "Presentation & Understanding": {
        "full": "Clear narrative arc, accessible explanation, good use of the 8-10 minute window. The student answers follow-up questions with confidence and specificity.",
        "partial": "The presentation is organized but has gaps in clarity or timing. The student answers most questions but struggles with some.",
        "minimal": "The presentation lacks structure or significantly over/under-runs the time. The student cannot answer basic questions about their work.",
        "none": "No presentation given, or the student cannot explain what their project does.",
    },
}


def generate_rubric(selected_nlp_indices, selected_cv_indices, project_description, presentation_type):
    """Call Gemini 2.0 Flash to generate customized rubric descriptions.

    Args:
        selected_nlp_indices: list of int indices into NLP_CLOS
        selected_cv_indices: list of int indices into CV_CLOS
        project_description: str, student's project description
        presentation_type: str, one of "Standalone NLP", "Standalone CV", "Combined (NLP + CV)"

    Returns:
        dict: {criterion_name: {"full": str, "partial": str, "minimal": str, "none": str}}
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY found. Using fallback rubric descriptions.")
        return FALLBACK

    # Build CLO text for the prompt
    clo_lines = []
    if selected_nlp_indices:
        clo_lines.append("NLP Course Learning Outcomes selected:")
        for i in selected_nlp_indices:
            clo_lines.append(f"  {i + 1}. {NLP_CLOS[i]}")
    if selected_cv_indices:
        clo_lines.append("CV Course Learning Outcomes selected:")
        for i in selected_cv_indices:
            clo_lines.append(f"  {i + 1}. {CV_CLOS[i]}")
    clo_text = "\n".join(clo_lines)

    prompt = f"""You are helping an instructor create a customized grading rubric for a student's
final portfolio presentation in an AI/ML course at Rose State College.

The student is doing a {presentation_type} presentation (8-10 minutes).

Project description:
"{project_description}"

{clo_text}

The rubric has four criteria. For each criterion, write descriptions for four scoring
levels: Full Credit, Partial Credit, Minimal Credit, and No Credit.

Rules:
- Each description is 1-2 sentences.
- Write in second person ("Your project...", "You demonstrate...").
- Reference the student's specific project and CLOs — do not write generic descriptions.
- Full Credit means everything works well. No Credit means the criterion is not met at all.
- Partial and Minimal are meaningfully distinct from each other.

The four criteria:
1. CLO Coverage (30 points) — Does the project demonstrate the selected CLOs with visible evidence?
2. Working Application (25 points) — Does the application run during the presentation?
3. Project Scope (20 points) — Is the project appropriately ambitious and well-scoped?
4. Presentation & Understanding (25 points) — Is the presentation clear and well-timed? Can the student answer questions?

Return ONLY a JSON object with this exact structure:
{{
  "CLO Coverage": {{"full": "...", "partial": "...", "minimal": "...", "none": "..."}},
  "Working Application": {{"full": "...", "partial": "...", "minimal": "...", "none": "..."}},
  "Project Scope": {{"full": "...", "partial": "...", "minimal": "...", "none": "..."}},
  "Presentation & Understanding": {{"full": "...", "partial": "...", "minimal": "...", "none": "..."}}
}}"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        result = json.loads(response.text)

        # Validate structure
        for criterion in CRITERIA:
            name = criterion["name"]
            if name not in result:
                print(f"Missing criterion '{name}' in Gemini response. Using fallback.")
                return FALLBACK
            for level in ("full", "partial", "minimal", "none"):
                if level not in result[name]:
                    print(f"Missing level '{level}' for '{name}'. Using fallback.")
                    return FALLBACK

        return result

    except Exception as e:
        print(f"Gemini API error: {e}. Using fallback rubric descriptions.")
        return FALLBACK
