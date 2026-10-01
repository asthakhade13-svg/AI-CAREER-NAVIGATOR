import sys
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("RUNNING COMPREHENSIVE BACKEND VERIFICATION SUITE")
    print("==================================================")

    tests_passed = 0
    total_tests = 0

    # 1. Health Check
    total_tests += 1
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. Root & Health API Check")
    tests_passed += 1

    # 2. Roadmap Subtask Toggle
    total_tests += 1
    res = client.post("/api/v1/roadmap/subtask/toggle", json={
        "student_id": "test_student_01",
        "track_key": "webdev",
        "subtask_id": "webdev_s0_t0",
        "subtask_text": "HTML5 Semantic Tags & Page Layout",
        "is_completed": True
    })
    assert res.status_code == 200 and res.json().get("success"), f"Subtask toggle failed: {res.text}"
    print("[PASS] 2. Roadmap Subtask Toggle")
    tests_passed += 1

    # 3. Roadmap Subtasks Query
    total_tests += 1
    res = client.get("/api/v1/roadmap/subtasks/test_student_01?track_key=webdev")
    assert res.status_code == 200 and "webdev_s0_t0" in res.json().get("completedIds", []), f"Subtask query failed: {res.text}"
    print("[PASS] 3. Roadmap Subtasks Retrieval")
    tests_passed += 1

    # 4. Dynamic Leaderboard
    total_tests += 1
    res = client.get("/api/v1/progress/leaderboard?college=OIST&branch=CSE")
    assert res.status_code == 200 and len(res.json().get("leaderboard", [])) > 0, f"Leaderboard failed: {res.text}"
    print("[PASS] 4. Dynamic Real-User Leaderboard")
    tests_passed += 1

    # 5. Quiz Attempt Logging
    total_tests += 1
    res = client.post("/api/v1/quiz/log-attempt", json={
        "student_id": "test_student_01",
        "track_key": "webdev",
        "score": 95,
        "total_questions": 10,
        "correct_answers": 9,
        "time_taken_sec": 110
    })
    assert res.status_code == 200 and res.json().get("success"), f"Quiz attempt log failed: {res.text}"
    print("[PASS] 5. Quiz Attempt Logging")
    tests_passed += 1

    # 6. Quiz History
    total_tests += 1
    res = client.get("/api/v1/quiz/history/test_student_01")
    assert res.status_code == 200 and len(res.json().get("history", [])) > 0, f"Quiz history failed: {res.text}"
    print("[PASS] 6. Quiz Multi-Attempt History")
    tests_passed += 1

    # 7. Certificate Generation & Verification
    total_tests += 1
    res = client.post("/api/v1/certificates/generate", json={
        "student_id": "test_student_01",
        "student_name": "Test Student",
        "track_key": "webdev",
        "score_percentage": 95
    })
    assert res.status_code == 200 and res.json().get("success"), f"Certificate generation failed: {res.text}"
    cert_id = res.json()["certificate"]["certificateId"]
    print(f"[PASS] 7. Certificate Generation (ID: {cert_id})")
    tests_passed += 1

    # 8. Certificate PDF Printable Download Route
    total_tests += 1
    res = client.get(f"/api/v1/certificates/download-pdf/{cert_id}")
    assert res.status_code == 200 and "Certificate of Completion" in res.text, f"PDF Download failed: {res.text}"
    print("[PASS] 8. Certificate Printable PDF Generator Route")
    tests_passed += 1

    # 9. Study Logger
    total_tests += 1
    res = client.post("/api/v1/progress/study-log", json={
        "student_id": "test_student_01",
        "day_name": "Mon",
        "hours_spent": 2.5
    })
    assert res.status_code == 200 and res.json().get("success"), f"Study log failed: {res.text}"
    print("[PASS] 9. Study Stopwatch Logger")
    tests_passed += 1

    # 10. Live Activity Stream
    total_tests += 1
    res = client.get("/api/v1/progress/activity/test_student_01")
    assert res.status_code == 200 and len(res.json().get("activities", [])) > 0, f"Activity stream failed: {res.text}"
    print("[PASS] 10. Live Activity Stream")
    tests_passed += 1

    # 11. Capstone Repository Verification
    total_tests += 1
    res = client.post("/api/v1/projects/verify-repo", json={
        "student_id": "test_student_01",
        "project_id": "p1",
        "github_url": "https://github.com/torvalds/linux"
    })
    assert res.status_code == 200 and res.json().get("success"), f"Repo verify failed: {res.text}"
    print("[PASS] 11. Capstone Repository Verification")
    tests_passed += 1

    # 12. ICS Calendar Scheduler
    total_tests += 1
    res = client.get("/api/v1/roadmap/export-ics/aiml")
    assert res.status_code == 200 and "BEGIN:VCALENDAR" in res.text, f"ICS export failed: {res.text}"
    print("[PASS] 12. ICS Calendar Scheduler")
    tests_passed += 1

    print("==================================================")
    print(f"ALL TESTS PASSED: {tests_passed}/{total_tests} (100%)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
