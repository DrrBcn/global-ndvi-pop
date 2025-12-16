# ============================================================================
# DEMO: Single City Health Impact Assessment using NDVI and Epidemiological Data
# Based on the global-ndvi-pop project methodology
# ============================================================================

library(tidyverse)

# ============================================================================
# STEP 1: Load epidemiological dose-response parameters
# ============================================================================
# Based on meta-analysis of green space and mortality reduction
# Source: Rojas et al. meta-analysis (see rojas_green_space_drf.R)

# Risk ratios for all-cause non-accidental mortality
# These represent the reduction in mortality risk for each 0.1 unit increase in NDVI

rr_params <- tibble(
  param = c("point_estimate", "strong_limit", "weak_limit"),
  risk_ratio = c(0.96, 0.94, 0.97),  # RR per 0.1 NDVI increase
  description = c(
    "Mean effect from meta-analysis",
    "Strong limit (conservative estimate)",
    "Weak limit (optimistic estimate)"
  )
)

print("Epidemiological Risk Ratios (Dose-Response):")
print(rr_params)
cat("\nInterpretation: A 0.1 increase in NDVI is associated with a ~4% reduction in mortality risk\n\n")

# ============================================================================
# STEP 2: Create demo data for a single city (New York City)
# ============================================================================

# Simplified NYC data with NDVI and population distribution
city_data <- tibble(
  city_name = "New York City",
  country = "United States",
  biome = "Temperate broadleaf and mixed forests",

  # Simplified pixel/zone data
  pixel_id = 1:100,

  # NDVI values (range 0-1, higher = more vegetation)
  ndvi_current = c(
    rep(runif(30, 0.2, 0.4), times = 1),  # Low NDVI areas (30% of pixels)
    rep(runif(40, 0.4, 0.6), times = 1),  # Medium NDVI areas (40% of pixels)
    rep(runif(30, 0.6, 0.8), times = 1)   # High NDVI areas (30% of pixels)
  ) %>% sort(decreasing = FALSE),

  # Population (simplified: population per pixel in people/km²)
  population_density = c(
    rep(5000, 30),   # 30% low NDVI, high density
    rep(3000, 40),   # 40% medium NDVI, medium density
    rep(2000, 30)    # 30% high NDVI, lower density
  ),

  # Population category for stratification (based on LandScan categories)
  pop_category = cut(population_density,
                     breaks = c(0, 500, 2500, 5000, 10000),
                     labels = c("1-500", "501-2500", "2501-5000", "5001+"))
)

print("DEMO CITY DATA: New York City")
print(head(city_data, 10))
cat("\nSummary Statistics:\n")
print(summary(city_data[, c("ndvi_current", "population_density")]))

# ============================================================================
# STEP 3: Calculate NDVI targets (tertile approach)
# ============================================================================
# The analysis recommends greening areas in the bottom 2 tertiles
# to the level of the top tertile

ndvi_quantiles <- city_data %>%
  summarise(
    q33 = quantile(ndvi_current, 0.33),
    q66 = quantile(ndvi_current, 0.67),
    max = max(ndvi_current)
  )

print("\nNDVI Tertiles (Current):")
print(ndvi_quantiles)

# Create greening scenario: boost low/medium NDVI areas to top tertile
city_data <- city_data %>%
  mutate(
    ndvi_tertile = case_when(
      ndvi_current <= ndvi_quantiles$q33 ~ "bottom",
      ndvi_current <= ndvi_quantiles$q66 ~ "middle",
      TRUE ~ "top"
    ),

    # Greening scenario: boost bottom and middle to median of top tertile
    ndvi_greened = case_when(
      ndvi_tertile %in% c("bottom", "middle") ~ ndvi_quantiles$max * 0.9,  # 90% of max
      TRUE ~ ndvi_current
    ),

    # NDVI change
    ndvi_change = ndvi_greened - ndvi_current
  )

print("\nNDVI Change from Greening Scenario:")
print(city_data %>%
  group_by(ndvi_tertile) %>%
  summarise(
    pixels = n(),
    current_ndvi = mean(ndvi_current),
    greened_ndvi = mean(ndvi_greened),
    change = mean(ndvi_change)
  ))

