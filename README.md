# report-generator (minimal)

Minimal project to generate monthly reports from Telegram messages.

Install

```bash
python -m venv .venv
.venv/bin/python -m pip install -r report-generator/requirements.txt
```

Run (defaults to last month)

```bash
cd report-generator && ../.venv/bin/python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +%Y-%m)
```

Cron (1st day of month at 10:00, logs to repo logs)

```cron
0 10 1 * * cd /home/karmanov/projects/report-generator/report-generator && ../.venv/bin/python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +\%Y-\%m) >> /home/karmanov/projects/report-generator/logs/report.log 2>&1
```


