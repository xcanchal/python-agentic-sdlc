from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ModelPrice:
    input_usd_per_million: Decimal
    output_usd_per_million: Decimal


MODEL_PRICES: dict[str, ModelPrice] = {
    "claude-sonnet-5-5": ModelPrice(
        input_usd_per_million=Decimal(2),
        output_usd_per_million=Decimal(10),
    ),
}