# ============================================================================
# STEP 4: Health Impact Calculations
# ============================================================================

# Calculate health benefits using dose-response relationship
# Formula: Deaths Prevented = Population × Baseline Mortality Rate × (1 - RR^(NDVI change / 0.1))

# Demo mortality parameters (based on WHO/GBD data for developed countries)
baseline_mortality_rate <- 0.006  # 6 per 1000 adults aged 30+
population_target_age <- 0.70    # 70% of population is aged 30+

# Function to calculate mortality reduction
calculate_mortality_reduction <- function(pop_density, ndvi_change, rr) {
  # Population
  population = pop_density * 1  # Assuming 1 km² area per pixel for demo
  population_target_age_group = population * population_target_age

  # Baseline deaths
  baseline_deaths = population_target_age_group * baseline_mortality_rate

  # Number of NDVI increments (0.1 unit each)
  ndvi_increments = ndvi_change / 0.1

  # Relative risk reduction: RR^(increments)
  rr_reduction = rr ^ ndvi_increments

  # Mortality rate after greening
  mortality_rate_after = baseline_mortality_rate * rr_reduction

  # Deaths prevented
  deaths_prevented = baseline_deaths - (population_target_age_group * mortality_rate_after)

  return(list(
    population = population,
    baseline_deaths = baseline_deaths,
    deaths_prevented = deaths_prevented,
    mortality_rate_reduction_pct = (1 - rr_reduction) * 100
  ))
}

# Calculate for each risk ratio scenario
results <- city_data %>%
  filter(ndvi_change > 0) %>%  # Only count greened areas
  summarise(
    total_pixels_greened = n(),
    total_population_greened = sum(population_density),
    total_ndvi_change = sum(ndvi_change),
    mean_ndvi_change = mean(ndvi_change),

    # Point estimate scenario
    deaths_prevented_pt = {
      rr <- 0.96
      sum(sapply(1:n(), function(i) {
        result <- calculate_mortality_reduction(
          pop_density = population_density[i],
          ndvi_change = ndvi_change[i],
          rr = rr
        )
        result$deaths_prevented
      }))
    },

    # Strong limit scenario (conservative)
    deaths_prevented_sl = {
      rr <- 0.94
      sum(sapply(1:n(), function(i) {
        result <- calculate_mortality_reduction(
          pop_density = population_density[i],
          ndvi_change = ndvi_change[i],
          rr = rr
        )
        result$deaths_prevented
      }))
    },

    # Weak limit scenario (optimistic)
    deaths_prevented_wl = {
      rr <- 0.97
      sum(sapply(1:n(), function(i) {
        result <- calculate_mortality_reduction(
          pop_density = population_density[i],
          ndvi_change = ndvi_change[i],
          rr = rr
        )
        result$deaths_prevented
      }))
    }
  )

# ============================================================================
# STEP 5: Display Results
# ============================================================================

cat("\n")
cat("╔════════════════════════════════════════════════════════════════╗\n")
cat("║       HEALTH IMPACT ASSESSMENT: URBAN GREENING SCENARIO        ║\n")
cat("║                     New York City (Demo)                       ║\n")
cat("╚════════════════════════════════════════════════════════════════╝\n\n")

cat("SCENARIO: Increase vegetation in low-NDVI areas to top tertile level\n\n")

cat("GREENING SCOPE:\n")
cat(sprintf("  • Pixels greened: %d\n", results$total_pixels_greened))
cat(sprintf("  • Population in greened areas: %.0f people/km²\n", results$total_population_greened / results$total_pixels_greened))
cat(sprintf("  • Mean NDVI increase: %.3f\n", results$mean_ndvi_change))
cat(sprintf("  • Total NDVI improvement: %.1f\n", results$total_ndvi_change))

cat("\n────────────────────────────────────────────────────────────────\n")
cat("HEALTH BENEFITS (Annual Deaths Prevented):\n")
cat("────────────────────────────────────────────────────────────────\n\n")

cat(sprintf("Point Estimate (mean effect):        %.1f deaths/year\n", results$deaths_prevented_pt))
cat(sprintf("Strong Limit (conservative):        %.1f deaths/year\n", results$deaths_prevented_sl))
cat(sprintf("Weak Limit (optimistic):            %.1f deaths/year\n", results$deaths_prevented_wl))

