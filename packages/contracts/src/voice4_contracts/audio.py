from typing import Literal, Self

from pydantic import Field, model_validator

from ._base import ContractModel

SampleRate = Literal[8000, 16000]
Codec = Literal["pcmu", "pcm16"]
Direction = Literal["inbound", "outbound"]


class AudioFrame(ContractModel):
    """One chunk of call audio.

    Telephony ingress is always 8 kHz PCMU (G.711 mu-law). Anything feeding a 16 kHz
    model must be explicitly resampled to `pcm16` @ 16000 first (AGENTS.md invariant 1).
    """

    call_id: str = Field(min_length=1)
    seq: int = Field(ge=0, description="Monotonic per call and direction")
    direction: Direction
    sample_rate: SampleRate
    codec: Codec
    payload: bytes = Field(description="Raw audio bytes; URL-safe base64 in JSON")
    timestamp_ms: int = Field(ge=0, description="Monotonic call clock, ms since call start")

    @model_validator(mode="after")
    def _codec_matches_rate(self) -> Self:
        if self.codec == "pcmu" and self.sample_rate != 8000:
            raise ValueError("pcmu (G.711 mu-law) frames must be 8000 Hz")
        return self
