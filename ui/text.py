"""
Purpose: Static copy & disclaimers
"""


DISCLAIMER = (
    "Directional calculator using April 2026 assumptions (pricing + throughput). "
    "Do not treat results as procurement quotes."
)

ASSUMPTIONS = [
    "Thinking tokens are billed and also treated as generation load (output+thinking) for self-host sizing.",
    "Self-host overhead is a fixed multiplier on infra cost.",
    "Throughput figures are approximate and depend on quantisation, batching, sequence length, etc.",
]
