# Lesson dubbing demo (source)

Not published: Jekyll skips folders starting with `_`. The page is `../lesson-demo/`.

How the four videos were made (12 Oct 2026):
1. `lines.json`: the English script (262 characters). Voiced by Sarvam text-to-speech, `bulbul:v3`, speaker `kavya`,
   pace 1.0, 44.1 kHz, `enable_preprocessing` on (numbers and ₹ read as words).
2. `slide.html` + `shot.mjs`: four slides rendered at 1280×720; ffmpeg joins each slide with its line plus 0.4 s of
   silence: `en.mp4`, 22.7 s.
3. Sarvam dubbing job: `src_lang en-IN`, targets `hi-IN ta-IN ml-IN`, `voice_cloning false`, `voice_id kavya`,
   `pace_preset normal`, `register modern-colloquial` (first version: `moderate` and `academic`, too slow and formal), `disable_watermark true`, exports video, audio and SRT.
   `poll.py` follows the job; `fetch2.py` downloads every export (`poll.py` stopped before all nine were listed).
4. Each MP4 is remuxed with `-movflags +faststart` so it starts before it has fully downloaded.

The key is read from a local `.key` file that is never committed.

`test_dub.mjs` checks the page logic on WebM copies (this machine's Chromium cannot decode H.264): each language
loads its own file, switching keeps the position, no sideways scroll at 375 px, and no request leaves the site. Its
server answers byte ranges as GitHub Pages does; without them a browser cannot seek a video.
