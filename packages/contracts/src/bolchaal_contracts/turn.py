from enum import StrEnum

from pydantic import Field

from ._base import ContractModel


class TurnEventType(StrEnum):
    USER_SPEECH_START = "user_speech_start"
    USER_TURN_END = "user_turn_end"
    BACKCHANNEL = "backchannel"
    BARGE_IN = "barge_in"
    AGENT_SPEECH_START = "agent_speech_start"
    AGENT_SPEECH_END = "agent_speech_end"
    TTS_FLUSHED = "tts_flushed"
    MAX_HOLD_ELAPSED = "max_hold_elapsed"


class TurnEvent(ContractModel):
    """Turn-taking state change emitted by voice-orchestrator (see SPEC 001 state machine)."""

    call_id: str = Field(min_length=1)
    turn_id: int = Field(ge=0)
    type: TurnEventType
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Turn-detector probability, when applicable"
    )
    timestamp_ms: int = Field(ge=0)
