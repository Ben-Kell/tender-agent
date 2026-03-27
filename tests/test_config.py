"""Tests for app.config."""

from app.config import Settings, get_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("GITHUB_REPO", raising=False)
    monkeypatch.delenv("GITHUB_BRANCH", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    settings = Settings()
    assert settings.openai_model == "gpt-4o"
    assert settings.github_repo == "Ben-Kell/tender-agent"
    assert settings.github_branch == "main"
    assert settings.openai_api_key == ""
    assert settings.github_token == ""


def test_settings_override(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo")
    monkeypatch.setenv("GITHUB_REPO", "org/repo")
    monkeypatch.setenv("GITHUB_BRANCH", "develop")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")

    settings = Settings()
    assert settings.openai_api_key == "sk-test"
    assert settings.openai_model == "gpt-4-turbo"
    assert settings.github_repo == "org/repo"
    assert settings.github_branch == "develop"
    assert settings.github_token == "ghp_test"


def test_get_settings_returns_settings_instance():
    # Clear the lru_cache so the test starts from a known state.
    get_settings.cache_clear()
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_settings_is_cached():
    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
