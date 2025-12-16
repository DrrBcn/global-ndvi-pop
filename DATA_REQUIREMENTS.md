# Data Assessment: Global NDVI-Pop Analysis Reproducibility

## Quick Answer
**NO - Your repository does NOT include enough data to replicate the analysis.**

The repository contains only:
- ✅ Analysis scripts (20 R files)
- ✅ Documentation and HTML outputs
- ✅ Results tables (pre-computed from analysis)
- ❌ Raw input data (NOT included)
- ❌ Processed data (NOT included)

**Total repo size: 75 MB**
- 35 MB: HTML documentation (global-ndvi-pop-overview.html with visualizations)
- 1 MB: Scripts and code
- 39 MB: Website library files

---

## Data Required to Replicate the Analysis

### 1. REMOTE SENSING DATA (Satellite Imagery)

#### NDVI (Vegetation Greenness)
- **Source:** MODIS MOD13A2 Version 6 via Google Earth Engine
- **What it is:** Annual maximum NDVI for each 1km pixel
- **Year:** 2019
- **Coverage:** Global (180°W to 180°E, 90°N to 90°S)
- **Format:** GeoTIFF rasters (~1 file per 1km global grid)
- **Size:** ~350-500 MB globally (large!)
- **Where to get:**
  - Google Earth Engine (free, requires GEE account)
  - USGS LPDAAC (direct download)
- **Access difficulty:** Medium (requires GIS setup or GEE JavaScript programming)

**Status in your repo:** ❌ NOT INCLUDED

---

#### LandScan Global Population 2019
- **Source:** Oak Ridge National Laboratory LandScan
- **What it is:** 1km global population density raster (RGB color-coded)
- **Year:** 2019
- **Coverage:** Global
- **Format:** GeoTIFF raster
- **Size:** ~3 GB (large!)
- **Color encoding (RGB to population categories):**
  - rgb(255,255,190) = 1-5 people/km²
  - rgb(255,255,115) = 6-25 people/km²
  - rgb(255,255,0) = 26-50 people/km²
  - rgb(255,170,0) = 51-100 people/km²
  - rgb(255,102,0) = 101-500 people/km²
  - rgb(255,0,0) = 501-2,500 people/km²
  - rgb(204,0,0) = 2,501-5,000 people/km²
  - rgb(115,0,0) = 5,001-185,000 people/km²
- **Where to get:** https://landscan.ornl.gov (free registration required)
- **Access difficulty:** Medium (registration, download link provided)

**Status in your repo:** ❌ NOT INCLUDED

---

### 2. ADMINISTRATIVE & GEOGRAPHIC BOUNDARIES

#### Global Urban Boundaries (GUB) 2018
- **Source:** Tsinghua University / ESS research
- **What it is:** Vector shapefile of ~16,000 urban areas globally
- **Coverage:** Global
- **Format:** Shapefile (.shp, .dbf, .shx, etc.)
- **Key fields:**
  - ORIG_FID (unique urban area ID)
  - area_km2 (area in square kilometers)
  - Geometry (polygon boundaries)
- **Size:** ~500 MB (when unzipped)
- **Where to get:** http://data.ess.tsinghua.edu.cn/gub.html (free)
- **Access difficulty:** Easy (direct download)
- **Reference:** https://iopscience.iop.org/article/10.1088/1748-9326/ab9be3

**Status in your repo:** ❌ NOT INCLUDED

---

#### Country Boundaries
- **Source:** rnaturalearth R package or Natural Earth
- **Format:** Shapefile
- **Use:** For linking country-level mortality data
- **Size:** Small (~50 MB)

**Status in your repo:** ✅ Downloaded automatically by scripts via rnaturalearth package

---

#### Biomes/Ecoregions 2017
- **Source:** RESOLVE Ecoregions 2017
- **What it is:** Vector polygons of 14 global biomes
- **Coverage:** Global
- **Format:** GeoJSON or Shapefile
- **Key field:** BIOME_NAME (14 categories)
- **Size:** Small (~100 MB)
- **Where to get:**
  - https://ecoregions.appspot.com (map interface)
  - Google Earth Engine dataset: RESOLVE_ECOREGIONS_2017
- **Access difficulty:** Medium (must convert GEE data or extract from map)

**Status in your repo:** ❌ NOT INCLUDED

---

### 3. HEALTH/DEMOGRAPHIC DATA

