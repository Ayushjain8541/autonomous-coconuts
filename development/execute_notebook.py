"""Execute and save the development notebook with this Python interpreter."""

from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
for name, suffix in (
    ("JUPYTER_CONFIG_DIR", ".jupyter/config"),
    ("JUPYTER_DATA_DIR", ".jupyter/data"),
    ("JUPYTER_RUNTIME_DIR", ".jupyter/runtime"),
    ("IPYTHONDIR", ".jupyter/ipython"),
    ("MPLCONFIGDIR", ".cache/matplotlib"),
):
    directory = ROOT / suffix
    directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault(name, str(directory))

# A project-local runtime can be used on Macs without a system OpenMP package.
# Set the search path before launching the child Python kernel.
local_openmp = ROOT.parent / ".venv/runtime/lib"
if (ROOT / ".venv/runtime/lib/libomp.dylib").is_file():
    local_openmp = ROOT / ".venv/runtime/lib"
system_openmp = (
    Path("/usr/local/opt/libomp/lib/libomp.dylib"),
    Path("/opt/homebrew/opt/libomp/lib/libomp.dylib"),
    Path("/usr/local/lib/libomp.dylib"),
)
if (sys.platform == "darwin" and not any(path.is_file() for path in system_openmp)
        and (local_openmp / "libomp.dylib").is_file()):
    os.environ.setdefault("DYLD_LIBRARY_PATH", str(local_openmp))

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", action="store_true", help="Open the notebook in JupyterLab.")
    args = parser.parse_args()
    path = ROOT / "collision_risk_development.ipynb"
    if args.lab:
        subprocess.run([sys.executable, "-m", "jupyterlab", str(path)], cwd=ROOT, check=True)
        return
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    manager = KernelManager(kernel_name="python3")
    # Explicitly use the invoking .venv; an unrelated system kernel may exist.
    manager.kernel_spec.argv = [
        sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"
    ]

    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == "code":
            print(f"Executing cell {cell_index + 1}/{len(notebook.cells)}", flush=True)

    client = NotebookClient(
        notebook, km=manager, timeout=900,
        resources={"metadata": {"path": str(ROOT)}}, on_cell_start=progress,
    )
    try:
        client.execute(cleanup_kc=True)
    finally:
        # Keep diagnostics if a cell fails; a nonzero exit still signals failure.
        nbformat.write(notebook, path)
    print(f"Executed and saved {path.name}", flush=True)


if __name__ == "__main__":
    main()
