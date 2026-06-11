"""
SaveJSON – ComfyUI custom node
Saves a JSON string to the output directory, with auto-incrementing filenames
for batch runs and an optional per-image filename override.

Drop this file into:
  ComfyUI/custom_nodes/save_json/save_json_node.py
and add an __init__.py alongside it (see bottom of this file).
"""

import json
import os
import re
import folder_paths


class SaveJSONNode:
    """
    Receives a JSON string (e.g. from LocateAnything) and writes it to
    ComfyUI's output directory.  Each call auto-increments the filename so
    batch workflows produce one file per image without overwriting each other.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "locate_anything"}),
            },
            "optional": {
                # Connect a Load Image node's filename output here to mirror
                # the source image name (e.g. "photo_001" → "photo_001.json").
                # Leave blank to use auto-increment instead.
                "source_filename": ("STRING", {"default": ""}),
                # Subdirectory inside the output folder (leave blank for root).
                "subfolder": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "save_json"
    OUTPUT_NODE = True          # marks this as a terminal / side-effect node
    CATEGORY = "utils/io"

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def save_json(
        self,
        json_string: str,
        filename_prefix: str = "locate_anything",
        source_filename: str = "",
        subfolder: str = "",
    ):
        # ── 1. Resolve output directory ─────────────────────────────────
        output_dir = folder_paths.get_output_directory()
        if subfolder.strip():
            output_dir = os.path.join(output_dir, subfolder.strip())
        os.makedirs(output_dir, exist_ok=True)

        # ── 2. Validate / pretty-print JSON ─────────────────────────────
        try:
            parsed = json.loads(json_string)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # Not valid JSON – save the raw string anyway so you don't lose data
            formatted = json_string
            print("[SaveJSON] ⚠  Input was not valid JSON; saving raw string.")

        # ── 3. Decide filename ───────────────────────────────────────────
        if source_filename.strip():
            # Strip path + extension from whatever Load Image gives us
            base = os.path.splitext(os.path.basename(source_filename.strip()))[0]
            # Sanitise for filesystem use
            base = re.sub(r'[^\w\-.]', '_', base)
            filename = base + ".json"
        else:
            counter = self._next_counter(output_dir, filename_prefix)
            filename = f"{filename_prefix}_{counter:05d}.json"

        filepath = os.path.join(output_dir, filename)

        # ── 4. Write file ────────────────────────────────────────────────
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(formatted)

        print(f"[SaveJSON] ✓  Saved → {filepath}")

        # ui dict surfaces the path in the node's text preview widget
        return {"ui": {"text": [filepath]}, "result": (filepath,)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _next_counter(directory: str, prefix: str) -> int:
        """
        Scan the output directory for existing files matching
        `<prefix>_NNNNN.json` and return max(N) + 1.
        Returns 0 if no matches exist yet.
        """
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)\.json$")
        max_n = -1
        try:
            for fname in os.listdir(directory):
                m = pattern.match(fname)
                if m:
                    max_n = max(max_n, int(m.group(1)))
        except FileNotFoundError:
            pass
        return max_n + 1


# ── Node registration ──────────────────────────────────────────────────────────

NODE_CLASS_MAPPINGS = {
    "SaveJSON": SaveJSONNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveJSON": "Save JSON",
}
