"""Skill extraction and gap analysis logic."""
import re

# Short/common English words: only match with the exact capitalisation of the skill name
CASE_SENSITIVE = {"express", "excel", "spring framework", "agile"}

WEIGHTS = {"required": 2, "preferred": 1}


def _pattern(term):
    # Not preceded/followed by letters, digits, + or # (so "Java" won't match "JavaScript")
    return r"(?<![A-Za-z0-9+#])" + re.escape(term) + r"(?![A-Za-z0-9+#])"


def build_matchers(skill_rows):
    """Return [(skill_row, [compiled regex, ...])] for every skill."""
    matchers = []
    for row in skill_rows:
        terms = [row["name"]] + [a.strip() for a in row["aliases"].split(",") if a.strip()]
        regs = []
        for t in terms:
            flags = 0 if t.lower() in CASE_SENSITIVE else re.IGNORECASE
            regs.append(re.compile(_pattern(t), flags))
        matchers.append((row, regs))
    return matchers


def extract_skills(text, matchers):
    """Return the set of skill ids found in text."""
    found = set()
    for row, regs in matchers:
        if any(r.search(text) for r in regs):
            found.add(row["id"])
    return found


def analyze(resume_text, target_skills, matchers):
    """
    target_skills: list of dicts {id, name, category, resource, importance}
    Returns matched / missing lists and a weighted match score (0-100).
    """
    resume_ids = extract_skills(resume_text, matchers)
    matched, missing = [], []
    total = got = 0
    for s in target_skills:
        w = WEIGHTS[s["importance"]]
        total += w
        if s["id"] in resume_ids:
            matched.append(s)
            got += w
        else:
            missing.append(s)
    score = round(100 * got / total) if total else 0
    # Required gaps first - they matter most
    missing.sort(key=lambda s: (s["importance"] != "required", s["name"]))
    matched.sort(key=lambda s: (s["importance"] != "required", s["name"]))
    extra = sorted(
        (r["name"] for r, _ in matchers
         if r["id"] in resume_ids and r["id"] not in {s["id"] for s in target_skills})
    )
    return {"score": score, "matched": matched, "missing": missing, "extra_skills": extra}
