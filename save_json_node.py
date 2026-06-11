"""
SaveJSON – ComfyUI custom node
Saves JSON output (single object or array) to disk.
Arrays are automatically split into one file per element —
useful for batched LocateAnything results.
"""

import json
import os
import re
import folder_paths


class SaveJSONNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "locate_anything"}),
                # Subfolder inside ComfyUI's output/ directory.
                # Leave blank to save directly in output/.
                "subfolder": ("STRING", {"default": ""}),
            },
            "optional": {
                # Wire to Load Image's filename output to mirror the source
                # image name (e.g. "photo_001.jpg" → "photo_001.json").
                # Overrides the auto-increment counter when provided.
                "source_filename": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_paths",)
    FUNCTION = "save_json"
    OUTPUT_NODE = True
    CATEGORY = "utils/io"

    def save_json(self, json_string, filename_prefix="locate_anything", subfolder="", source_filename=""):

        # ── Resolve output directory ────────────────────────────────────
        output_dir = folder_paths.get_output_directory()
        if subfolder.strip():
            output_dir = os.path.join(output_dir, subfolder.strip())
        os.makedirs(output_dir, exist_ok=True)

        # ── Parse input ─────────────────────────────────────────────────
        try:
            parsed = json.loads(json_string)
        except json.JSONDecodeError:
            print("[SaveJSON] ⚠  Input was not valid JSON; saving raw string.")
            parsed = json_string  # save as-is

        # ── If it's an array, split into one file per element ───────────
        if isinstance(parsed, list):
            saved = []
            for item in parsed:
                path = self._write(output_dir, filename_prefix, item, source_filename)
                saved.append(path)
            print(f"[SaveJSON] ✓  Saved {len(saved)} files → {output_dir}")
            return {"ui": {"text": saved}, "result": (" | ".join(saved),)}

        # ── Single object / raw string ──────────────────────────────────
        path = self._write(output_dir, filename_prefix, parsed, source_filename)
        print(f"[SaveJSON] ✓  Saved → {path}")
        return {"ui": {"text": [path]}, "result": (path,)}

    # ── Helpers ─────────────────────────────────────────────────────────

    def _write(self, directory, prefix, data, source_filename=""):
        """Write one JSON file, using source_filename if provided, otherwise auto-increment."""
        if source_filename.strip():
            base = os.path.splitext(os.path.basename(source_filename.strip()))[0]
            base = re.sub(r'[^\w\-.]', '_', base)
            filename = base + ".json"
        else:
            counter = self._next_counter(directory, prefix)
            filename = f"{prefix}_{counter:05d}.json"

        filepath = os.path.join(directory, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            if isinstance(data, str):
                fh.write(data)
            else:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        return filepath

    @staticmethod
    def _next_counter(directory, prefix):
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


NODE_CLASS_MAPPINGS = {"SaveJSON": SaveJSONNode}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveJSON": "Save JSON"}
