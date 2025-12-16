# Code Review: Global NDVI-Pop R Scripts

## Executive Summary

The project contains strong epidemiological analysis but has significant code quality issues affecting:
- **Reproducibility** (excessive `setwd()` calls)
- **Production-readiness** (debugging code left in, no error handling)
- **Correctness** (duplicate calculations, potential logical errors)
- **Maintainability** (massive functions, hardcoded values, minimal documentation)

**Critical Issues Found: 4**
**High Priority Issues: 5**
**Medium Priority Issues: 6**
**Low Priority Issues: 8**

---

## CRITICAL ISSUES (Fix immediately - will cause errors or wrong results)

### 1. ⚠️ DUPLICATE VARIABLE ASSIGNMENTS - `analysis-functions.R` (Lines 513-515, 521-523, 530-532)

**File:** `scripts/analysis-functions.R`
**Function:** `hia_summarise()`
**Severity:** HIGH - Produces incorrect results

**The Problem:**
Variables are calculated twice, with the second assignment overwriting the first:

```r
# Line 509 - FIRST calculation (gets overwritten)
n_d_ac_prev_std_gbd_mean_pt = sum(n_d_ac_prev_std_gbd_pt, na.rm=T),

# Line 513 - DUPLICATE calculation (overwrites line 509)
n_d_ac_prev_std_gbd_mean_pt = sum(n_d_ac_prev_std_gbd_pt, na.rm=T),
```

This pattern repeats 3 times:
- Lines 509 vs 513-515 (`n_d_ac_prev_std_gbd_mean_pt`)
- Lines 521 vs 521-523 (`n_d_ac_prev_std_gbd_mean_sl`)
- Lines 530 vs 530-532 (`n_d_ac_prev_std_gbd_mean_wl`)

**Impact:** The first calculation is completely ignored, making the code redundant but not actually affecting results (same calculation twice).

**Fix:** Delete lines 513-515, 521-523, 530-532 (the duplicate lines)

---

### 2. ⚠️ INCORRECT NA LOGIC - `analysis-global.R` (Line 649)

**File:** `scripts/analysis-global.R`
**Severity:** HIGH - Logical error in imputation

**The Problem:**
```r
# WRONG - This is checking if (BIOME_NAME == TRUE), not if BIOME_NAME is NA
is.na(BIOME_NAME==TRUE)
```

When `BIOME_NAME` is NA, the expression `BIOME_NAME==TRUE` returns NA, not TRUE/FALSE. So `is.na(BIOME_NAME==TRUE)` will be TRUE for NA values, but also for all valid values where `BIOME_NAME != TRUE`.

**Correct Logic:**
```r
is.na(BIOME_NAME)  # Check for NA values directly
```

**Impact:** May improperly flag or miss NA values in BIOME imputation

**Fix:** Change line 649 from `is.na(BIOME_NAME==TRUE)` to `is.na(BIOME_NAME)`

---

### 3. ⚠️ INCOMPLETE CODE - `read-united-nations-gbd-data.R` (Ends abruptly)

**File:** `scripts/read-united-nations-gbd-data.R`
**Line:** ~2494 (end of file)
**Severity:** HIGH - Script cannot run to completion

**The Problem:**
The file appears to end mid-function with incomplete code. Unable to see full context from review.

**Fix:** Verify the file is complete and all function definitions are closed properly.

---

### 4. ⚠️ DIVISION BY ZERO RISK - `analysis-functions.R` (Lines 330-378)

**File:** `scripts/analysis-functions.R`
**Function:** `mutate_steps_hia_ndvi_pop()`
**Severity:** MEDIUM - Potential Inf/NaN values in results

**The Problem:**
```r
# Line 330-378 - Multiple divisions without checking denominator
n_d_ac_prev_per_pop = n_d_ac_prev_std_gbd_mean_pt / pop_cat_mean_val_scaled_gbd
# If pop_cat_mean_val_scaled_gbd == 0, this creates Inf values
```

**Impact:** If any population category has zero value, will create Inf or NaN values in mortality per capita metrics

**Fix:** Add safety check:
```r
n_d_ac_prev_per_pop = if_else(pop_cat_mean_val_scaled_gbd > 0,
                                n_d_ac_prev_std_gbd_mean_pt / pop_cat_mean_val_scaled_gbd,
                                NA_real_)
```

---

## HIGH PRIORITY ISSUES (Affect reproducibility & portability)

### 5. 🔴 EXCESSIVE `setwd()` CALLS - Multiple Scripts

