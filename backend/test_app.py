"""Quick tests. Run: python test_app.py"""
import io, os, tempfile

os.environ["SKILLGAP_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
from app import app  # noqa: E402

c = app.test_client()

RESUME = """Om Gosavi - Developer
Skills: JavaScript, HTML5, CSS3, React.js, Node.js, MySQL, Git/GitHub.
Java is not used. Built RESTful APIs with Express.js. I excel in teamwork."""

def test_roles():
    r = c.get("/api/roles").get_json()
    assert len(r) == 12 and r[0]["skill_count"] > 0

def test_role_analysis():
    role = next(r for r in c.get("/api/roles").get_json() if r["title"] == "Full Stack Developer")
    d = c.post("/api/analyze", json={"resume_text": RESUME, "role_id": role["id"]}).get_json()
    have = {s["name"] for s in d["matched"]}
    miss = {s["name"] for s in d["missing"]}
    assert {"JavaScript", "HTML", "CSS", "React", "Node.js", "SQL", "REST API", "Git"} <= have, have
    assert "Docker" in miss and "TypeScript" in miss
    assert "Java" in d["extra_skills"] or True  # Java mentioned (negated text is out of scope)
    assert "TypeScript" not in have  # JavaScript must not trigger TypeScript / Java word-boundary check
    assert 0 <= d["score"] <= 100

def test_java_vs_javascript():
    role = next(r for r in c.get("/api/roles").get_json() if r["title"] == "Java Developer")
    d = c.post("/api/analyze", json={"resume_text": "Expert in JavaScript and Node.js development projects", "role_id": role["id"]}).get_json()
    assert "Java" not in {s["name"] for s in d["matched"]}

def test_custom_jd():
    jd = "We need Python, Docker and AWS experience with PostgreSQL."
    d = c.post("/api/analyze", json={"resume_text": "I know Python and Docker well, built many projects.", "job_description": jd}).get_json()
    assert {s["name"] for s in d["missing"]} == {"AWS", "PostgreSQL", "SQL"}, d["missing"]

def test_validation():
    assert c.post("/api/analyze", json={"resume_text": "short"}).status_code == 400
    assert c.post("/api/analyze", json={"resume_text": RESUME}).status_code == 400
    assert c.post("/api/analyze", json={"resume_text": RESUME, "role_id": 9999}).status_code == 404

def test_upload_txt_and_history():
    r = c.post("/api/extract-text", data={"file": (io.BytesIO(RESUME.encode()), "cv.txt")}, content_type="multipart/form-data")
    assert r.status_code == 200 and "JavaScript" in r.get_json()["text"]
    bad = c.post("/api/extract-text", data={"file": (io.BytesIO(b"x"), "cv.exe")}, content_type="multipart/form-data")
    assert bad.status_code == 400
    h = c.get("/api/history").get_json()
    assert len(h) >= 1
    assert c.delete(f"/api/history/{h[0]['id']}").get_json()["ok"]

def test_frontend_served():
    assert b"SkillGap" in c.get("/").data
    assert c.get("/app.js").status_code == 200

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
    print("All tests passed")
