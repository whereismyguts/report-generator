from calendar import month
import json
import logging
import requests
import datetime
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def openrouter_call(prompt: str) -> requests.Response:
    r = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            # "HTTP-Referer": "https://github.com/wiki-autocommit",
            # "X-Title": "Wiki Autocommit",
        },
        data=json.dumps({
            # "model": "deepseek/deepseek-chat",
            "model": "google/gemini-2.0-flash-001",
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }),
        timeout=10  # timeout after 10 seconds
    )
    logging.info(f"prompt: {prompt}")
    logging.info(f"response: {r.text}")
    return r


from typing import Union


def process_days(content: dict, month: Union[datetime.date, str]) -> dict:

    if isinstance(month, str):
        month = datetime.datetime.strptime(month, '%Y-%m').date()

    days_to_fill = []
    for day in content['not-mentioned-days']:

        date_obj = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        if date_obj.weekday() >= 5:  # Saturday or Sunday
            print(f" - Weekend date: {day}")
            continue

        if date_obj.month != month.month or date_obj.year != month.year:
            print(f" - Out of month date: {day}")
            continue

        print(f" Working day to fill: {day}")
        days_to_fill.append(day)

    days = []
    for day in content.get('days', []):
        date_obj = datetime.datetime.strptime(day['date'], '%Y-%m-%d').date()
        if date_obj.month != month.month or date_obj.year != month.year:
            print(f" - Skipping day out of month: {day['date']}")
            continue
        days.append(day)

    content['days-to-fill'] = days_to_fill
    content['days'] = days
    return content


if __name__ == '__main__':

    import os
    import argparse
    import datetime
    parser = argparse.ArgumentParser(description="Generate report data.")
    parser.add_argument(
        "-m", "--month",
        type=str,
        required=True,
        help="Month in format 'YYYY-MM'. If not provided, current month will be used."
    )
    args = parser.parse_args()

    prompt_path = 'report-prompt-v2.md'
    output_path = f'data/report_data_{args.month}.json'
    raw_messages_path = f'data/raw_messages_{args.month}.json'
    month = datetime.datetime.strptime(args.month, '%Y-%m')

    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    with open(raw_messages_path, 'r', encoding='utf-8') as f:
        history_json = json.load(f)

    message = prompt + '\n\n' + json.dumps(history_json, indent=2, ensure_ascii=False)
    response = openrouter_call(message)

    if response.status_code == 200:
        try:
            result_json = response.json()

            content = result_json.get('choices', [{}])[0].get('message', {}).get('content', '')
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end + 1]

            content = json.loads(content)  # parse the JSON content

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
                print(f"Report data saved to {output_path}")

            content = process_days(content, month)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print("Report data generated successfully.")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        print("Response content:", response.text)
