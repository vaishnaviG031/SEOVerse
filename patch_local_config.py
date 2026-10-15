import re
from pathlib import Path
p = Path(r"C:\Users\DELL\Downloads\youtube_seo_agent_v1_crewai-project\src\youtube_seo_agent\crew.py")
s = p.read_text(encoding="utf-8")
s = s.replace("max_iter=25,", "max_iter=2,")
s, n = re.subn(r'llm=LLM\(\s*model=DEFAULT_MODEL,\s*\)', 'llm=LLM(model=DEFAULT_MODEL, max_tokens=512, temperature=0.2)', s)
s = s.replace('chat_llm=LLM(model=DEFAULT_MODEL)', 'chat_llm=LLM(model=DEFAULT_MODEL, max_tokens=512, temperature=0.2)')
p.write_text(s, encoding="utf-8")
print(f"Updated agent LLM token limits in {n} agents; max_iter is capped at 2.")
