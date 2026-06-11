# save_JSON_comfy

A small utility node for saving JSON strings to disk. I made this because I wanted a way to export bounding box data without having to manually copy the text preview each time, especially when running batches. It'll work with any node that outputs a JSON string. It's intended to be a tool for artists! 

---
 
## Installation
 
1. Create a folder called `save_json` inside `ComfyUI/custom_nodes/`
2. Drop `save_json_node.py` and `__init__.py` inside it
3. Restart ComfyUI
The node will show up as **Save JSON** under `utils/io` in the node menu.
 
---
 
## Inputs
 
| Input | Required | Description |
|---|---|---|
| `json_string` | yes | Connect this to whatever node is outputting your data, since it contains the JSON string to save. |
| `filename_prefix` | yes | Base name for the output files. Defaults to `locate_anything`. |
| `subfolder` | yes | Folder inside your ComfyUI `output/` directory to save into. Leave blank to save directly in `output/`. |
| `source_filename` | no | Wire this to a Load Image node's filename output and the saved JSON files will use the source image name as their prefix instead of `filename_prefix`. |
 
---
 
## Outputs
 
| Output | Description |
|---|---|
| `saved_paths` | The full path(s) of the file(s) written. Also displayed in the node's text preview. |
 
---
 
## How filenames work
 
Files are always saved with a zero-padded counter: `prefix_00000.json`, `prefix_00001.json`, and so on. The counter scans the output folder on each run and picks up from the highest existing number, so re-running a workflow won't overwrite anything.
 
If you connect `source_filename`, the source image name becomes the prefix:
 
```
photo_001.jpg  →  photo_001_00000.json
photo_002.jpg  →  photo_002_00000.json
image.jpg      →  image_00000.json
image.jpg      →  image_00001.json   ← same name, counter increments
```
 
---
 
## Batch processing
 
If the incoming JSON is an array (which is typical when processing a batch), the node automatically splits it and writes one file per element. You don't need to do anything special, just connect it and run.
 
---
 
## Notes
 
- If the input isn't valid JSON, the node will still save it as a raw text file and print a warning to the console. 
- Files are saved as UTF-8 with 2-space indentation.
- The node is marked as `OUTPUT_NODE = True`, which means ComfyUI will always execute it even if nothing is connected downstream.
