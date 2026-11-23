# Voice 4.0 Phonetic Agent Demo

The primary MVP is now a Streamlit application that records speech in the browser and performs transcription on the Python server with local `faster-whisper`. It does not depend on the browser vendor's speech-recognition service.

## Run locally

From this directory, create an environment and install the dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run streamlit_app.py
```

Then visit the Local URL printed by Streamlit, normally `http://localhost:8501`.

The first analysis downloads the selected Whisper model into `.models/`. `base.en` is the recommended balance for the MVP.

## What it demonstrates

- Live microphone recording with `st.audio_input`
- Server-side English transcription across varied accents
- Word timestamps and decoding confidence
- Retained audio, alternate decoding hypotheses, and task context
- A unified-agent decision to clarify only consequential uncertainty
- Customer-name, booking-code, street-address, and general-English contexts

Microphone capture requires browser permission and HTTPS (or localhost). The static `dist/` version remains available as the earlier browser-only prototype, but the Streamlit application is the supported version.
