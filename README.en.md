# AI Avatar Video Maker

Generate continuous character footage in Muse, download it, then use local Whisper + TTS2 to correct the Mandarin narration and edit its timing to the existing mouth movement.

[中文](README.md) · [Setup and commands (Chinese)](docs/usage.md) · [Agent Skill](skills/ai-avatar-video-maker/SKILL.md)

## Two finished examples

Click a poster to watch or download the complete video.

| Talking-head demo · 30 s | Elegant Xiao Ya · 27 s |
|:---:|:---:|
| [<img src="docs/demos/talking-head.jpg" width="250" alt="Watch the full 30-second talking-head sample">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/talking-head-stickers.mp4) | [<img src="docs/demos/xiaoya.jpg" width="250" alt="Watch Xiao Ya speaking and dancing for 27 seconds">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/xiaoya-elegant.mp4) |
| Voice 6 · Captions · Yellow stickers | Voice 10 · Dialogue and dance · Guqin/guzheng |

## 1. Prepare the character and script

Keep the face, clothing and setting consistent. Split speech into short phrases; for action scenes such as Xiao Ya's, plan speaking, standing and turning separately.

![Planning diagram: short talking-head phrases versus dialogue followed by character actions](docs/guide/01-plan.jpg)

## 2. Generate a clip, then hand off its actual tail frame

Review the first clip and choose the cut. **Trim first, then extract the retained clip's last frame.** Upload that exact image with the next Muse request, asking it to continue the same pose, framing and lighting.

![Actual early test: retain 173 frames from a 10-second clip, extract frame 172, upload the same PNG for the next request](docs/guide/02-handoff.jpg)

The handoff figures use an earlier white-shirt test, not reconstructed cut points from the two final samples. An image reference does not guarantee a locked first frame.

## 3. Review the join before assembling

Compare the outgoing last frame with the generated first frame, then play roughly one second on either side. Check face scale, gaze, shoulders, clothing, props, background and lighting. Use a direct cut when they match; remove repeated action without replaying or holding the tail frame.

![Actual tail/reference versus generated first frame, with alignment guides and a continuous audio timeline](docs/guide/03-join.jpg)

**Keep the same outgoing cut used to extract the reference.** If it changes, extract a new reference and review downstream clips. Also watch the complete next clip for character drift. Arrange music or ambience continuously across the timeline.

## 4. Download, correct the Mandarin voice, and align its rhythm

**Muse's native Mandarin output in this production contained wrong or unclear words and unnatural pacing. Both finished samples therefore use replacement TTS2 narration.** After reviewing the footage:

1. Download the video and extract its audio. Use `whisper-cli` for approximate phrase locations, then refine speech boundaries using the waveform and check them against the picture.
2. Generate the **confirmed script** with external TTS2. ASR mistakes must not replace the intended words. The selected voices were auditions 6 and 10, not bundled presets.
3. Split the new audio into phrases, remove excess silence, adjust each duration without changing pitch, and shift it to the corresponding speaking start while keeping pauses.
4. Replace the Muse audio track, review caption timing against the final voice, and mix music separately.

![Local redubbing: download, Whisper timing, TTS2 reading of the correct script, and actual waveforms before and after phrase alignment](docs/guide/04-voice.jpg)

For the talking-head sample, a complete TTS recording was split into **12 phrases**. Its first speech starts around **0.85 s** in the 30-second export, not at zero. This edits audio timing to the existing mouth movement; it does not regenerate the mouth or guarantee phoneme-level synchronization after correcting words. See [the actual process and reusable commands (Chinese)](docs/redubbing.md).

## 5. Finish and export

The talking-head sample adds captions and yellow stickers. Xiao Ya keeps room for movement and pairs dialogue and dance with guqin/guzheng music. Watch the full export for caption errors, audio jumps, visible joins and flashes.

![Same-frame before and after talking-head packaging, alongside Xiao Ya speaking and dancing](docs/guide/05-finish.jpg)

Deliver an **MP4 and an editable Remotion project**. These samples include manual editing and post-production; the base template does not reproduce every effect in one click. See [production notes and music credits](docs/demos/README.md).

## Get started

Requires Python 3, FFmpeg/FFprobe, whisper.cpp `whisper-cli` with a local model, Node.js 18+ and npm. TTS is optional and external; TTS2 is not bundled.

[Setup and complete commands →](docs/usage.md)

Generation happens in your own Muse interface. This repository prepares offline requests; it provides no Muse API/MCP and does not submit or pay for generation. Verify current duration limits, options and prices in Muse.

## Attribution and license

Based on [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo), reusing its caption timeline, some local scripts and Remotion packaging components, with added or adapted Muse handoff and dubbing workflows. See [Attribution and changes](ATTRIBUTION.md). The upstream [MIT license](LICENSE), [notice](NOTICE.md) and [third-party information](THIRD_PARTY.md) are retained. Media and third-party services have separate rights and terms.
