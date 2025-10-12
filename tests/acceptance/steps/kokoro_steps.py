# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: AGPL-3.0-only

# Part of the aquarion-libtts library of the Aquarion AI project.
# Copyright (C) 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

"""Kokoro TTS BDD steps."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final
from unittest import mock

import torch
from bsdiff4 import diff
from radish import then, when

if TYPE_CHECKING:
    from radish.stepmodel import Step

MIN_GPU_MEMORY_ALLOCATION: Final = 300_000_000  # bytes
MAX_GPU_RESIDUAL_MEMORY: Final = 10_000_000  # bytes
MAX_SPEECH_DIFF_LEN: Final = 28_000  # NDIFF4 bytes
MAX_GPU_LOOP_RESIDUAL_MEMORY: Final = 12_000_000  # bytes


class LocalDataNotFoundError(RuntimeError):
    """Raised if a Kokoro data file from Hugging Face is not already locally cached."""

    def __init__(self, message: str) -> None:
        """Append shared extra text to the given message and initialize the class."""
        super().__init__(
            f"{message}  This could be due to acceptance tests being shuffled on a "
            "fresh clone.  Try re-running the tests."
        )


def _is_newer(first_path: Path, second_path: Path) -> bool:
    """Return True if second_path's last modified data is newer than first_path."""
    return second_path.stat().st_mtime > first_path.stat().st_mtime


def _find_newest_hf_snapshot(root_path: Path) -> Path:
    """Return the path to the most recent Hugging Face cached snapshot."""
    message = "No Kokoro data downloaded yet from Hugging Face."
    if not root_path.is_dir():
        raise LocalDataNotFoundError(message)
    most_recent_snapshot = None
    for sub_path in root_path.iterdir():
        if not sub_path.is_dir():
            continue
        if most_recent_snapshot is None or _is_newer(sub_path, most_recent_snapshot):
            most_recent_snapshot = sub_path
    if most_recent_snapshot is None:
        raise LocalDataNotFoundError(message)
    return most_recent_snapshot


def _ensure_exists(root_path: Path, file_name: str) -> Path:
    """Return the path to the given file or raise an error if not found."""
    file_path = root_path / file_name
    if not file_path.is_file():
        message = f"Kokoro data file not found '{file_path}'."
        raise LocalDataNotFoundError(message)
    return file_path


def find_local_paths() -> dict[str, Path]:
    """Find locally cached Kokoro files that huggingface_hub previously downloaded."""
    cache_root = (
        Path("~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/")
        .expanduser()
        .resolve()
    )
    snapshot_path = _find_newest_hf_snapshot(cache_root)
    return {
        "config_path": _ensure_exists(snapshot_path, "config.json"),
        "model_path": _ensure_exists(snapshot_path, "kokoro-v1_0.pth"),
        "voice_path": _ensure_exists(snapshot_path / "voices", "af_heart.pt"),
    }


### GIVENs ###


### WHENs ###


@when("I make new settings using {locale:w} and {voice:w}")
def _(step: Step, locale: str, voice: str) -> None:
    step.context.settings = step.context.plugin.make_settings(
        from_dict={"locale": locale, "voice": voice}
    )


@when("I measure baseline GPU memory usage")
def _(step: Step) -> None:
    step.context.baseline_gpu_memory = torch.cuda.memory_allocated()


@when("I convert text to speech '{count:d}' times in a row")
def _(step: Step, count: int) -> None:
    def _convert(i: int = 0) -> None:
        b"".join(list(step.context.backend.convert(f"Hi there! {i}")))

    # Run once to prime the memory.
    _convert()
    step.context.starting_gpu_memory = torch.cuda.memory_allocated()
    for _ in range(count):
        _convert()
    step.context.ending_gpu_memory = torch.cuda.memory_allocated()


@when("I make settings with paths to pre-existing local files")
def _(step: Step) -> None:
    local_paths = find_local_paths()
    step.context.settings = step.context.plugin.make_settings(from_dict=local_paths)
    # Also have to patch here to prevent real downloads.
    message = "Download from Hugging Face was attempted.  Expected no downloads."
    patcher = mock.patch(
        "huggingface_hub.file_download._download_to_tmp_and_move",
        side_effect=AssertionError(message),
    )
    patcher.start()


### THENs ###


@then("the model should be loaded in the GPU")
def _(step: Step) -> None:
    expected_min_gpu_memory = (
        step.context.baseline_gpu_memory + MIN_GPU_MEMORY_ALLOCATION
    )

    current_gpu_memory = torch.cuda.memory_allocated()
    assert current_gpu_memory > expected_min_gpu_memory, (
        f"GPU memory of {current_gpu_memory} is not greater than "
        "{expected_min_gpu_memory}"
    )


@then("the model should be loaded in the CPU")
def _(step: Step) -> None:
    expected_gpu_memory = step.context.baseline_gpu_memory
    current_gpu_memory = torch.cuda.memory_allocated()
    assert current_gpu_memory <= expected_gpu_memory, (
        f"GPU memory of {current_gpu_memory} greater than {expected_gpu_memory}"
    )
    assert current_gpu_memory < MAX_GPU_RESIDUAL_MEMORY, (
        "GPU memory was used in this test"
    )


@then("the audio output should be as expected")
def _(step: Step) -> None:
    expected = ((Path(__file__).parent) / "kokoro_expected.pcm").read_bytes()
    audio_bytes = b"".join(list(step.context.audio))
    diff_len = len(diff(audio_bytes, expected))
    assert diff_len < MAX_SPEECH_DIFF_LEN, (
        "Generated speech audio is more different than expected.  "
        f"({diff_len} > {MAX_SPEECH_DIFF_LEN})"
    )


@then("GPU memory usage remain consistent")
def _(step: Step) -> None:
    memory_difference = (
        step.context.ending_gpu_memory - step.context.starting_gpu_memory
    )
    assert memory_difference < MAX_GPU_LOOP_RESIDUAL_MEMORY


@then("no network downloading occurs")
def _(step: Step) -> None:
    # Nothing to do here as the previously mocked _download_to_tmp_and_move will raise
    # an exception if any downloading is actually attempted.
    pass
