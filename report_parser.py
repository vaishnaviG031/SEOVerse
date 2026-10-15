"""Parser to extract structured data from YouTube SEO Agent reports."""
import re
from typing import Dict, Any, List

def parse_report_to_json(report_text: str, topic: str = "") -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "topic": topic,
        "opportunity_score": None,
        "scorecard": [],
        "growth_benchmarks": {},
        "research": {
            "persona_name": "",
            "demographics": "",
            "emotional_drivers": [],
            "traffic_split": {},
        },
        "prediction_methodology": [],
        "competitor_gaps": [],
        "concepts": [],
        "keywords": {
            "informational": [],
            "tutorial": [],
            "comparison": [],
            "troubleshooting": [],
            "matrix": [],
        },
        "packaging": [],
        "launch_calendar": [],
        "anomalies": [],
        "raw_markdown": report_text,
    }

    if not report_text:
        return data

    # Extract Topic if not provided
    if not topic:
        topic_match = re.search(r"\*\*Topic:\*\*\s*(.+)", report_text)
        if topic_match:
            data["topic"] = topic_match.group(1).strip()

    # Extract Concepts
    concept_blocks = re.findall(r"### Concept \d+:\s*(.+?)(?=\n### Concept \d+:|\n## |\Z)", report_text, re.DOTALL)
    for block in concept_blocks:
        title_line = block.strip().split("\n")[0].strip()
        working_title_match = re.search(r"\* \*\*Working Title:\*\*\s*`?([^`\n]+)`?", block)
        angle_match = re.search(r"\* \*\*Angle:\*\*\s*(.+?)(?=\n\* |\n\n|\Z)", block, re.DOTALL)
        takeaway_match = re.search(r"\* \*\*Target Viewer Takeaway:\*\*\s*(.+?)(?=\n\* |\n\n|\Z)", block, re.DOTALL)
        
        hook_items = re.findall(r"\* `([\d:]+[–\-][\d:]+)`:\s*(.+)", block)
        hook_timeline = [{"time": time_range, "description": desc.strip()} for time_range, desc in hook_items]

        data["concepts"].append({
            "name": title_line,
            "working_title": working_title_match.group(1).strip() if working_title_match else title_line,
            "angle": angle_match.group(1).strip().replace("\n", " ") if angle_match else "",
            "takeaway": takeaway_match.group(1).strip().replace("\n", " ") if takeaway_match else "",
            "hook_timeline": hook_timeline,
            "retention_potential": "Creative hypothesis · not measured"
        })

    # Extract Keywords
    def extract_list_under_header(header_pattern: str, text: str) -> List[str]:
        match = re.search(header_pattern + r"\s*\n((?:\* [^\n]+\n*)+)", text)
        if not match:
            return []
        items = re.findall(r"\* `?([^`\n]+)`?", match.group(1))
        return [item.strip() for item in items if item.strip()]

    data["keywords"]["informational"] = extract_list_under_header(r"#### A\. Informational Intent[^\n]*", report_text)
    data["keywords"]["tutorial"] = extract_list_under_header(r"#### B\. Tutorial & How-To Intent[^\n]*", report_text)
    data["keywords"]["comparison"] = extract_list_under_header(r"#### C\. Comparison Intent[^\n]*", report_text)
    data["keywords"]["troubleshooting"] = extract_list_under_header(r"#### D\. Troubleshooting Intent[^\n]*", report_text)

    # Extract Packaging Studio (Title options, thumbnail specs, description, tags)
    packaging_blocks = re.findall(r"### Concept \d+:[^\n]*\n(.*?)---\n", report_text, re.DOTALL)
    for p_block in packaging_blocks:
        curiosity_match = re.search(r"\* \*Curiosity Hook:\*\s*`([^`]+)`", p_block)
        direct_match = re.search(r"\* \*Direct Value:\*\s*`([^`]+)`", p_block)
        contrarian_match = re.search(r"\* \*Contrarian:\*\s*`([^`]+)`", p_block)
        tags_match = re.search(r"\* \*\*Tags \(\d+\):\*\*\s*`([^`]+)`", p_block)
        overlay_match = re.search(r"Overlay Text:\s*\*\*`([^`]+)`\*\*", p_block)
        desc_match = re.search(r"\* \*\*Optimized Description:\*\*\s*```(?:markdown)?\n(.*?)\n```", p_block, re.DOTALL)

        if curiosity_match or direct_match or tags_match:
            data["packaging"].append({
                "titles": {
                    "curiosity": curiosity_match.group(1).strip() if curiosity_match else "",
                    "direct_value": direct_match.group(1).strip() if direct_match else "",
                    "contrarian": contrarian_match.group(1).strip() if contrarian_match else ""
                },
                "overlay_text": overlay_match.group(1).strip() if overlay_match else "",
                "description": desc_match.group(1).strip() if desc_match else "",
                "tags": [t.strip() for t in tags_match.group(1).split(",") if t.strip()] if tags_match else []
            })


    return data
