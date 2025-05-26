import uuid
from datetime import datetime
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field


class ResultPayload(BaseModel):
    """
    Represents the output of the last completed task in the pipeline.
    """
    source: str                    # e.g., "chart_registry", "log_registry", "s3", "generated"
    type: str                      # e.g., "reference", "raw_log", "chart", "gzip_json"
    data: Union[dict, str, bytes]  # Actual result content
    ts_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class TaskPayload(BaseModel):
    """
    The standard payload contract for all chart generation tasks.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_name: Optional[str] = None
    log_id: str
    chart_name: str
    webhook_url: Optional[str] = None

    status: str = "queued"
    phase: str = "not_started"
    retries: int = 0
    errors: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)

    result: Optional[ResultPayload] = None
    meta: Dict = Field(default_factory=dict)

    def set_phase(self, phase: str, status: Optional[str] = None, task_name: Optional[str] = None):
        self.phase = phase
        if status:
            self.status = status
        if task_name:
            self.task_name = task_name

    def set_result(self, *, source: str, type_: str, data: Union[dict, str, bytes]):
        self.result = ResultPayload(source=source, type=type_, data=data)

    def require_result_type(self, expected_type: str, expected_source: Optional[str] = None):
        if self.result is None:
            raise ValueError("Missing result")
        if self.result.type != expected_type:
            raise ValueError(f"Expected result type '{expected_type}', got '{self.result.type}'")
        if expected_source and self.result.source != expected_source:
            raise ValueError(f"Expected result source '{expected_source}', got '{self.result.source}'")

    def log_error(self, error: Union[str, Exception]):
        error_msg = str(error) if isinstance(error, Exception) else error
        self.errors.append(error_msg)

    def log_message(self, msg: str):
        self.logs.append(msg)

    def increment_retries(self):
        self.retries += 1

    @classmethod
    def from_dict(cls, data: dict) -> "TaskPayload":
        return cls(**data)
