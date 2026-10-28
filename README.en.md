# Digital Human Koubo · Muse community edition

A community adaptation of [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo): plan short talking-head clips, use Muse through its actual interface, select a cut, extract the last frame, use it as the next image reference, and finish the result locally with Whisper and Remotion.

[完整中文指南 / Full Chinese guide](README.md)

**Scope:** This repository does not contain a Muse API, model weights, TTS2, account, demo presenter, or user media. Request preparation is offline; you or a computer-using agent must actually upload each image and generate/download each clip in Muse. Check your current Muse duration limits, capabilities, credit balance and prices before submitting. A tail image is a reference, not a guaranteed locked first frame. Later voice replacement does not drive lip movement.

## Requirements

Python 3, FFmpeg/FFprobe, whisper.cpp `whisper-cli` and a local model, Node.js 18+, and npm. Use faces, voices, and music you are entitled to use. Remotion has separate license terms: see [THIRD_PARTY.md](THIRD_PARTY.md).

## Workflow

1. Copy `examples/persona.json` and `examples/script.json` to a private work directory. Add your own `portrait.png` and edit the script and voice description. Run `build_tasks.py` to prepare local prompts.
2. Generate the first clip in Muse. Review speech and expression, choose the cut, then run `handoff.py` to create a trimmed clip, its actual last frame and a new task list bound to the image. Upload that image with the next prompt and repeat. Review all joins.
3. Create `results.json` from the real downloaded clips; run `import_muse.py`. After actually watching and listening, set each approved clip to `approved`. Run `assemble.py` with `--keep-frames` for the retained cuts and `align.py` to create `tl.json`. Whisper similarity is not a substitute for listening or lip-sync review.
4. Optionally place external, separately generated phrase audio using `timed_voice.py` and manually chosen start times. Review the replacement voice and subtitle timing; mouth movement is unchanged.
5. Run `prepare_edit.py --video main.mp4 --timeline tl.json --output community-edit`. In the new project run `npm install --no-audit --no-fund` followed by `bash scripts/render.sh ../finished.mp4`. Optional custom stickers, audio and music are documented in the Chinese guide. The finished MP4 and the new Remotion project are separate deliverables.

The complete copyable commands and example JSON are in [README.md](README.md). The local scripts do not upload, charge, or automatically retry. The cut, export, and render tools refuse to overwrite existing targets. Review the full output, including joins, captions, audio, and possible rendering artifacts.

## License and attribution

Derived from [digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo), with its [MIT license](LICENSE), [notice](NOTICE.md), and [third-party information](THIRD_PARTY.md) retained. The original author's demonstration images and videos are not included. Third-party services and media have their own terms.
