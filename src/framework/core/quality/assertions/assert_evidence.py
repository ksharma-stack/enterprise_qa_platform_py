"""capture screenshot for evidense helpers"""

from pathlib import Path
from datetime import datetime


def capture_screenshot(page, test_name: str):
    """capture screenshot for evidense helpers"""
    screenshots_dir = Path("artifacts/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = screenshots_dir / f"{test_name}_{timestamp}.png"

    page.screenshot(path=str(file_path), full_page=True)
    return str(file_path)


def stop_and_save_trace(context, test_name: str):
    """
    Helper method for handling traces

    Attributes:
        page: Playwright Page instance used to interact with the browser.
        base_url: The application's base URL.
    """
    traces_dir = Path("artifacts/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    trace_path = traces_dir / f"{test_name}_{timestamp}.zip"

    context.tracing.stop(path=str(trace_path))
    return str(trace_path)
