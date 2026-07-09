"""Scenario loader — reads industrial process definitions from JSON configs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_DIR = Path(__file__).resolve().parent / "config" / "scenarios"


class Scenario:
    """A named industrial process with sensor labels, mimic stages, and thresholds."""

    def __init__(self, path: str | Path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.name: str = data["name"]
        self.description: str = data.get("description", "")
        sensors = data["sensors"]
        self.sensor_keys: tuple = tuple(sensors.keys())
        self.sensor_labels: dict[str, str] = {k: v["label"] for k, v in sensors.items()}
        self.sensor_units: dict[str, str] = {k: v["unit"] for k, v in sensors.items()}
        self.stages: tuple[str, ...] = tuple(data["stages"])
        self.stage_sensor: dict[str, Optional[str]] = {
            stage: data.get("stage_sensor", {}).get(stage) for stage in self.stages
        }
        self.nominal: dict[str, float] = data["nominal"]
        self.fault_targets: dict = data.get("fault_targets", {})
        self.thresholds: dict = data.get("thresholds", {})
        self.fault_explanations: dict[str, str] = data.get("fault_explanations", {})
        self.fault_tuning: dict = data.get("fault_tuning", {})


def list_scenarios(directory: str | Path = DEFAULT_DIR) -> list[dict]:
    _dir = Path(directory)
    if not _dir.exists():
        return []
    results = []
    for f in sorted(_dir.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            results.append({"id": f.stem, "name": data.get("name", f.stem),
                            "description": data.get("description", ""), "path": str(f)})
        except Exception:
            continue
    return results


def load_scenario(scenario_id: str, directory: str | Path = DEFAULT_DIR) -> Optional[Scenario]:
    path = Path(directory) / f"{scenario_id}.json"
    if not path.exists():
        return None
    return Scenario(path)
