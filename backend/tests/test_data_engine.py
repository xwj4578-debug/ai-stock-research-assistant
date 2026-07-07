from backend.app.domain import ResearchEngine
from backend.app.providers import MockMarketProvider
from backend.app.repository import MarketRepository, MemoryCacheRepository
from backend.app.application import WorkspaceService


class FailingProvider(MockMarketProvider):
    name = "failing"

    def get_market_overview(self):
        raise RuntimeError("source unavailable")


def test_repository_falls_back_to_mock_provider():
    repository = MarketRepository(
        provider=FailingProvider(),
        fallback_provider=MockMarketProvider(),
        cache=MemoryCacheRepository(),
        retries=0,
    )

    market = repository.get_market_overview()

    assert market["emotion_score"] >= 0


def test_research_engine_uses_repository_boundary():
    repository = MarketRepository(provider=MockMarketProvider(), cache=MemoryCacheRepository())
    engine = ResearchEngine(repository)

    workspace = engine.build_workspace_model()

    assert workspace["marketPulse"]
    assert workspace["researchQueue"]
    assert workspace["hotSectors"]


def test_workspace_service_exposes_data_engine_metadata():
    service = WorkspaceService(
        engine=ResearchEngine(MarketRepository(provider=MockMarketProvider(), cache=MemoryCacheRepository()))
    )

    workspace = service.build_workspace_v1()

    assert workspace["dataEngine"]["application"] == "WorkspaceService"
    assert workspace["dataEngine"]["domain"] == "ResearchEngine"
    assert workspace["dataEngine"]["repository"] == "MarketRepository"
