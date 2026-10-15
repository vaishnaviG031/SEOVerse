from pathlib import Path

p = Path(__file__).with_name("api_server.py")
s = p.read_text(encoding="utf-8")
old_import = "from dotenv import load_dotenv\n"
new_import = old_import + "from youtube_data import search_youtube, format_youtube_section\n"
if "from youtube_data import search_youtube, format_youtube_section" not in s:
    if old_import not in s:
        raise SystemExit("Could not find dotenv import; no changes made.")
    s = s.replace(old_import, new_import, 1)

old_func = "def run_crew(topic: str) -> str:\n    from youtube_seo_agent.crew import YoutubeSeoAgentCrew\n"
new_func = "def run_crew(topic: str) -> str:\n    # Retrieve real public YouTube results before generating the strategy.\n    youtube_data = search_youtube(topic)\n    from youtube_seo_agent.crew import YoutubeSeoAgentCrew\n"
if "youtube_data = search_youtube(topic)" not in s:
    if old_func not in s:
        raise SystemExit("Could not find run_crew entry point; no changes made.")
    s = s.replace(old_func, new_func, 1)

old_save = '''    report = sanitize_unverified_metrics(report)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(
        f"# YouTube SEO Strategy\\n\\n**Topic:** {topic}\\n\\n"
        f"**Model:** {os.getenv('MODEL', 'ollama/llama3.2:1b')}\\n\\n"
        "**Data note:** Local-model suggestions only; no live YouTube search results, private channel analytics, measured keyword volumes, or rankings were retrieved.\\n\\n"
        f"{report}\\n",
        encoding="utf-8"
    )
'''
new_save = '''    report = sanitize_unverified_metrics(report)
    youtube_section = format_youtube_section(youtube_data)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    data_note = (
        "Live public YouTube video metadata was retrieved using YouTube Data API v3; "
        "keyword search volume, private channel analytics, and future view predictions are not provided."
        if youtube_data.get("connected") and youtube_data.get("videos")
        else "Live YouTube data was not successfully retrieved; report suggestions are not verified live research."
    )
    REPORT_PATH.write_text(
        f"# YouTube SEO Strategy\\n\\n**Topic:** {topic}\\n\\n"
        f"**Model:** {os.getenv('MODEL', 'ollama/llama3.2:1b')}\\n\\n"
        f"**Data note:** {data_note}\\n\\n"
        f"{youtube_section}\\n\\n---\\n\\n{report}\\n",
        encoding="utf-8"
    )
    report = youtube_section + "\\n\\n---\\n\\n" + report
'''
if "youtube_section = format_youtube_section(youtube_data)" not in s:
    if old_save not in s:
        raise SystemExit("Could not find report-save block; no changes made.")
    s = s.replace(old_save, new_save, 1)

p.write_text(s, encoding="utf-8")
print("Backend patched with YouTube Data API retrieval and report section.")
