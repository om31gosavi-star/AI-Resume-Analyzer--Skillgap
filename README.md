# SkillGap – Resume Skill Gap Analyzer

Job seekers often don't know which skills their resume is missing for a given job.
SkillGap compares your resume against a target role (or a pasted job description) and shows:

- a weighted **match score** (required skills count 2x, preferred 1x)
- **missing skills**, required ones first, each with a learning link
- skills you already have, plus other skills detected in your resume
- a saved **history** of past analyses

## Tech stack
| Layer | Tech |
|-------|------|
| Frontend | HTML, CSS, vanilla JavaScript (`frontend/`) |
| Backend | Python 3.9+, Flask REST API (`backend/`) |
| Database | SQLite (`database/`) – schema + seed data for 59 skills and 12 job roles |

## Run it
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open **http://localhost:5000**. The database is created automatically on first run
(or run `python init_db.py` to rebuild it from `database/schema.sql` + `database/seed.sql`).

Run the tests: `python test_app.py`

## Project structure
```
skillgap/
├── backend/
│   ├── app.py            # Flask app + REST endpoints, serves the frontend
│   ├── analyzer.py       # skill extraction + gap/score logic
│   ├── db.py             # SQLite connection and init
│   ├── init_db.py        # rebuild the database
│   ├── test_app.py       # tests
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── database/
    ├── schema.sql        # tables: skills, job_roles, job_skills, analyses
    ├── seed.sql          # skills, roles, role->skill mappings
    └── skillgap.db       # ready-to-use database
```

## API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/roles` | list job roles |
| GET | `/api/skills` | list all known skills |
| POST | `/api/extract-text` | upload PDF/DOCX/TXT (multipart `file`) → plain text |
| POST | `/api/analyze` | body: `resume_text` + (`role_id` or `job_description`) |
| GET | `/api/history` | last 20 analyses |
| DELETE | `/api/history/<id>` | delete one analysis |

## Customising
- Add skills/roles by inserting rows in `database/seed.sql` (or directly in the DB):
  `skills` (with comma-separated `aliases`), `job_roles`, and `job_skills` (`required`/`preferred`).
- Skill detection is dictionary-based (whole-word matching with aliases), so it only recognises skills in the database.
- Scanned/image-only PDFs have no text layer and are not supported.
