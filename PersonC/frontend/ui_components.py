"""Small, reusable Streamlit presentation helpers."""

from __future__ import annotations

from api_client import Diagnosis


def render_diagnosis(st, result: Diagnosis) -> None:
    st.subheader("Diagnosis result")
    st.metric("Confidence", f"{result.confidence:.0%}")
    st.write(f"**Likely condition:** {result.disease}")
    if result.explanation:
        st.write(result.explanation)

    if result.status == "high":
        st.success("High confidence: follow the treatment guidance below.")
        if result.treatment:
            st.info(f"**Treatment guidance:** {result.treatment}")
    elif result.status == "borderline":
        st.warning("Borderline confidence: a few more details are needed.")
        for question in result.questions:
            st.write(f"- {question}")
        if result.treatment:
            st.info(f"**Preliminary guidance:** {result.treatment}")
    else:
        st.error("Low confidence: please consult a local agriculture expert.")
        if result.expert_referral:
            st.info(f"**Expert referral:** {result.expert_referral}")

    st.caption(f"Response source: {result.source}")
