""""
Purpose: API pricing + blended cost
Contains

Gemini Flash prices (constants)
Function to compute blended $/1M tokens
Function to compute monthly API cost

Example responsibilities:

blended_price(alpha, beta, gamma)
api_monthly_cost(tokens_per_day, blended_price)

No GPUs. No utilisation. Just API economics.
"""


"""
API pricing and blended cost computation.
"""

from .models import ApiPricing
from config import TOKENS_PER_MILLION, DAYS_PER_MONTH, FRACTION_SUM_TOL


# Gemini 2.5 Flash prices (USD per 1M tokens) - from the paper
FLASH_PRICES = {
    "<=200k": ApiPricing(pin=0.15, pout=0.60, pthink=0.70),
    ">200k":  ApiPricing(pin=0.30, pout=2.50, pthink=0.70),
}


def validate_fractions(alpha: float, beta: float, gamma: float) -> None:
    s = alpha + beta + gamma
    if abs(s - 1.0) > FRACTION_SUM_TOL:
        raise ValueError(f"alpha+beta+gamma must sum to 1. Got {s:.6f}")


def blended_price_per_1m(alpha: float, beta: float, gamma: float, pricing: ApiPricing) -> float:
    """
    P_blended = alpha*P_in + beta*P_out + gamma*P_think
    """
    validate_fractions(alpha, beta, gamma)
    return (alpha * pricing.pin) + (beta * pricing.pout) + (gamma * pricing.pthink)


def api_monthly_cost_usd(total_tokens_per_day: int, p_blended_per_1m: float) -> float:
    """
    C_api_monthly = T_daily * 30 * P_blended / 1,000,000
    """
    return (total_tokens_per_day / TOKENS_PER_MILLION) * DAYS_PER_MONTH * p_blended_per_1m