# Severe LVH Risk Calculator

A simplified Python Streamlit calculator for the final nine-predictor L2-regularized logistic regression model.

## Files

- `app.py`: Streamlit interface.
- `model_core.py`: dependency-free probability and nomogram point calculations.
- `model_parameters.json`: fixed coefficients, intercept, and preprocessing parameters.
- `assets/`: publication-ready traditional nomogram.
- `requirements.txt`: Streamlit dependency for cloud deployment.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload all files in this folder.
2. Sign in to `share.streamlit.io` with GitHub.
3. Select **Create app**.
4. Choose the repository, branch, and `app.py` as the entrypoint.
5. Choose an available `streamlit.app` subdomain and deploy.

No patient-level development or validation data are included in this package. The app contains only fixed model parameters and static nomogram assets. All user inputs are used only for the current calculation and are not saved by the app code.

The webpage intentionally displays prediction content only. Random seeds, validation results, model tuning details, and patient-level data are not shown.
