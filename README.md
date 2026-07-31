\# AI Video Enhancement Pipeline



A modular, fully local, AI-powered video enhancement pipeline for Windows, built around FFmpeg, Python, CUDA, and Real-ESRGAN.



> \*\*Project Status:\*\* 🚧 In Development (Architecture Complete, AI Runtime In Progress)



\---



\# Vision



The goal of this project is to build a production-quality, one-command video enhancement pipeline.



Eventually the workflow should be as simple as:



```

Drop videos into Input/



↓



Run



run\_pipeline.bat



↓



Receive enhanced videos in Output/

```



The entire pipeline should work completely offline and use only free and open-source software.



\---



\# Primary Goals



\- Fully local processing

\- No cloud services

\- CUDA acceleration

\- RTX 3060 optimized

\- Modular architecture

\- Easily extensible

\- Production-quality logging

\- Batch processing

\- Resume support (future)

\- Optional denoising

\- Optional frame interpolation

\- Future stabilization support



\---



\# Planned Processing Pipeline



```

Input Video

&#x20;     │

&#x20;     ▼

FFprobe

&#x20;     │

&#x20;     ▼

Extract Frames

&#x20;     │

&#x20;     ▼

(Optional) AI Denoise

&#x20;     │

&#x20;     ▼

Real-ESRGAN Upscaling

&#x20;     │

&#x20;     ▼

(Optional) Resize

&#x20;     │

&#x20;     ▼

Rebuild Video

&#x20;     │

&#x20;     ▼

Restore Original Audio

&#x20;     │

&#x20;     ▼

Output Video

```



\---



\# Current Project Structure



```

AI-Video-Workflow/



├── Input/

├── Output/

├── Temp/

├── Models/

├── Workflows/

├── Logs/



└── Scripts/

&#x20;   ├── main.py

&#x20;   ├── config.py

&#x20;   ├── logger.py

&#x20;   ├── ffmpeg\_utils.py

&#x20;   ├── video\_job.py

&#x20;   ├── video\_pipeline.py

&#x20;   ├── chainner\_runner.py   (temporary)

&#x20;   └── utils.py

```



\---



\# Current Progress



\## Phase 1 — Environment Setup ✅



Completed



\- Windows 11

\- NVIDIA CUDA installed

\- FFmpeg installed

\- chaiNNer installed

\- PyTorch dependency installed

\- GPU inference verified

\- Real-ESRGAN workflow tested



\---



\## Phase 2 — Batch Image Processing ✅



Completed



Successfully modified the workflow to:



\- Process folders

\- Preserve filenames

\- Overwrite existing outputs

\- Support image batches



Verified working.



\---



\## Phase 3 — Denoising



Status:



⏸ Deferred



Originally planned using SCUNet.



During implementation we discovered the installed chaiNNer version does not expose SCUNet nodes.



Decision:



Denoising will become an optional pipeline stage rather than a mandatory dependency.



\---



\## Phase 4 — FFmpeg Integration ✅



Completed



Verified:



\### Frame Extraction



```

Video



↓



PNG Frames

```



Confirmed:



\- sequential numbering

\- no dropped frames

\- correct extraction



\---



\### Video Reconstruction



Verified rebuilding



```

Frames



↓



MP4

```



using



\- libx264

\- yuv420p



\---



\### Audio Restoration



Verified



```

Original Audio



↓



Final Video

```



using stream copy.



\---



\## Phase 5 — Python Architecture 🚧



Current Status:



Core architecture completed.



Implemented:



\- config.py

\- logger.py

\- ffmpeg\_utils.py

\- video\_job.py

\- video\_pipeline.py

\- main.py



Current design separates:



\- data

\- pipeline

\- logging

\- ffmpeg

\- configuration



\---



\# Architectural Decisions



\## Why Python?



Python is used as the orchestration layer.



Python does \*\*not\*\* perform image enhancement itself.



Responsibilities:



\- discover videos

\- create jobs

\- call FFmpeg

\- call AI runtime

\- logging

\- cleanup

\- error handling



\---



\## Why FFmpeg?



Industry standard.



Reliable.



Cross-platform.



Supports virtually every codec.



\---



\## Why Modular?



Instead of one large script, the project is divided into independent modules.



```

main.py



↓



video\_pipeline.py



↓



ffmpeg\_utils.py

```



Each module has a single responsibility.



\---



\# chaiNNer Investigation



Originally the project intended to automate chaiNNer directly.



Investigation results:



\- GUI works correctly.

\- Workflow execution works manually.

\- No supported CLI entry point was found.

\- No documented headless execution available.



Decision:



chaiNNer will remain the visual workflow editor.



The production runtime will migrate to direct Python inference.



Reason:



This provides:



\- better logging

\- easier automation

\- no GUI dependency

\- better future extensibility



\---



\# Planned Runtime



Instead of:



```

Python



↓



chaiNNer GUI



↓



AI

```



The project will become:



```

Python



↓



Real-ESRGAN Python



↓



CUDA



↓



Frames

```



The same model weights will be used.



Only the runtime changes.



\---



\# Future Pipeline



The long-term architecture is stage based.



```

Extract Frames



↓



Denoise



↓



Upscale



↓



Interpolate



↓



Encode



↓



Restore Audio

```



Each stage should be independently removable or replaceable.



\---



\# Planned Folder Structure



```

Scripts/



app/

&#x20;   main.py

&#x20;   pipeline.py

&#x20;   ffmpeg\_utils.py

&#x20;   logger.py

&#x20;   config.py



stages/

&#x20;   extract\_frames.py

&#x20;   realesrgan.py

&#x20;   scunet.py

&#x20;   interpolate.py

&#x20;   encode.py

&#x20;   mux\_audio.py



batch/

&#x20;   run\_pipeline.bat

&#x20;   cleanup\_temp.bat

```



\---



\# Planned Features



\## Logging



\- console logging

\- file logging

\- timestamps

\- per-stage timing



\---



\## Batch Processing



Process every video inside



```

Input/

```



without user interaction.



\---



\## Resume Support



Future:



If enhancement stops halfway through a 2-hour video,



the pipeline should continue from the last completed stage.



\---



\## Configuration File



Eventually:



```yaml

pipeline:



&#x20; - extract\_frames

&#x20; - denoise

&#x20; - upscale

&#x20; - encode

&#x20; - mux\_audio

```



Changing the YAML should modify the pipeline without changing Python code.



\---



\# Current Limitations



\- AI execution not yet migrated from chaiNNer.

\- No Real-ESRGAN runtime integrated yet.

\- No progress bars.

\- No resume support.

\- No checkpointing.

\- No batch scheduler.

\- No GUI.



\---



\# Next Milestone



Replace the temporary `chainner\_runner.py` with a native `realesrgan\_runner.py`.



Goals:



\- Official Real-ESRGAN runtime

\- FP16

\- CUDA

\- Direct model loading

\- Folder processing

\- Progress reporting

\- Automatic GPU optimization



\---



\# Long-Term Goals



Future versions may include:



\- SCUNet

\- RIFE Frame Interpolation

\- Video Stabilization

\- HDR handling

\- AI sharpening

\- AI color restoration

\- Multiple model support

\- Plugin architecture

\- YAML-configurable pipeline

\- Parallel processing



\---



\# Philosophy



This project prioritizes:



\- correctness over shortcuts

\- maintainability over cleverness

\- extensibility over one-off scripts



The objective is not simply to enhance videos, but to build a reusable AI media processing framework that can evolve as new models and techniques become available.

