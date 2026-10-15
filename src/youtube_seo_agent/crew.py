import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding so emojis never cause 'charmap' codec crashes
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

# Load .env
load_dotenv()


def normalize_model_name(model_name: str) -> str:
    """Normalize the configured model string for CrewAI / LiteLLM."""
    value = (model_name or "gemini/gemini-3.5-flash-lite").strip()
    if not value:
        value = "gemini/gemini-3.5-flash-lite"

    providers = (
        "gemini/",
        "google/",
        "openai/",
        "openrouter/",
        "anthropic/",
        "ollama/",
        "groq/",
        "bedrock/",
        "azure/",
    )
    if any(value.startswith(prefix) for prefix in providers):
        return value

    if value.startswith("gemini-"):
        return f"gemini/{value}"

    return f"gemini/{value}"


DEFAULT_MODEL = normalize_model_name(
    os.getenv("MODEL", "gemini/gemini-3.5-flash-lite")
)

# Optional Serper search tool (enabled only if SERPER_API_KEY is configured)
_serper_key = os.getenv("SERPER_API_KEY", "").strip()
_research_tools = [SerperDevTool()] if _serper_key else []


def _make_llm(max_tokens: int = 4096, temperature: float = 0.4, model_name: str = None) -> LLM:
    """Create a configured CrewAI LLM instance."""
    target_model = normalize_model_name(model_name or os.getenv('MODEL') or DEFAULT_MODEL)
    api_key = None if "ollama" in target_model.lower() else (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return LLM(
        model=target_model,
        api_key=api_key,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=180,
    )


@CrewBase
class YoutubeSeoAgentCrew:
    """YoutubeSeoAgent crew — full 6-agent sequential pipeline."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def youtube_channel_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_channel_analyst"],  # type: ignore[index]
            tools=_research_tools,
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=4096, temperature=0.4),
            verbose=True,
        )

    @agent
    def youtube_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_research_agent"],  # type: ignore[index]
            tools=_research_tools,
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=4096, temperature=0.6),
            verbose=True,
        )

    @agent
    def youtube_competitor_market_research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_competitor_market_research_specialist"],  # type: ignore[index]
            tools=_research_tools,
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=4096, temperature=0.3),
            verbose=True,
        )

    @agent
    def youtube_seo_search_intent_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_seo_search_intent_strategist"],  # type: ignore[index]
            tools=_research_tools,
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=4096, temperature=0.3),
            verbose=True,
        )

    @agent
    def youtube_metadata_ctr_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_metadata_ctr_specialist"],  # type: ignore[index]
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=4096, temperature=0.7),
            verbose=True,
        )

    @agent
    def senior_content_strategy_report_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["senior_content_strategy_report_editor"],  # type: ignore[index]
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=5,
            max_rpm=15,
            max_execution_time=300,
            llm=_make_llm(max_tokens=8192, temperature=0.4),
            verbose=True,
        )

    @task
    def analyze_channel_generate_predictions(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_channel_generate_predictions"],  # type: ignore[index]
            markdown=True,
        )

    @task
    def generate_ai_tools_video_ideas_for_college_students(self) -> Task:
        return Task(
            config=self.tasks_config["generate_ai_tools_video_ideas_for_college_students"],  # type: ignore[index]
            markdown=True,
        )

    @task
    def analyze_competitor_content(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_competitor_content"],  # type: ignore[index]
            markdown=True,
        )

    @task
    def perform_keyword_search_intent_research(self) -> Task:
        return Task(
            config=self.tasks_config["perform_keyword_search_intent_research"],  # type: ignore[index]
            markdown=True,
        )

    @task
    def optimize_video_metadata(self) -> Task:
        return Task(
            config=self.tasks_config["optimize_video_metadata"],  # type: ignore[index]
            markdown=True,
        )

    @task
    def generate_final_youtube_seo_strategy_report(self) -> Task:
        return Task(
            config=self.tasks_config["generate_final_youtube_seo_strategy_report"],  # type: ignore[index]
            markdown=True,
            output_file="reports/latest_report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the YoutubeSeoAgent crew with all 6 stages enabled."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            chat_llm=_make_llm(max_tokens=4096, temperature=0.4),
        )
