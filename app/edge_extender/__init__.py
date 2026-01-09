from pathlib import Path

from ..config import data_dir
from . import attempt, cleanup, inputs, lines, merge, outputs
from .utils import apply_funcs

funcs = [inputs.main, lines.main, attempt.main, merge.main, outputs.main, cleanup.main]


def edge_extender(input_path: Path) -> None:
    """Run main function."""
    file = data_dir / "tmp" / f"{input_path.stem}.parquet"
    name = file.name.replace(".", "_")
    args = [name, file, file.stem, *funcs]
    apply_funcs(*args)
