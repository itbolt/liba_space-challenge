# AI Algorithm Engineer Intern - Take-Home Challenge

This repo includes two runnable demos matching the prompt:

- Part 1 - AI-Powered Resume Customization: ingest a Job Description (JD) and a Resume (PDF/DOCX/TXT), extract relevant skills/requirements, and output an ATS-friendly tailored PDF.
- Part 2 - AI Resume Auto-Submission (Simplified): open a job posting (e.g., Greenhouse/Ashby) with Playwright, fill basic fields, upload the tailored resume PDF, and click submit. Returns a JSON log.

No LLM calls are used so the demo is fully offline/runnable. You can swap in your favorite model later if desired.

--------------------------------------------------------------------------

## Quickstart

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Part 1: Resume Customizer

Inputs: --jd (txt/pdf/docx) and --resume (pdf/docx/txt)  
Output: a tailored PDF at out/tailored_resume.pdf

```
python part1_resume_customizer/jd_to_resume.py   --jd samples/jd_software_intern.txt   --resume samples/resume_sample.txt   --out out/tailored_resume.pdf
```

What it does:
- Parses the JD and resume into text.
- Extracts key skills/requirements from the JD using a lightweight keyword extractor plus a small skills lexicon.
- Rebuilds an ATS-friendly resume with standardized section headers, bullet points, clear fonts, and consistent spacing (no tables).
- Highlights and surfaces JD-matching bullets and skills from the source resume.

Notes:
- This is intentionally deterministic and dependency-light. You can plug in spaCy/transformers later to improve extraction/ranking.
- It does not attempt perfect resume structure recovery; instead it creates a clean, compliant PDF with the most relevant content up-front.

### Part 2: Auto-Submission (Simplified)

Inputs: --job_url, --name, --email, --phone, --resume_pdf  
Output: JSON application log printed to stdout

```
# First-time only (installs browser binaries)
python -m playwright install

python part2_auto_submission/auto_submit.py   --job_url "https://boards.greenhouse.io/.../jobs/..."   --name "Ada Lovelace"   --email "ada@example.com"   --phone "+1-555-123-4567"   --resume_pdf out/tailored_resume.pdf
```

How it works:
- Opens the page.
- Finds common name/email/phone fields by label/input name heuristics.
- Uploads your resume PDF to the first visible file input.
- Clicks a button with text variants like "Submit" / "Apply".
- Prints a JSON log including job_url, status, and submitted_at ISO timestamp.

Sites vary. The script aims for Greenhouse/Ashby defaults and will still be easy to customize (selectors are all in one place).

--------------------------------------------------------------------------

## Folder Layout

```
ai_intern_challenge/
├─ requirements.txt
├─ README.md
├─ samples/
│  ├─ jd_software_intern.txt
│  └─ resume_sample.txt
├─ out/                  # generated here
├─ part1_resume_customizer/
│  ├─ jd_to_resume.py
│  ├─ parsers.py
│  ├─ skills_lexicon.py
│  └─ pdf_writer.py
└─ part2_auto_submission/
   └─ auto_submit.py
```

--------------------------------------------------------------------------

## Extending the Demo

- Swap in an LLM to enhance bullet rewriting, quantification, and phrasing for a stronger match to the JD.
- Expand the skills lexicon with domain-specific terms (CV, NLP, distributed systems, CUDA, etc.).
- Harden the Playwright selectors for your target ATS (e.g., Workday, Lever, Ashby) and add support for additional custom questions.
