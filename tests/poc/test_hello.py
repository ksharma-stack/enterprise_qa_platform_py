"""Test method"""

import pytest

# from src.framework.core.observability.logger_config.log_setup import LogFactory


@pytest.mark.poc
def test_msg_display(config, logger):
    """test method"""
    # logger = logger  # Use the logger from fixture
    logger.info("Starting test execution .")
    msg = "roll a dice"
    # logger.info(msg.capitalize())
    assert True
