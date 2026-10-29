"""Pure-Python calculation core for the severe LVH risk calculator."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping


def load_model(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def logistic(linear_predictor: float) -> float:
    if linear_predictor >= 0:
        z = math.exp(-linear_predictor)
        return 1.0 / (1.0 + z)
    z = math.exp(linear_predictor)
    return z / (1.0 + z)


def default_values(model: Mapping[str, Any]) -> dict[str, float]:
    return {
        predictor["key"]: float(predictor["default"])
        for predictor in model["predictors"]
    }


def calculate_risk(
    values: Mapping[str, float], model: Mapping[str, Any]
) -> dict[str, Any]:
    linear_predictor = float(model["intercept_original"])
    total_points = 0.0
    contributions: list[dict[str, Any]] = []

    for predictor in model["predictors"]:
        key = predictor["key"]
        value = float(values[key])
        raw_contribution = float(predictor["coefficient_original"]) * value
        points = (
            raw_contribution - float(predictor["contribution_min"])
        ) / float(model["point_scale"])
        linear_predictor += raw_contribution
        total_points += points
        contributions.append(
            {
                "key": key,
                "label": predictor["label"],
                "value": value,
                "points": points,
            }
        )

    return {
        "probability": logistic(linear_predictor),
        "linear_predictor": linear_predictor,
        "total_points": total_points,
        "contributions": contributions,
    }


def outside_central_range(
    values: Mapping[str, float], model: Mapping[str, Any]
) -> list[str]:
    outside = []
    for predictor in model["predictors"]:
        if predictor["type"] == "binary":
            continue
        value = float(values[predictor["key"]])
        if value < float(predictor["nomogram_min"]) or value > float(
            predictor["nomogram_max"]
        ):
            outside.append(predictor["label"])
    return outside

