from decimal import Decimal

from agentic_sdlc.application.costs import compute_cost_usd


def test_compute_cost_usd() -> None:
    cost = compute_cost_usd(
        model="claude-sonnet-5-5", input_tokens=1_000, output_tokens=2_000
    )

    assert cost == Decimal("0.022")


def test_compute_cost_usd_unknown_model() -> None:
    cost = compute_cost_usd(model="unknown-model", input_tokens=1, output_tokens=1)

    assert cost is None
