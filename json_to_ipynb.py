import json
from pathlib import Path
from typing import Any, Dict, Union


def json_to_ipynb(
    data: Union[str, Dict[str, Any]],
    output_path: Union[str, Path],
    *,
    ensure_nbformat: bool = True,
    indent: int = 1,
) -> Path:
    """
    Convert a Jupyter Notebook JSON (dict or JSON string / JSON file path) to a .ipynb file.

    Parameters
    ----------
    data:
        - dict: already-parsed notebook JSON
        - str:
            * JSON string (starts with "{" or "[")
            * or a path to a .json file containing notebook JSON
    output_path:
        Target .ipynb path.
    ensure_nbformat:
        If True, add nbformat / nbformat_minor if missing (defaults: 4 / 5).
    indent:
        JSON indentation level for output .ipynb.

    Returns
    -------
    Path to the written .ipynb file.
    """
    output_path = Path(output_path)
    if output_path.suffix.lower() != ".ipynb":
        output_path = output_path.with_suffix(".ipynb")

    # Load input JSON
    if isinstance(data, dict):
        nb = data
    elif isinstance(data, str):
        s = data.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                nb = json.loads(s)
            except json.JSONDecodeError as e:
                start = max(0, e.pos - 120)
                end = min(len(s), e.pos + 120)
                context = s[start:end]
                raise ValueError(
                    f"Invalid JSON in notebook string/file.\n"
                    f"{e}\n\n"
                    f"Context around error (pos={e.pos}):\n"
                    f"{context}"
                ) from None

        else:
            # treat as file path
            p = Path(s)
            with p.open("r", encoding="utf-8") as f:
                nb = json.load(f)
    else:
        raise TypeError("data must be a dict or str (JSON string or JSON file path).")

    if not isinstance(nb, dict):
        raise ValueError("Notebook JSON must be a JSON object (dict) at the top level.")

    # Ensure notebook format fields (optional, but helps compatibility)
    if ensure_nbformat:
        nb.setdefault("nbformat", 4)
        nb.setdefault("nbformat_minor", 5)
        nb.setdefault("cells", [])
        nb.setdefault("metadata", {})

    # Write .ipynb
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=indent)
        f.write("\n")

    return output_path


if __name__ == "__main__":
    # Example 1: JSON string -> ipynb
    notebook_json_str = r'''
        {
          "cells": [
            {
              "cell_type": "markdown",
              "metadata": {},
              "source": ["# Hello\\n", "This is a notebook."]
            },
            {
              "cell_type": "code",
              "metadata": {},
              "execution_count": null,
              "outputs": [],
              "source": ["print('hi')\\n"]
            }
          ],
          "metadata": {},
          "nbformat": 4,
          "nbformat_minor": 5
        }
        '''
    out1 = json_to_ipynb(notebook_json_str, "output_example.ipynb")
    print(f"Wrote: {out1}")

    # Example 2: JSON file -> ipynb
    # out2 = json_to_ipynb("notebook.json", "notebook.ipynb")
    # print(f"Wrote: {out2}")

    # Example 3: Python dict -> ipynb
    # nb_dict = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    # out3 = json_to_ipynb(nb_dict, "empty.ipynb")
    # print(f"Wrote: {out3}")
