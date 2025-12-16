#!/usr/bin/env python3
"""
============================================================================
DEMO: Single City Health Impact Assessment using NDVI and Epidemiological Data
Based on the global-ndvi-pop project methodology
============================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: Load epidemiological dose-response parameters
# ============================================================================
# Based on meta-analysis of green space and mortality reduction
# Source: Rojas et al. meta-analysis

print("\n" + "="*70)
print("HEALTH IMPACT ASSESSMENT: Urban Greening & Mortality Reduction")
print("="*70 + "\n")

# Risk ratios for all-cause non-accidental mortality
# These represent the reduction in mortality risk for each 0.1 unit increase in NDVI

rr_params = pd.DataFrame({
    'param': ['point_estimate', 'strong_limit', 'weak_limit'],
    'risk_ratio': [0.96, 0.94, 0.97],
    'description': [
        'Mean effect from meta-analysis',
        'Strong limit (conservative estimate)',
        'Weak limit (optimistic estimate)'
    ]
})

print("Epidemiological Risk Ratios (Dose-Response):")
print(rr_params.to_string(index=False))
print("\nInterpretation: A 0.1 increase in NDVI is associated with a ~4% reduction in mortality risk\n")

# ============================================================================
# STEP 2: Create demo data for a single city (New York City)
# ============================================================================

print("-" * 70)
print("CREATING DEMO CITY DATA: New York City")
print("-" * 70 + "\n")

# Set random seed for reproducibility
np.random.seed(42)

# Create synthetic NYC data with NDVI and population distribution
n_pixels = 100

# NDVI values (range 0-1, higher = more vegetation)
# Simulate realistic distribution: many low NDVI (concrete/built-up), fewer high NDVI (parks)
ndvi_low = np.random.uniform(0.2, 0.4, 30)      # 30% low NDVI (built-up)
ndvi_mid = np.random.uniform(0.4, 0.6, 40)      # 40% medium NDVI
ndvi_high = np.random.uniform(0.6, 0.8, 30)     # 30% high NDVI (parks/forests)
ndvi_current = np.sort(np.concatenate([ndvi_low, ndvi_mid, ndvi_high]))

# Population density (inverse relationship: high density in low NDVI areas)
population_density = np.array(
    [5000] * 30 +      # 30% low NDVI, high density (dense urban)
    [3000] * 40 +      # 40% medium NDVI, medium density
    [2000] * 30        # 30% high NDVI, lower density (parks)
)

# Create dataframe
city_data = pd.DataFrame({
    'city_name': 'New York City',
    'country': 'United States',
    'biome': 'Temperate broadleaf and mixed forests',
    'pixel_id': range(1, n_pixels + 1),
    'ndvi_current': ndvi_current,
    'population_density': population_density
})

# Add population category for stratification
city_data['pop_category'] = pd.cut(
    city_data['population_density'],
    bins=[0, 500, 2500, 5000, 10000],
    labels=['1-500', '501-2500', '2501-5000', '5001+']
)

print("Sample of city data:")
print(city_data.head(10).to_string(index=False))

print("\nSummary Statistics:")
print(city_data[['ndvi_current', 'population_density']].describe().to_string())

# ============================================================================
# STEP 3: Calculate NDVI targets (tertile approach)
# ============================================================================

print("\n" + "-" * 70)
print("NDVI TERTILE ANALYSIS")
print("-" * 70 + "\n")

q33 = city_data['ndvi_current'].quantile(0.33)
q66 = city_data['ndvi_current'].quantile(0.67)
q_max = city_data['ndvi_current'].max()

print(f"NDVI Tertiles (Current):")
print(f"  Bottom tertile (0-33%):     {city_data['ndvi_current'].min():.3f} - {q33:.3f}")
print(f"  Middle tertile (33-67%):    {q33:.3f} - {q66:.3f}")
print(f"  Top tertile (67-100%):      {q66:.3f} - {q_max:.3f}")

# Define tertile groups
def assign_tertile(ndvi):
    if ndvi <= q33:
        return 'bottom'
    elif ndvi <= q66:
        return 'middle'
    else:
        return 'top'

city_data['ndvi_tertile'] = city_data['ndvi_current'].apply(assign_tertile)

# Create greening scenario: boost low/medium NDVI areas to top tertile
target_ndvi = q_max * 0.90  # 90% of maximum NDVI

city_data['ndvi_greened'] = city_data.apply(
    lambda row: target_ndvi if row['ndvi_tertile'] in ['bottom', 'middle'] else row['ndvi_current'],
    axis=1
)

city_data['ndvi_change'] = city_data['ndvi_greened'] - city_data['ndvi_current']

# Summary by tertile
tertile_summary = city_data[city_data['ndvi_change'] > 0].groupby('ndvi_tertile').agg({
    'ndvi_current': ['count', 'mean'],
    'ndvi_greened': 'mean',
    'ndvi_change': 'mean'
}).round(3)

print(f"\nGREENING SCENARIO: Increase areas in bottom/middle tertiles to {target_ndvi:.2f}")
print("\nNDVI Changes by Tertile:")
print(tertile_summary.to_string())

# ============================================================================
# STEP 4: Health Impact Calculations
# ============================================================================

print("\n" + "-" * 70)
print("HEALTH IMPACT CALCULATIONS")
print("-" * 70 + "\n")

# Demo mortality parameters (based on WHO/GBD data for developed countries)
baseline_mortality_rate = 0.006  # 6 per 1000 adults aged 30+
population_target_age = 0.70    # 70% of population is aged 30+ (30+ age group)

def calculate_mortality_reduction(pop_density: float, ndvi_change: float, rr: float) -> Dict:
    """
    Calculate mortality reduction using dose-response relationship.

    Formula: Deaths Prevented = Population × Baseline Mortality Rate × (1 - RR^(NDVI change / 0.1))

    Args:
        pop_density: Population density (people/km²)
        ndvi_change: Change in NDVI from intervention
        rr: Risk ratio (per 0.1 NDVI increment)

    Returns:
        Dictionary with mortality calculations
    """
    # Population (assuming 1 km² per pixel)
    population = pop_density * 1
    population_target_age_group = population * population_target_age

    # Baseline deaths
    baseline_deaths = population_target_age_group * baseline_mortality_rate

    # Number of NDVI increments (0.1 unit each)
    ndvi_increments = ndvi_change / 0.1

    # Relative risk reduction: RR^(increments)
    # For example: if NDVI increases 0.2 (2 increments) and RR=0.96,
    # then mortality multiplier = 0.96^2 = 0.9216 (7.84% reduction)
    rr_reduction = rr ** ndvi_increments

    # Mortality rate after greening
    mortality_rate_after = baseline_mortality_rate * rr_reduction

    # Deaths prevented
    deaths_prevented = baseline_deaths - (population_target_age_group * mortality_rate_after)

    return {
        'population': population,
        'baseline_deaths': baseline_deaths,
        'deaths_prevented': deaths_prevented,
        'mortality_rate_reduction_pct': (1 - rr_reduction) * 100
    }

# Calculate for each risk ratio scenario
greened_data = city_data[city_data['ndvi_change'] > 0].copy()

# Point estimate
deaths_prevented_pt = greened_data.apply(
    lambda row: calculate_mortality_reduction(row['population_density'], row['ndvi_change'], 0.96)['deaths_prevented'],
    axis=1
).sum()

# Strong limit (conservative)
deaths_prevented_sl = greened_data.apply(
    lambda row: calculate_mortality_reduction(row['population_density'], row['ndvi_change'], 0.94)['deaths_prevented'],
    axis=1
).sum()

# Weak limit (optimistic)
deaths_prevented_wl = greened_data.apply(
    lambda row: calculate_mortality_reduction(row['population_density'], row['ndvi_change'], 0.97)['deaths_prevented'],
    axis=1
).sum()

# ============================================================================
# STEP 5: Display Results
# ============================================================================

print("\n" + "╔" + "="*68 + "╗")
print("║" + " "*68 + "║")
print("║" + "HEALTH IMPACT ASSESSMENT: URBAN GREENING SCENARIO".center(68) + "║")
print("║" + "New York City (Demo)".center(68) + "║")
print("║" + " "*68 + "║")
print("╚" + "="*68 + "╝\n")

print(f"SCENARIO: Increase vegetation in low-NDVI areas to top tertile level")
print(f"          Target NDVI: {target_ndvi:.3f}\n")

print("GREENING SCOPE:")
print(f"  • Pixels greened: {len(greened_data)}")
print(f"  • Population in greened areas: {greened_data['population_density'].mean():.0f} people/km²")
print(f"  • Mean NDVI increase: {greened_data['ndvi_change'].mean():.3f}")
print(f"  • Total NDVI improvement: {greened_data['ndvi_change'].sum():.1f}")

print("\n" + "-"*70)
print("HEALTH BENEFITS (Annual Deaths Prevented):")
print("-"*70 + "\n")

print(f"Point Estimate (mean effect):        {deaths_prevented_pt:>8.1f} deaths/year")
print(f"Strong Limit (conservative):         {deaths_prevented_sl:>8.1f} deaths/year")
print(f"Weak Limit (optimistic):             {deaths_prevented_wl:>8.1f} deaths/year")

print(f"\nUNCERTAINTY RANGE (95%% CI):")
print(f"  {deaths_prevented_sl:.1f} to {deaths_prevented_wl:.1f} deaths/year")

# Per capita metrics
total_pop_30_plus = city_data['population_density'].sum() * population_target_age

print(f"\nAge-Standardized Rate (per 100,000 adults 30+):")
print(f"  • Point estimate: {(deaths_prevented_pt / total_pop_30_plus) * 100000:>6.1f} deaths prevented per 100,000")
print(f"  • Range: {(deaths_prevented_sl / total_pop_30_plus) * 100000:>6.1f} - {(deaths_prevented_wl / total_pop_30_plus) * 100000:>6.1f} per 100,000")

# ============================================================================
# STEP 6: Stratified Analysis by Population Density
# ============================================================================

print("\n" + "-"*70)
print("STRATIFIED ANALYSIS: Health Benefits by Population Density")
print("-"*70 + "\n")

stratified = []
for pop_cat in ['1-500', '501-2500', '2501-5000', '5001+']:
    subset = greened_data[greened_data['pop_category'] == pop_cat]

    if len(subset) > 0:
        deaths_prev = subset.apply(
            lambda row: calculate_mortality_reduction(row['population_density'], row['ndvi_change'], 0.96)['deaths_prevented'],
            axis=1
        ).sum()

        total_pop = subset['population_density'].sum() * population_target_age
        rate_per_100k = (deaths_prev / total_pop) * 100000 if total_pop > 0 else 0

        stratified.append({
            'Population Density': pop_cat,
            'N Pixels': len(subset),
            'Mean Pop Density': subset['population_density'].mean(),
            'Mean NDVI Change': subset['ndvi_change'].mean(),
            'Deaths Prevented': deaths_prev,
            'Rate per 100k': rate_per_100k
        })

stratified_df = pd.DataFrame(stratified)
print(stratified_df.to_string(index=False))

# ============================================================================
# STEP 7: Sensitivity Analysis
# ============================================================================

print("\n" + "-"*70)
print("SENSITIVITY ANALYSIS: Impact of Different Greening Levels")
print("-"*70 + "\n")

scenarios = [
    ("Conservative (75% of max NDVI)", 0.75),
    ("Moderate (85% of max NDVI)", 0.85),
    ("Optimistic (95% of max NDVI)", 0.95)
]

sensitivity_results = []
for scenario_name, target_pct in scenarios:
    # Recalculate with new target
    target_ndvi_scenario = q_max * target_pct

    city_data_scenario = city_data.copy()
    city_data_scenario['ndvi_greened_scenario'] = city_data_scenario.apply(
        lambda row: target_ndvi_scenario if row['ndvi_tertile'] in ['bottom', 'middle'] else row['ndvi_current'],
        axis=1
    )
    city_data_scenario['ndvi_change_scenario'] = city_data_scenario['ndvi_greened_scenario'] - city_data_scenario['ndvi_current']

    greened_scenario = city_data_scenario[city_data_scenario['ndvi_change_scenario'] > 0]

    if len(greened_scenario) > 0:
        deaths_prev_scenario = greened_scenario.apply(
            lambda row: calculate_mortality_reduction(row['population_density'], row['ndvi_change_scenario'], 0.96)['deaths_prevented'],
            axis=1
        ).sum()
    else:
        deaths_prev_scenario = 0

    sensitivity_results.append({
        'Scenario': scenario_name,
        'Target NDVI': f"{target_pct:.0%}",
        'Deaths Prevented': deaths_prev_scenario
    })

sensitivity_df = pd.DataFrame(sensitivity_results)
print(sensitivity_df.to_string(index=False))

# ============================================================================
# STEP 8: Summary
# ============================================================================

print("\n" + "╔" + "="*68 + "╗")
print("║" + " "*68 + "║")
print("║" + "ANALYSIS COMPLETE".center(68) + "║")
print("║" + " "*68 + "║")
print("║" + "This demo shows the global-ndvi-pop methodology applied to".center(68) + "║")
print("║" + "a single city. The full project analyzes ~15,917 urban".center(68) + "║")
print("║" + "areas globally using satellite NDVI data and population".center(68) + "║")
print("║" + "data stratified by biome and population density.".center(68) + "║")
print("║" + " "*68 + "║")
print("╚" + "="*68 + "╝\n")

print("KEY FINDINGS:")
print(f"  • With strategic greening to match top-performing neighborhoods,")
print(f"    NYC could prevent ~{deaths_prevented_pt:.0f} deaths per year")
print(f"  • This represents approximately {(deaths_prevented_pt / total_pop_30_plus) * 100000:.1f} prevented deaths")
print(f"    per 100,000 adults aged 30+")
print(f"  • Maximum potential range: {deaths_prevented_sl:.0f}-{deaths_prevented_wl:.0f} deaths/year")
print(f"    (accounting for epidemiological uncertainty)")
print()