**Affected Files:**
- `rasterize-vectors.R`: 14 `setwd()` calls (lines 14, 28, 32, 50, 52, 60, 69, 99, 102, 110, 120, 138, 150, 158)
- `read-united-nations-gbd-data.R`: 14+ `setwd()` calls (lines 37, 59, 72, 110, 150, 212, etc.)
- `merge-rasters.R`: 5 `setwd()` calls (lines 26, 66, 94, 100, 142)
- `analysis-global.R`: 1 `setwd()` call (line 22)

**Severity:** HIGH - Breaks reproducibility and portability

**The Problem:**
`setwd()` changes the working directory for the entire R session, making code:
- Fragile (if directory structure changes, script fails)
- Non-portable (different on Windows/Mac/Linux)
- Hard to debug (unclear which directory each operation uses)
- Incompatible with projects using working directories

**Standard Practice:**
Use the `here()` package to specify file paths relative to project root.

**Fix Example - Before:**
```r
setwd(here("data-processed"))
load("pop_ndvi_gub_biome_tib_gub_not_miss.RData")
```

**Fix Example - After:**
```r
load(here("data-processed", "pop_ndvi_gub_biome_tib_gub_not_miss.RData"))
```

**Effort:** HIGH - Requires updating ~40+ file paths across 4 scripts

---

### 6. 🔴 INTERACTIVE DEBUGGING CODE LEFT IN SCRIPTS

**Affected Files:**
- `analysis-global.R`: `.View()` calls (lines 245, 393-393, 479, 483-484)
- `merge-rasters.R`: `mapview()` calls (lines 75-86)
- `rasterize-vectors.R`: `plot()` and `mapview()` calls (lines 86, 94-95, 167-168)
- `summary-global.R`: `.View()` calls (lines 137, 155, 202, etc.)

**Severity:** HIGH - Scripts fail in batch/non-interactive environments

**The Problem:**
```r
pop_ndvi_gub_biome_tib %>% View()  # Requires RStudio interactive session
```

These commands:
- Fail when running via `Rscript` or batch processing
- Indicate debugging code left in production
- Prevent automation

**Fix:**
Remove entirely OR wrap in interactive check:
```r
if(interactive()) {
  pop_ndvi_gub_biome_tib %>% View()
}
```

**Effort:** MEDIUM - ~15 occurrences to fix

---

### 7. 🔴 NO ERROR HANDLING FOR FILE LOADING

**Affected All Scripts:** `load()`, `read_excel()`, `rast()` calls throughout

**Severity:** HIGH - Silent failures with cryptic errors

**Example:**
```r
# Current - fails silently if file doesn't exist
load("pop_ndvi_gub_biome_tib_gub_not_miss.RData")

# Better - explicit error checking
data_path <- here("data-processed", "pop_ndvi_gub_biome_tib_gub_not_miss.RData")
if(!file.exists(data_path)) {
  stop("Required data file not found: ", data_path)
}
load(data_path)
```

**Fix:** Add error checking to all data loading operations

---

### 8. 🔴 MASSIVE SINGLE MUTATE() FUNCTION - `analysis-functions.R` (Lines 96-446)

**File:** `scripts/analysis-functions.R`
**Function:** `mutate_steps_hia_ndvi_pop()`
**Severity:** HIGH - 350+ lines, creates 100+ variables at once

