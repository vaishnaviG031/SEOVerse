import os

from youtube_seo_agent.crew import DEFAULT_MODEL, YoutubeSeoAgentCrew


def test_crew_uses_supported_default_model():
    crew = YoutubeSeoAgentCrew().crew()
    expected_model = DEFAULT_MODEL

    configured_models = [agent.llm.model for agent in crew.agents]
    assert configured_models
    assert all(model.replace("gemini/", "") == expected_model.replace("gemini/", "") for model in configured_models)
    assert all("gpt-5.6-luna" not in model for model in configured_models)
