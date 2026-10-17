from __future__ import annotations

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def convert(model_dir: Path, backup_bin: bool = True) -> Path:
    """Convert `pytorch_model.bin` to `model.safetensors` for bge-m3.

    This avoids `transformers` refusing to load `.bin` weights under torch<2.6 due to the torch.load safety gate.

    Args:
        model_dir: Directory containing `pytorch_model.bin`.
        backup_bin: If True, rename original bin to `pytorch_model.bin.bak` after conversion.

    Returns:
        Path to generated safetensors file.
    """
    import torch
    from safetensors.torch import save_file  # type: ignore

    bin_path = model_dir / "pytorch_model.bin"
    out_path = model_dir / "model.safetensors"
    if not bin_path.exists():
        raise FileNotFoundError(str(bin_path))
    if out_path.exists():
        logger.info("Already exists: %s", out_path)
        return out_path

    logger.info("Loading state dict from: %s", bin_path)
    state = torch.load(bin_path, map_location="cpu")
    if not isinstance(state, dict):
        raise ValueError("Unexpected checkpoint format (expected state dict).")
    logger.info("Saving safetensors to: %s", out_path)
    save_file(state, out_path.as_posix())

    if backup_bin:
        bak = model_dir / "pytorch_model.bin.bak"
        bin_path.rename(bak)
        logger.info("Backed up original bin to: %s", bak)

    return out_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert bge-m3 pytorch_model.bin -> model.safetensors")
    p.add_argument("--model-dir", type=Path, default=Path("models/bge-m3"))
    p.add_argument("--no-backup", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out = convert(args.model_dir, backup_bin=(not args.no_backup))
    print(f"ok: {out}")


if __name__ == "__main__":
    main()




