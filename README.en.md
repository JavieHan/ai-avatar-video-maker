# AI Avatar Video Maker

**An AI talking-head workflow powered by agents and scripts, with you in control.** For creators who want continuous character videos from Muse and control over the character, script and voice. A computer-using agent can submit Muse requests and download clips; local scripts extract frames, assemble footage, replace narration, add captions and export an editable project. You review the results and approve key decisions.

[中文](README.md) · [Codex / Claude setup](docs/agent-setup.md) · [Tools and installation](docs/tools.md) · [Commands](docs/usage.md)

| External tool | What it is and where to get it |
|---|---|
| **Muse** | Meta's AI assistant, used here to generate short video clips. [Product](https://ai.meta.com/muse/) · [Download](https://ai.meta.com/muse/download/). Check that image-to-video generation is available to your account. |
| **TTS2 / Breeze TTS 2** | A speech model for narration and voice cloning. [Official project](https://github.com/breezeblue-ai/breeze-tts) · [Community MLX port for Mac](https://huggingface.co/mlx-community/Breeze-TTS-2-mlx). Self-hosted models and outputs are restricted to research and non-commercial use; see the [model license](https://huggingface.co/BreezeBlue/Breeze-TTS-2/blob/main/LICENSE). |

## What you can make

Click a poster to watch or download the full MP4.

| Everyday talking-head · 30 s | Period-style dialogue and movement · 27 s |
|:---:|:---:|
| [<img src="docs/demos/talking-head.jpg" width="250" alt="Watch the complete talking-head sample">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/talking-head-stickers.mp4) | [<img src="docs/demos/xiaoya.jpg" width="250" alt="Watch the complete speaking and dancing sample">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/xiaoya-elegant.mp4) |
| Local narration · Captions · Yellow stickers | Narration · Standing and sleeve movement · Guqin/guzheng |

## The whole workflow

![Generate in Muse, use the retained last frame for the next clip, review and assemble locally, redub with Whisper and TTS2, add captions and graphics, export MP4 and an editable project](docs/guide/00-workflow.jpg)

## Configure Codex / Claude Code

Clone the repository, then run one command to register the project skill and check dependencies:

```bash
git clone https://github.com/JavieHan/ai-avatar-video-maker.git
cd ai-avatar-video-maker
bash setup.sh both
```

Open this directory in Codex or Claude Code, then start with **`$ai-avatar-video-maker`** or **`/ai-avatar-video-maker`**, respectively. See [setup details and a copyable prompt](docs/agent-setup.md).

Run `sh skills/ai-avatar-video-maker/scripts/doctor.sh` to check the environment again. Setup reports missing dependencies; prepare your own Muse access, speech model and media.

## 1. Prepare the character and script

Keep the face, clothing and setting consistent. Split speech into short phrases; plan dialogue, standing and turning in order when the character needs to move.

![Plan short talking-head phrases or dialogue followed by character actions](docs/guide/01-plan.jpg)

## 2. Generate clips and continue from the last retained frame

Review a clip and select the outgoing cut. **Trim first, then extract the retained clip's last frame.** Upload that image to Muse with the next request, continuing the same character, pose, framing and lighting.

![Extract frame 172 from a retained 173-frame clip and upload that PNG as the next image reference](docs/guide/02-handoff.jpg)

## 3. Check the join and assemble

Compare the outgoing last frame with the incoming first frame, then play about one second on either side. Cut directly when the states match, remove repeated action, and keep the outgoing cut used for the reference. Arrange music or ambience continuously across the timeline.

![Compare face scale, shoulders, clothing, background and lighting, with a continuous audio track across the edit](docs/guide/03-join.jpg)

## 4. Download and correct the Mandarin narration

Native Mandarin speech can contain wrong or unclear words or awkward pacing. Both samples retain the footage and replace the narration locally:

1. **Whisper finds timing:** locate phrases in the source audio, then refine speaking boundaries using the waveform and picture.
2. **TTS2 reads the correct script:** generate the selected voice from your final text.
3. **Edit to the mouth's rhythm:** split phrases, trim excess silence, adjust durations without changing pitch, and position each phrase at its speaking start while keeping pauses.
4. **Replace audio and retime captions:** review against the final voice, then mix background music separately.

![Download, Whisper timing, TTS2 reading of the correct script, and actual waveforms before and after phrase alignment](docs/guide/04-voice.jpg)

[Detailed redubbing process and commands →](docs/redubbing.md)

## 5. Finish and export

Add captions and optional graphics to dialogue; leave room for arms and sleeves during movement. Watch the complete export for caption errors, audio issues, visible joins and flashes. Deliver an **MP4 and an editable Remotion project**.

![Same-frame before and after packaging, alongside speaking and movement shots](docs/guide/05-finish.jpg)

Figures use sample screenshots and an earlier continuity test; see [sample notes and music credits](docs/demos/README.md). Reference images guide generation, while local dubbing adjusts audio timing and retains the existing mouth footage.

## Attribution and license

Based on [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo), adapting its caption timeline, some local scripts and Remotion components. See [Attribution](ATTRIBUTION.md). Code retains the upstream [MIT license](LICENSE); external models, services and media have separate terms in [Third-party information](THIRD_PARTY.md).
