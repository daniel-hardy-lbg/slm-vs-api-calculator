"""
Purpose: Throughput & GPU constants
"""




"""
Self-host throughput + GPU cost assumptions.

Important: your paper has some internal inconsistencies (e.g. 8B tok/s on 4090).
For the calculator we choose ONE canonical set, explicitly.
"""

from .models import SelfHostConfig, ModelClass

# Hourly prices chosen to match the paper’s monthly costs in Table 6:
# RTX4090: $317/mo => 317/720 = 0.44
# A100:    $1073/mo => 1.49
# H100:    $2153/mo => 2.99

# Model+GPU matrix for throughput, GPUs per replica, and price (from paper)
# Format: (throughput_tok_s, gpus_per_replica, gpu_price_per_hour)
MODEL_GPU_MATRIX = {
    ("small", "RTX4090"):   (8000, 1, 0.44),
    ("small", "A100_80GB"): (12000, 1, 1.49),
    ("small", "H100_80GB"): (18000, 1, 2.99),
    ("medium", "A100_80GB"): (3400, 1, 1.49),
    ("medium", "H100_80GB"): (6000, 1, 2.99),
    ("large", "H100_80GB"):  (1500, 2, 2.99),  # 2xH100 for 70B (TP2)
    ("large", "4xH100_80GB"): (3000, 4, 2.99),  # 4xH100 for 70B (TP4)
}

# Name shown in UI
CONFIG_NAMES = {
    "small": "8B on 1×RTX 4090",
    "medium": "13B on 1×A100 80GB",
    "large": "70B on 2×H100 80GB (TP2)",
}


def self_host_config_for(model_class: str, gpu_name: str) -> SelfHostConfig:
    # Use the model+GPU matrix for throughput, GPUs per replica, and price
    key = (model_class, gpu_name)
    if key not in MODEL_GPU_MATRIX:
        # Fallback: use A100 for medium, H100 for large, 4090 for small
        fallback = {
            "small": (8000, 1, 0.44),
            "medium": (3400, 1, 1.49),
            "large": (1500, 2, 2.99),
        }
        tok_s, gpus_per_replica, gpu_price_per_hour = fallback.get(model_class, (3400, 1, 1.49))
    else:
        tok_s, gpus_per_replica, gpu_price_per_hour = MODEL_GPU_MATRIX[key]
    return SelfHostConfig(
        name=f"{model_class} on {gpu_name}",
        gpu_name=gpu_name,
        gpus_per_replica=gpus_per_replica,
        gpu_price_per_hour=gpu_price_per_hour,
        throughput_tok_per_s=tok_s,
    )
