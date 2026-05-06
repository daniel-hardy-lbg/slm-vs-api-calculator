"""
Purpose: All user inputs
"""



import streamlit as st

from calculator.models import WorkloadInputs
from config import DEFAULT_CONTEXT_BUCKET, DEFAULT_OVERHEAD_RATE, DEFAULT_UTILISATION_TARGET

PRESETS = {
    "Simple extraction (no thinking)": (0.50, 0.50, 0.00),
    "Standard chat (some thinking)":   (0.40, 0.30, 0.30),
    "Heavy reasoning (agentic)":       (0.25, 0.25, 0.50),
}


def workload_inputs() -> WorkloadInputs:    
    st.subheader("Inputs")

    total_tokens_millions = st.number_input(
        "Total tokens per day (millions)",
        min_value=1.0,
        value=30.0,
        step=1.0,
        format="%g",
        help="Enter total daily tokens in millions. We'll split them using the profile below.",
    )
    total_tokens_per_day = int(total_tokens_millions * 1_000_000)

    profile = st.selectbox("Workload profile", list(PRESETS.keys()))
    default_alpha, default_beta, default_gamma = PRESETS[profile]

    model_class = st.radio(
        "Model class (drives self-host config)",
        options=["small", "medium", "large"],
        index=0,
        help="Small≈1B, Medium≈8-13B, Large≈70B (TP2).",
        horizontal=True,
    )

    with st.expander("Advanced assumptions", expanded=False):
        context_bucket = st.radio(
            "Context bucket (affects API prices)",
            options=["<=200k", ">200k"],
            index=0 if DEFAULT_CONTEXT_BUCKET == "<=200k" else 1,
            horizontal=True,
        )

        utilisation_target = st.slider(
            "Target GPU utilisation",
            min_value=0.50,
            max_value=0.90,
            value=float(DEFAULT_UTILISATION_TARGET),
            step=0.05,
            help="Used when sizing replica count.",
        )

        overhead_rate = st.slider(
            "Operational overhead rate (added to infra cost)",
            min_value=0.0,
            max_value=1.0,
            value=float(DEFAULT_OVERHEAD_RATE),
            step=0.05,
        )

        st.markdown("**Token split (% of total):**")
        default_alpha_pct = int(default_alpha * 100)
        default_beta_pct = int(default_beta * 100)
        token_split = st.slider(
            "Input / Output % (drag ends)",
            min_value=0,
            max_value=100,
            value=(default_alpha_pct, default_alpha_pct + default_beta_pct),
            step=1,
            help="Adjust the range to set Input and Output %. Thinking % is the remainder to 100%.",
        )
        alpha = token_split[0]
        beta = token_split[1] - token_split[0]
        gamma = 100 - token_split[1]
        st.caption(f"Input: {alpha}% | Output: {beta}% | Thinking: {gamma}%")
        alpha, beta, gamma = alpha/100, beta/100, gamma/100

        # GPU type selection
        # GPU options depend on model class
        if model_class == "large":
            GPU_OPTIONS = [
                ("H100_80GB", "2×H100 80GB (TP2)"),
                ("4xH100_80GB", "4×H100 80GB (TP4)"),
            ]
        else:
            GPU_OPTIONS = [
                ("RTX4090", "RTX 4090"),
                ("A100_80GB", "A100 80GB"),
                ("H100_80GB", "H100 80GB"),
            ]
        gpu_names = [g[0] for g in GPU_OPTIONS]
        gpu_labels = [g[1] for g in GPU_OPTIONS]
        default_gpu = 0
        gpu_idx = st.selectbox(
            "GPU type (self-host)",
            options=list(range(len(GPU_OPTIONS))),
            format_func=lambda i: gpu_labels[i],
            index=default_gpu,
            help="Choose the GPU type for self-hosted cost calculation.",
        )
        gpu_name = gpu_names[gpu_idx]

        # Manual override for number of replicas
        manual_replicas = st.number_input(
            "Manual override: number of replicas",
            min_value=0,
            value=0,
            step=1,
            help="Set to >0 to override automatic replica calculation. This is for testing only and may not be physically achievable!",
        )
        if manual_replicas > 0:
            st.warning("Manual replica override is enabled. This may not be physically achievable and is for testing only.")

    return WorkloadInputs(
        total_tokens_per_day=int(total_tokens_per_day),
        alpha_in=float(alpha),
        beta_out=float(beta),
        gamma_think=float(gamma),
        model_class=(model_class, gpu_name),
        utilisation_target=float(utilisation_target),
        overhead_rate=float(overhead_rate),
        context_bucket=context_bucket,
        # Pass manual_replicas as an extra attribute (will be ignored if not used)
        manual_replicas=int(manual_replicas),
    )
