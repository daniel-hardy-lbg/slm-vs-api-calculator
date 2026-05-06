"""
Purpose: Decision logic + comparison
"""

import math
from typing import List, Dict

from config import SECONDS_PER_DAY, HOURS_PER_MONTH, TOKENS_PER_MILLION
from .models import WorkloadInputs, CalcResult
from .pricing import FLASH_PRICES, blended_price_per_1m, api_monthly_cost_usd
from .benchmarks import self_host_config_for


def replicas_required(
    daily_generated_tokens: float,
    throughput_tok_per_s: float,
    utilisation_target: float
) -> int:
    """
    N = ceil( tokens/day / (throughput * 86400 * utilisation_target) )
    """
    capacity_per_replica = throughput_tok_per_s * SECONDS_PER_DAY * utilisation_target
    return max(1, math.ceil(daily_generated_tokens / capacity_per_replica))


def self_host_monthly_cost_usd(
    n_replicas: int,
    gpus_per_replica: int,
    gpu_price_per_hour: float,
) -> float:
    """
    C_gpu_monthly = N * GPUs_per_replica * $/hr * 720
    """
    return n_replicas * gpus_per_replica * gpu_price_per_hour * HOURS_PER_MONTH


def evaluate_workload(inputs: WorkloadInputs, include_debug: bool = False) -> CalcResult:
    """
    Returns a CalcResult suitable for UI display.
    """

    # --- API pricing ---
    pricing = FLASH_PRICES[inputs.context_bucket]
    p_blended = blended_price_per_1m(inputs.alpha_in, inputs.beta_out, inputs.gamma_think, pricing)
    api_monthly = api_monthly_cost_usd(inputs.total_tokens_per_day, p_blended)

    # --- Token breakdown ---
    daily_input_tokens = inputs.alpha_in * inputs.total_tokens_per_day
    daily_output_tokens = inputs.beta_out * inputs.total_tokens_per_day
    daily_thinking_tokens = inputs.gamma_think * inputs.total_tokens_per_day

    # For self-host compute, generation work ~ output + thinking tokens (both consume decode steps).
    daily_generated_tokens = daily_output_tokens + daily_thinking_tokens

    # --- Self-host sizing ---
    if isinstance(inputs.model_class, tuple):
        model_class, gpu_name = inputs.model_class
    else:
        model_class = inputs.model_class
        gpu_name = "RTX4090" if model_class == "small" else ("A100_80GB" if model_class == "medium" else "H100_80GB")

    cfg = self_host_config_for(model_class, gpu_name)
    # Manual override for number of replicas (for testing only)
    manual_replicas = getattr(inputs, "manual_replicas", 0)
    if manual_replicas > 0:
        n = manual_replicas
        manual_warning = True
    else:
        n = replicas_required(daily_generated_tokens, cfg.throughput_tok_per_s, inputs.utilisation_target)
        manual_warning = False

    infra_monthly = self_host_monthly_cost_usd(n, cfg.gpus_per_replica, cfg.gpu_price_per_hour)
    self_host_total = infra_monthly * (1.0 + inputs.overhead_rate)

    # Actual utilisation estimate (based on theoretical max without utilisation_target baked in)
    theoretical_capacity = n * cfg.throughput_tok_per_s * SECONDS_PER_DAY
    actual_util = float(daily_generated_tokens / theoretical_capacity) if theoretical_capacity > 0 else 0.0

    # Break-even total tokens/day using paper equation:
    # T_break_even = (C_selfhost_total * 1,000,000) / (30 * P_blended)
    break_even_tpd = (self_host_total * TOKENS_PER_MILLION) / (30.0 * p_blended) if p_blended > 0 else float("inf")

    # --- Decision ---
    recommendation = "SELF_HOST" if self_host_total < api_monthly else "API"

    # Reasons: keep to 3-5 concise bullets
    reasons = []
    if manual_warning:
        reasons.append("Manual replica override is enabled. This may not be physically achievable and is for testing only.")
    ratio = (api_monthly / self_host_total) if self_host_total > 0 else float("inf")
    reasons: List[str] = []

    reasons.append(f"API monthly ≈ ${api_monthly:,.0f} vs self-host ≈ ${self_host_total:,.0f} (×{ratio:.2f} API/self-host).")
    reasons.append(f"Self-host needs {n} replica(s) of {cfg.name} at target utilisation {inputs.utilisation_target:.0%}.")
    reasons.append(f"Estimated actual utilisation ≈ {actual_util:.0%} (low utilisation = self-host looks worse).")
    reasons.append(f"Break-even total volume ≈ {break_even_tpd/1e6:,.1f}M tokens/day for this profile & assumptions.")

    debug: Dict = {}
    if include_debug:
        debug = {
            "daily_input_tokens": daily_input_tokens,
            "daily_output_tokens": daily_output_tokens,
            "daily_thinking_tokens": daily_thinking_tokens,
            "daily_generated_tokens": daily_generated_tokens,
            "p_blended_per_1m": p_blended,
            "api_pricing": pricing,
            "self_host_config": cfg,
            "infra_monthly": infra_monthly,
        }

    return CalcResult(
        recommendation=recommendation,
        api_monthly_usd=float(api_monthly),
        self_host_monthly_usd=float(self_host_total),
        self_host_monthly_usd_infra_only=float(infra_monthly),
        blended_price_per_1m=float(p_blended),
        replicas_required=int(n),
        estimated_actual_utilisation=float(actual_util),
        break_even_total_tokens_per_day=float(break_even_tpd),
        reasons=reasons,
        debug=debug if include_debug else None,
    )
