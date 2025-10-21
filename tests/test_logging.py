import logging
import os
import tempfile


from crypticorn_utils.logging import (
    _LogLevel,
    _CustomFormatter,
    configure_logging,
    disable_logging,
)
from crypticorn_utils.ansi_colors import AnsiColors as C


class TestLogLevel:
    """Test the _LogLevel enum and its get_color method."""

    def test_get_color_debug(self):
        """Test that DEBUG level returns the correct color."""
        assert _LogLevel.get_color("DEBUG") == C.GREEN_BRIGHT

    def test_get_color_info(self):
        """Test that INFO level returns the correct color."""
        assert _LogLevel.get_color("INFO") == C.BLUE_BRIGHT

    def test_get_color_warning(self):
        """Test that WARNING level returns the correct color."""
        assert _LogLevel.get_color("WARNING") == C.YELLOW_BRIGHT

    def test_get_color_error(self):
        """Test that ERROR level returns the correct color."""
        assert _LogLevel.get_color("ERROR") == C.RED_BRIGHT

    def test_get_color_critical(self):
        """Test that CRITICAL level returns the correct color."""
        assert _LogLevel.get_color("CRITICAL") == C.RED_BOLD

    def test_get_color_unknown(self):
        """Test that unknown level returns reset color."""
        assert _LogLevel.get_color("UNKNOWN") == C.RESET


class TestCustomFormatter:
    """Test the _CustomFormatter class."""

    def test_format_adds_levelcolor(self):
        """Test that format method adds levelcolor attribute to record."""
        # Use the default format string to test the color functionality
        from crypticorn_utils.logging import _LOGFORMAT, _DATEFMT

        formatter = _CustomFormatter(fmt=_LOGFORMAT, datefmt=_DATEFMT)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Check that levelcolor was added to the record
        assert hasattr(record, "levelcolor")
        assert record.levelcolor == C.BLUE_BRIGHT
        # Check that the formatted string contains the color (using the actual string value)
        assert C.BLUE_BRIGHT.value in formatted

    def test_format_time_trims_milliseconds(self):
        """Test that formatTime trims the last 3 digits to get milliseconds."""
        formatter = _CustomFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Mock the timestamp to have microseconds
        record.created = 1234567890.123456

        formatted_time = formatter.formatTime(record)

        # Should trim last 3 digits (456) from microseconds (123456)
        # So 123456 microseconds becomes 1234 (trimming last 3 digits)
        assert formatted_time.endswith("1234")


class TestConfigureLogging:
    """Test the configure_logging function."""

    def test_configure_logging_root_logger(self):
        """Test configuring the root logger."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers.copy()
        root_logger.handlers.clear()

        try:
            configure_logging()

            # Check that handler was added
            assert len(root_logger.handlers) == 1
            assert isinstance(root_logger.handlers[0], logging.StreamHandler)
            assert root_logger.handlers[0].level == logging.INFO
        finally:
            # Restore original handlers
            root_logger.handlers.clear()
            root_logger.handlers.extend(original_handlers)

    def test_configure_logging_named_logger(self):
        """Test configuring a named logger."""
        logger_name = "test_logger"
        logger = logging.getLogger(logger_name)

        # Clear any existing handlers
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()

        try:
            configure_logging(name=logger_name)

            # Check that handler was added and propagate is False
            assert len(logger.handlers) == 1
            assert not logger.propagate
        finally:
            # Restore original state
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)
            logger.propagate = True

    def test_configure_logging_with_file(self):
        """Test configuring logging with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            logger_name = "file_test_logger"
            logger = logging.getLogger(logger_name)

            # Clear any existing handlers
            original_handlers = logger.handlers.copy()
            logger.handlers.clear()

            try:
                configure_logging(name=logger_name, log_file=log_file)

                # Check that both stdout and file handlers were added
                assert len(logger.handlers) == 2
                handler_types = [type(h).__name__ for h in logger.handlers]
                assert "StreamHandler" in handler_types
                assert "RotatingFileHandler" in handler_types

                # Check that log file was created
                assert os.path.exists(log_file)
            finally:
                # Restore original state
                logger.handlers.clear()
                logger.handlers.extend(original_handlers)
                logger.propagate = True

    def test_configure_logging_custom_levels(self):
        """Test configuring logging with custom log levels."""
        logger_name = "custom_level_logger"
        logger = logging.getLogger(logger_name)

        # Clear any existing handlers
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()

        try:
            configure_logging(
                name=logger_name, stdout_level=logging.DEBUG, file_level=logging.ERROR
            )

            # Check that logger level is set to most verbose (DEBUG)
            assert logger.level == logging.DEBUG

            # Check handler levels
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    assert handler.level == logging.DEBUG
        finally:
            # Restore original state
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)
            logger.propagate = True

    def test_configure_logging_clears_existing_handlers(self):
        """Test that configure_logging clears existing handlers."""
        logger_name = "clear_test_logger"
        logger = logging.getLogger(logger_name)

        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        logger.addHandler(dummy_handler)
        original_handlers = logger.handlers.copy()

        try:
            configure_logging(name=logger_name)

            # Check that only one handler exists (the new one)
            assert len(logger.handlers) == 1
            assert logger.handlers[0] != dummy_handler
        finally:
            # Restore original state
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)
            logger.propagate = True

    def test_configure_logging_with_filters(self):
        """Test configure_logging with custom filters."""
        logger_name = "filter_test_logger"
        logger = logging.getLogger(logger_name)

        # Create a custom filter that only allows INFO level and above
        class InfoLevelFilter(logging.Filter):
            def filter(self, record):
                return record.levelno >= logging.INFO

        # Clear any existing handlers
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()

        try:
            # Test with filters for stdout only
            configure_logging(name=logger_name, filters=[InfoLevelFilter()])

            # Check that handler was added and has the filter
            assert len(logger.handlers) == 1
            assert len(logger.handlers[0].filters) == 1
            assert isinstance(logger.handlers[0].filters[0], InfoLevelFilter)
        finally:
            # Restore original state
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)
            logger.propagate = True

    def test_configure_logging_with_filters_and_file(self):
        """Test configure_logging with filters for both stdout and file handlers."""
        logger_name = "filter_file_test_logger"
        logger = logging.getLogger(logger_name)

        # Create a custom filter
        class CustomFilter(logging.Filter):
            def filter(self, record):
                return "test" in record.getMessage()

        # Clear any existing handlers
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                log_file = os.path.join(temp_dir, "test.log")

                # Test with filters for both stdout and file
                configure_logging(
                    name=logger_name, log_file=log_file, filters=[CustomFilter()]
                )

                # Check that both handlers were added and have the filter
                assert len(logger.handlers) == 2
                for handler in logger.handlers:
                    assert len(handler.filters) == 1
                    assert isinstance(handler.filters[0], CustomFilter)
        finally:
            # Restore original state
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)
            logger.propagate = True


class TestDisableLogging:
    """Test the disable_logging function."""

    def test_disable_logging(self):
        """Test that disable_logging disables the crypticorn logger."""
        logger_name = "crypticorn"
        logger = logging.getLogger(logger_name)

        # Store original disabled state
        original_disabled = logger.disabled

        try:
            disable_logging()
            assert logger.disabled is True
        finally:
            # Restore original state
            logger.disabled = original_disabled
