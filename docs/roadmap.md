# Roadmap

## Now

- [x] FFmpeg frame extraction and rebuild with rational FPS
- [x] Safe AAC audio muxing
- [x] FFmpeg progress bars
- [x] Native Real-ESRGAN runner with model-param override
- [ ] End-to-end test on a short video

## Next

- [ ] Chunked processing to reduce peak disk use
- [ ] Checkpointing / resume support for interrupted runs
- [ ] Optional post-upscale resize
- [ ] YAML-driven pipeline configuration
- [ ] Temporal video super-resolution stage (RealBasicVSR / BasicVSR++)

## Future

- [ ] Stream frames directly through FFmpeg (avoid disk frames entirely)
- [ ] Denoising stage (SCUNet or equivalent)
- [ ] Frame interpolation (RIFE)
- [ ] Video stabilization
- [ ] HDR and multiple model support
- [ ] Plugin / stage architecture
