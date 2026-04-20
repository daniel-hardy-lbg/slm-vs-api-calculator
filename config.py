"""
Purpose: One place to change global constants
Contains:

Utilisation default (0.75)
Engineering overhead (0.30)
Month length (30)
Token-to-word constants (future)

If a reviewer questions assumptions → point them here.
"""


"""
Global defaults / assumptions.

Keep these conservative and explicit. If someone challenges an assumption,
you can point them here.
"""

DAYS_PER_MONTH = 30
HOURS_PER_MONTH = 24 * DAYS_PER_MONTH  # 720

DEFAULT_UTILISATION_TARGET = 0.75
DEFAULT_OVERHEAD_RATE = 0.30  # engineering/monitoring/redundancy
DEFAULT_CONTEXT_BUCKET = "<=200k"  # or ">200k"

# If user inputs are in "tokens per day" as integers, we convert to millions using:
TOKENS_PER_MILLION = 1_000_000
SECONDS_PER_DAY = 86_400

# Tolerance for alpha+beta+gamma checks
FRACTION_SUM_TOL = 1e-6