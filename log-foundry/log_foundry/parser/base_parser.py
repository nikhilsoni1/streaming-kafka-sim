# ulog_insights/parser/base_parser.py
from px4_typecast import typecast_dict
from dataframe_helpers import apply_typecasts
import pandas as pd
from pyulog import ULog


class ULogParser:

    def __init__(self, ulg_path: str):
        self.ulg = ULog(ulg_path)
        self.topic_map = self._create_topic_map()
        self.topic_typecasts = self._create_typecast_map()

    def _create_topic_map(self):
        topic_map = {}
        for data in self.ulg.data_list:
            topic_map.setdefault(data.name, []).append(data)
        return topic_map

    def _create_typecast_map(self):
        topic_typecasts = {}
        for data in self.ulg.data_list:
            type_cast_dict = {}
            for field in data.field_data:
                type_cast_dict[field.field_name] = typecast_dict.get(field.type_str)
            topic_typecasts.setdefault(data.name, []).append(type_cast_dict)
        return topic_typecasts

    def list_topics(self):
        return list(self.topic_map.keys())

    def get_topic_df(self, topic_name: str, index: int = 0, custom_cast: dict = None) -> pd.DataFrame:
        if topic_name not in self.topic_map:
            raise ValueError(f"Topic '{topic_name}' not found.")
        if index >= len(self.topic_map[topic_name]):
            raise IndexError(f"Index {index} is out of range for topic '{topic_name}'.")

        topic_data = self.topic_map[topic_name][index]
        df = pd.DataFrame(topic_data.data)

        # Apply typecasting
        typecasts = custom_cast or self.topic_typecasts.get(topic_name, [{}])[index]
        df = apply_typecasts(df, typecasts)

        return df

    def show_typecasts(self, topic_name: str, index: int = 0):
        casts = self.topic_typecasts.get(topic_name)
        if casts:
            return casts[index]
        else:
            raise ValueError(f"No typecasts found for topic '{topic_name}'.")

if __name__ == "__main__":
    test_log_path = "/Users/nikhilsoni/workspace/streaming-kafka-sim/log-foundry/data/test_log.ulg"
    parser = ULogParser(test_log_path)
    topics = parser.list_topics()
    foo = parser.ulg.data_list[3]
    foo_vars = vars(foo)
    import json
    with open("/Users/nikhilsoni/Downloads/test_mockup.json", "w") as f:
        json.dump(foo_vars, f, indent=4, default=str, sort_keys=True)
    df = parser.get_topic_df("sensor_combined", 0)
    debug = True