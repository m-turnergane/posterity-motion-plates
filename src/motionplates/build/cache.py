"""Content-hash based shot caching for motion plate builds.

Provides a mechanism to cache rendered clips by content hash, allowing
re-use only when all inputs (plate, config, fx settings, engine) match exactly.
Stale clips are renamed rather than deleted for safety.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union


def md5_file(path: Union[str, Path]) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_cache_key(
    plate_path: Union[str, Path],
    segment_config: Dict[str, Any],
    fx_config: Optional[Dict[str, Any]] = None,
    engine_path: Optional[Union[str, Path]] = None,
) -> str:
    """Compute a content-based cache key for a shot.

    Args:
        plate_path: Path to the plate image file.
        segment_config: Segment configuration (timing, crop, anchor, etc.).
        fx_config: Optional fx/smoke configuration dict.
        engine_path: Optional path to the engine file (for versioning).

    Returns:
        MD5 hash string uniquely identifying this combination of inputs.
    """
    parts = []

    parts.append(f"plate:{md5_file(plate_path)}")

    seg_json = json.dumps(segment_config, sort_keys=True, default=str)
    parts.append(f"segment:{hashlib.md5(seg_json.encode()).hexdigest()}")

    if fx_config:
        fx_json = json.dumps(fx_config, sort_keys=True, default=str)
        parts.append(f"fx:{hashlib.md5(fx_json.encode()).hexdigest()}")

    if engine_path and os.path.exists(engine_path):
        parts.append(f"engine:{md5_file(engine_path)}")

    combined = "|".join(parts)
    return hashlib.md5(combined.encode()).hexdigest()


class ShotCache:
    """Manages cached shot clips with content-based validation.

    Usage:
        cache = ShotCache(clips_dir)
        key = cache.compute_key(plate_path, segment, fx_config)

        if cache.is_valid(shot_id, key):
            print("Reusing cached clip")
        else:
            # Render the clip...
            cache.mark_valid(shot_id, key)
    """

    KEY_SUFFIX = ".key"
    STALE_PREFIX = ".stale-"

    def __init__(self, cache_dir: Union[str, Path]):
        """Initialize the cache manager.

        Args:
            cache_dir: Directory where clips and key files are stored.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _clip_path(self, shot_id: str) -> Path:
        """Get the path for a shot's clip file."""
        return self.cache_dir / f"{shot_id}.mp4"

    def _key_path(self, shot_id: str) -> Path:
        """Get the path for a shot's key file."""
        return self.cache_dir / f"{shot_id}{self.KEY_SUFFIX}"

    def compute_key(
        self,
        plate_path: Union[str, Path],
        segment_config: Dict[str, Any],
        fx_config: Optional[Dict[str, Any]] = None,
        engine_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Compute cache key for a shot. Convenience wrapper around compute_cache_key."""
        return compute_cache_key(plate_path, segment_config, fx_config, engine_path)

    def read_key(self, shot_id: str) -> Optional[str]:
        """Read the stored cache key for a shot, or None if not cached."""
        key_file = self._key_path(shot_id)
        if not key_file.exists():
            return None
        try:
            return key_file.read_text().strip()
        except OSError:
            return None

    def is_valid(self, shot_id: str, expected_key: str) -> bool:
        """Check if a cached clip exists and matches the expected key.

        Args:
            shot_id: Identifier for the shot.
            expected_key: The expected content hash key.

        Returns:
            True if both the clip and key file exist and the key matches.
        """
        clip = self._clip_path(shot_id)
        if not clip.exists():
            return False

        stored_key = self.read_key(shot_id)
        return stored_key == expected_key

    def mark_stale(self, shot_id: str) -> Optional[Path]:
        """Mark an existing clip as stale by renaming it.

        Args:
            shot_id: Identifier for the shot.

        Returns:
            Path to the stale file if renamed, None if no clip existed.
        """
        clip = self._clip_path(shot_id)
        if not clip.exists():
            return None

        timestamp = int(time.time())
        stale_name = f"{shot_id}{self.STALE_PREFIX}{timestamp}.mp4"
        stale_path = self.cache_dir / stale_name

        try:
            clip.rename(stale_path)
            key_file = self._key_path(shot_id)
            if key_file.exists():
                key_file.unlink()
            return stale_path
        except OSError:
            return None

    def mark_valid(self, shot_id: str, key: str) -> None:
        """Write the cache key for a successfully rendered shot.

        Args:
            shot_id: Identifier for the shot.
            key: The content hash key to store.
        """
        key_file = self._key_path(shot_id)
        key_file.write_text(key)

    def invalidate_if_stale(self, shot_id: str, expected_key: str) -> bool:
        """Check if cached clip is stale and mark it if so.

        Args:
            shot_id: Identifier for the shot.
            expected_key: The expected content hash key.

        Returns:
            True if the clip needed to be (re-)rendered (was missing or stale),
            False if the cached clip is valid.
        """
        if self.is_valid(shot_id, expected_key):
            return False

        self.mark_stale(shot_id)
        return True
