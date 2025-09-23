# Report Generator

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

## Usage

```bash
python -m ks_reporter.scripts.run_report_pipeline --month YYYY-MM
```

## Cron Job

```bash
0 10 1 * * cd /path/to/project && python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +\%Y-\%m)
```
