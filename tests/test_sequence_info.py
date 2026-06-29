import pytest
from native_fisher_py.data.classes import SequenceInfo, SequenceFileWriter


def test_sequence_info():
    info = SequenceInfo()

    # Test column_width
    info.column_width = [1, 2, 3]
    assert info.column_width == [1, 2, 3]

    # Test type_to_column_position
    info.type_to_column_position = [4, 5, 6]
    assert info.type_to_column_position == [4, 5, 6]

    # Test bracket
    info.bracket = 42
    assert info.bracket == 42

    # Test user_private_label
    info.user_private_label = ["private", "labels"]
    assert info.user_private_label == ["private", "labels"]

    # Test user_label
    info.user_label = ["user", "labels"]
    assert info.user_label == ["user", "labels"]

    # Test tray_configuration
    info.tray_configuration = "Tray A"
    assert info.tray_configuration == "Tray A"


def test_sequence_file_writer():
    writer = SequenceFileWriter()

    # Test basic properties
    writer.bracket = 10
    assert writer.bracket == 10

    writer.file_error = "some error"
    assert writer.file_error == "some error"

    writer.file_header = "header info"
    assert writer.file_header == "header info"

    writer.file_name = "sequence.seq"
    assert writer.file_name == "sequence.seq"

    writer.is_error = 1
    assert writer.is_error == 1

    writer.tray_configuration = "Tray B"
    assert writer.tray_configuration == "Tray B"

    # Test SequenceInfo composition
    info = SequenceInfo()
    info.bracket = 55
    writer.info = info
    assert writer.info.bracket == 55

    # Test user column labels dictionary wrapper
    assert writer.get_user_column_label(1) == ""
    writer.set_user_column_label(1, "Column 1 Label")
    assert writer.get_user_column_label(1) == "Column 1 Label"