#### United Nations Mortality Data
- **Source:** UN World Population Prospects (WPP)
- **What it is:** Age-specific mortality rates by country, 2019
- **Specifically needed:**
  - Deaths (total, all-cause, non-accidental)
  - Population counts
  - Age-sex breakdown (adults 30+)
- **Format:** Excel files (.xlsx) or CSV
- **Coverage:** All UN member countries (~195 countries)
- **Size:** Small (~10 MB total)
- **Where to get:** https://population.un.org/wpp/Download/Standard/Mortality/ (free)
- **Access difficulty:** Easy (registration optional, direct download)

**Status in your repo:** ❌ NOT INCLUDED (but scripts show how to import specific Excel files)

---

#### WHO Mortality Data (Optional)
- **Source:** World Health Organization
- **Use:** Age-standardization, mortality per 100,000
- **Specifics:** Not detailed in documentation
- **Status in your repo:** ❌ Referenced but details unclear

---

#### GBD (Global Burden of Disease) Data (Optional)
- **Source:** IHME Global Burden of Disease Study
- **Use:** Alternative mortality estimates
- **Status in your repo:** ❌ Referenced but not detailed

---

### 4. EPIDEMIOLOGICAL PARAMETERS

#### Dose-Response Functions
- **Source:** Meta-analysis by Rojas et al.
- **What it is:** Risk ratios for mortality reduction per 0.1 NDVI increase
- **Included in repo:** ✅ YES - hardcoded in `rojas_green_space_drf.R`
  ```r
  rr_pt = 0.96        # Point estimate
  rr_sl = 0.94        # Strong limit (conservative)
  rr_wl = 0.97        # Weak limit (optimistic)
  ndvi_increment = 0.1
  ```

**Status in your repo:** ✅ INCLUDED

---

## Data Requirements Summary Table

| Data Type | Source | Size | Status in Repo | Access Difficulty |
|-----------|--------|------|----------------|-------------------|
| **NDVI 2019 Global** | MODIS via GEE | 350-500 MB | ❌ Missing | Hard (GEE required) |
| **LandScan 2019** | ORNL | 3 GB | ❌ Missing | Medium (registration) |
| **Urban Boundaries (GUB)** | Tsinghua | 500 MB | ❌ Missing | Easy |
| **Biomes/Ecoregions** | RESOLVE | 100 MB | ❌ Missing | Medium |
| **Country Boundaries** | Natural Earth | 50 MB | ✅ Auto-downloaded | Easy |
| **UN Mortality Data** | UN WPP | 10 MB | ❌ Missing | Easy |
| **WHO/GBD Data** | WHO/IHME | Unknown | ❌ Missing | Unknown |
| **Dose-Response Params** | Rojas meta-analysis | NA | ✅ Included | NA |

---

## Total Data Requirements

**Minimum dataset needed to replicate global analysis:**
- NDVI: 350-500 MB
- LandScan: 3 GB
- Urban boundaries: 500 MB
- Biomes: 100 MB
- UN mortality: 10 MB
- **TOTAL: ~4 GB minimum**

**Processing requirements:**
- R with packages: terra, sf, tidyverse, raster
- RAM: 8-16 GB recommended (for global 1km operations)
- Storage: 20-30 GB working space (during processing)
- Time: 2-4 hours for full global analysis (depending on hardware)

---

## How to Obtain This Data

### Option 1: Download from Original Sources (RECOMMENDED)
This is the most transparent and reproducible approach.

**Step-by-step:**

1. **NDVI via Google Earth Engine** (Free)
   - Create GEE account: https://code.earthengine.google.com
   - Use this script to get annual max NDVI 2019:
   ```javascript
   var ndvi = ee.ImageCollection('MODIS/061/MOD13A2')
     .filterDate('2019-01-01', '2019-12-31')
     .select('NDVI')
     .max()
     .multiply(0.0001);  // Scale factor for MOD13A2

   Export.image.toDrive({
     image: ndvi,
     description: 'NDVI_2019_Global',
     scale: 1000,  // 1km
     crs: 'EPSG:4326'
   });
   ```
   - Download from Google Drive (will take hours for global data)

2. **LandScan Population 2019**
   - Register at: https://landscan.ornl.gov
   - Download 2019 global dataset (comes as GeoTIFF)
   - File size: ~3 GB

3. **Urban Boundaries**
   - Download from: http://data.ess.tsinghua.edu.cn/gub.html
   - Extract shapefile

