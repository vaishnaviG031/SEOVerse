#!/usr/bin/env python
import sys
from youtube_seo_agent.crew import YoutubeSeoAgentCrew


def run():
    """Run the crew."""
    topic = "AI tools for productivity"
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "train", "replay", "test"):
        topic = " ".join(sys.argv[1:])
    elif len(sys.argv) > 2:
        topic = " ".join(sys.argv[2:])
    inputs = {
        "topic": topic,
        "live_context": "",
    }
    result = YoutubeSeoAgentCrew().crew().kickoff(inputs=inputs)
    print("\n--- Strategy Blueprint Output ---\n")
    print(getattr(result, "raw", str(result)))


def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        "topic": "AI tools for productivity",
        "live_context": "",
    }
    try:
        YoutubeSeoAgentCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        YoutubeSeoAgentCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return results."""
    inputs = {
        "topic": "AI tools for productivity",
        "live_context": "",
    }
    try:
        YoutubeSeoAgentCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <run|train|replay|test> [topic]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
