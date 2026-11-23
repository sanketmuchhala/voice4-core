const contexts = {
  name: {
    text: "Capturing the caller’s name. Exact spelling may be consequential.",
    old: "The top name transcript is silently accepted.",
    new: "The audio and alternate name hypotheses remain available."
  },
  booking: {
    text: "Capturing an alphanumeric booking code. Every character is consequential.",
    old: "The top booking-code transcript drives the lookup.",
    new: "Competing letters and digits can trigger a confirmation."
  },
  address: {
    text: "Capturing a street address. Local spelling and pronunciation may differ.",
    old: "The first address transcript is sent to validation.",
    new: "Alternate place-name hypotheses are preserved for resolution."
  },
  general: {
    text: "General English conversation with no assumed regional accent.",
    old: "Only the browser’s top English transcript survives.",
    new: "The captured audio and recognition alternatives stay together."
  }
};

const query = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const els = {
  status: query("#captureStatus"), transcript: query("#liveTranscript"), transcriptText: query("#transcriptText"),
  sttConfidence: query("#sttConfidence"), sttConfidenceLabel: query("#sttConfidenceLabel"),
  signalEvidence: query("#signalEvidence"), candidateList: query("#candidateList"),
  contextText: query("#contextText"), agentResponse: query("#agentResponse"),
  decisionActions: query("#decisionActions"), oldOutcome: query("#oldOutcome"),
  newOutcome: query("#newOutcome"), waveform: query("#waveform"), record: query("#recordButton"),
  playCapture: query("#playCapture"), run: query("#runAnalysis"), speak: query("#speakAgent"),
  accent: query("#accentProfile"), browserNote: query("#browserNote"), listeningLabel: query("#listeningLabel")
};

let activeContext = "name";
let recognition = null;
let mediaRecorder = null;
let mediaStream = null;
let audioContext = null;
let analyser = null;
let animationFrame = null;
let audioChunks = [];
let captureUrl = null;
let captureStartedAt = 0;
let captureDuration = 0;
let isListening = false;
let currentTranscript = "";
let currentConfidence = null;
let hypotheses = [];
let agentSpeech = "";
let runTimers = [];

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function buildWaveform() {
  const heights = [18,31,44,25,64,38,78,43,58,24,84,52,35,72,48,91,57,32,68,43,80,36,61,29,74,46,88,38,65,26,55,42,76,34,62,47,81,30,53,69,39,73,45,86,28,58,41,70];
  els.waveform.innerHTML = heights.map((height, index) => `<i style="--h:${height}%;--delay:-${index * 0.035}s"></i>`).join("");
}

function setNote(message, type = "") {
  els.browserNote.textContent = message;
  els.browserNote.className = `browser-note ${type}`.trim();
}

function setStage(stageId, state) {
  const stage = query(`#${stageId}Stage`);
  const label = query(`#${stageId}State`);
  stage.classList.remove("active", "complete");
  if (state === "active") {
    stage.classList.add("active");
    label.textContent = "ANALYZING";
  } else if (state === "complete") {
    stage.classList.add("complete");
    label.textContent = "COMPLETE";
  } else {
    label.textContent = stageId === "transcript" ? "READY" : "WAITING";
  }
}

function resetPipeline() {
  runTimers.forEach(clearTimeout);
  runTimers = [];
  setStage("transcript", "idle");
  setStage("evidence", "idle");
  setStage("decision", "idle");
  els.speak.disabled = true;
  els.run.textContent = "Run evidence pass";
  els.run.disabled = !currentTranscript || isListening;
}

function renderContext() {
  const context = contexts[activeContext];
  els.contextText.textContent = context.text;
  els.oldOutcome.textContent = context.old;
  els.newOutcome.textContent = context.new;
}

function formatConfidence(value) {
  return typeof value === "number" && value > 0 ? `${Math.round(value * 100)}%` : "N/A";
}

function renderLiveResult() {
  const text = currentTranscript || "Listening for speech…";
  els.transcript.textContent = text;
  els.transcriptText.innerHTML = currentTranscript
    ? (currentConfidence !== null && currentConfidence < .78 ? `<mark>${escapeHtml(currentTranscript)}</mark>` : escapeHtml(currentTranscript))
    : "Your live transcript will appear here.";
  const confidencePercent = currentConfidence === null ? 0 : Math.max(4, Math.round(currentConfidence * 100));
  els.sttConfidence.style.width = `${confidencePercent}%`;
  els.sttConfidenceLabel.textContent = formatConfidence(currentConfidence);
}

