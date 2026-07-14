import datetime
import logging
import os
import re

import azure.functions as func
import requests
from azure.data.tables import TableServiceClient


def clean_table_key(value: str) -> str:
    """
    Azure Table Storage PartitionKey and RowKey cannot contain certain characters.
    This keeps the key safe while preserving enough detail to identify the site.
    """
    return re.sub(r"[\\/#?]", "_", value)


def main(mytimer: func.TimerRequest) -> None:
    """
    Timer-triggered uptime monitor.

    Checks:
    1. Website reachability
    2. HTTP status code
    3. Response time
    4. Expected content

    Writes every result to Azure Table Storage.
    Logs failures for Azure Monitor alerting.
    """

    target_url = os.environ["TARGET_URL"]
    expected_text = os.environ["EXPECTED_TEXT"]
    storage_conn = os.environ["AzureWebJobsStorage"]

    check_time = datetime.datetime.utcnow()
    result_status = "PASS"
    error_detail = ""
    response_ms = 0

    try:
        response = requests.get(target_url, timeout=10)
        response_ms = int(response.elapsed.total_seconds() * 1000)

        if response.status_code != 200:
            result_status = "FAIL"
            error_detail = f"Unexpected HTTP status code: {response.status_code}"

        elif response_ms > 5000:
            result_status = "SLOW"
            error_detail = f"Response time exceeded threshold: {response_ms}ms"

        elif expected_text.lower() not in response.text.lower():
            result_status = "FAIL"
            error_detail = f"Expected text not found: {expected_text}"

    except requests.exceptions.Timeout:
        result_status = "FAIL"
        error_detail = "Request timed out after 10 seconds"

    except requests.exceptions.ConnectionError:
        result_status = "FAIL"
        error_detail = "Connection error — website unreachable"

    except Exception as exc:
        result_status = "FAIL"
        error_detail = f"Unexpected error: {str(exc)}"

    entity = {
        "PartitionKey": clean_table_key(target_url),
        "RowKey": check_time.strftime("%Y%m%d%H%M%S"),
        "CheckTimeUtc": check_time.isoformat(),
        "Status": result_status,
        "ResponseMs": response_ms,
        "ErrorDetail": error_detail,
        "TargetUrl": target_url,
        "ExpectedText": expected_text,
    }

    try:
        table_service = TableServiceClient.from_connection_string(storage_conn)
        table_client = table_service.get_table_client(table_name="uptimechecks")
        table_client.upsert_entity(entity)

        logging.info(
            f"UPTIME CHECK: {result_status} | {response_ms}ms | {target_url}"
        )

    except Exception as exc:
        logging.error(f"TABLE WRITE FAILURE: {str(exc)}")

    if result_status != "PASS":
        logging.error(
            f"SITE DOWN: {target_url} | {result_status} | {error_detail}"
        )