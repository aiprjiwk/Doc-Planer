# 📑 IWK Document Plan & Quality Gate Dashboard (Doc-Planer)

Real-time Excel formula-driven documentation tracking and quality gate progress system with automated Delivery Overview synchronization.

## 🚀 Key Features
- **📊 1. Resource Analytics & Workload Intelligence**: Workload distribution, capacity balance, and individual team member analysis.
- **📈 2. Visual Project Tracking**: Visual progress comparison across projects, horizontal stacked completion bars, and status donut charts with hide-complete toggle.
- **📋 3. Clean Overview Table**: Streamlined project overview table without milestone columns for clarity.
- **📅 4. Quality Gate Timeline Stepper**: Calendar week (CW) filtering and Quality Gate phase tracking (QG4, QG5, IFD, FAT, PL).
- **📝 5. Tracking Matrix & Checklist Editor**: Edit individual project checklist items and metadata with full formula preservation (100% of Excel LET/COUNTIF formulas preserved).
- **🔄 6. Delivery Overview Sync**: Smart fuzzy-matching sync with Delivery Overview files to update milestones and project codes.
- **🎨 7. Modern Executive Slate UI**: Clean, high-contrast executive theme inspired by modern SaaS dashboards (Stripe, Linear, Apple).

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Microsoft Excel / OpenPyXL dependencies

### Installation
```bash
pip install streamlit pandas openpyxl plotly
```

### Running the Dashboard
```bash
streamlit run app.py --server.port 8502
```
or double click `start.bat`.
