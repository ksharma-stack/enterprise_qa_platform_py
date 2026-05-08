"""This file manages Pytest hooks implementation"""

from __future__ import annotations

import json
import os
from pathlib import Path
import pytest
from typing import Generator, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from src.framework.adapters.azure_openai_client import AzureOpenAIAdapter
from src.framework.services.locator_healing_service import LocatorHealingService
from src.framework.core.config.models import Settings

# import framework.core.config.variables import config
from src.framework.core.utils.utils_loader import load_settings
from src.framework.core.utils.utils_path import mkdir
from src.framework.core.observability.logger_config.log_setup import LogFactory

from src.framework.adapters.playwright_factory import create_context, create_browser


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command-line options."""
    parser.addoption(
        "--env",
        action="store",
        default=os.getenv("TEST_ENV", "dev"),
        help="Environment to run tests against (dev, qa, staging, prod)",
    )
    parser.addoption(
        "--config-dir",
        action="store",
        default="configs",
        help="Custom configuration directory path",
    )


# -------------------------
# Hooks
# -------------------------
@pytest.hookimpl()
def pytest_sessionstart(session):
    """Session start hook"""
    logger = LogFactory.get_logger(__name__)
    logger.info("Test session started")


@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    """Session finish hook"""
    logger = LogFactory.get_logger(__name__)
    logger.info("Test session finished", exit_status=exitstatus)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call: pytest.CallInfo):
    """Store test report for each phase and log results."""

    if call.when == "call":
        logger = LogFactory.get_logger(__name__)
        outcome = "failed" if call.excinfo else "passed"

        logger.info(
            "Test executed",
            outcome=outcome,
            # duration_sec=call.duration,
        )

    outcome = yield

    report = outcome.get_result()

    # Only act after the test call phase
    if report.when != "call":
        return
    # Only generate RCA on failures (and optionally xfail)

    # if report.failed:
    # Collect deterministic context
    artifacts_dir = os.path.join(Path(__file__).parent.resolve(), "artifacts")

    context = {
        "nodeid": item.nodeid,
        "outcome": report.outcome,
        "duration": getattr(report, "duration", None),
        "longrepr": str(report.longrepr),
        "markers": [m.name for m in item.iter_markers()],
    }

    # Optional: pull per-test logs path if you already emit logs
    log_path = getattr(item, "qa_log_path", None)
    if log_path:
        context["log_path"] = log_path

        #     # Optional: attach Playwright trace/screenshot if you store it on item
        #     # e.g. item.qa_trace_path, item.qa_screenshot_path set by your fixtures
        #     for key in ("qa_trace_path", "qa_screenshot_path", "qa_video_path"):
        #         p = getattr(item, key, None)
        #         if p:
        #             context[key] = p

        #     # Write raw context (always)
        #     raw_path = os.path.join(
        #         artifacts_dir,
        #         "rca_context",
        #         item.nodeid.replace("/", "_").replace("::", "__") + ".json",
        #     )
        #     os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        #     with open(raw_path, "w", encoding="utf-8") as f:
        #         json.dump(context, f, indent=2)

        # # --- AI hook: RCA summary (policy-controlled) ---
        # # keep it non-blocking: failures should not fail due to AI
        # try:
        #     from src.framework.services.ai.rca_summary_service import RCASummaryService
        #     from src.framework.core.ai.policies import AIPolicy
        #     from src.framework.adapters.ai.azure_openai_client import (
        #         AzureOpenAIProvider,
        #     )  # or your provider

        #     policy = AIPolicy.from_env_or_config()
        #     if policy.enabled("rca"):
        #         svc = RCASummaryService(
        #             ai_provider=AzureOpenAIProvider.from_env(),
        #             policy=policy,
        #         )
        #         rca = svc.summarize_failure(context)

        #         out_path = os.path.join(
        #             artifacts_dir,
        #             "rca",
        #             item.nodeid.replace("/", "_").replace("::", "__") + ".json",
        #         )
        #         os.makedirs(os.path.dirname(out_path), exist_ok=True)
        #         with open(out_path, "w", encoding="utf-8") as f:
        #             json.dump(
        #                 rca.model_dump() if hasattr(rca, "model_dump") else rca,
        #                 f,
        #                 indent=2,
        #             )

        # except Exception:
        #     # Never break test run if AI fails
        #     pass


# -------------------------
# Fixtures Config
# -------------------------
@pytest.fixture(scope="session")
def config(pytestconfig: pytest.Config) -> Settings:
    """Load test config from configuration based on environment.
    Args:
        pytestconfig: pytest Config instance for accessing options.
    Returns:
        Settings: Loaded configuration config for the test environment.
    """
    env = pytestconfig.getoption("--env")
    config_dir: str = None
    # Conditionally set base path
    config_dir = pytestconfig.getoption("--config-dir")

    # Load settings
    s = load_settings(env=env, config_dir=config_dir)

    # # Ensure artifact folders exist
    # if detect_ide():
    #     artifacts = "automation_framework/artifacts"
    # else:
    artifacts = "artifacts"
    mkdir(f"{artifacts}/screenshots")
    mkdir(f"{artifacts}/traces")
    mkdir(f"{artifacts}/logs")
    mkdir(f"{artifacts}/reports")
    return s


# -------------------------
# Log Fixtures
# -------------------------
@pytest.fixture(scope="session", autouse=True)
def logger(config: Settings):
    """Session-scoped, autouse fixture to initialize and configure logger instance with dependency injection.

    This fixture:
    - Sets up structlog with the configured logging level and file path
    - Injects the logger into WebUiAssert for all assertion methods
    - Runs automatically (autouse=True) to ensure logger is ready before tests

    Args:
        config: The loaded settings configuration.

    Returns:
        Logger instance configured with config from the environment.
    """
    LogFactory.configure_logging(config.logging.level, config.logging.file)
    configured_logger = LogFactory.get_logger(__name__)
    yield configured_logger


@pytest.fixture(autouse=True)
def bind_test_context(request):
    """
    Automatically enrich all logs with test metadata.
    """
    import structlog

    structlog.contextvars.bind_contextvars(
        test_name=request.node.name,
        nodeid=request.node.nodeid,
        worker=os.environ.get("PYTEST_XDIST_WORKER", "master"),
    )
    yield
    structlog.contextvars.clear_contextvars()


# -------------------------
# Playwright (Web) Fixtures
# -------------------------
@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Initialize and return a Playwright instance for the test session.

    Yields:
        Playwright: The Playwright sync API instance.
    """
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(
    playwright_instance: Playwright, config: Settings
) -> Generator[Browser, None, None]:
    """Create and return a Browser instance for the test session.

    Args:
        playwright_instance: The Playwright sync API instance.
        config: The loaded settings configuration.

    Yields:
        Browser: The initialized browser instance.
    """
    b = create_browser(playwright_instance, config.web)
    yield b
    b.close()


