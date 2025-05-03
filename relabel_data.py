#!/usr/bin/env python3
"""
Rewrite action‑labels in Volleyball annotations.

Folder structure
----------------
decompl/
├── rewrite_labels.py     <-- (this script)
└── reannotations/
    ├── 1/
    │   └── annotations_corrected.txt
    ├── 2/
    │   └── annotations_corrected.txt
    └── ...
        └── 54/annotations_corrected.txt

Behaviour
---------
* Walks through every sub‑folder of ./reannotations
* Opens `annotations_corrected.txt`
* For every line:
    image_name  group_label  [x y w h person_label]×12
  only the **person action_label** (every 5‑th token after the
  group label) is touched:
    - kept if it is  spiking/setting/digging/blocking  (case‑insensitive)
    - otherwise replaced with the literal string  'None'
* Saves the file back to disk (over‑writes the original).
  A safety backup  annotations_corrected.txt.bak  is written once
  per folder.
"""

import pathlib
import shutil

# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #
ROOT          = pathlib.Path(__file__).parent
REANNOTATIONS = ROOT / "reannotations"
KEEP          = {"spiking", "setting", "digging", "blocking"}

# --------------------------------------------------------------------------- #
def rewrite_file(txt_path: pathlib.Path) -> None:
    """Rewrite one annotations_corrected.txt in‑place."""
    bak_path = txt_path.with_suffix(txt_path.suffix + ".bak")
    if not bak_path.exists():          # one backup per folder
        shutil.copy2(txt_path, bak_path)

    new_lines = []
    with txt_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            tokens = line.strip().split()
            if len(tokens) < 2:
                new_lines.append(line)            # malformed – keep as is
                continue

            # tokens[0] = image name, tokens[1] = group label  -> leave intact
            head = tokens[:2]
            body = tokens[2:]

            # the body should come in chunks of 5:  x  y  w  h  label
            for i in range(0, len(body), 5):
                if i + 4 >= len(body):            # guard against short lines
                    break
                label_idx = i + 4
                label     = body[label_idx]
                if label.lower() not in KEEP:
                    body[label_idx] = "None"

            new_lines.append(" ".join(head + body) + "\n")

    # overwrite the original file
    with txt_path.open("w", encoding="utf-8") as fh:
        fh.writelines(new_lines)


def main() -> None:
    txt_files = sorted(REANNOTATIONS.glob("*/annotations_corrected.txt"))
    if not txt_files:
        print("No annotation files found – check folder structure.")
        return

    for txt in txt_files:
        rewrite_file(txt)
        print(f"✔  Re‑labelled {txt.relative_to(ROOT)}")

    print("\nDone – All non‑target labels rewritten to 'None'.")


if __name__ == "__main__":
    main()
