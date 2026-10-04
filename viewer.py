"""Serve a small local viewer for CVAT COCO polygon annotations."""

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def load_annotations(annotation_path, image_root):
    """Resolve COCO image filenames within an image folder.

    Args:
        annotation_path: Path to a CVAT COCO JSON export.
        image_root: Folder containing the original images, including subfolders.

    Returns:
        COCO data with a relative viewer_path for each available image.
    """
    data = json.loads(annotation_path.read_text())
    files = {}
    for path in image_root.rglob('*'):
        if path.is_file():
            files.setdefault(path.name, []).append(path)
    for image in data['images']:
        exact = (image_root / image['file_name']).resolve()
        matches = files.get(Path(image['file_name']).name, [])
        if exact.is_relative_to(image_root) and exact.is_file():
            image['viewer_path'] = exact.relative_to(image_root).as_posix()
        elif len(matches) == 1:
            image['viewer_path'] = matches[0].relative_to(image_root).as_posix()
        else:
            image['viewer_path'] = None
    return data


class ViewerHandler(SimpleHTTPRequestHandler):
    """Serve the viewer and annotation data alongside the image directory."""

    def do_GET(self):
        """Handle the current GET request.

        Parameters: None; request details come from the HTTP handler.
        Returns: None. Writes the response to the client.
        """
        route = urlsplit(self.path).path
        if route == '/':
            content = Path(__file__).with_name('viewer.html').read_bytes()
            content_type = 'text/html; charset=utf-8'
        elif route == '/annotations.json':
            content = self.server.annotation_bytes
            content_type = 'application/json'
        else:
            super().do_GET()
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    """Start the local viewer using command-line options.

    Parameters: None; options are read from the command line.
    Returns: None. Serves until interrupted with Ctrl+C.
    """
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations', type=Path,
                        default=root / 'seal_annotation/merged_annotations_coco_cvat.json')
    parser.add_argument('--images', type=Path, default=root / 'seal_annotation')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    image_root = args.images.resolve()
    if not image_root.is_dir():
        parser.error(f'Image folder does not exist: {image_root}')
    try:
        data = load_annotations(args.annotations, image_root)
    except (OSError, ValueError, KeyError) as error:
        parser.error(f'Cannot load annotations: {error}')
    handler = partial(ViewerHandler, directory=str(image_root))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        server.annotation_bytes = json.dumps(data).encode()
        print(f'Open http://127.0.0.1:{args.port} — Ctrl+C to stop', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
