# Encoding (v0.2.1)

Pipeline: raw RGB frames are piped straight into ONE ffmpeg (no intermediate lossless MP4, no second lossy pass).
`scale=in_range=pc:out_range=tv:out_color_matrix=bt709:flags=area+accurate_rnd+full_chroma_int,format=yuv420p`, libx264 crf 14 preset slow,
tags `color_primaries=bt709 color_trc=bt709 colorspace=bt709 color_range=tv`, `+faststart`, `-f mp4`.
Output is written to `<dst>.tmp.mp4`, then checked (ffmpeg exit code, ffprobe codec/size/fps/frame count/colour tags, full decode of every frame) and only then atomically renamed. A failure removes the tmp file and raises `EncodeError` (CLI exit 4).
`--at` (stills only) never produces a video. Legacy path (2-pass, untagged) is kept only as the benchmark baseline (`tools/bench_encode.py`).
Why: the old path converted RGB->YUV twice and wrote untagged video, so players guessed BT.601 vs 709 (visible colour shift on some players). Benchmark results are in the v0.2.1 report (direct tagged is ~1.7x faster to encode than the 2-pass path; quality metrics equal within noise).
