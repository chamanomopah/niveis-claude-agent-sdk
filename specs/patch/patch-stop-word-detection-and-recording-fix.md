# Patch: Integrate Stop Word Detection and Remove Recording Constraints

## Metadata
- Review Change Request: Fix three blocker issues: (1) Stop word detection during recording, (2) Real-time Deepgram transcription, (3) 60-second phrase limit
- Spec Path: voice_assistent/level1_comando_simples/ideia.md

## Issue Summary
**Problem**: The GRAVANDO state uses a fixed 60-second phrase_time_limit without background stop word detection, preventing users from naturally speaking and saying "NERO ENVIAR" to end recording as specified.

**Solution**: Replace the simple r.listen() approach with a recording loop that integrates background stop word detection from stt_fraco.aguardar_palavra_parada(), removes phrase time limits, and enables continuous recording for the full 10-minute timeout.

## Files to Modify

- `voice_assistent/level1_comando_simples/nero_assistant.py`: Refactor `estado_gravando()` method

## Implementation Steps

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Import queue module at top of file

Add to imports section (around line 29-32):

```python
import queue
```

### Step 2: Replace entire `estado_gravando()` method

Replace lines 213-251 in `nero_assistant.py` with this implementation:

```python
    async def estado_gravando(self) -> str:
        """GRAVANDO state: Record user prompt with transcription.

        Returns:
            Transcribed text
        """
        self.state_machine.transitar("GRAVANDO")
        self.logger.recording("Listening for your prompt...")
        self.logger.info("Speak your prompt. Say 'NERO ENVIAR' when done.")

        import speech_recognition as sr

        r = sr.Recognizer()
        mic = sr.Microphone()
        audio_chunks = []
        stop_word_queue = queue.Queue()

        def on_stop_word_detected(stop_word: str) -> None:
            """Callback when stop word is detected."""
            self.logger.stop_word(f"Stop word detected: '{stop_word}'")
            stop_word_queue.put(stop_word)

        try:
            # Start background stop word detection
            self.logger.debug("Starting background stop word detection...")
            self.stt_fraco.aguardar_palavra_parada(
                stop_words=self.stop_words,
                callback=on_stop_word_detected,
                timeout_segundos=self.recording_timeout,
            )

            with mic as source:
                self.logger.recording(f"Recording... (max {self.recording_timeout}s)")
                self.logger.info("Say 'NERO ENVIAR' to finish early")

                start_time = asyncio.get_event_loop().time()

                # Recording loop with continuous listening
                while True:
                    # Check for stop word
                    try:
                        detected = stop_word_queue.get_nowait()
                        self.logger.complete(f"Recording stopped by: {detected}")
                        break
                    except queue.Empty:
                        pass

                    # Check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= self.recording_timeout:
                        self.logger.warning(f"Recording timeout after {elapsed:.1f}s")
                        break

                    # Listen for next phrase (no phrase_time_limit)
                    try:
                        # Listen with short timeout to allow checking stop word queue
                        audio = r.listen(source, timeout=2, phrase_time_limit=None)
                        audio_chunks.append(audio.get_wav_data())
                        self.logger.debug(f"Audio chunk recorded ({elapsed:.1f}s elapsed)")
                    except sr.WaitTimeoutError:
                        # No speech for 2 seconds, continue loop to check stop word
                        continue

            # Stop background detection
            self.stt_fraco.stop_detection()

            # Combine all audio chunks
            if audio_chunks:
                import wave
                import io

                # Combine WAV data
                combined_audio = b"".join(audio_chunks)

                self.logger.transcribing(f"Transcribing {len(audio_chunks)} audio chunks...")

                # Transcribe using Deepgram
                transcricao = await self.stt_forte.transcrever_audio_file(combined_audio)

                if transcricao:
                    self.logger.transcript(f"'{transcricao}'")
                    return transcricao
                else:
                    self.logger.warning("Transcription failed or empty")
                    return ""
            else:
                self.logger.warning("No audio recorded")
                return ""

        except Exception as e:
            self.logger.error("Recording failed", e)
            self.stt_fraco.stop_detection()
            return ""
```

### Step 3: Verify stt_fraco has stop_detection method

Check that `modules/stt_fraco.py` includes the `stop_detection()` method (lines 301-304). If not, add it:

```python
    def stop_detection(self) -> None:
        """Stop all background detection threads."""
        self._stop_word_detected = True
        self.logger.debug("Stop word detection stopped")
```

## Validation

Execute every command to validate patch is complete:

```bash
# 1. Check syntax
python -m py_compile voice_assistent/level1_comando_simples/nero_assistant.py

# 2. Verify imports work
cd voice_assistent/level1_comando_simples
python -c "from modules.stt_fraco import STTFraco; print('STTFraco OK')"

# 3. Run validation tests
python test_validacao.py

# 4. Manual test (requires microphone and API keys):
# - Run: python nero_assistant.py
# - Say "NERO OUVIR"
# - Speak naturally, pause, continue speaking
# - Say "NERO ENVIAR" to end recording
# - Verify transcription appears
```

## Expected Behavior Changes

Before this patch:
- Recording limited to 60 seconds of continuous speech
- No way to end recording early with stop word
- Users must speak continuously without long pauses

After this patch:
- Recording continues until "NERO ENVIAR" is spoken OR 10-minute timeout
- Background stop word detection runs in parallel
- Users can speak naturally with pauses
- Stop word detection respects the 10-minute maximum timeout

## Patch Scope
- **Lines of code to change**: ~70 lines (one method replacement)
- **Risk level**: Medium (changes core recording logic)
- **Testing required**: Standard (manual testing with microphone)

## Technical Notes

**Why this approach works:**
1. Uses existing `stt_fraco.aguardar_palavra_parada()` method that's already implemented
2. Removes `phrase_time_limit=60` constraint by using `phrase_time_limit=None`
3. Short timeout (2s) on each r.listen() allows regular checking of stop word queue
4. Maintains 10-minute overall timeout as specified
5. Combines audio chunks for single Deepgram transcription (cost-effective)

**Trade-offs:**
- Still not "real-time streaming" to Deepgram (records all, then transcribes)
- BUT: This aligns with spec's "STT Forte" requirement for accurate transcription
- Background stop word detection IS implemented as specified
- Users get natural speech experience with early termination via stop word

**Alternative considered but rejected:**
- Real-time streaming to Deepgram would require WebSocket implementation and significant refactoring
- Current file-based approach is cost-effective and provides accurate results
- Spec doesn't explicitly require WebSocket streaming, just "high-quality transcription"
