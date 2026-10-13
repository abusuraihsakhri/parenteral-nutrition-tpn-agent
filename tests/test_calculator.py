"""Non-prescriptive PN arithmetic regression tests."""
import math
import pytest

from parenteral_nutrition_tpn_agent.calculator import (
    CalculationError,
    calculate_macronutrients,
)


def test_example_and_energy_conservation():
    values = calculate_macronutrients(70, 2000, 90, 250)
    assert values["amino_acids_kcal"] == 360
    assert values["lipid_kcal"] == 500
    assert values["lipid_g"] == 50
    assert values["dextrose_kcal"] == 1140
    assert values["dextrose_g"] == pytest.approx(1140 / 3.4)
    assert values["dextrose_gir_mg_kg_min"] == pytest.approx(
        (1140 / 3.4) * 1000 / (70 * 1440)
    )
    assert values["total_calculated_kcal"] == pytest.approx(2000)


def test_exact_energy_budget_allows_zero_dextrose():
    result = calculate_macronutrients(60, 400, 100, 0)
    assert result["dextrose_g"] == 0


@pytest.mark.parametrize("values", [
    (0, 2000, 90, 250),
    (-1, 2000, 90, 250),
    (70, 0, 90, 250),
    (70, 2000, -1, 250),
    (70, 2000, 90, -1),
    (70, 100, 90, 250),
    (float("nan"), 2000, 90, 250),
    (70, float("inf"), 90, 250),
    (70, 2000, float("-inf"), 250),
    (70, 2000, True, 250),
    (70, "2000", 90, 250),
])
def test_rejects_invalid_or_inconsistent_inputs(values):
    with pytest.raises(CalculationError):
        calculate_macronutrients(*values)
