#!/usr/bin/env python3
"""catalog.json as tab-separated lines, for the launcher's bash.

Both kinema_catalog.sh on the host and entrypoint.sh in the container read the
catalog through this, so neither parses JSON itself. Standard library only: on
the host it runs with whatever python3 is installed.

One line per entry, eight fields:

    id  category  submodule  format  entry  args  mesh_base  name

args are xacro's name:=value words, space-separated; args and mesh_base are -
when empty.
"""

import json
import sys


def main(path: str) -> int:
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError) as exc:
        print(f"catalog_rows: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    for entry in document.get("entries", []):
        args = " ".join(f"{name}:={value}" for name, value in entry["args"].items())
        fields = [entry["id"], entry["category"], entry["submodule"], entry["format"],
                  entry["entry"], args or "-", entry["mesh_base"] or "-", entry["name"]]
        if any("\t" in field or "\n" in field for field in fields):
            print(f"catalog_rows: {entry['id']}: a field contains a tab or a newline",
                  file=sys.stderr)
            return 1
        print("\t".join(fields))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: catalog_rows.py catalog.json", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
