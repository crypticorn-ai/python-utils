
from crypticorn_utils.warnings import CrypticornDeprecationWarning, CrypticornExperimentalWarning


class TestCrypticornDeprecationWarning:
    """Test the CrypticornDeprecationWarning class."""

    def test_deprecation_warning_initialization(self):
        """Test CrypticornDeprecationWarning initialization with all parameters."""
        warning = CrypticornDeprecationWarning(
            "This feature is deprecated",
            since=(2, 1),
            expected_removal=(3, 0)
        )
        assert warning.message == "This feature is deprecated"
        assert warning.since == (2, 1)
        assert warning.expected_removal == (3, 0)

    def test_deprecation_warning_default_removal(self):
        """Test CrypticornDeprecationWarning with default expected_removal."""
        warning = CrypticornDeprecationWarning(
            "This feature is deprecated",
            since=(2, 1)
        )
        assert warning.message == "This feature is deprecated"
        assert warning.since == (2, 1)
        assert warning.expected_removal == (3, 0)  # since[0] + 1, 0

    def test_deprecation_warning_message_stripping(self):
        """Test that message dots are stripped."""
        warning = CrypticornDeprecationWarning(
            "This feature is deprecated.",
            since=(2, 1)
        )
        assert warning.message == "This feature is deprecated"

    def test_deprecation_warning_str_representation(self):
        """Test the string representation of CrypticornDeprecationWarning."""
        warning = CrypticornDeprecationWarning(
            "This feature is deprecated",
            since=(2, 1),
            expected_removal=(3, 0)
        )
        expected = "This feature is deprecated. Deprecated in Crypticorn v2.1 to be removed in v3.0."
        assert str(warning) == expected

    def test_deprecation_warning_str_with_default_removal(self):
        """Test string representation with default expected_removal."""
        warning = CrypticornDeprecationWarning(
            "This feature is deprecated",
            since=(1, 5)
        )
        expected = "This feature is deprecated. Deprecated in Crypticorn v1.5 to be removed in v2.0."
        assert str(warning) == expected

    def test_deprecation_warning_inheritance(self):
        """Test that CrypticornDeprecationWarning inherits from DeprecationWarning."""
        warning = CrypticornDeprecationWarning(
            "Test message",
            since=(1, 0)
        )
        assert isinstance(warning, DeprecationWarning)
        assert isinstance(warning, Warning)

    def test_deprecation_warning_with_args(self):
        """Test CrypticornDeprecationWarning with additional args."""
        warning = CrypticornDeprecationWarning(
            "Feature %s is deprecated",
            "old_api",
            since=(2, 0)
        )
        # The args should be passed to the parent constructor
        assert warning.args == ("Feature %s is deprecated", "old_api")


class TestCrypticornExperimentalWarning:
    """Test the CrypticornExperimentalWarning class."""

    def test_experimental_warning_initialization(self):
        """Test CrypticornExperimentalWarning initialization."""
        warning = CrypticornExperimentalWarning("This is experimental")
        assert str(warning) == "This is experimental"

    def test_experimental_warning_inheritance(self):
        """Test that CrypticornExperimentalWarning inherits from Warning."""
        warning = CrypticornExperimentalWarning("Test message")
        assert isinstance(warning, Warning)
        assert not isinstance(warning, DeprecationWarning)

    def test_experimental_warning_with_args(self):
        """Test CrypticornExperimentalWarning with additional args."""
        warning = CrypticornExperimentalWarning(
            "Feature %s is experimental",
            "new_api"
        )
        assert warning.args == ("Feature %s is experimental", "new_api")
