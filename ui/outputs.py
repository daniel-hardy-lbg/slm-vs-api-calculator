"""
Purpose: Results rendering
"""


import streamlit as st
from calculator.models import CalcResult


def show_results(res: CalcResult) -> None:

    # Recommendation Card
    if res.recommendation == "API":
        st.markdown("""
            <div style='background-color:#e0f7fa;padding:1.5rem 1rem 1rem 1rem;border-radius:1rem;margin-bottom:1.5rem;'>
                <h3 style='color:#00796b;margin-bottom:0.5rem;'>
                    🤖 Recommendation: <b>Gemini Cortex API</b>
                </h3>
                <span style='color:#555;'>API is more cost-effective for your workload under current assumptions.</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background-color:#f1f8e9;padding:1.5rem 1rem 1rem 1rem;border-radius:1rem;margin-bottom:1.5rem;'>
                <h3 style='color:#33691e;margin-bottom:0.5rem;'>
                    🖥️ Recommendation: <b>Self-Hosted SLMs</b>
                </h3>
                <span style='color:#555;'>Self-hosting is more cost-effective for your workload under current assumptions.</span>
            </div>
        """, unsafe_allow_html=True)

    # Cost Comparison Cards as colored boxes
    c1, c2, c3 = st.columns([1.2,1.2,0.8], gap="large")
    with c1:
        st.markdown(f"""
            <div style='background-color:#e3f2fd;padding:1.2rem 0.5rem 1rem 0.5rem;border-radius:0.9rem;text-align:center;box-shadow:0 2px 8px #e3f2fd;'>
                <span style='font-size:1.1em;color:#1976d2;font-weight:bold;'>Gemini Cortex API</span><br>
                <span style='font-size:2em;font-weight:bold;'>${res.api_monthly_usd:,.0f}</span><br>
                <span style='font-size:1em;color:#555;'>per month</span>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style='background-color:#e8f5e9;padding:1.2rem 0.5rem 1rem 0.5rem;border-radius:0.9rem;text-align:center;box-shadow:0 2px 8px #e8f5e9;'>
                <span style='font-size:1.1em;color:#388e3c;font-weight:bold;'>Self-Hosted SLMs</span><br>
                <span style='font-size:2em;font-weight:bold;'>${res.self_host_monthly_usd:,.0f}</span><br>
                <span style='font-size:1em;color:#555;'>per month</span>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style='background-color:#fff3e0;padding:1.2rem 0.5rem 1rem 0.5rem;border-radius:0.9rem;text-align:center;box-shadow:0 2px 8px #fff3e0;'>
                <span style='font-size:1.1em;color:#f57c00;font-weight:bold;'>Replicas Needed</span><br>
                <span style='font-size:2em;font-weight:bold;'>{res.replicas_required}</span>
            </div>
        """, unsafe_allow_html=True)

    # Move blended price/utilisation lower
    st.markdown("<div style='height:1.5em'></div>", unsafe_allow_html=True)
    st.caption(
        f"Blended API price ≈ ${res.blended_price_per_1m:.3f} per 1M tokens. "
        f"Estimated utilisation ≈ {res.estimated_actual_utilisation:.0%}."
    )

    # Why Section with selective bolding
    st.markdown("<h4 style='margin-top:2rem;'>Why this result?</h4>", unsafe_allow_html=True)
    import re
    def bold_key_results(text):
        # Only bold price, replicas, utilisation, break-even volume
        text = re.sub(r'(\$[\d,]+)', r'<b>\1</b>', text)  # Bold $ amounts
        text = re.sub(r'(\d+ replica\(s\))', r'<b>\1</b>', text)  # Bold replicas
        text = re.sub(r'(\d+% utilisation|utilisation ≈ \d+%)', r'<b>\1</b>', text)  # Bold utilisation
        text = re.sub(r'(\d+\.\d+M tokens\/day|\d+M tokens\/day|break-even total volume ≈ [\d\.]+M tokens\/day)', r'<b>\1</b>', text, flags=re.IGNORECASE)  # Bold break-even volume
        return text
    for r in res.reasons[:5]:
        st.markdown(f"<li style='font-size:1.1em;margin-bottom:0.5em;'>{bold_key_results(r)}</li>", unsafe_allow_html=True)

    # Move calculation details lower
    st.markdown("<div style='height:2em'></div>", unsafe_allow_html=True)
    with st.expander("Show calculation details", expanded=False):
        st.write(f"Infra-only self-host monthly: ${res.self_host_monthly_usd_infra_only:,.0f}")
        st.write(f"Break-even total tokens/day: {res.break_even_total_tokens_per_day/1e6:,.1f}M")
        if res.debug:
            st.json(res.debug)
