"""Deterministic, non-prescriptive parenteral macronutrient arithmetic.

Energy conversion assumptions:
* Dextrose: 3.4 kcal/g (intravenous).
* Amino acids: 4 kcal/g (accounting convention).
* 20% intravenous lipid emulsion: 2 kcal/mL and 0.2 g lipid/mL.

20% lipid emulsion energy density depends on the specific product; confirm its
label before interpreting an example. This module does not calculate
electrolytes, osmolarity, fluid balance, refeeding risk, or a prescription.
"""

import math
from typing import Dict


class CalculationError(ValueError):
    """Invalid or internally inconsistent macronutrient inputs."""


def _number(name: str, value: float, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalculationError(f"{name} must be a number")
    number = float(value)
    if not math.isfinite(number) or number < 0 or (positive and number == 0):
        condition = "positive" if positive else "non-negative"
        raise CalculationError(f"{name} must be a finite {condition} number")
    return number


def calculate_macronutrients(
    weight_kg: float,
    energy_kcal: float,
    amino_acids_g: float,
    lipid_20pct_ml: float,
) -> Dict[str, float]:
    """Calculate the dextrose needed to balance an already chosen energy target.

    Does NOT select clinical targets or establish whether inputs are safe.
    Energy is kcal/day, amino acids are g/day, lipid is mL/day.
    """
    weight = _number("weight_kg", weight_kg, positive=True)
    energy = _number("energy_kcal", energy_kcal, positive=True)
    amino = _number("amino_acids_g", amino_acids_g)
    lipid = _number("lipid_20pct_ml", lipid_20pct_ml)

    amino_kcal = amino * 4.0
    lipid_kcal = lipid * 2.0
    dextrose_kcal = energy - amino_kcal - lipid_kcal
    if dextrose_kcal < -1e-9:
        raise CalculationError(
            "Amino-acid and lipid calories exceed the specified energy target"
        )

    dextrose_kcal = max(0.0, dextrose_kcal)
    dextrose_g = dextrose_kcal / 3.4
    return {
        "weight_kg": weight,
        "energy_kcal": energy,
        "amino_acids_g": amino,
        "amino_acids_kcal": amino_kcal,
        "lipid_20pct_ml": lipid,
        "lipid_g": lipid * 0.2,
        "lipid_kcal": lipid_kcal,
        "dextrose_g": dextrose_g,
        "dextrose_kcal": dextrose_kcal,
        "dextrose_gir_mg_kg_min": dextrose_g * 1000.0 / (weight * 1440.0),
        "total_calculated_kcal": amino_kcal + lipid_kcal + dextrose_kcal,
    }
