# Fix: Koda hallucinates on long dictation

**Captured:** 2026-04-13 (laptop session)
**For:** Home PC session — paste the prompt below into Claude Code

## Symptom

Koda transcribes short utterances correctly, but during longer dictation
sessions it starts hallucinating words. Example: Alex said "paid in full"
and it transcribed "patent". Gets worse the longer the session runs.

## Prompt to paste into Claude Code on home PC

```
Koda is hallucinating words during long dictation sessions. Example: I said
"paid in full" and it transcribed "patent". Short utterances are fine — it
only breaks down on longer speeches.

This is a known Whisper behavior. Common causes:
1. Audio buffer growing too long without segmentation (Whisper hallucinates
   on audio >30s or with long silences)
2. No VAD (voice activity detection) to split on natural pauses
3. condition_on_previous_text=True causing cascading errors where one bad
   transcription poisons the next chunk
4. Missing initial_prompt or hallucination suppression params
5. Temperature too high / no fallback temperature ladder

Please:
1. Read voice.py and whatever handles the transcription pipeline to see how
   audio is currently chunked and passed to Whisper
2. Check current Whisper params (model, temperature, condition_on_previous_text,
   no_speech_threshold, logprob_threshold, compression_ratio_threshold)
3. Diagnose which of the above is causing hallucination on long audio
4. Propose a fix BEFORE implementing (Alex's workflow rule: proposals before
   building). Likely candidates: add VAD-based chunking (silero-vad or
   webrtcvad), set condition_on_previous_text=False, tune thresholds, or
   switch to faster-whisper with built-in VAD
5. After approval, implement and test with a long dictation to verify

ALSO check for conflicting speech-to-text software running on the machine:
- Koda has NO detection of other STT apps (Dragon, Wispr Flow, Windows
  Speech Recognition / Win+H, Otter, Talon, VoiceAttack, Cortana)
- Koda opens the mic in SHARED mode via sounddevice.InputStream
  (voice.py:1050, voice.py:1650) — another STT app recording at the
  same time can corrupt the audio buffer and produce exactly this
  "long dictation hallucinates" symptom
- Koda's only single-instance check is a Windows mutex for OTHER Koda
  instances (voice.py:1726 _acquire_single_instance)
- Global hotkey (ctrl+space / F-keys) via the keyboard library uses
  low-level Windows hooks — another app grabbing the same combo can
  suppress or double-fire
- SAPI5 TTS read-back (voice.py:775) can clash with Windows Narrator
  or other TTS engines

Before assuming the fix is a Whisper pipeline issue, ask me to run:
  Get-Process | Where-Object {$_.ProcessName -match "wispr|dragon|otter|
  talon|voiceattack|speech"}
in PowerShell on the machine that's hallucinating, and confirm no other
STT tool is active. If one is, that may be the whole problem.

Repo: C:\Users\alex\Projects\koda
Relevant handovers: docs/sessions/
```
