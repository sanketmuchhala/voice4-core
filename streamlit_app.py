"""Voice 4.0: server-side, accent-flexible English speech evidence demo."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from voice_engine import SpeechEvidence, analyze_audio

APP_DIR = Path(__file__).resolve().parent
MODEL_DIR = APP_DIR / ".models"

CONTEXTS = {
    "Customer name": "Capturing the caller's name. Exact spelling may be consequential.",
    "Booking code": "Capturing an alphanumeric booking code. Every character is consequential.",
    "Street address": "Capturing a street address. Local spelling and pronunciation may differ.",
    "General English": "General English conversation without assuming a regional accent.",
}

MODEL_OPTIONS = {
    "Tiny · fastest": "tiny.en",
    "Base · recommended": "base.en",
    "Small · more accurate": "small.en",
}


st.set_page_config(
    page_title="Voice 4.0 · Phonetic Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --signal: #d6ff3f; --ink: #10151b; --blue: #335cff; --alert: #ff674d; }
    .stApp { background: #f2f4ee; color: var(--ink); }
    [data-testid="stSidebar"] { background: #111823; }
    [data-testid="stSidebar"] * { color: #f7f8f3; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stTextInput input { background: #202a37; border-color: #536071; }
    .v4-kicker { font-family: ui-monospace, monospace; font-weight: 800; letter-spacing: .11em; font-size: .78rem; }
    .v4-hero { padding: 2.2rem 0 2.8rem; border-bottom: 1px solid #cfd4cd; margin-bottom: 2rem; }
    .v4-hero h1 { font-size: clamp(3rem, 7vw, 6.8rem); line-height: .91; letter-spacing: -.06em; margin: .8rem 0 1.2rem; }
    .v4-hero em { color: var(--blue); font-family: Georgia, serif; font-weight: 400; }
    .v4-hero p { max-width: 760px; font-size: 1.18rem; color: #535c61; }
    .evidence-card { min-height: 300px; padding: 1.35rem; background: #111823; color: white; border-top: 5px solid #526071; }
    .evidence-card.signal { border-color: var(--signal); }
    .evidence-card.alert { border-color: var(--alert); }
    .evidence-label { color: #9ba6b4; font-family: ui-monospace, monospace; font-size: .72rem; font-weight: 800; letter-spacing: .08em; }
    .evidence-card h3 { margin: .45rem 0 1.2rem; font-size: 1.25rem; }
    .evidence-card .big-copy { font-family: Georgia, serif; font-size: 1.35rem; line-height: 1.35; }
    .confidence-bar { height: 7px; background: #303b48; margin: 1.2rem 0 .35rem; }
    .confidence-bar i { display:block; height:100%; background: var(--signal); }
    .candidate { padding: .65rem 0; border-bottom: 1px solid #36404e; }
    .candidate:last-child { border-bottom: 0; }
    .candidate small { display:block; color:#9ba6b4; margin-top:.2rem; }
    .agent-card { background: var(--signal); color: var(--ink); padding: 1.35rem; min-height: 300px; border-top: 5px solid #9fc800; }
    .agent-card blockquote { font-family: Georgia, serif; font-size: 1.35rem; line-height: 1.4; margin: 1.6rem 0; }
    .truth-note { padding: 1rem 1.2rem; border-left: 4px solid var(--blue); background: white; margin: 1.5rem 0; }
    div.stButton > button[kind="primary"] { background: var(--ink); color:white; border:0; border-radius:0; min-height: 3rem; font-weight:800; }
    div[data-testid="stAudioInput"] { border: 1px solid #cfd4cd; background: white; padding: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_model(model_name: str):
    from faster_whisper import WhisperModel

    MODEL_DIR.mkdir(exist_ok=True)
    return WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR),
    )


def render_speech_button(text: str) -> None:
    encoded = json.dumps(text)
    components.html(
        f"""
        <button id="speak" style="width:100%;min-height:42px;background:#10151b;color:white;
        border:0;font:700 14px system-ui;cursor:pointer;">Play agent response</button>
        <script>
        document.getElementById('speak').onclick = () => {{
          speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance({encoded});
          utterance.lang = 'en';
          utterance.rate = 0.94;
          speechSynthesis.speak(utterance);
        }};
        </script>
        """,
        height=50,
    )


def render_results(evidence: SpeechEvidence) -> None:
    confidence_percent = round(evidence.confidence * 100)
    duration = f"{evidence.duration_seconds:.1f}s" if evidence.duration_seconds else "unknown"
    transcript = html.escape(evidence.transcript)
    agent_response = html.escape(evidence.agent_response)
    left, middle, right = st.columns(3, gap="small")

    with left:
        st.markdown(
            f"""
            <div class="evidence-card alert">
              <div class="evidence-label">01 / CONVENTIONAL STT</div>
              <h3>Top transcript</h3>
              <div class="big-copy">“{transcript}”</div>
              <div class="confidence-bar"><i style="width:{confidence_percent}%"></i></div>
              <small>{confidence_percent}% sequence confidence</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with middle:
        candidate_html = "".join(
            f'<div class="candidate"><strong>{html.escape(item.text)}</strong>'
            f'<small>{round(item.confidence * 100)}% · {item.source}</small></div>'
            for item in evidence.hypotheses
        )
        st.markdown(
            f"""
            <div class="evidence-card signal">
              <div class="evidence-label">02 / RETAINED EVIDENCE</div>
              <h3>Audio + hypotheses</h3>
              <small>Raw WAV retained · {duration} · English model</small>
              {candidate_html or '<div class="candidate">No speech hypothesis</div>'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="agent-card">
              <div class="evidence-label" style="color:#435600">03 / UNIFIED AGENT</div>
              <h3>Resolve or clarify</h3>
              <blockquote>{agent_response}</blockquote>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_speech_button(evidence.agent_response)

    with st.expander("Inspect word-level evidence"):
        if evidence.words:
            st.dataframe(
                [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "confidence": (
                            round(word.probability * 100, 1)
                            if word.probability is not None
                            else None
                        ),
                    }
                    for word in evidence.words
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No word-level evidence was returned for this recording.")

    st.download_button(
        "Download evidence bundle",
        data=json.dumps(evidence.to_dict(), indent=2),
        file_name="voice4-evidence.json",
        mime="application/json",
    )


with st.sidebar:
    st.markdown('<div class="v4-kicker">VOICE / SIGNAL LAB</div>', unsafe_allow_html=True)
    st.title("Capture settings")
    context_name = st.selectbox("Conversation task", list(CONTEXTS), index=0)
    model_label = st.selectbox("Local English model", list(MODEL_OPTIONS), index=1)
    expected_vocabulary = st.text_input(
        "Expected vocabulary",
        placeholder="Names, locations, product terms…",
        help="Optional terms that may appear in this call. They guide decoding without fixing an accent.",
    )
    thorough = st.toggle(
        "Generate alternate hypothesis",
        value=True,
        help="Runs a second decoding strategy. It is slower but can expose ambiguity.",
    )
    st.markdown("---")
    st.caption("The first use downloads the selected Whisper model into `voice4-demo/.models`. Audio is processed by this Streamlit server, not the browser speech service.")

st.markdown(
    """
    <section class="v4-hero">
      <div class="v4-kicker">SERVER-SIDE SPEECH EVIDENCE / MVP 02</div>
      <h1>Speak naturally.<br><em>Keep the evidence.</em></h1>
      <p>Record English in your natural accent. A local English speech model retains the audio,
      word timing, decoding confidence, and competing interpretations before the agent responds.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="truth-note"><strong>Active context:</strong> {CONTEXTS[context_name]}</div>',
    unsafe_allow_html=True,
)