4. **Biomes/Ecoregions**
   - Via GEE (same as NDVI):
   ```javascript
   var ecoregions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')
   Export.table.toDrive({
     collection: ecoregions,
     description: 'RESOLVE_ECOREGIONS_2017'
   });
   ```
   - OR download GeoJSON from: https://ecoregions.appspot.com

5. **UN Mortality Data**
   - Download from: https://population.un.org/wpp/Download/Standard/Mortality/
   - Files needed: "Deaths by age", "Population by age group"

---

### Option 2: Use Published Processed Data (EASIEST)

The original project's author published pre-processed data on **Figshare**:
- **URL:** https://figshare.com/projects/Potential_of_greenness_to_prevent_premature_mortality_in_15_917_urban_areas_considering_within-area_population_density_and_ecological_zone/221455

This contains:
- ✅ Pre-processed rasters (merged, aligned, ready for analysis)
- ✅ Pre-processed vector boundaries
- ✅ HIA results tables
- ✅ Supplementary data

**Advantage:** Don't need to download/process raw data (~10 GB vs 4 GB)
**Disadvantage:** Less control over data processing steps; harder to verify methods

---

### Option 3: Partial Replication (LOCAL REGION)

To test the methodology without downloading global data:

1. **Use same sources but smaller geographic extent:**
   - Just one country (e.g., USA) - 10x smaller than global
   - One state (e.g., Colorado) - 100x smaller than global

2. **Example: USA-only replication**
   - NDVI for USA: ~100 MB
   - LandScan USA: ~300 MB
   - GUB USA: subset available
   - Total: ~500 MB
   - **Analysis script already exists:** `analysis-usa.R` (uses 48 continental states)

---

## What the Scripts Expect

The R scripts are designed to load data from this structure:

```
project_root/
├── data-input/
│   ├── ndvi-2019-global/              # MODIS NDVI GeoTIFF files
│   │   └── ndvi_2019_global.tif (or multiple tiles)
│   ├── ls-global-2019-alt-dl/         # LandScan population raster
│   │   └── ls_2019_global.tif
│   ├── ecoregions-biomes/             # RESOLVE Ecoregions shapefile
│   │   ├── RESOLVE_ECOREGIONS_2017.shp
│   │   ├── RESOLVE_ECOREGIONS_2017.dbf
│   │   └── ...
│   ├── global-urban-boundaries/       # GUB shapefile
│   │   ├── gub_global.shp
│   │   ├── gub_global.dbf
│   │   └── ...
│   └── united-nations-mortality-data/ # UN Excel files
│       ├── WPP2019_Mortality_Indicators.xlsx
│       ├── WPP2019_PopulationByAge.xlsx
│       └── ...
│
└── data-processed/                    # Generated during analysis
    ├── pop_ndvi_gub_biome_tib.RData
    ├── summary_results_global.RData
    └── ...
```

---

## Can You Run the Analysis Without Raw Data?

**Currently: NO**

The scripts require raw data as input. However, you could:

1. **Use the pre-computed Figshare data** (easiest)
2. **Download your own from sources** (most transparent, but ~4-10 GB)
3. **Run local/regional analysis only** (subset of global)
4. **Run the demo scripts** (already included in this repo):
   - `demo-single-city-analysis.py` - Uses synthetic data
   - `demo-single-city-analysis.R` - Uses synthetic data

---

## Recommendations

### To Replicate the Published Results:
1. Download pre-processed data from Figshare (~10 GB, 1-2 hours)
2. Download this repo code
3. Run `source("scripts/source-scripts.R")` to re-generate all results
4. Compare outputs against published paper

### To Understand the Methodology (No Large Data Needed):
1. Run the demo scripts (Python/R)
2. Read the CODE_REVIEW.md for code analysis
3. Read the Rmd documentation
4. Study individual scripts

### To Deploy for Your Own Analysis:
1. Gather data for your region of interest (much smaller)
2. Modify `analysis-global.R` to use your data
3. Run analysis workflow

---

## Summary

| Question | Answer |
|----------|--------|
| **Is data in repo?** | No (75 MB repo, but need 4-10 GB data) |
| **Can I run scripts as-is?** | No, missing input data |
| **How to get data?** | Figshare pre-processed (easiest) or download sources |
| **Can I replicate results?** | Yes, with Figshare data + scripts |
| **Can I adapt to my region?** | Yes, with regional data sources |
| **What's included?** | Scripts, methodology, and demo data |