@pytest.fixture()
def context(
    browser: Browser, config: Settings, request: pytest.FixtureRequest
) -> Generator[BrowserContext, None, None]:
    """Create a browser context and persist a trace when a test fails."""

    ctx = create_context(browser, config.web, artifacts_dir="artifacts")

    # Start tracing if enabled
    if config.web.trace_on_failure:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield ctx

    # Teardown: save trace on failure
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    # if config.web.trace_on_failure:
    #     if failed:
    #         # trace_file = artifact_path(
    #         #     "artifacts/traces",
    #         #     f"{request.node.name.replace(os.sep, '_')}.zip",
    #         # )
    #         # ctx.tracing.stop(path=trace_file)
    #     else:
    #         ctx.tracing.stop()

    ctx.tracing.stop()
    ctx.close()


@pytest.fixture()
def page(
    context: BrowserContext, config: Settings, request: pytest.FixtureRequest
) -> Generator[Page, None, None]:
    """Create a page and capture a screenshot when a test fails."""

    p = context.new_page()
    yield p

    # Screenshot on failure
    # failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    # if failed and config.web.screenshot_on_failure:
    #     shot_file = artifact_path(
    #         "artifacts/screenshots",
    #         f"{request.node.name.replace(os.sep, '_')}.png",
    #     )
    #     try:
    #         p.screenshot(path=shot_file, full_page=True)
    #     except Exception:
    #         pass
    p.close()


# -------------------------
# API Fixtures
# -------------------------
def authenticated_api_client(api_client, test_user):
    """Provides an authenticated API client."""
    api_client.login(test_user.username, test_user.password)
    return api_client

# -------------------------
# AI Fixtures
# -------------------------


@pytest.fixture(scope="session")
def azure_openai_service(config: Settings):
    """
    Session-scoped Azure OpenAI service.
    """

    # config = app_config.ai.azure_openai

    if not config.enabled:
        return None

    adapter = AzureOpenAIAdapter(config)
    return LocatorHealingService(adapter)
