# Bioprocess Optimization: Methanol Feeding Strategy for Recombinant Protein Production

Systematic analysis of fed-batch fermentation data to identify optimal conditions for β-lactoglobulin production in *Komagataella phaffii*.

---

## Project Overview

**Objective:** Optimize methanol feeding strategy for recombinant protein production

**Experimental Design:**
- 2 engineered strains (KP-B1, KP-B2)  
- 3 feeding strategies (Continuous, Pulsed, Ramped)  
- 6 experimental runs (2×3 factorial)  
- 120-hour fed-batch fermentation

**Key Result:** Identified optimal combination (KP-B2 + Ramped) achieving 38 g/L protein titer, representing 40% improvement over baseline.

---

## Repository Structure

```
bioprocess-feedlact/
├── 01_data_exploration_and_eda.ipynb       # EDA pipeline (consolidate, clean, visualize)
├── 02_statistical_and_predictive_modeling.ipynb  # ANOVA, ML, ODE models
├── 03_insights_and_recommendations.ipynb   # Executive summary & PDF report
├── config_ferm.py                          # Experiment-specific settings
├── config_domain_bioprocess.py             # Generic fermentation parameters
├── utils.py                                # Universal reusable functions
├── requirements.txt                        # Python dependencies
├── README.md                               # Documentation
├── .gitignore                              # Git ignore rules
│
├── ferm_data/                              # Raw data (6 runs × 3 files = 18 CSVs)
│   └── Run_*/
│       ├── offline_samples.csv
│       ├── bioreactor_log.csv
│       └── feed_log.csv
│
├── ferm_data_cleaned/                      # Cleaned data (4 files)
│   ├── master_offline_samples.csv
│   ├── master_bioreactor_log.csv
│   ├── master_feed_log.csv
│   └── metadata.csv
│
└── outputs/                                # Results
    ├── figures/                            # 8 PNG visualizations
    ├── models/                             # Trained models (RF, ODE)
    └── *.txt, *.pdf                        # Reports
```

---

## Analysis Pipeline

**Data Quality & Cleaning (Cells 1-3)**
- Consolidate 18 raw data files from 6 experimental runs
- Execute 7 automated quality checks (missing values, duplicates, range validation, time continuity)
- Apply cleaning transformations with full audit trail

**Exploratory Analysis (Cells 4-9)**
- Growth kinetics and protein production time-course analysis
- Bioreactor process parameter monitoring (pH, DO, temperature, agitation)
- Substrate consumption tracking and cell viability assessment
- Quantitative performance comparison across experimental conditions
- Statistical correlation analysis

**Outputs:** 5 publication-quality figures, quality assessment report, cleaning audit log

---

## Key Features

**Modular Architecture**
- Universal functions (90% reusable across experiments)
- Domain-specific configurations (fermentation parameters)
- Experiment-specific settings (cleanly separated)

**Data Quality Pipeline**
- Automated validation with file-level traceability
- Comprehensive quality reports with remediation guidance
- Complete cleaning documentation

**Professional Deliverables**
- Publication-ready visualizations
- Statistical summaries
- Reproducible analysis workflow

---

## Key Findings

| Factor | Result | Impact |
|--------|--------|--------|
| Optimal strain | KP-B2 | 45% higher productivity vs KP-B1 |
| Optimal strategy | Ramped feeding | 25% improvement over alternatives |
| Best combination | KP-B2 + Ramped | 38 g/L final titer |
| Process consistency | CV = 8.5% | Excellent reproducibility |

---

## Installation & Usage

**Requirements:** Python 3.9+, Jupyter Notebook
```bash
# Clone repository
git clone https://github.com/susihad/bioprocess-feedlact.git
cd bioprocess-feedlact

# Install dependencies
pip install -r requirements.txt

# Run analysis
jupyter notebook 01_data_exploration_and_eda.ipynb
```

**Note:** Execute cells sequentially (Cell 1 through Cell 9)

---

## Technologies

- Data processing: pandas, numpy
- Statistical analysis: scipy, statsmodels
- Visualization: matplotlib, seaborn
- Environment: Jupyter Notebook

---

## Contact

**Susi**  
Data Analyst | Bioprocess Engineer
[LinkedIn](https://www.linkedin.com/in/susilahadiyati/) | [Portfolio](https://www.notion.so/hadiyati/Bio-Data-Portfolio-28cfe43e2446806982bcf9574924117d)
