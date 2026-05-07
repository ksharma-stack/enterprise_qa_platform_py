import time

import pytest


class PerformancePlugin:
    """Tracks test execution time."""

    def __init__(self):
        self.test_times = {}

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        """Measure test execution time."""
        start = time.time()
        outcome = yield
        duration = time.time() - start

        self.test_times[item.nodeid] = duration

        if duration > 5.0:
            print(f"\nSlow test: {item.nodeid} ({duration:.2f}s)")

    def pytest_terminal_summary(self, terminalreporter):
        """Display slowest tests."""
        terminalreporter.section("Slowest Tests")
        sorted_tests = sorted(
            self.test_times.items(), key=lambda x: x[1], reverse=True
        )[:10]

        for test, duration in sorted_tests:
            terminalreporter.write_line(f"{test}: {duration:.2f}s")


def pytest_configure(config):
    """Register plugin."""
    config.pluginmanager.register(PerformancePlugin())
