from backend.app.domain import RecommendationEngine, RiskEngine, ScoringEngine
from backend.app.domain.config_loader import load_domain_config
from backend.app.domain.ranking import rank_research_queue
from backend.app.domain.research_engine import ResearchEngine
from backend.app.providers import MockMarketProvider
from backend.app.repository import MarketRepository, MemoryCacheRepository


def test_domain_config_loads_yaml_files():
    scoring = load_domain_config("scoring.yaml")
    ranking = load_domain_config("ranking.yaml")
    market_profile = load_domain_config("market-profile.yaml")

    assert scoring["weights"]["market"] > 0
    assert ranking["research_queue"]["limit"] > 0
    assert "cn_a" in market_profile["markets"]


def test_scoring_engine_returns_explainable_details():
    engine = ScoringEngine()
    result = engine.explain_score(
        {
            "overall_score": 90,
            "trend_score": 80,
            "buy_point_score": 70,
            "risk_score": 20,
        },
        {"market_score": 78, "heat_score": 88},
    )

    assert result["totalScore"] == sum(result["details"].values())
    assert set(result["details"]) == {"market", "sector", "trend", "volume", "capital", "risk"}
    assert all(result["reasons"].values())


def test_risk_and_recommendation_read_thresholds_from_yaml():
    risk = RiskEngine()
    recommendation = RecommendationEngine()

    assert risk.level(80) == "High"
    assert recommendation.next_action({"risk_score": 80, "buy_point_score": 90}) == "wait"
    assert recommendation.next_action({"risk_score": 20, "buy_point_score": 80}) == "research"


def test_ranking_is_configuration_driven():
    rows = [
        {"code": "a", "risk_score": 10, "buy_point_score": 20, "heat_score": 20, "overall_score": 20},
        {"code": "b", "risk_score": 80, "buy_point_score": 90, "heat_score": 90, "overall_score": 90},
    ]

    ranked = rank_research_queue(rows)

    assert ranked[0]["code"] == "b"


def test_research_engine_adds_score_details_to_queue():
    repository = MarketRepository(provider=MockMarketProvider(), cache=MemoryCacheRepository())
    engine = ResearchEngine(repository)

    workspace = engine.build_workspace_model()
    first = workspace["researchQueue"][0]

    assert "research_score" in first
    assert "score_details" in first
    assert first["score_details"]["details"]