function collectResults(results) {
  const transcriptParts = [];
  const confidenceValues = [];
  const alternatives = new Map();

  for (let index = 0; index < results.length; index += 1) {
    const result = results[index];
    const best = result[0];
    transcriptParts.push(best.transcript.trim());
    if (best.confidence > 0) confidenceValues.push(best.confidence);

    for (let altIndex = 0; altIndex < result.length; altIndex += 1) {
      const alternative = result[altIndex];
      const phrase = alternative.transcript.trim();
      if (!phrase) continue;
      const existing = alternatives.get(phrase.toLowerCase());
      const confidence = alternative.confidence > 0 ? alternative.confidence : Math.max(.45, .9 - altIndex * .11);
      if (!existing || confidence > existing.confidence) alternatives.set(phrase.toLowerCase(), { phrase, confidence });
    }
  }

  currentTranscript = transcriptParts.join(" ").replace(/\s+/g, " ").trim();
  currentConfidence = confidenceValues.length
    ? confidenceValues.reduce((sum, value) => sum + value, 0) / confidenceValues.length
    : null;
  hypotheses = [...alternatives.values()].sort((a, b) => b.confidence - a.confidence).slice(0, 5);
  if (currentTranscript && !hypotheses.some(item => item.phrase.toLowerCase() === currentTranscript.toLowerCase())) {
    hypotheses.unshift({ phrase: currentTranscript, confidence: currentConfidence || .9 });
  }
  renderLiveResult();
  els.run.disabled = !currentTranscript || isListening;
}

function startMeter(stream) {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return;
  audioContext = new AudioContextClass();
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 128;
  audioContext.createMediaStreamSource(stream).connect(analyser);
  const values = new Uint8Array(analyser.frequencyBinCount);
  const bars = $$("#waveform i");

  const update = () => {
    analyser.getByteFrequencyData(values);
    bars.forEach((bar, index) => {
      const value = values[Math.floor(index * values.length / bars.length)] || 0;
      bar.style.height = `${Math.max(8, Math.min(100, value / 1.8))}%`;
    });
    animationFrame = requestAnimationFrame(update);
  };
  update();
}

function stopMeter() {
  if (animationFrame) cancelAnimationFrame(animationFrame);
  animationFrame = null;
  if (audioContext) audioContext.close().catch(() => {});
  audioContext = null;
  analyser = null;
}

function createRecognition() {
  if (!SpeechRecognition) return null;
  const instance = new SpeechRecognition();
  instance.lang = els.accent.value;
  instance.continuous = true;
  instance.interimResults = true;
  instance.maxAlternatives = 5;

  instance.onresult = event => {
    collectResults(event.results);
    els.status.textContent = "HEARING SPEECH";
  };
  instance.onerror = event => {
    const messages = {
      "no-speech": "No clear speech was detected. Try again and speak closer to the microphone.",
      "audio-capture": "The microphone could not be captured.",
      "not-allowed": "Microphone or speech-recognition permission was denied.",
      "network": "The browser speech service could not be reached."
    };
    setNote(messages[event.error] || `Speech recognition stopped: ${event.error}.`, "error");
  };
  instance.onend = () => {
    if (isListening) stopCapture(false);
  };
  return instance;
}

async function startCapture() {
  if (!navigator.mediaDevices?.getUserMedia) {
    setNote("This browser does not expose microphone capture to the page.", "error");
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
    });
  } catch (error) {
    setNote("Microphone access was not granted. Allow access in the browser and try again.", "error");
    return;
  }

  if (captureUrl) URL.revokeObjectURL(captureUrl);
  captureUrl = null;
  currentTranscript = "";
  currentConfidence = null;
  hypotheses = [];
  audioChunks = [];
  captureStartedAt = performance.now();
  isListening = true;
  resetPipeline();
  renderLiveResult();
  els.record.classList.add("listening");
  els.record.setAttribute("aria-label", "Stop microphone capture");
  els.waveform.classList.add("listening");
  els.status.textContent = "LISTENING — TAP TO STOP";
  els.listeningLabel.textContent = "LIVE TRANSCRIPT";
  els.playCapture.disabled = true;
  setNote(`Listening with ${els.accent.options[els.accent.selectedIndex].text}. Speak naturally, then tap stop.`, "success");
  startMeter(mediaStream);

  if (window.MediaRecorder) {
    try {
      mediaRecorder = new MediaRecorder(mediaStream);
      mediaRecorder.ondataavailable = event => { if (event.data.size) audioChunks.push(event.data); };
      mediaRecorder.onstop = () => {
        if (!audioChunks.length) return;
        const blob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/webm" });
        captureUrl = URL.createObjectURL(blob);
        els.playCapture.disabled = false;
      };
      mediaRecorder.start();
    } catch (_) {
      mediaRecorder = null;
    }
  }

  recognition = createRecognition();
  if (recognition) {
    try {
      recognition.start();
    } catch (_) {
      setNote("Speech recognition could not start. Stop and try another English profile.", "error");
    }
  } else {
    setNote("Audio recording is active, but this browser does not expose live speech recognition.", "error");
  }
}

