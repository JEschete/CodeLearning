"""Entry point for `python -m antenna_tool`."""

from core.logging_config import setup_logging
setup_logging()

from core.cli import main

if __name__ == "__main__":
    main()
