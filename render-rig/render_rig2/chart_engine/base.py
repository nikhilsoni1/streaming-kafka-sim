# base.py
class Chart:
    chart_name = "chart_base"

    def is_topic_available(self, log_data: dict) -> bool:
        raise NotImplementedError

    def generate(self, log_data: dict):
        raise NotImplementedError

    def to_json(self, fig) -> str:
        import plotly.io as pio

        return pio.to_json(fig)

    def to_html(self, fig) -> str:
        import plotly.io as pio

        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
