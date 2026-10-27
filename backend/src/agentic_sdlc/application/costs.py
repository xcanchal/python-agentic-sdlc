from decimal import Decimal

from agentic_sdlc.config.prices import MODEL_PRICES

ONE_MILLION = Decimal(1_000_000)


def compute_cost_usd(
    *, model: str, input_tokens: int, output_tokens: int
) -> Decimal | None:
    """Return the cost of a model call, or None when the model has no price"""
    price = MODEL_PRICES.get(model)
    if price is None:
        return None

    input_cost = input_tokens * price.input_usd_per_million / ONE_MILLION
    output_cost = output_tokens * price.output_usd_per_million / ONE_MILLION
    return input_cost + output_cost