function stopCapture(stopRecognition = true) {
  if (!isListening) return;
  isListening = false;
  captureDuration = Math.max(.1, (performance.now() - captureStartedAt) / 1000);
  if (stopRecognition && recognition) {
    try { recognition.stop(); } catch (_) {}
  }
  recognition = null;
  if (mediaRecorder?.state === "recording") mediaRecorder.stop();
  mediaStream?.getTracks().forEach(track => track.stop());
  mediaStream = null;
  stopMeter();
  els.record.classList.remove("listening");
  els.record.setAttribute("aria-label", "Start microphone capture");
  els.waveform.classList.remove("listening");
  els.status.textContent = currentTranscript ? "CAPTURE COMPLETE" : "NO TRANSCRIPT CAPTURED";
  els.signalEvidence.textContent = `Audio retained · ${captureDuration.toFixed(1)}s · ${els.accent.options[els.accent.selectedIndex].text}`;
  els.run.disabled = !currentTranscript;
  if (currentTranscript) {
    setNote("Capture complete. Run the evidence pass to compare the transcript and alternatives.", "success");
  }
}

function renderCandidates() {
  const items = hypotheses.length ? hypotheses : [{ phrase: currentTranscript, confidence: currentConfidence || .8 }];
  els.candidateList.innerHTML = items.slice(0, 4).map((item, index) => {
    const score = Math.round((item.confidence || Math.max(.45, .9 - index * .11)) * 100);
    return `<div class="candidate">
      <strong>${escapeHtml(item.phrase)}</strong><span>${score}% hypothesis</span>
      <div class="candidate-meter"><i style="width:${score}%"></i></div>
    </div>`;
  }).join("");
}

function buildAgentDecision() {
  const top = hypotheses[0]?.phrase || currentTranscript;
  const second = hypotheses.find(item => item.phrase.toLowerCase() !== top.toLowerCase())?.phrase;
  if (second) {
    agentSpeech = `I heard ${top}. Another possibility is ${second}. Which one is correct?`;
    els.agentResponse.textContent = `“I heard ‘${top}.’ Another possibility is ‘${second}.’ Which is correct?”`;
    els.decisionActions.innerHTML = `<button class="choice-chip">${escapeHtml(top)}</button><button class="choice-chip">${escapeHtml(second)}</button><button class="choice-chip">Neither</button>`;
  } else {
    agentSpeech = `I heard ${top}. Did I get that right?`;
    els.agentResponse.textContent = `“I heard ‘${top}.’ Did I get that right?”`;
    els.decisionActions.innerHTML = `<button class="choice-chip">Yes, correct</button><button class="choice-chip">No, correct it</button>`;
  }
}

function runPipeline() {
  if (!currentTranscript) return;
  resetPipeline();
  renderCandidates();
  buildAgentDecision();
  els.run.disabled = true;
  els.run.textContent = "Analyzing signal…";
  setStage("transcript", "active");
  runTimers.push(setTimeout(() => {
    setStage("transcript", "complete");
    setStage("evidence", "active");
  }, 650));
  runTimers.push(setTimeout(() => {
    setStage("evidence", "complete");
    setStage("decision", "active");
  }, 1450));
  runTimers.push(setTimeout(() => {
    setStage("decision", "complete");
    els.speak.disabled = false;
    els.run.disabled = false;
    els.run.textContent = "Run again";
  }, 2250));
}

function speakAgent() {
  if (!("speechSynthesis" in window) || !agentSpeech) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(agentSpeech);
  utterance.rate = .94;
  utterance.lang = els.accent.value;
  window.speechSynthesis.speak(utterance);
}

function playCapture() {
  if (!captureUrl) return;
  const audio = new Audio(captureUrl);
  els.waveform.classList.add("playing");
  els.playCapture.textContent = "Playing…";
  audio.onended = () => {
    els.waveform.classList.remove("playing");
    els.playCapture.textContent = "Play capture";
  };
  audio.play().catch(() => setNote("The captured audio could not be played.", "error"));
}

$$('.scenario-tab').forEach(tab => tab.addEventListener("click", () => {
  activeContext = tab.dataset.context;
  $$('.scenario-tab').forEach(item => {
    const selected = item === tab;
    item.classList.toggle("active", selected);
    item.setAttribute("aria-selected", selected);
  });
  renderContext();
  resetPipeline();
}));

els.record.addEventListener("click", () => isListening ? stopCapture() : startCapture());
els.playCapture.addEventListener("click", playCapture);
els.run.addEventListener("click", runPipeline);
els.speak.addEventListener("click", speakAgent);
els.decisionActions.addEventListener("click", event => {
  if (!event.target.matches(".choice-chip")) return;
  $$(".choice-chip").forEach(chip => chip.classList.toggle("selected", chip === event.target));
});
els.accent.addEventListener("change", () => {
  if (isListening) stopCapture();
  setNote(`Ready for ${els.accent.options[els.accent.selectedIndex].text}. Accent selection guides recognition but does not guarantee accuracy.`);
});

buildWaveform();
renderContext();
resetPipeline();
if (!SpeechRecognition) {
  setNote("This browser can record audio but does not expose live speech recognition. Try a browser with Web Speech Recognition support.", "error");
}
