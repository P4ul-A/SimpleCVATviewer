# SimpleCVATviewer

**Completely vibed, enjoy with care**


A small local viewer for CVAT **COCO JSON** exports. Draws colored polygons on
the original images, with image navigation, category labels, and adjustable fill.
Uses Python 3.9+ and a browser; no packages to install.

```sh
python3 viewer.py
```

Open http://127.0.0.1:8000. The default loads
`seal_annotation/merged_annotations_coco_cvat.json` and finds the original
images in the `seal_annotation` subfolders. Stop with Ctrl+C.

Use Previous/Next or select an image by filename. Toggle annotations and labels
or adjust the fill slider to see the original image more clearly.

To use a different export:

```sh
python3 viewer.py --annotations path/to/annotations.json --images path/to/images --port 8001
```

Image filenames are matched to their relative paths or unique filenames within
the image folder. Missing or ambiguous matches are shown in the viewer.
Supports COCO polygons and bounding boxes; CVAT XML and RLE masks are not supported.
The viewer only displays annotations; it does not edit images or exports.
