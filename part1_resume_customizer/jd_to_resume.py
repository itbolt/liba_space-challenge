\
import re
import os
import argparse
from collections import Counter

from parsers import read_any, normalize_text
from skills_lexicon import DEFAULT_SKILLS
from pdf_writer import build_pdf

def tokenize(text: str):
    return re.findall(r"[A-Za-z][A-Za-z+\-#]*", text.lower())

def extract_phrases(text: str, min_len=2, max_len=4):
    words = tokenize(text)
    phrases = []
    for n in range(min_len, max_len+1):
        for i in range(len(words)-n+1):
            phrases.append(" ".join(words[i:i+n]))
    return phrases

def extract_skills_from_jd(jd_text: str):
    tokens = tokenize(jd_text)
    phrases = extract_phrases(jd_text)
    from collections import Counter
    counts = Counter(tokens + phrases)

    # Score lexicon skills and also top n-grams
    scored = {}
    for s in DEFAULT_SKILLS:
        scored[s] = counts.get(s.lower(), 0)
    # Also include top phrases that look technical
    techish = [p for p in counts if any(k in p for k in ["ml", "nlp", "python", "torch", "tensor", "embed", "vector", "db", "playwright", "puppeteer", "regression", "classification", "clustering", "retrieval"])]
    for p in techish:
        scored[p] = counts[p]

    top = sorted([k for k,v in scored.items() if v>0], key=lambda k: (-scored[k], k))
    return top[:20]

def split_resume_into_lines(resume_text: str):
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    return lines

def guess_name(resume_text: str):
    # Use the first non-empty line as the name (common in resumes)
    for line in resume_text.splitlines():
        s = line.strip()
        if s:
            return s[:80]
    return "Candidate Name"

def filter_bullets_by_skills(lines, skills):
    skill_set = set(skills)
    matched = []
    others = []
    for ln in lines:
        ln_l = ln.lower()
        if any(s in ln_l for s in skill_set):
            matched.append(ln)
        else:
            others.append(ln)
    return matched, others

def build_sections(jd_text: str, resume_text: str):
    skills = extract_skills_from_jd(jd_text)
    name = guess_name(resume_text)

    lines = split_resume_into_lines(resume_text)

    # Derive a short summary
    summary = "AI/ML intern with hands-on experience matching this JD: {}.".format(", ".join(skills[:6])) if skills else "AI/ML intern with hands-on experience."

    # Partition bullets
    matched, others = filter_bullets_by_skills(lines, skills)

    # Skills section: de-duplicate and prettify
    def pretty(s): 
        return s.title() if len(s) < 25 else s
    seen = set()
    skills_section = []
    for s in skills:
        if s not in seen:
            skills_section.append(pretty(s))
            seen.add(s)

    # Work Experience: surface matched bullets first, then a few others
    work_exp = matched[:8] + others[:4]

    # Education: find likely lines
    import re as _re
    edu_candidates = [ln for ln in lines if _re.search(r"(B\.?S\.?|BSc|M\.?S\.?|MSc|Ph\.?D|Bachelor|Master|University|College)", ln, _re.I)]
    education = edu_candidates[:4]

    sections = {
        "Summary": summary,
        "Skills": skills_section,
        "Work Experience": work_exp,
        "Education": education or ["Education details available upon request."],
    }
    return name, sections

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jd", required=True, help="Path to job description (txt/pdf/docx)")
    ap.add_argument("--resume", required=True, help="Path to resume (pdf/docx/txt)")
    ap.add_argument("--out", default="out/tailored_resume.pdf", help="Output PDF path")
    args = ap.parse_args()

    jd_text = normalize_text(read_any(args.jd))
    resume_text = normalize_text(read_any(args.resume))

    name, sections = build_sections(jd_text, resume_text)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    build_pdf(args.out, name, sections)
    print("Wrote tailored resume:", args.out)

if __name__ == "__main__":
    main()
