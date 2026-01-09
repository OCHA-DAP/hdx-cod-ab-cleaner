from .clean.cod_ab import clean_admin, clean_admin_em
from .config import data_dir
from .download.admin0 import download_admin0
from .edge_extender import edge_extender


def main() -> None:
    """Run main Function."""
    download_admin0()
    for layer in sorted((data_dir / "inputs").glob("*adm*")):
        clean_admin(layer)
        edge_extender(layer)
        clean_admin_em(layer)


if __name__ == "__main__":
    main()
