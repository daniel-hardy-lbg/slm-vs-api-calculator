"""
Think of app.py as glue code only.
"""

import streamlit as st

from ui.inputs import workload_inputs
from ui.outputs import show_results
from ui.text import DISCLAIMER
from calculator.decision import evaluate_workload


def main() -> None:
    st.set_page_config(
        page_title="Self-host vs API Calculator",
        page_icon="💡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom background color using markdown
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # Sidebar with clear disclaimer and info
    with st.sidebar:
        st.markdown("# Self-Hosted SLMs vs Gemini Cortex API")
        st.warning("""
**Early version – for directional guidance only!**

This calculator uses April 2026 pricing and throughput assumptions. Results are not procurement quotes or guarantees. Always validate with your vendor and engineering team before making decisions.

**Assumptions:**
- Model throughput and costs are approximate and may vary in production.
- Overheads and utilisation are based on typical values, not tailored to your infra.
- API and self-hosted costs are compared on a like-for-like basis, but real-world factors may differ.
        """, icon="⚠️")

    st.title("💡 Self-Hosted SLMs vs Gemini Cortex API Calculator")
    st.divider()

    st.markdown("### 1. Enter Workload Details")
    with st.container():
        with st.form("workload_form"):
            inputs = workload_inputs()
            submitted = st.form_submit_button("🚀 Calculate")

    st.divider()
    if submitted:
        st.markdown("### 2. Results")
        with st.container():
            res = evaluate_workload(inputs, include_debug=False)
            show_results(res)


if __name__ == "__main__":
    main()
