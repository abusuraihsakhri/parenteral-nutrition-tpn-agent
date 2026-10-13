"use strict";

const form = document.querySelector("#pn-form");
const results = document.querySelector("#results");
const errorNode = document.querySelector("#form-error");

function entry(label, value, unit) {
  const card = document.createElement("div");
  card.className = "result-item";
  const description = document.createElement("p");
  description.className = "metric-label";
  description.textContent = label;
  const result = document.createElement("div");
  result.className = "metric-value";
  result.append(document.createTextNode(value + " "));
  const suffix = document.createElement("span");
  suffix.textContent = unit;
  result.append(suffix);
  card.append(description, result);
  return card;
}

function render(calculated) {
  const fragment = document.createDocumentFragment();
  const hero = document.createElement("div");
  hero.className = "result-hero";
  const label = document.createElement("p");
  label.className = "metric-label";
  label.textContent = "Remaining dextrose";
  const value = document.createElement("div");
  value.className = "metric-value";
  value.textContent = calculated.dextrose_g.toFixed(1) + " g/day";
  hero.append(label, value);

  const grid = document.createElement("div");
  grid.className = "result-grid";
  grid.append(
    entry("Dextrose energy", calculated.dextrose_kcal.toFixed(0), "kcal"),
    entry("Glucose infusion rate", calculated.dextrose_gir_mg_kg_min.toFixed(2), "mg/kg/min"),
    entry("Amino-acid energy", calculated.amino_acids_kcal.toFixed(0), "kcal"),
    entry("Lipid energy", calculated.lipid_kcal.toFixed(0), "kcal"),
    entry("Lipid mass (20%)", calculated.lipid_g.toFixed(1), "g"),
    entry("Total calculated energy", calculated.total_calculated_kcal.toFixed(0), "kcal")
  );
  fragment.append(hero, grid);
  results.replaceChildren(fragment);
}

function calculateFromForm() {
  errorNode.hidden = true;
  errorNode.textContent = "";
  if (!form.reportValidity()) {
    results.replaceChildren();
    return;
  }
  try {
    const read = name => {
      const control = form.elements.namedItem(name);
      if (!control || control.value.trim() === "") {
        throw new RangeError("All fields are required");
      }
      return Number(control.value);
    };
    render(window.TPNCalculator.calculate({
      weight_kg: read("weight_kg"),
      energy_kcal: read("energy_kcal"),
      amino_acids_g: read("amino_acids_g"),
      lipid_20pct_ml: read("lipid_20pct_ml")
    }));
  } catch (error) {
    results.replaceChildren();
    errorNode.textContent = error.message || "Unable to calculate these values.";
    errorNode.hidden = false;
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  calculateFromForm();
});
form.addEventListener("reset", () => {
  requestAnimationFrame(calculateFromForm);
});
calculateFromForm();
