# Test for parser
import pytest
import pandas as pd
from log_foundry.parser.base_parser import ULogParser


# Dummy classes to mock pyulog.ULog structure
class DummyField:
    def __init__(self, name, dtype):
        self.field_name = name
        self.type_str = dtype


class DummyData:
    def __init__(self, name, columns, fields):
        self.name = name
        self.data = columns  # <--- dict of lists/arrays, like real PX4 logs
        self.field_data = fields


class DummyULog:
    def __init__(self):
        self.data_list = [
            DummyData(
                name="sensor_accel",
                columns={"x": [1.0], "y": [2.0], "z": [3.0]},
                fields=[
                    DummyField("x", "float"),
                    DummyField("y", "float"),
                    DummyField("z", "float"),
                ],
            ),
            DummyData(
                name="sensor_gyro",
                columns={"x": [4.0], "y": [None], "z": [6.0]},
                fields=[
                    DummyField("x", "float"),
                    DummyField("y", "float"),
                    DummyField("z", "float"),
                ],
            ),
            DummyData(
                name="custom_data",
                columns={"flag": [1]},
                fields=[DummyField("flag", "uint128_t")],  # unsupported type
            ),
        ]


# Monkeypatch ULog in base_parser to return our DummyULog
@pytest.fixture
def mock_ulog(monkeypatch):
    monkeypatch.setattr("log_foundry.parser.base_parser.ULog", lambda _: DummyULog())


def test_list_topics(mock_ulog):
    parser = ULogParser("dummy.ulg")
    assert set(parser.list_topics()) == {"sensor_accel", "sensor_gyro", "custom_data"}


def test_get_topic_df_valid(mock_ulog):
    parser = ULogParser("dummy.ulg")
    df = parser.get_topic_df("sensor_accel")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["x", "y", "z"]
    assert df["x"].iloc[0] == 1.0


def test_get_topic_df_nulls(mock_ulog):
    parser = ULogParser("dummy.ulg")
    df = parser.get_topic_df("sensor_gyro")
    assert df["y"].isnull().any()


def test_get_topic_df_unsupported_type_warns(monkeypatch, mock_ulog):
    warnings_triggered = []
    monkeypatch.setattr("warnings.warn", lambda msg: warnings_triggered.append(msg))

    parser = ULogParser("dummy.ulg")
    df = parser.get_topic_df("custom_data")
    assert "flag" in df.columns
    assert len(warnings_triggered) > 0
    assert "No dtype mapping found for column" in warnings_triggered[0]


def test_invalid_topic_raises(mock_ulog):
    parser = ULogParser("dummy.ulg")
    with pytest.raises(ValueError, match="not found"):
        parser.get_topic_df("nonexistent")


def test_index_out_of_bounds(mock_ulog):
    parser = ULogParser("dummy.ulg")
    with pytest.raises(IndexError, match="out of range"):
        parser.get_topic_df("sensor_accel", index=99)