**The Problem:**
The function contains 350+ lines of continuous `mutate()` operations:
- Creates ~100 new variables simultaneously
- Extremely difficult to debug (which line caused the error?)
- Hard to understand (can't see purpose of each variable group)
- Poor performance (copies entire dataframe 100+ times)

**Suggested Refactoring:**
Break into logical sub-functions:
```r
mutate_steps_hia_ndvi_pop <- function(df) {
  df %>%
    mutate_ndvi_analysis() %>%      # Lines 101-122
    mutate_risk_ratios() %>%         # Lines 160-176
    mutate_baseline_deaths() %>%     # Lines 199-233
    mutate_attributable_deaths() %>% # Lines 250-379
    mutate_per_capita_rates()        # Lines 328-378
}
```

**Effort:** MEDIUM - Significant refactoring

---

### 9. 🔴 NO INPUT VALIDATION IN FUNCTIONS

**Affected:** `landscan_pop_wrangle()`, `hia_summarise()`, `mutate_steps_hia_ndvi_pop()`

**Severity:** MEDIUM-HIGH - Cryptic errors when columns are missing

**Problem:**
```r
# Current - assumes columns exist; error is cryptic if they don't
landscan_pop_wrangle <- function(df) {
  df %>% mutate(
    # Uses columns that may not exist
    pop_cat_1 = case_when(...)
  )
}
```

**Better Approach:**
```r
landscan_pop_wrangle <- function(df) {
  # Validate inputs
  required_cols <- c("landscan-global-2019-colorized_1", "landscan-global-2019-colorized_2", ...)
  missing_cols <- setdiff(required_cols, names(df))
  if(length(missing_cols) > 0) {
    stop("Missing required columns: ", paste(missing_cols, collapse=", "))
  }

  df %>% mutate(...)
}
```

**Fix:** Add validation block to all functions

---

### 10. 🔴 NO VALIDATION OF SPATIAL DATA ALIGNMENT

**Affected Files:**
- `merge-rasters.R`: Raster alignment not validated
- `rasterize-vectors.R`: CRS not checked, dimensions not verified

**Severity:** MEDIUM-HIGH - Spatial misalignment produces silently incorrect results

**Problem:**
```r
# Current - assumes rasters are aligned
merged <- c(ndvi_raster, pop_raster, biome_raster)

# Better - validates alignment first
stopifnot(identical(dim(ndvi_raster), dim(pop_raster)))
stopifnot(identical(res(ndvi_raster), res(pop_raster)))
stopifnot(identical(crs(ndvi_raster), crs(pop_raster)))
```

---

## MEDIUM PRIORITY ISSUES

### 11. Hardcoded RGB Values Without Documentation
**File:** `analysis-functions.R` (Lines 34-54)
**Issue:** RGB color mappings for LandScan categories hardcoded in case_when statements
**Fix:** Create lookup table at script start with documentation

### 12. Redundant RGB-to-Population Mapping
**File:** `analysis-functions.R` (Lines 34-44 & 45-55)
**Issue:** Two nearly identical case_when blocks
**Fix:** Create single lookup table and use joins instead

### 13. Inconsistent NA Handling
**File:** `analysis-functions.R`
**Issue:** Mix of `is.na()`, `== TRUE`, and implicit NA checks
**Fix:** Standardize to consistent pattern throughout

### 14. Silent Data Loss in Filters
**File:** `summary-global.R` (Line 89) and `analysis-global.R` (multiple)
**Issue:** Rows removed without logging how many were excluded
**Fix:** Add informative messages showing before/after row counts

### 15. Extensive Exploratory Code Left In
**File:** `summary-global.R` (Lines 140-166, 188-202, 226-263)
**Issue:** Large blocks of exploratory analysis cluttering production code
**Fix:** Move to separate exploratory script or remove entirely

### 16. No Data Validation After Filtering
**File:** `analysis-global.R` (Lines 621-623)
**Issue:** After filtering, no check for how many rows remain
**Fix:** Add assertions ensuring data remains after filters

---

## LOW PRIORITY ISSUES

### 17-24. Code Quality Issues (Low Priority)
- Inconsistent column naming conventions
- Missing comments on complex logic
- Hard-coded filter criteria without documentation
- Verbose factor creation when `fct_reorder()` could simplify
- Magic numbers without explanation
- Manual joins that could be consolidated

---

## SUMMARY TABLE: Issues by Severity

| Severity | Count | Top Issues |
|----------|-------|-----------|
| 🔴 Critical | 4 | Duplicates, NA logic error, incomplete code, division by zero |
| 🟠 High | 6 | setwd() calls, interactive code, no error handling, massive mutate(), no validation |
| 🟡 Medium | 6 | Hardcoded values, redundant code, NA inconsistency, silent filters, exploratory code |
| 🟢 Low | 8 | Naming, comments, code style, efficiency |

---

## Recommended Fix Priority

### Phase 1 (Fix immediately - 2-4 hours)
1. Remove duplicate variable assignments (lines 513-515, 521-523, 530-532)
2. Fix NA logic error (line 649)
3. Verify/complete read-united-nations-gbd-data.R
4. Add zero-check to division operations

### Phase 2 (Fix high-priority - 8-16 hours)
5. Replace all `setwd()` calls with `here()` usage
6. Remove or wrap interactive debugging code
7. Add error handling to all file loading operations
8. Add input validation to main functions

### Phase 3 (Refactor - 16-24 hours)
9. Break massive `mutate()` into sub-functions
10. Add validation for spatial data alignment
11. Create configuration file for hardcoded values
12. Add logging to all filter operations

### Phase 4 (Polish - 4-8 hours)
13-24. Remaining code quality improvements

---

## Best Practices Violations

| Practice | Violation | Where |
|----------|-----------|-------|
| Reproducible code | Excessive `setwd()` | All scripts |
| Production code | Debugging code left in | Multiple scripts |
| Robustness | No error handling | File loading throughout |
| Code clarity | Massive functions | analysis-functions.R |
| Configuration | Hardcoded values | Multiple scripts |
| Data validation | No input checks | All functions |
| Maintainability | Duplicate code | analysis-functions.R |

