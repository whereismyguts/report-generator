# LLM-Driven Work Report Generator

- Fetch user messages written in free form from a specified Telegram chat within a given month.  
- Summarize activities and generate a strictly structured task report JSON using an LLM.  
- Validate the generated report against limitations and content requirements, and highlight skipped days to be filled.  
- Generate and send an XLS file with the full monthly worklog, time consumed, and total hours.  
- Ensure reproducibility, documentation, and configurability via environment variables.  
- Save the report in the `reports/` directory and send it to a private Telegram account.  

## Install

```bash
python -m venv .venv
.venv/bin/python -m pip install -r report-generator/requirements.txt
```

## Run (defaults to last month)

```bash
cd report-generator && ../.venv/bin/python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +%Y-%m)
```

The first run will create a session file for the Telegram API. You will need to authenticate using the code sent to your Telegram app.

### Schedule with cron (1st day of the month at 10:00, logs stored in repo)

```cron
0 10 1 * * cd /path/to/report-generator && ../.venv/bin/python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +\%Y-\%m) >> /path/to/report-generator/logs/report.log 2>&1
```

## TODO

- Add an agent mode that reminds about daily work logging and allows discussion.
- Add unit tests for core logic.
- Implement retry/backoff and error handling for AI API calls in `report-generator/ks_reporter/common/ai_client.py` (handle 429 errors, timeouts, non-JSON responses).
- Add support for additional data sources (Jira, GitHub, Google Calendar) via a pluggable retriever interface.
- Introduce prompt template versioning and maintain a suite of prompt-output regression tests (store prompts in `report-generator/prompts/`).
- Configure log rotation using `logging.handlers.RotatingFileHandler`.
