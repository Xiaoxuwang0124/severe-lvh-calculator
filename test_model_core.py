from pathlib import Path

from model_core import calculate_risk, default_values, load_model


APP_DIR = Path(__file__).resolve().parent


def test_default_prediction():
    model = load_model(APP_DIR / "model_parameters.json")
    result = calculate_risk(default_values(model), model)
    assert abs(result["probability"] - 0.1553637840658864) < 1e-12


def test_high_risk_example():
    model = load_model(APP_DIR / "model_parameters.json")
    values = {
        "sex": 1,
        "beta_blocker": 1,
        "raas_inhibitor": 1,
        "erythropoietin": 1,
        "sbp": 180,
        "hemoglobin": 80,
        "total_cholesterol": 3.0,
        "ipth": 800,
        "smr": 25.0,
    }
    result = calculate_risk(values, model)
    assert abs(result["probability"] - 0.9447750415145482) < 1e-12
    assert abs(result["total_points"] - 310.0979210350064) < 1e-10

