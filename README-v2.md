# KS Reporter - Modular Reporter and Vacancy Filter

A comprehensive Telegram-based system for generating activity reports and filtering job vacancies using AI.

## 🌟 Features

### 📊 **Report Generation**

- **Automated monthly reports** from Telegram activity logs
- **AI-powered content analysis** using OpenRouter API
- **Excel report generation** with detailed task breakdown
- **Telegram delivery** of generated reports

### 🎯 **Vacancy Filter**

- **Multi-channel monitoring** of 12+ job boards
- **AI-powered matching** against your resume and preferences
- **Smart filtering** with relevance scoring
- **Automated notifications** for relevant opportunities
- **Scheduled checking** with customizable intervals

## 🏗️ Project Structure

```text
ks_reporter/
│
├── common/                   # Shared utilities
│   ├── telegram.py           # Base Telegram client
│   ├── ai_client.py          # AI API client (OpenRouter)
│   ├── data_manager.py       # Data persistence utilities
│   ├── link_extractor.py     # Link extraction and processing
│   └── utils.py              # Common utility functions
│
├── report/                   # Report generation module
│   ├── retriever.py          # Fetches logs from Telegram
│   ├── generator.py          # Generates report using AI
│   ├── formatter.py          # Creates Excel reports (openpyxl)
│   └── sender.py             # Sends reports to Telegram
│
├── vacancy/                  # Vacancy filtering module
│   ├── filter.py             # Filters job vacancies with AI
│   └── scheduler.py          # Automates vacancy checking
│
└── scripts/                  # Entry point scripts
    ├── run_report_pipeline.py        # Report generation script
    ├── run_vacancy_filter.py         # Vacancy filtering script
    ├── run_vacancy_scheduler.py      # Scheduler script
    └── setup_vacancy_filter.py       # Setup script
```

## ⚡ Quick Start

### 📋 Prerequisites

1. **Python 3.8+**
2. **Telegram API credentials** (api_id, api_hash, phone)
3. **OpenRouter API key** for AI processing
4. **Active Telegram account** subscribed to relevant channels

### 🔧 Installation

```bash
# Clone the repository
git clone <repository-url>
cd report-generator

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 🌐 Environment Setup

Create a `.env` file in the project root:

```env
# Telegram API credentials (get from https://my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# OpenRouter API key (get from https://openrouter.ai)
OPENROUTER_API_KEY=your_openrouter_key

# Optional: Target user/channel for notifications
TELEGRAM_TARGET_USER=your_user_id
TELEGRAM_CHANNEL_ID=your_channel_id
```

### 📝 Configuration Files

#### `resume.json` - Your professional profile

```json
{
  "personal_info": {
    "name": "Your Name",
    "location": "Your Location",
    "experience_years": 5
  },
  "skills": {
    "languages": ["Python", "JavaScript", "TypeScript"],
    "frameworks": ["Django", "FastAPI", "React"],
    "technologies": ["PostgreSQL", "Docker", "AWS"]
  },
  "preferences": {
    "work_type": ["remote", "hybrid"],
    "salary_min": 100000,
    "relocate": false
  }
}
```

#### `vacancy-filter-prompt.md` - AI filtering instructions

Template for how AI should evaluate job vacancies against your profile.

## 🚀 Usage

### 📊 Report Generation

#### Generate Monthly Report (Full Pipeline)

```bash
# Generate report for specific month
python -m ks_reporter.scripts.run_report_pipeline --month 2025-07 --session session-3 --target-user 258610595

# Skip message fetching (use existing data)
python -m ks_reporter.scripts.run_report_pipeline --month 2025-07 --skip-fetch --session session-3
```

#### Manual Steps

```bash
# 1. Fetch Telegram messages
python telegram_retriever.py --month 2025-07

# 2. Generate report data with AI
python generate_report_data.py -m 2025-07

# 3. Create Excel report
python report_v2.py -f data/report_data_2025-07.json
```

### 🎯 Vacancy Filter

#### Initial Setup

```bash
# Run setup wizard
python -m ks_reporter.scripts.setup_vacancy_filter

