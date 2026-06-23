"""Callbot Gateway — EventMapper / StreamAnalysisResult / CallDirection tests."""
import json

import pytest

from app.constants.call_direction import CallDirection
from app.constants.integration_contract import EVENT_AGENT_ESCALATION, EVENT_STT_PARTIAL
from app.models.stream_result import StreamAnalysisResult


def test_stream_result_snake_case_required_fields():
    payload = StreamAnalysisResult(
        event=EVENT_STT_PARTIAL,
        fds_flag="NORMAL",
        stt_text="카드 분실",
        fds_score=0.1,
    ).model_dump_json()
    data = json.loads(payload)
    assert data["event"] == EVENT_STT_PARTIAL
    assert data["fds_flag"] == "NORMAL"
    assert data["stt_text"] == "카드 분실"
    assert "fds_score" in data


def test_stream_result_text_alias_sync():
    result = StreamAnalysisResult(text="hello")
    assert result.stt_text == "hello"


def test_escalation_event_schema():
    result = StreamAnalysisResult(
        event=EVENT_AGENT_ESCALATION,
        fds_flag="CRITICAL",
        stt_text="검찰",
        reason="test",
    )
    dumped = json.loads(result.model_dump_json())
    assert dumped["event"] == EVENT_AGENT_ESCALATION
    assert dumped["fds_flag"] == "CRITICAL"


@pytest.mark.parametrize(
    "direction,segment",
    [
        (CallDirection.INBOUND, "inbound"),
        (CallDirection.OUTBOUND, "outbound"),
    ],
)
def test_call_direction_path_segment(direction, segment):
    assert direction.path_segment() == segment
