from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from model_core import calculate_risk, default_values, load_model, outside_central_range


APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "model_parameters.json"
NOMOGRAM_PNG = APP_DIR / "assets" / "traditional_nomogram.png"
NOMOGRAM_PDF = APP_DIR / "assets" / "traditional_nomogram.pdf"
EXPECTED_DEFAULT_PROBABILITY = 0.1553637840658864


st.set_page_config(
    page_title="Severe LVH Risk Calculator for Patients Receiving Maintenance Dialysis",
    page_icon="♥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def get_model():
    model = load_model(MODEL_PATH)
    default_result = calculate_risk(default_values(model), model)
    if abs(default_result["probability"] - EXPECTED_DEFAULT_PROBABILITY) > 1e-12:
        raise RuntimeError("The calculator model did not pass its numerical self-test.")
    return model


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
          --navy: #17324d;
          --deep: #0d2438;
          --ink: #253947;
          --muted: #687d8b;
          --cream: #f4f2ec;
          --accent: #d8563a;
          --teal: #1b7775;
        }
        [data-testid="stAppViewContainer"] {
          background: var(--cream);
        }
        [data-testid="stHeader"] {
          background: transparent;
        }
        .block-container {
          max-width: 1180px;
          padding-top: 1.4rem;
          padding-bottom: 4rem;
        }
        .hero {
          background: radial-gradient(circle at 82% 20%, #29556a 0%, transparent 32%),
                      linear-gradient(125deg, var(--deep), var(--navy));
          color: white;
          border-radius: 24px;
          padding: 45px 48px;
          margin-bottom: 24px;
          box-shadow: 0 18px 50px rgba(16, 43, 63, 0.13);
        }
        .hero h1 {
          font-family: Georgia, serif;
          font-size: clamp(3rem, 6vw, 5.4rem);
          line-height: .92;
          letter-spacing: -.045em;
          font-weight: 500;
          margin: 0 0 20px;
        }
        .hero h1 span {
          display: block;
          color: #a9ddd8;
          font-size: clamp(1.7rem, 3vw, 3rem);
          line-height: 1.08;
          letter-spacing: -.03em;
          margin-top: .3em;
        }
        .hero p { color: #d8e6eb; font-size: 1.05rem; max-width: 650px; margin: 0; }
        .section-label {
          color: var(--accent);
          font-size: .76rem;
          letter-spacing: .15em;
          font-weight: 800;
          margin: 0 0 4px;
        }
        .section-title {
          color: var(--navy);
          font-family: Georgia, serif;
          font-size: 2rem;
          line-height: 1.05;
          margin: 0 0 8px;
        }
        .section-copy { color: var(--muted); margin-bottom: 22px; }
        .result-card {
          color: white;
          background: linear-gradient(145deg, var(--deep), var(--navy));
          border-radius: 22px;
          padding: 30px;
          margin: 0 0 20px;
          box-shadow: 0 18px 50px rgba(16, 43, 63, 0.13);
        }
        .result-kicker {
          color: #8dd7d1;
          font-size: .74rem;
          letter-spacing: .15em;
          font-weight: 800;
        }
        .risk-value {
          font-family: Georgia, serif;
          font-size: clamp(4rem, 8vw, 6rem);
          line-height: .95;
          letter-spacing: -.06em;
          margin-top: 8px;
        }
        .risk-caption { color: #bdced7; font-size: .86rem; }
        .risk-track { height: 11px; background: rgba(255,255,255,.15); border-radius: 99px; margin: 24px 0 5px; overflow: hidden; }
        .risk-fill { height: 100%; background: linear-gradient(90deg, #74c8c1, #f1876f); border-radius: 99px; }
        .risk-scale { display: flex; justify-content: space-between; color: #aebfc8; font-size: .7rem; }
        .points-box {
          margin-top: 20px;
          border: 1px solid rgba(255,255,255,.13);
          background: rgba(255,255,255,.05);
          border-radius: 12px;
          padding: 13px 15px;
        }
        .points-box span { color: #adbec8; font-size: .74rem; display: block; }
        .points-box strong { font-size: 1.2rem; }
        .contribution-card {
          background: white;
          border-radius: 22px;
          padding: 26px;
          box-shadow: 0 18px 50px rgba(16, 43, 63, 0.09);
        }
        .contribution-row {
          display: grid;
          grid-template-columns: 150px 1fr 38px;
          gap: 9px;
          align-items: center;
          margin: 12px 0;
        }
        .contribution-name {
          color: var(--navy);
          font-size: .75rem;
          font-weight: 700;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .contribution-track { height: 8px; background: #e9eff1; border-radius: 99px; overflow: hidden; }
        .contribution-fill { height: 100%; background: var(--teal); border-radius: 99px; }
        .contribution-points { text-align: right; color: var(--muted); font-size: .72rem; }
        .nomogram-card {
          background: white;
          border-radius: 22px;
          padding: 28px;
          margin-top: 28px;
          box-shadow: 0 18px 50px rgba(16, 43, 63, 0.09);
        }
        .footer-note { color: var(--muted); font-size: .78rem; text-align: center; margin-top: 30px; }
        div[data-testid="stNumberInput"] label, div[data-testid="stRadio"] label {
          color: var(--navy);
          font-weight: 700;
        }
        div[data-testid="stAlert"] { border-radius: 12px; }
        @media (max-width: 720px) {
          .hero { padding: 34px 25px; }
          .contribution-row { grid-template-columns: 110px 1fr 34px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def binary_input(predictor):
    labels = predictor["categories"]
    default_index = int(round(float(predictor["default"])))
    selected = st.radio(
        predictor["label"],
        options=[0, 1],
        index=default_index,
        format_func=lambda value: labels[value],
        horizontal=True,
        key=f"input_{predictor['key']}",
    )
    return float(selected)


def continuous_input(predictor):
    decimals = int(predictor["decimals"])
    observed_range = float(predictor["observed_max"]) - float(predictor["observed_min"])
    step = 1.0 if decimals == 0 else max(0.1, round(observed_range / 400.0, 1))
    label = predictor["label"]
    if predictor["unit"]:
        label += f" ({predictor['unit']})"
    return float(
        st.number_input(
            label,
            min_value=float(predictor["observed_min"]),
            max_value=float(predictor["observed_max"]),
            value=float(predictor["default"]),
            step=float(step),
            format="%.0f" if decimals == 0 else "%.1f",
            key=f"input_{predictor['key']}",
        )
    )


def contribution_html(contributions):
    rows = []
    for item in contributions:
        width = max(0.0, min(100.0, float(item["points"])))
        rows.append(
            f"""
            <div class="contribution-row">
              <span class="contribution-name" title="{html.escape(item['label'])}">{html.escape(item['label'])}</span>
              <div class="contribution-track"><div class="contribution-fill" style="width:{width:.2f}%"></div></div>
              <span class="contribution-points">{item['points']:.0f}</span>
            </div>
            """
        )
    return "".join(rows)


def main():
    inject_styles()
    model = get_model()

    st.markdown(
        """
        <section class="hero">
          <h1>Severe LVH Risk Calculator<span>for Patients Receiving Maintenance Dialysis</span></h1>
          <p>This calculator estimates the probability of severe left ventricular hypertrophy in adult patients receiving maintenance hemodialysis or peritoneal dialysis.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">DYNAMIC NOMOGRAM</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Enter the patient’s values</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">输入9个临床变量后，预测概率和积分会自动更新。</p>', unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92], gap="large")
    values = {}
    with left:
        st.markdown('<p class="section-label">PATIENT INPUTS</p>', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Nine predictors</h2>', unsafe_allow_html=True)
        binary_predictors = [p for p in model["predictors"] if p["type"] == "binary"]
        continuous_predictors = [p for p in model["predictors"] if p["type"] != "binary"]

        binary_columns = st.columns(2)
        for index, predictor in enumerate(binary_predictors):
            with binary_columns[index % 2]:
                values[predictor["key"]] = binary_input(predictor)

        for predictor in continuous_predictors:
            values[predictor["key"]] = continuous_input(predictor)

        outside = outside_central_range(values, model)
        if outside:
            st.warning(
                "These values are outside the main range of the training data: "
                + ", ".join(outside)
                + "."
            )

    result = calculate_risk(values, model)
    probability_percent = result["probability"] * 100.0
    with right:
        st.markdown(
            f"""
            <section class="result-card">
              <div class="result-kicker">PREDICTED RISK</div>
              <div class="risk-value">{probability_percent:.1f}%</div>
              <div class="risk-caption">predicted probability of severe LVH</div>
              <div class="risk-track"><div class="risk-fill" style="width:{max(0, min(100, probability_percent)):.2f}%"></div></div>
              <div class="risk-scale"><span>0%</span><span>100%</span></div>
              <div class="points-box"><span>Total nomogram points</span><strong>{result['total_points']:.1f}</strong></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <section class="contribution-card">
              <p class="section-label">LIVE POINTS</p>
              <h2 class="section-title">Dynamic nomogram</h2>
              {contribution_html(result['contributions'])}
            </section>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<section class="nomogram-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">TRADITIONAL NOMOGRAM</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Static nomogram</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">Locate each value, add the points, and convert the total points to predicted risk.</p>', unsafe_allow_html=True)
    st.image(str(NOMOGRAM_PNG), use_container_width=True)
    with NOMOGRAM_PDF.open("rb") as handle:
        st.download_button(
            "Download nomogram (PDF)",
            data=handle.read(),
            file_name="Severe_LVH_Traditional_Nomogram.pdf",
            mime="application/pdf",
            use_container_width=False,
        )
    st.markdown('</section>', unsafe_allow_html=True)
    st.markdown('<p class="footer-note">For research use only.</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
