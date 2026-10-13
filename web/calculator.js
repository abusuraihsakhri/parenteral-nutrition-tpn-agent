/* Parenteral macronutrient arithmetic only; not a prescription. */
(function (root, factory) {
  const calculator = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = calculator;
  } else {
    root.TPNCalculator = calculator;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function asNonnegativeNumber(name, value, positive) {
    if (typeof value !== "number" || !Number.isFinite(value) ||
        value < 0 || (positive && value === 0)) {
      throw new RangeError(
        name + " must be a finite " + (positive ? "positive" : "non-negative") + " number"
      );
    }
    return value;
  }

  function calculate({weight_kg, energy_kcal, amino_acids_g, lipid_20pct_ml}) {
    const weight = asNonnegativeNumber("weight_kg", weight_kg, true);
    const energy = asNonnegativeNumber("energy_kcal", energy_kcal, true);
    const amino = asNonnegativeNumber("amino_acids_g", amino_acids_g, false);
    const lipid = asNonnegativeNumber("lipid_20pct_ml", lipid_20pct_ml, false);

    // Energy factors: IV dextrose 3.4 kcal/g; amino acids 4 kcal/g;
    // example 20% IV lipid emulsion 2 kcal/mL (product dependent).
    const aminoKcal = amino * 4;
    const lipidKcal = lipid * 2;
    const dextroseKcal = energy - aminoKcal - lipidKcal;
    if (![aminoKcal, lipidKcal, dextroseKcal].every(Number.isFinite)) {
      throw new RangeError("Inputs cause arithmetic overflow");
    }
    if (dextroseKcal < -1e-9) {
      throw new RangeError("Amino-acid and lipid calories exceed the specified energy target");
    }
    const availableDextroseKcal = Math.max(0, dextroseKcal);
    const dextroseG = availableDextroseKcal / 3.4;
    const gir = dextroseG * 1000 / (weight * 1440);
    if (!Number.isFinite(gir)) {
      throw new RangeError("Inputs cause glucose infusion rate overflow");
    }
    return {
      weight_kg: weight,
      energy_kcal: energy,
      amino_acids_g: amino,
      amino_acids_kcal: aminoKcal,
      lipid_20pct_ml: lipid,
      lipid_g: lipid * 0.2,
      lipid_kcal: lipidKcal,
      dextrose_g: dextroseG,
      dextrose_kcal: availableDextroseKcal,
      dextrose_gir_mg_kg_min: gir,
      total_calculated_kcal: aminoKcal + lipidKcal + availableDextroseKcal
    };
  }

  return { calculate };
});
