from pathlib import Path
from types import SimpleNamespace

import pytest

from src.utils import video_chunker
from src.utils.video_chunker import _get_video_duration, chunk_video


def test_chunk_video_splits_and_invokes_ffmpeg(tmp_path, monkeypatch):
    video = tmp_path / "input.mp4"
    video.write_bytes(b"\x00" * 1024)
    output_dir = tmp_path / "chunks"

    def fake_run(cmd, **kwargs):
        if "ffprobe" in cmd[0]:
            return SimpleNamespace(returncode=0, stdout="120\n", stderr="")
        # FFmpeg chunk creation
        Path(cmd[-1]).write_bytes(b"chunk")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(video_chunker.subprocess, "run", fake_run)

    chunks = chunk_video(video, chunk_duration_minutes=1, output_dir=output_dir)

    assert len(chunks) == 2
    assert all(path.exists() and path.read_bytes() == b"chunk" for path in chunks)


def test_chunk_video_raises_when_duration_unknown(tmp_path, monkeypatch):
    video = tmp_path / "bad.mp4"
    video.write_bytes(b"\x00")

    def failing_run(cmd, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="ffprobe error")

    monkeypatch.setattr(video_chunker.subprocess, "run", failing_run)

    with pytest.raises(Exception):
        chunk_video(video, chunk_duration_minutes=1, output_dir=tmp_path / "chunks")

