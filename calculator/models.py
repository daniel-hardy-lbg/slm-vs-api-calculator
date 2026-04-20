""""
Purpose: Pure data structures (optional but clean)
Contains

@dataclass definitions for:

WorkloadInputs
CostResult

Example:
@dataclass
class Workload:
    daily_output_tokens: int
    thinking_ratio: float
    model_class: str
    utilisation: float
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional


ContextBucket = Literal["<=200k", ">200k"]
ModelClass = Literal["small", "medium", "large"]
ProfileMode = Literal["preset", "manual"]


@dataclass(frozen=True)
class WorkloadInputs:
    """
    User-facing inputs.

    We ask for total tokens/day plus a token split (alpha/beta/gamma).
    This matches the paper’s P_blended setup and keeps UI simple.

    total_tokens_per_day = input + output + thinking (combined)
    alpha,beta,gamma are fractions summing to 1.
    """

    total_tokens_per_day: int  # tokens/day
    alpha_in: float            # fraction of total tokens that are input
    beta_out: float            # fraction of total tokens that are output
    gamma_think: float         # fraction of total tokens that are thinking
    model_class: ModelClass
    utilisation_target: float
    overhead_rate: float
    context_bucket: ContextBucket = "<=200k"
    manual_replicas: int = 0


@dataclass(frozen=True)
class ApiPricing:
    """
    Per-1M token prices in USD.
    """
    pin: float       # input price
    pout: float      # output price
    pthink: float    # thinking price


@dataclass(frozen=True)
class SelfHostConfig:
    """
    Canonical self-host configuration chosen by model_class.
    """
    name: str
    gpu_name: str
    gpus_per_replica: int
    gpu_price_per_hour: float
    throughput_tok_per_s: float  # generation throughput (tokens/sec)


@dataclass(frozen=True)
class CalcResult:
    """
    What we return to the UI.
    """
    recommendation: str                 # "API" or "SELF_HOST"
    api_monthly_usd: float
    self_host_monthly_usd: float
    self_host_monthly_usd_infra_only: float
    blended_price_per_1m: float
    replicas_required: int
    estimated_actual_utilisation: float
    break_even_total_tokens_per_day: float
    reasons: List[str]
    debug: Optional[Dict] = None