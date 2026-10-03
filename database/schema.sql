-- SkillGap database schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS skills (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,
    category  TEXT NOT NULL,            -- Language, Frontend, Backend, Database, DevOps, Data, Soft Skill...
    aliases   TEXT NOT NULL DEFAULT '', -- comma-separated alternative spellings
    resource  TEXT NOT NULL DEFAULT ''  -- a learning link for the skill
);

CREATE TABLE IF NOT EXISTS job_roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS job_skills (
    role_id    INTEGER NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    skill_id   INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance TEXT NOT NULL CHECK (importance IN ('required','preferred')),
    PRIMARY KEY (role_id, skill_id)
);

CREATE TABLE IF NOT EXISTS analyses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    target        TEXT NOT NULL,       -- role title or "Custom job description"
    match_score   INTEGER NOT NULL,    -- 0-100
    matched_json  TEXT NOT NULL,
    missing_json  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_job_skills_role ON job_skills(role_id);