audio_value = st.audio_input(
    "Record your voice",
    sample_rate=16_000,
    help="Press record, speak naturally, then stop. The recording is uploaded to this Streamlit server as WAV audio.",
)

if audio_value:
    audio_bytes = audio_value.getvalue()
    st.audio(audio_bytes, format="audio/wav")
    current_key = hashlib.sha256(
        audio_bytes
        + MODEL_OPTIONS[model_label].encode()
        + context_name.encode()
        + expected_vocabulary.encode()
        + str(thorough).encode()
    ).hexdigest()

    if st.button("Analyze speech evidence", type="primary", use_container_width=True):
        try:
            with st.status("Loading the local speech model…", expanded=True) as status:
                model = load_model(MODEL_OPTIONS[model_label])
                status.write("Transcribing English speech and retaining word timing…")
                evidence = analyze_audio(
                    model,
                    audio_bytes,
                    context=CONTEXTS[context_name],
                    expected_vocabulary=expected_vocabulary,
                    thorough=thorough,
                )
                st.session_state["voice4_evidence"] = evidence
                st.session_state["voice4_key"] = current_key
                status.update(label="Evidence bundle ready", state="complete", expanded=False)
        except ModuleNotFoundError:
            st.error("`faster-whisper` is not installed. Run `python3 -m pip install -r requirements.txt`, then restart the app.")
        except Exception as exc:
            st.exception(exc)

    if st.session_state.get("voice4_key") == current_key:
        render_results(st.session_state["voice4_evidence"])
else:
    st.info("Record a short name, booking code, address, or sentence to begin.")

st.markdown(
    """
    <div class="truth-note">
      <strong>MVP boundary:</strong> Whisper is designed for varied speech, but no model can guarantee
      perfect recognition for every English accent or noisy environment. This design makes uncertainty
      visible and retains the raw audio so the agent can clarify instead of silently guessing.
    </div>
    """,
    unsafe_allow_html=True,
)

