# SPDX-License-Identifier: AGPL-3.0-only

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_project_extras_are_declared():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    declared = project.get("project", {}).get("optional-dependencies", {})
    # Scope is project-relative pip installs in this workflow, not arbitrary YAML.
    requested = {
        name.strip()
        for extras in re.findall(r"\bpip\s+install[^\r\n]*?\.\[([^\]\r\n]+)\]", workflow)
        for name in extras.split(",")
    }
    missing = sorted(requested.difference(declared))
    assert not missing, f"CI requests undeclared project extras: {missing}"
