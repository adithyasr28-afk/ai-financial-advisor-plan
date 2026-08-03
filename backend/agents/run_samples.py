import json
from pathlib import Path
from .system import AGENTS, AgentContext, orchestrate


def main() -> None:
    context = AgentContext.from_project()
    samples = {name: orchestrate(context, name.replace("_", " ")) for name in list(AGENTS) + ["comprehensive report"]}
    output = context.root / "agents" / "samples.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(samples, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"agents": len(AGENTS), "output": str(output)}))


if __name__ == "__main__":
    main()