# Check environment only
python -m ks_reporter.scripts.setup_vacancy_filter --check-only
```

The setup will:

1. ✅ Validate environment variables
2. ✅ Check required files (resume.json, prompt template)
3. 🔍 Discover your subscribed Telegram channels
4. 🤖 Auto-select relevant job channels (12+ configured)
5. 💾 Save configuration to `vacancy_config.json`
6. 🧪 Test the filtering system

#### Manual Vacancy Check

```bash
# Check for vacancies in last 24 hours
python -m ks_reporter.scripts.run_vacancy_filter --hours 24 --session session-3 --target-user 258610595

# Dry run (don't send notifications)
python -m ks_reporter.scripts.run_vacancy_filter --hours 24 --session session-3 --dry-run

# Check specific channels
python -m ks_reporter.scripts.run_vacancy_filter --channels -1001803553802 -1001554908103
```

#### Automated Scheduling

```bash
# Run once and exit
python -m ks_reporter.scripts.run_vacancy_scheduler --once --session session-3 --target-user 258610595

# Run continuously (background monitoring)
python -m ks_reporter.scripts.run_vacancy_scheduler --continuous --session session-3 --target-user 258610595
```

## 📡 Configured Job Channels

The system monitors these job boards automatically:

| Channel | Focus | Language |
|---------|-------|----------|
| **RVC Global** | Remote IT jobs worldwide | EN/RU |
| **RVC СНГ** | CIS region IT jobs | RU |
| **Python Jobs** | Python-specific positions | RU |
| **Machine Learning Jobs** | ML/AI opportunities | EN |
| **IT Freelance & Remote** | Freelance work | EN/RU |
| **Remocate** | Relocation opportunities | RU |
| **Jobs Abroad** | International positions | EN |
| **Remote Dev Jobs** | Remote development | EN |

## 🔄 Automation Options

### Cron Jobs (Linux/Mac)

```bash
# Daily vacancy check at 9 AM
0 9 * * * cd /path/to/project && python -m ks_reporter.scripts.run_vacancy_scheduler --once
````

# Monthly report generation on the 1st at 10 AM

```bash
0 10 1 * * cd /home/karmanov/projects/report-generator && .venv/bin/python -m ks_reporter.scripts.run_report_pipeline --month $(date --date='last month' +\%Y-\%m)  >> /home/karmanov/projects/report-generator/logs/report.log 2>&1
```

### Background Process

```bash
# Run vacancy scheduler continuously
nohup python -m ks_reporter.scripts.run_vacancy_scheduler --continuous &
```

## 📁 Generated Files

```text
data/                         # Report data
├── raw_messages_2025-07.json       # Fetched Telegram messages
└── report_data_2025-07.json        # AI-processed report data

reports/                      # Generated Excel reports
└── Anton_Karmanov_2025_07_v20250807.xlsx

logs/                         # Application logs
├── report_generator.log
├── vacancy_filter.log
└── setup_vacancy_filter.log

vacancy_config.json           # Vacancy filter configuration
```

## 🛠️ Configuration

### Vacancy Filter Settings (`vacancy_config.json`)

```json
{
  "filtering_config": {
    "check_interval_hours": 6,          # How often to check
    "max_messages_per_channel": 200,    # Message limit per channel
    "min_score_threshold": 0.4,         # Minimum relevance score
    "max_results_to_send": 10,          # Max vacancies to send
    "auto_send_results": true           # Auto-send or manual review
  },
  "notification_settings": {
    "send_daily_summary": true,         # Daily digest
    "send_immediate_alerts": true,      # Instant notifications
    "quiet_hours": {                    # No notifications during
      "start": "22:00",
      "end": "08:00"
    }
  }
}
```

## 🔧 Troubleshooting

### Common Issues

**No messages found**

- Check channel subscriptions in Telegram
- Verify channel IDs in configuration
- Increase time range (`--hours` parameter)

**AI filtering failed**

- Check OpenRouter API key
- Verify prompt template exists
- Check API quota/limits

**Telegram connection issues**

- Verify API credentials in `.env`
- Check session files (`session-3.session`)
- Ensure phone number is correct

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python -m ks_reporter.scripts.run_vacancy_filter --dry-run
```

## 📦 Dependencies

- **telethon** - Telegram client
- **openpyxl** - Excel file generation
- **requests** - HTTP client for API calls
- **python-dotenv** - Environment variable management

## 🔒 Security Notes

- Keep `.env` file private (never commit to version control)
- Telegram session files contain authentication data
- API keys should be kept secure
- Consider using environment variables in production
