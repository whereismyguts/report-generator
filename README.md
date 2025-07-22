# Automated Monthly Reporting System

## 🏗️ System Architecture

The system consists of 6 autonomous components that work together to create monthly reports:

```
Telegram Channel → Log Retrieval → Data Processing → Report Generation → Document Creation → Auto-Delivery
```

## 📁 Components

### 1. **Telegram Log Retrieval** (`telegram_retriever.py`)

- Fetches logs from designated Telegram channel
- Supports incremental and full sync
- Stores raw messages in structured JSON format

### 2. **Log Processing Engine** (`log_processor.py`)

- Parses raw Telegram messages into task logs
- Converts to standard `tasks-log.txt` format
- Handles multiple log entry formats

### 3. **Data Transformation** (`data_transformer.py`)

- Converts logs to JSON using v2 schema
- Estimates task durations intelligently
- Generates comprehensive task metadata

### 4. **Report Generation** (`report-v2.py`)

- Creates Excel reports with task breakdowns
- Generates structured data analysis
- Compatible with existing v2 schema format

### 5. **Telegram Delivery** (`telegram_sender.py`)

- Sends generated reports back to Telegram
- Includes summary messages and file attachments
- Handles error notifications

### 6. **Orchestrator** (`report_orchestrator.py`)

- Coordinates all services
- Handles scheduling and error recovery
- Supports cron integration

## 🚀 Usage

### Initial Setup

```bash
pip install telethon openpyxl colorama python-dotenv
```

```bash
cp .env.example .env
# Edit .env with your Telegram credentials
```

### Manual Execution

`python telegram_retriever.py --month 2025-06`

`python generate_report_data.py -m 2025-06`

`python report-v2.py -f data/report_data_2025-06.json`
