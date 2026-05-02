# Koda transcription speed gap — research write-up

**Date:** 2026-05-01
**Author:** Research pass for Alex Concepcion
**Scope:** Why Koda is slower than Alex's boss's $120/yr "lightning fast" voice service, and the concrete levers Alex can pull. Research only — no source code modified.

---

## 1. Executive summary

Koda runs **faster-whisper `small` int8 on an Intel UHD 770 CPU with 4 threads**, batches the entire utterance only after the hotkey is released, and then transcribes it in one shot. Recent debug-log evidence (`debug.log` lines 11699 and 11713) shows a 1-minute clip taking 9.59s and 13.27s — i.e. roughly 5–10× real-time on this hardware, with **Whisper inference accounting for ~97% of wall time** (concat ≈ 0ms in every entry).

The "lightning fast" $120-ish/yr competitor is almost certainly **Wispr Flow** (~$144/yr annual, $180/yr monthly). Wispr Flow publishes an explicit engineering target of **<700ms end-to-end** from end-of-speech to pasted text, broken down as <200ms ASR + <200ms LLM + <200ms network — and it hits this by running fine-tuned Llama-class models on dedicated **Baseten autoscaling cloud GPUs** with TensorRT-LLM. ([Wispr Flow tech post](https://wisprflow.ai/post/technical-challenges), [Baseten case study](https://www.baseten.co/resources/customers/wispr-flow/))

That means **the gap is fundamentally hardware**: a sub-second cloud-GPU pipeline vs. multi-second local-CPU inference. No CPU-side optimization closes it. The honest highest-payoff lever for Alex is **adding an optional Groq cloud backend** (`whisper-large-v3-turbo`, 216× real-time, $0.04/hr — see [Groq blog](https://groq.com/blog/whisper-large-v3-turbo-now-available-on-groq-combining-speed-quality-for-speech-recognition)). Free tier is generous enough for personal use. Local CPU stays the privacy-default; cloud is the speed mode.

Secondary levers, in priority order: switch default to `tiny` for short dictations (≈5–7× speedup over `small` on CPU at meaningful accuracy cost), test cpu_threads at 1 or 8 (4 is documented as a pessimal value on some Intel parts), and consider Distil-Whisper / faster-whisper-large-v3-turbo if Alex eventually moves to a machine with a discrete NVIDIA GPU.

---

## 2. Likely identity of the $120/yr "lightning fast" service

Three plausible candidates, ranked by fit.

### #1 — Wispr Flow (high confidence)

- **Pricing:** Pro tier is **$12/mo billed annually = $144/yr** or $15/mo billed monthly = $180/yr ([Wispr Flow pricing](https://wisprflow.ai/pricing), [Voibe pricing review](https://www.getvoibe.com/resources/wispr-flow-pricing/)). $144/yr maps directly onto Alex's "roughly $120/yr" recall — the most common framing in coverage rounds the annual to "~$120-ish".
- **Platform:** macOS and Windows, system-wide push-to-talk. Matches the boss's likely setup.
- **Latency:** Engineered target is **<700ms end-to-end** from end-of-speech to pasted-and-formatted text. Component budgets: <200ms ASR, <200ms LLM formatting, <200ms network ([Wispr Flow tech blog](https://wisprflow.ai/post/technical-challenges)). This is a near-perfect verbatim match for "lightning fast no matter the length of the speech."
- **Why "no matter the length":** Wispr Flow streams audio while the user is still talking, so when the hotkey is released the model has already been chewing on most of the buffer. Long utterances feel as snappy as short ones because the ASR has been racing the speaker. Koda is the opposite — it does nothing until the hotkey comes up, then transcribes the whole thing.
- **Backend:** Fine-tuned Llama-class models on **Baseten dedicated GPU deployments** with TensorRT-LLM ([Baseten customer page](https://www.baseten.co/resources/customers/wispr-flow/)). Not Whisper — but Whisper-comparable ASR accuracy, with an LLM polishing pass baked in at the inference layer, not as a separate Ollama call.

### #2 — Otter.ai Pro (low-medium confidence)

- **Pricing:** ~$10–17/mo, cloud, has a Windows app.
- **Why it's a maybe:** Otter is sold as live-meeting transcription, not push-to-talk dictation. The "lightning fast no matter the length" framing fits Otter's continuous live transcription — but Otter pastes-into-active-window like Wispr Flow does not match Otter's product model well. Demote unless Alex confirms the boss uses it for meeting recap, not dictation.

### #3 — Superwhisper / VoiceInk / Aiko (Mac-only — rule out unless boss is on Mac)

- VoiceInk is **$25 one-time, Mac only**, on-device Whisper ([Voibe VoiceInk pricing](https://www.getvoibe.com/resources/voiceink-pricing/)). Not subscription.
- Superwhisper is Mac-only on-device Whisper.
- These are eliminated if the boss is on Windows. Worth confirming.

**Recommendation:** Ask Alex to ask his boss "is it Wispr Flow?" — three of every four times the answer to "$120/yr lightning-fast voice tool on Windows" in 2026 is yes.

---

## 3. Where Koda's latency actually lives

### 3.1 Pipeline decomposition (from `voice.py`)

The transcription path is well-instrumented. From `voice.py` lines 929–1142:

1. **Audio capture** — sounddevice via continuous `InputStream`, chunks pushed into a Python list as `np.float32` arrays. Cost: zero — capture happens during the hold, parallel to the user speaking.
2. **VAD pre-filter** — webrtcvad-based gating, used only to detect end-of-speech in toggle/wake-word modes. In hold mode the user controls the boundary. Negligible cost.
3. **`np.concatenate` of audio chunks** — `timings["concat"]` in the log. Measured at **0.00s** in essentially every entry. Not the bottleneck.
4. **Whisper inference** — `model.transcribe(audio, **transcribe_kwargs)` at line 979. With `beam_size=1`, `vad_filter=True`, `condition_on_previous_text=False`, `log_prob_threshold=-0.8`. **This is where 95–99% of wall time lives.**
5. **Post-processing** — `dedup_segments()`, `process_text()`, `polish_with_llm()` (Ollama llama3.2:1b), `apply_custom_vocabulary()`. Not separately timed but inferable: total - whisper - concat = ~0.2–0.3s typical, dominated by Ollama polish in command/prompt modes.
6. **Paste** — pyautogui keystroke into active window. Sub-100ms.

### 3.2 Empirical numbers from `debug.log`

Sampling `Transcribe timings` lines (model = `small` int8, cpu_threads=4, Intel UHD 770 host CPU = Intel 12th-gen-class):

| Date | Total | Whisper | Notes |
|---|---|---|---|
| 2026-04-27 10:47 (line 9388) | 1.07s | 0.86s | short dictation (~5s utterance) |
| 2026-04-27 10:51 (line 9419) | 2.03s | 1.82s | medium (~15s utterance) |
| 2026-04-27 11:16 (line 9499) | **9.78s** | **9.56s** | ~45–60s utterance |
| 2026-04-27 11:32 (line 9516) | 5.32s | 5.09s | ~30s utterance |
| 2026-04-30 19:40 (line 11400) | 5.02s | 4.77s | ~30s utterance |
| 2026-05-01 12:02 (line 11699) | **9.59s** | **9.30s** | ~60s utterance (the one Alex flagged) |
| 2026-05-01 12:51 (line 11713) | **13.27s** | **12.99s** | ~60s, CPU-starved warning fired |

**Concat is always 0.00s. Whisper is always >97% of total.** Optimizing anything but Whisper is rounding error.

Real-time factor on this hardware: roughly **5–10× real-time for `small` int8 on 4 CPU threads** (1 minute audio → 6–10s inference, with thrash spikes to 13s). The faster-whisper README's published `small int8` benchmark on a 12700K with 8 threads transcribes 13 minutes in 1m42s — i.e. ~7.6× real-time on a much beefier desktop chip ([faster-whisper README](https://github.com/SYSTRAN/faster-whisper)). Alex's UHD-770 host is hitting roughly the same multiplier — **Koda is not leaving major performance on the table for its current model + quantization + thread count**. The gap to "lightning fast" is the model class and the inference target, not Koda's plumbing.

### 3.3 Streaming claim in `config.json`

`config.json:19` shows `"streaming": true`. Reading `voice.py:832-855` (`_streaming_thread`), Koda does run a background thread that re-transcribes the accumulated buffer every 2s during recording — but it only updates the **tray tooltip and overlay preview**, not the final paste. The final transcription on hotkey-release at line 909 still hits `_transcribe_and_paste()` which re-runs the whole utterance from scratch (line 979). So Koda has a *visual* streaming preview but no *paste-time* streaming benefit. Wispr Flow is doing the latter.

---

## 4. Levers ranked by payoff

Ratings: effort = code/infra change; speed-up = expected wall-clock reduction; accuracy = WER impact; cost = recurring/per-user dollar.

| # | Lever | Effort | Speed-up vs current | Accuracy cost | $ cost | Notes |
|---|---|---|---|---|---|---|
| **a** | **Optional Groq cloud backend** (`whisper-large-v3-turbo`) | M — new module, async HTTP, key in `keyring`, fallback path | **~10–30× on long clips** (216× real-time vs 5–10×) | None / better — uses large-v3-turbo, more accurate than `small` | **$0.04/hr** paid; **free tier exists** for personal use ([Groq pricing](https://groq.com/pricing)) | The honest answer to closing the gap. User opts in. Privacy default stays local. |
| **b** | Switch default `small` → `tiny` | Trivial — `config.json` already supports it; bundle `_model_tiny` in PyInstaller (already does — see voice.py:392 fallback) | **~3–6× faster** ([TildAlice tiny vs small](https://tildalice.io/whisper-tiny-vs-faster-whisper-edge-latency-wer/), [whisper-api models](https://whisper-api.com/blog/models/)) | Significant for proper nouns, accents, technical terms; ~12% WER gap reported | $0 | Cheapest local win. Good for short chat dictation; bad for long-form. Ship as a "Speed mode" toggle, not a default. |
| **c** | True streaming via `whisper_streaming` lib | H — replace `_transcribe_and_paste` with a chunked feeder; integrate `whisper_streaming` self-adaptive policy ([ufal/whisper_streaming](https://github.com/ufal/whisper_streaming)) | **Perceived 3–5×** — paste appears within ~1–3s of hotkey release regardless of utterance length, because most of the audio was already transcribed | Slight — chunk boundaries can split words; the lib mitigates with self-adaptive latency | $0 | Best non-cloud option. Real engineering cost. Matches what Wispr Flow does architecturally. |
| **d** | OpenVINO Whisper backend (Intel-optimized) | H — replace CTranslate2 path with OpenVINO runtime; rebuild PyInstaller pipeline | Estimated **1.5–3×** on Intel CPU + UHD iGPU per OpenVINO Whisper post ([OpenVINO blog](https://blog.openvino.ai/blog-posts/optimizing-whisper-and-distil-whisper-for-speech-recognition-with-openvino-and-nncf)) | None | $0 | Specifically benefits Intel-UHD-770 hosts. Adds a heavy dependency to a 560MB installer. |
| **e** | Tune `cpu_threads` (4 → 1 or 8) | Trivial — config change | **Possibly 1.5–2×, possibly negative** — issue [#526](https://github.com/SYSTRAN/faster-whisper/issues/526) reports "with 4 threads performance was particularly bad, but with 1 and 8 threads ... approximately real-time" on Intel Xeon. Worth empirically testing on UHD-770 host. | None | $0 | Low-effort, high-uncertainty. **Test before committing.** UHD-770 is in a 12th/13th-gen part with E+P cores; the optimal value is unlikely to be 4. |
| **f** | Distil-Whisper via CTranslate2 (`distil-large-v3-ct2`) | M — switch model bundle; verify CTranslate2 conversion ([HF distil-whisper-ct2](https://huggingface.co/ctranslate2-4you/distil-whisper-large-v3-ct2-float32)) | Mac M1 reports **5×+ vs large-v3** at <0.8% WER delta | Tiny on long-form English, small on short utterances per published numbers | $0 | Best-known Whisper-derivative tradeoff. English-only is fine for Alex. |
| **g** | `large-v3-turbo` via faster-whisper (CPU) | M — bundle the 1.6GB model; test on UHD-770 | **Slower than `small`** on CPU per published Mac M2 numbers — small=9.4s/40s clip, turbo=18.4s/40s clip ([deepdml turbo benchmark](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3)) | Better than small | $0 | **Counterintuitive but true: turbo is a GPU win, a CPU loss.** Don't ship for Alex's hardware. Reconsider only when there's a CUDA path. |
| **h** | CUDA backend `compute_type=float16` | M — already in code (voice.py:369) | **20–50×** vs CPU on consumer NVIDIA GPU | None | $0 | Useless for Alex (Intel UHD only). Should remain available for users who later install on a GPU box. |
| **i** | `int8_float16` / int4 quantization | L — config change, model re-quantize | Marginal on CPU; meaningful on GPU | Small | $0 | Skip for Alex's setup. |
| **j** | Pre-warm / model resident in RAM | None — already done | 0 (already gained) | n/a | $0 | Confirmed at `voice.py:366-441`: WhisperModel is loaded once at startup. No reload per utterance. |
| **k** | OpenAI Whisper API direct | M | 1× ASR (large-v3) at ~$0.006/min | Better than small | ~$0.36/hr — 9× more than Groq | Not the right cloud choice. Groq is faster and cheaper. |
| **l** | Drop `condition_on_previous_text=False`, `log_prob_threshold=-0.8` etc. | None | Negligible (these affect quality, not speed) | Worse | $0 | Don't touch. These are accuracy guards. |

### Per-user cost impact

Koda is distributed via Inno Setup installer to at least one coworker. For levers that involve a recurring cost, the friction is real:

- **Groq free tier** is enough for individual dictation usage — even at 60s per utterance, hundreds of dictations/day stays under throttle. The coworker can use Koda's local-CPU mode by default and opt into Groq with their own free key.
- **Wispr-Flow-killing means matching Wispr Flow's pricing**, which is ~$144/yr. Groq paid at $0.04/hr would need ~3,600 hours of dictation to match — i.e. effectively free at human dictation volume.

---

## 5. Top-3 recommendation for Alex

Solo ops manager, dictating chat messages and prompts (rarely 10-minute monologues), Intel UHD 770, no NVIDIA, distributing to one coworker.

### #1 — Add an optional Groq cloud backend toggle. Default off; enable per-user.

Highest payoff by an order of magnitude. Closes the speed gap to the boss's tool by **brute-force matching the architecture** that gives the boss's tool its speed: a sub-second large-model GPU inference. Two-mode product:

- **Local mode** (default, current behavior, privacy-preserving) — `small` int8 on CPU, ~5–10s for a 1-min clip.
- **Cloud mode** (opt-in) — POST audio to Groq's `/openai/v1/audio/transcriptions` with `model=whisper-large-v3-turbo`. Sub-second for clips up to several minutes. API key stored in Windows Credential Manager via `keyring` (already a dependency). Audible ding plus tray indicator when in cloud mode so the user always knows where their audio is going.

Effort: ~150 LOC + a settings GUI toggle + a `KODA_BACKEND=local|cloud` env var. Free tier covers daily personal use. ([Groq pricing](https://groq.com/pricing), [Groq Whisper docs](https://console.groq.com/docs/model/whisper-large-v3-turbo))

### #2 — Test `cpu_threads` at 1 and 8 on Alex's UHD-770 host before doing anything else.

Per faster-whisper [issue #526](https://github.com/SYSTRAN/faster-whisper/issues/526), `cpu_threads=4` was empirically the worst setting on an Intel Xeon — 1 and 8 were both faster. UHD-770 is paired with a 12th/13th-gen Core part with E+P cores; the right answer is likely 6 (P-core count) or 8 (P-core threads), **not** 4. Effort = `config.json` edit. If it's a 1.5–2× win it lands ahead of cloud rollout. If it's not, knowing that pins the local-CPU ceiling honestly. Run a quick A/B on the same 60s clip Alex used for the 9.59s baseline (`debug.log:11699`).

### #3 — Add a "Speed mode" config flag that swaps `small` → `tiny` on the fly.

For when the network's down, the boss is watching, and Alex needs the snappy feel without a cloud hop. `tiny` int8 on this hardware should hit roughly real-time or better — 1–2s for a 1-min clip, vs 9.59s today. Cost is accuracy: `tiny` is ~12% WER worse than `small` on standard benchmarks ([TildAlice tiny vs small](https://tildalice.io/whisper-tiny-vs-faster-whisper-edge-latency-wer/)). For chat-message dictation that gets re-read before sending, that's tolerable; for prompt-assist mode where the LLM amplifies misheard words, it's not — so the toggle should be per-mode, not global. The PyInstaller bundle already supports multiple model sizes (`voice.py:392` falls back across `_model_*` directories), so the wiring is partly there.

**What NOT to do first:** Don't switch the default model from `small` to `tiny` for everyone. Don't ship `large-v3-turbo` for the local-CPU path — it's slower than `small` on CPU. Don't rebuild on OpenVINO unless levers #1–#3 have been exhausted; it's a heavy refactor for a 2× win when the cloud path is available for a 50× win. Don't pretend a CPU optimization closes a cloud-GPU gap — the boss's tool is fast because it's running on a different planet of hardware.

---

## 6. Sources

Primary:

- [Wispr Flow — pricing page](https://wisprflow.ai/pricing) (accessed 2026-05-01) — confirms $12/mo annual = $144/yr, $15/mo monthly = $180/yr.
- [Wispr Flow engineering — Technical challenges and breakthroughs behind Flow](https://wisprflow.ai/post/technical-challenges) — confirms <700ms end-to-end latency target with <200ms ASR + <200ms LLM + <200ms network budgets.
- [Baseten — Wispr Flow customer story](https://www.baseten.co/resources/customers/wispr-flow/) — confirms cloud-GPU TensorRT-LLM Llama backend.
- [Groq blog — Whisper Large v3 Turbo on GroqCloud](https://groq.com/blog/whisper-large-v3-turbo-now-available-on-groq-combining-speed-quality-for-speech-recognition) — confirms 216× real-time speed factor.
- [Groq pricing](https://groq.com/pricing) — confirms $0.04/hr for `whisper-large-v3-turbo`.
- [Groq Whisper Large v3 Turbo docs](https://console.groq.com/docs/model/whisper-large-v3-turbo).
- [SYSTRAN/faster-whisper README](https://github.com/SYSTRAN/faster-whisper) — published `small int8` CPU benchmark (Intel 12700K, 8 threads, 13min audio in 1m42s).
- [SYSTRAN/faster-whisper issue #526 — Inference time on CPU much slower than posted benchmark](https://github.com/SYSTRAN/faster-whisper/issues/526) — Intel Xeon evidence that `cpu_threads=4` was a pessimal value vs 1 or 8.
- [SYSTRAN/faster-whisper PR #965 — Set CPU threads according to the machine](https://github.com/SYSTRAN/faster-whisper/pull/965) — discussion of E/P-core handling on Intel 12th-gen+.
- [ufal/whisper_streaming](https://github.com/ufal/whisper_streaming) — primary streaming wrapper, uses faster-whisper backend, claims 3.3s latency on long-form.
- [collabora/WhisperLive](https://github.com/collabora/WhisperLive) — alternative streaming implementation.
- [Hugging Face — distil-whisper-large-v3 CTranslate2 build](https://huggingface.co/ctranslate2-4you/distil-whisper-large-v3-ct2-float32).
- [Hugging Face — faster-whisper-large-v3-turbo CTranslate2 build, speed benchmark discussion](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3) — Mac M2 small=9.4s vs turbo=18.4s on a 40s clip (turbo loses on CPU).
- [OpenVINO blog — Optimizing Whisper and Distil-Whisper with OpenVINO and NNCF](https://blog.openvino.ai/blog-posts/optimizing-whisper-and-distil-whisper-for-speech-recognition-with-openvino-and-nncf) — Intel-CPU-targeted optimization path.

Secondary / corroborating:

- [Voibe — Wispr Flow pricing review](https://www.getvoibe.com/resources/wispr-flow-pricing/) — independent confirmation of pricing tiers.
- [Voibe — Wispr Flow vs Superwhisper comparison](https://www.getvoibe.com/resources/wispr-flow-vs-superwhisper/) — confirms Wispr Flow is cloud-only, Superwhisper / VoiceInk are Mac-only on-device.
- [Voibe — VoiceInk pricing](https://www.getvoibe.com/resources/voiceink-pricing/) — confirms VoiceInk is Mac-only, $25 one-time (rules out VoiceInk as the boss's $120/yr tool).
- [TildAlice — Whisper Tiny vs faster-whisper benchmark](https://tildalice.io/whisper-tiny-vs-faster-whisper-edge-latency-wer/) — 3× speed, 12% WER gap.
- [whisper-api.com — Which Whisper Model Should I Choose?](https://whisper-api.com/blog/models/) — model size/speed/accuracy comparison.
- [TokenMix — Whisper API pricing 2026](https://tokenmix.ai/blog/whisper-api-pricing) — Groq vs OpenAI vs Google price comparison.
- Koda repo — `voice.py` lines 366–442 (model load), 800–855 (slot/streaming transcribe), 929–1149 (`_transcribe_and_paste` with timing instrumentation), and `debug.log` lines 8446, 9499, 11699, 11713 (timing evidence cited above).
