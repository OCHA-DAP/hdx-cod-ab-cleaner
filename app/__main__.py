import argparse

from .clean.cod_ab import clean_admin, clean_admin_em
from .config import data_dir
from .download.admin0 import download_admin0
from .edge_extender import edge_extender


def main() -> None:
    """Run main Function."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--edge-match",
        action="store_true",
        help="Run edge extender and em cleaning steps",
    )
    args = parser.parse_args()

    if args.edge_match:
        download_admin0()
    for layer in sorted((data_dir / "inputs").glob("*adm*")):
        clean_admin(layer)
        if args.edge_match:
            edge_extender(layer)
            clean_admin_em(layer)


if __name__ == "__main__":
    main()
