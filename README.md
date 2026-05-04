---
title: Portfolio Assignment Generator
emoji: 📝
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
pinned: false
---

# Final Portfolio Assignment Generator

Rose State College — AIML 2003 / AIML 2013 — Spring 2026.

Students fill out a form describing their final portfolio presentation. The app
calls Gemini 2.0 Flash to generate a customized rubric and produces a
downloadable DOCX assignment sheet for the instructor to sign.

See [`SPEC.md`](SPEC.md) for full design and architecture notes.

## Secrets

Set `GEMINI_API_KEY` in the Space settings. Without it, the app falls back to
generic rubric descriptions.
