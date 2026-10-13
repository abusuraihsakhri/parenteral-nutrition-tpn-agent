"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {calculate} = require("../web/calculator.js");

test("energy balance and GIR match independently calculated values", () => {
  const result = calculate({
    weight_kg: 70, energy_kcal: 2000, amino_acids_g: 90, lipid_20pct_ml: 250
  });
  assert.equal(result.amino_acids_kcal, 360);
  assert.equal(result.lipid_kcal, 500);
  assert.equal(result.lipid_g, 50);
  assert.equal(result.dextrose_kcal, 1140);
  assert.ok(Math.abs(result.dextrose_g - 1140 / 3.4) < 1e-10);
  assert.ok(Math.abs(result.dextrose_gir_mg_kg_min - ((1140 / 3.4) * 1000 / (70 * 1440))) < 1e-10);
  assert.equal(result.total_calculated_kcal, 2000);
});

test("zero dextrose allowed if all calories allocated to amino acids and lipid", () => {
  assert.equal(calculate({
    weight_kg: 70, energy_kcal: 500, amino_acids_g: 100, lipid_20pct_ml: 50
  }).dextrose_g, 0);
});

test("non-finite, invalid, and impossible inputs are rejected", () => {
  const valid = {weight_kg: 70, energy_kcal: 2000, amino_acids_g: 90, lipid_20pct_ml: 250};
  for (const invalid of [
    {weight_kg: 0}, {weight_kg: -1}, {weight_kg: NaN}, {weight_kg: Infinity},
    {energy_kcal: 0}, {energy_kcal: -1}, {energy_kcal: "2000"},
    {amino_acids_g: -1}, {amino_acids_g: true}, {lipid_20pct_ml: -2},
    {energy_kcal: 100}
  ]) {
    assert.throws(() => calculate({...valid, ...invalid}), RangeError);
  }
});

test("browser implementation is local and contains no backend request", () => {
  const fs = require("node:fs");
  const html = fs.readFileSync("web/index.html", "utf8");
  const app = fs.readFileSync("web/app.js", "utf8");
  assert.doesNotMatch(app, /\bfetch\s*\(/);
  assert.doesNotMatch(app, /innerHTML/);
  assert.match(html, /Content-Security-Policy/);
});
