"""Server-side speech evidence extraction for the Voice 4.0 Streamlit MVP."""

from __future__ import annotations

import io
import math
import wave
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass
class WordEvidence:
    word: str
    start: float
    end: float
    probability: float | None


@dataclass
class Hypothesis:
    text: str
    confidence: float
    source: str


@dataclass
class SpeechEvidence:
    transcript: str
    confidence: float
    duration_seconds: float | None
    language: str
    language_probability: float
    words: list[WordEvidence]
    hypotheses: list[Hypothesis]
    context: str
    agent_response: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decode_wav(audio_bytes: bytes) -> tuple[np.ndarray, float]:
    """Decode Streamlit's PCM WAV directly, bypassing external file decoders."""
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            frames = wav_file.readframes(frame_count)
    except (wave.Error, EOFError, ZeroDivisionError) as exc:
        raise ValueError("The microphone recording is not a readable PCM WAV file.") from exc

    if sample_rate != 16_000:
        raise ValueError(f"Expected 16 kHz microphone audio, received {sample_rate} Hz.")
    if frame_count == 0 or not frames:
        raise ValueError("The microphone recording contains no audio samples.")
    if sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {sample_width * 8}-bit.")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    duration = frame_count / float(sample_rate)
    return np.ascontiguousarray(audio, dtype=np.float32), duration


def confidence_from_log_probabilities(values: list[float]) -> float:
    if not values:
        return 0.0
    confidence = math.exp(sum(values) / len(values))
    return max(0.0, min(1.0, confidence))


def normalize_hypothesis(text: str) -> str:
    return " ".join(text.lower().strip().rstrip(".?!").split())


def build_agent_response(hypotheses: list[Hypothesis], confidence: float) -> str:
    if not hypotheses:
        return "I could not hear that clearly. Could you please repeat it?"

    top = hypotheses[0].text.strip()
    alternate = next(
        (
            item.text.strip()
            for item in hypotheses[1:]
            if normalize_hypothesis(item.text) != normalize_hypothesis(top)
        ),
        None,
    )
    if alternate:
        return f'I heard “{top}”. Another possibility is “{alternate}”. Which is correct?'
    if confidence < 0.72:
        return f'I heard “{top}”, but the signal was uncertain. Could you confirm that?'
    return f'I heard “{top}”. Is that correct?'


def _run_pass(
    model: Any,
    audio_waveform: np.ndarray,
    *,
    source: str,
    temperature: float,
    beam_size: int,
    best_of: int,
    hotwords: str | None,
    include_words: bool,
) -> tuple[Hypothesis, list[WordEvidence], Any]:
    segments, info = model.transcribe(
        audio_waveform,
        language="en",
        task="transcribe",
        beam_size=beam_size,
        best_of=best_of,
        temperature=temperature,
        word_timestamps=include_words,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 350},
        condition_on_previous_text=False,
        hotwords=hotwords,
    )
    completed_segments = list(segments)
    text = " ".join(segment.text.strip() for segment in completed_segments).strip()
    confidence = confidence_from_log_probabilities(
        [segment.avg_logprob for segment in completed_segments]
    )
    words: list[WordEvidence] = []
    if include_words:
        for segment in completed_segments:
            for word in segment.words or []:
                words.append(
                    WordEvidence(
                        word=word.word.strip(),
                        start=round(word.start, 2),
                        end=round(word.end, 2),
                        probability=(
                            round(float(word.probability), 4)
                            if word.probability is not None
                            else None
                        ),
                    )
                )
    return Hypothesis(text=text, confidence=confidence, source=source), words, info


def analyze_audio(
    model: Any,
    audio_bytes: bytes,
    *,
    context: str,
    expected_vocabulary: str = "",
    thorough: bool = True,
) -> SpeechEvidence:
    """Run multiple decoding strategies and retain their competing hypotheses."""
    audio_waveform, duration = decode_wav(audio_bytes)
    hotwords = expected_vocabulary.strip() or None
    primary, words, info = _run_pass(
        model,
        audio_waveform,
        source="context-aware beam search" if hotwords else "beam search",
        temperature=0.0,
        beam_size=5,
        best_of=5,
        hotwords=hotwords,
        include_words=True,
    )
    hypotheses = [primary]

    if thorough:
        exploratory, _, _ = _run_pass(
            model,
            audio_waveform,
            source="exploratory decoding",
            temperature=0.4,
            beam_size=1,
            best_of=5,
            hotwords=None,
            include_words=False,
        )
        hypotheses.append(exploratory)

    unique: dict[str, Hypothesis] = {}
    for item in hypotheses:
        key = normalize_hypothesis(item.text)
        if not key:
            continue
        if key not in unique or item.confidence > unique[key].confidence:
            unique[key] = item
    ranked = sorted(unique.values(), key=lambda item: item.confidence, reverse=True)
    transcript = ranked[0].text if ranked else ""
    confidence = ranked[0].confidence if ranked else 0.0
    response = build_agent_response(ranked, confidence)

    return SpeechEvidence(
        transcript=transcript,
        confidence=confidence,
        duration_seconds=duration,
        language=getattr(info, "language", "en"),
        language_probability=float(getattr(info, "language_probability", 0.0)),
        words=words,
        hypotheses=ranked,
        context=context,
        agent_response=response,
    )