cat("\nUNCERTAINTY RANGE:\n")
cat(sprintf("  95%% CI: %.1f to %.1f deaths/year\n",
            results$deaths_prevented_sl,
            results$deaths_prevented_wl))

# Per capita metrics (per 100,000 population in target age group)
total_pop_30_plus <- city_data$population_density %>% sum() * population_target_age

cat(sprintf("\nAge-Standardized Rate (per 100,000 adults 30+):\n"))
cat(sprintf("  • Point estimate: %.1f deaths prevented per 100,000\n",
            (results$deaths_prevented_pt / total_pop_30_plus) * 100000))
cat(sprintf("  • Range: %.1f - %.1f per 100,000\n",
            (results$deaths_prevented_sl / total_pop_30_plus) * 100000,
            (results$deaths_prevented_wl / total_pop_30_plus) * 100000))

# ============================================================================
# STEP 6: Stratified Analysis by Population Density
# ============================================================================

cat("\n────────────────────────────────────────────────────────────────\n")
cat("STRATIFIED ANALYSIS: Health Benefits by Population Density\n")
cat("────────────────────────────────────────────────────────────────\n\n")

stratified_results <- city_data %>%
  filter(ndvi_change > 0) %>%
  group_by(pop_category) %>%
  summarise(
    n_pixels = n(),
    mean_pop_density = mean(population_density),
    mean_ndvi_change = mean(ndvi_change),
    total_pop_target = sum(population_density) * population_target_age,

    # Deaths prevented (point estimate)
    deaths_prevented = {
      rr <- 0.96
      sum(sapply(1:n(), function(i) {
        result <- calculate_mortality_reduction(
          pop_density = population_density[i],
          ndvi_change = ndvi_change[i],
          rr = rr
        )
        result$deaths_prevented
      }))
    },

    .groups = 'drop'
  ) %>%
  mutate(
    rate_per_100k = (deaths_prevented / total_pop_target) * 100000
  )

print(stratified_results %>%
  select(pop_category, n_pixels, mean_pop_density, deaths_prevented, rate_per_100k))

# ============================================================================
# STEP 7: Sensitivity Analysis
# ============================================================================

cat("\n────────────────────────────────────────────────────────────────\n")
cat("SENSITIVITY ANALYSIS: Impact of Different Greening Levels\n")
cat("────────────────────────────────────────────────────────────────\n\n")

greening_scenarios <- tibble(
  scenario = c(
    "Conservative (75% of max NDVI)",
    "Moderate (85% of max NDVI)",
    "Optimistic (95% of max NDVI)"
  ),
  target_ndvi_pct = c(0.75, 0.85, 0.95)
) %>%
  mutate(
    results = map(target_ndvi_pct, function(pct) {
      data <- city_data %>%
        mutate(
          ndvi_greened_scenario = if_else(
            ndvi_tertile %in% c("bottom", "middle"),
            ndvi_quantiles$max * pct,
            ndvi_current
          ),
          ndvi_change_scenario = ndvi_greened_scenario - ndvi_current
        ) %>%
        filter(ndvi_change_scenario > 0) %>%
        summarise(
          deaths_prevented_pt = {
            rr <- 0.96
            sum(sapply(1:n(), function(i) {
              result <- calculate_mortality_reduction(
                pop_density = population_density[i],
                ndvi_change = ndvi_change_scenario[i],
                rr = rr
              )
              result$deaths_prevented
            }))
          }
        )
      return(data$deaths_prevented_pt)
    })
  ) %>%
  unnest(results, keep_empty = TRUE) %>%
  rename(deaths_prevented = results)

print(greening_scenarios)

cat("\n")
cat("╔════════════════════════════════════════════════════════════════╗\n")
cat("║                    ANALYSIS COMPLETE                           ║\n")
cat("║                                                                ║\n")
cat("║  This demo shows the global-ndvi-pop methodology applied to    ║\n")
cat("║  a single city. The full project analyzes ~15,917 urban        ║\n")
cat("║  areas globally using satellite NDVI data and population       ║\n")
cat("║  data stratified by biome and population density.              ║\n")
cat("╚════════════════════════════════════════════════════════════════╝\n")
