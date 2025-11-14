from pathlib import Path

import pytest

from src.utils.script_chunker import (
    chunk_script,
    estimate_duration,
    _split_into_paragraphs,
)


def test_chunk_script_creates_multiple_chunks(tmp_path, capsys):
    script = tmp_path / "script.txt"
    # Create two paragraphs totalling > 150 words so chunk_duration=1 produces 2 chunks.
    para1 = "Paragraph one " + " ".join([f"word{i}" for i in range(120)])
    para2 = "Paragraph two " + " ".join([f"word{i}" for i in range(90)])
    script.write_text(f"# Title\n\n{para1}\n\n{para2}\n")

    chunk_dir = tmp_path / "chunks"
    chunks = chunk_script(script, chunk_duration_minutes=1, output_dir=chunk_dir)

    assert len(chunks) == 2
    assert all(path.exists() for path in chunks)
    captured = capsys.readouterr()
    assert "Created 2 chunks" in captured.out

    first_chunk_text = chunks[0].read_text()
    assert first_chunk_text.startswith("# Title")
    assert "Paragraph one" in first_chunk_text


def test_chunk_script_missing_file():
    with pytest.raises(FileNotFoundError):
        chunk_script(Path("does_not_exist.txt"), chunk_duration_minutes=1)


def test_split_into_paragraphs_handles_single_lines():
    text = "Line one\nLine two\n\n# Heading line\n\nLine three"
    paragraphs = _split_into_paragraphs(text)
    assert "Line one" in paragraphs[0]
    assert "Line three" in paragraphs[-1]
    assert all(not para.startswith("#") for para in paragraphs)


def test_estimate_duration():
    text = " ".join(["word"] * 300)
    assert estimate_duration(text) == pytest.approx(2.0)

