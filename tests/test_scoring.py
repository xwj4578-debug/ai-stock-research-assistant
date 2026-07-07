from app.data import COMPANIES
from app.company_profile import fetch_company_profile
from app.research import build_research_report
from app.scoring import WEIGHTS, score_company


def test_score_has_transparent_weighted_items():
    score = score_company(COMPANIES["601138"])

    assert score["total"] == sum(item["score"] for item in score["items"])
    assert {item["name"] for item in score["items"]} == set(WEIGHTS)
    assert all(item["score"] <= item["max"] for item in score["items"])
    assert all(item["reasons"] for item in score["items"])


def test_industrial_fulian_is_researchable_sample():
    score = score_company(COMPANIES["601138"])

    assert score["total"] >= 75
    assert "基本面" in score["verdict"]


def test_leon_micro_is_available():
    company = COMPANIES["605358"]
    score = score_company(company)

    assert company.name == "立昂微"
    assert "半导体" in company.concepts
    assert score["total"] > 0


def test_research_report_for_known_sample():
    report = build_research_report("605358")

    assert report["code"] == "605358"
    assert report["name"] == "立昂微"
    assert report["summary"]
    assert report["score"]["items"]


def test_company_profile_for_jingfang_technology():
    profile = fetch_company_profile("603005")

    assert profile
    assert "封装" in profile["business_summary"]
    assert profile["products"]
