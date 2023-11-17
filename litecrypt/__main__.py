import sys
import warnings

from litecrypt.core.safepack.gui import main_object

if sys.version_info < (3, 7):  # pragma: no cover
    warnings.warn(
        message="""\033[38;5;214m
            This Python version is no longer supported by the Python team,
            nor is it supported by this project.
            Python 3.7 or newer is required for this library to work properly.
            Existing..\033[0m
        """,
        stacklevel=2,
    )
    sys.exit()


if __name__ == "__main__":
    main_object.mainloop()
