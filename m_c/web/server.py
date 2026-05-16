import base64
import binascii
import json
import mimetypes
import os
import re
import tempfile
import uuid
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import quote, unquote, urlparse

from m_c.core.file_utils import (
    SUPPORTED_CHECKSUM_ALGORITHMS,
    get_file_checksum,
    get_safe_output_path,
)
from m_c.core.metadata_processor import MetadataProcessor
from m_c.core.reporting import processing_warnings

MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def _safe_json(value):
    return json.loads(json.dumps(value, default=str, sort_keys=True))


def _safe_filename(filename: str) -> str:
    name = os.path.basename(filename or "upload.bin")
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    return name or "upload.bin"


def _decode_upload(payload: dict, max_upload_bytes: int) -> tuple[str, bytes]:
    filename = _safe_filename(str(payload.get("filename") or "upload.bin"))
    encoded = payload.get("content_base64")
    if not isinstance(encoded, str) or not encoded:
        raise ValueError("content_base64 is required")

    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("content_base64 is not valid base64") from exc

    if not content:
        raise ValueError("uploaded file is empty")
    if len(content) > max_upload_bytes:
        raise ValueError("uploaded file exceeds the configured size limit")
    return filename, content


@dataclass
class DownloadRecord:
    file_path: str
    filename: str


@dataclass
class StoredFile:
    file_path: str
    filename: str
    collection: str
    size: int
    modified: float

    def to_payload(self) -> dict:
        quoted_name = quote(self.filename, safe="")
        return {
            "filename": self.filename,
            "collection": self.collection,
            "size": self.size,
            "modified": self.modified,
            "view_url": f"/api/files/{self.collection}/{quoted_name}",
            "delete_url": f"/api/files/{self.collection}/{quoted_name}",
        }


def _parse_file_route(path: str) -> tuple[str, str]:
    parts = path.split("/", 4)
    if len(parts) != 5 or parts[:3] != ["", "api", "files"] or not parts[4]:
        raise ValueError("invalid file route")
    return parts[3], unquote(parts[4])


class WebApp:
    def __init__(self, workspace: str, max_upload_bytes: int = MAX_UPLOAD_BYTES):
        self.workspace = workspace
        self.max_upload_bytes = max_upload_bytes
        self.downloads: dict[str, DownloadRecord] = {}
        os.makedirs(self.workspace, exist_ok=True)
        os.makedirs(self.cleaned_dir, exist_ok=True)

    @property
    def upload_dir(self) -> str:
        return os.path.join(self.workspace, "uploads")

    @property
    def cleaned_dir(self) -> str:
        return os.path.join(self.workspace, "cleaned")

    def _collection_dir(self, collection: str) -> str:
        collections = {
            "originals": self.upload_dir,
            "cleaned": self.cleaned_dir,
        }
        if collection not in collections:
            raise ValueError("unsupported file collection")
        return collections[collection]

    def _stored_file_path(self, collection: str, filename: str) -> str:
        if filename != os.path.basename(filename):
            raise ValueError("invalid filename")
        if _safe_filename(filename) != filename:
            raise ValueError("invalid filename")

        collection_dir = os.path.abspath(self._collection_dir(collection))
        file_path = os.path.abspath(os.path.join(collection_dir, filename))
        if os.path.commonpath([collection_dir, file_path]) != collection_dir:
            raise ValueError("invalid filename")
        return file_path

    def list_files(self, collection: str) -> list[dict]:
        collection_dir = self._collection_dir(collection)
        if not os.path.isdir(collection_dir):
            return []

        files = []
        for filename in sorted(os.listdir(collection_dir), key=str.lower):
            try:
                file_path = self._stored_file_path(collection, filename)
            except ValueError:
                continue
            if not os.path.isfile(file_path):
                continue
            stat_result = os.stat(file_path)
            files.append(
                StoredFile(
                    file_path=file_path,
                    filename=filename,
                    collection=collection,
                    size=stat_result.st_size,
                    modified=stat_result.st_mtime,
                ).to_payload()
            )
        return files

    def files_response(self) -> dict:
        return {
            "originals": self.list_files("originals"),
            "cleaned": self.list_files("cleaned"),
        }

    def save_upload(self, payload: dict) -> str:
        filename, content = _decode_upload(payload, self.max_upload_bytes)
        os.makedirs(self.upload_dir, exist_ok=True)
        upload_path = get_safe_output_path(
            os.path.join(self.upload_dir, filename),
            create_dirs=True,
        )
        with open(upload_path, "wb") as uploaded_file:
            uploaded_file.write(content)
        return upload_path

    def metadata_response(self, payload: dict) -> dict:
        upload_path = self.save_upload(payload)
        metadata = MetadataProcessor().view_metadata(upload_path)
        metadata = _safe_json(metadata or {})
        return {
            "status": "success" if metadata else "no_metadata",
            "filename": os.path.basename(upload_path),
            "metadata": metadata,
            "metadata_count": len(metadata),
            "warnings": processing_warnings(upload_path),
        }

    def clean_response(
        self,
        payload: dict,
        checksum_algorithm: str = "sha256",
    ) -> dict:
        checksum_algorithm = checksum_algorithm.lower()
        if checksum_algorithm not in SUPPORTED_CHECKSUM_ALGORITHMS:
            raise ValueError("unsupported checksum algorithm")

        upload_path = self.save_upload(payload)
        original_metadata = _safe_json(MetadataProcessor().view_metadata(upload_path) or {})
        cleaned_path = get_safe_output_path(
            upload_path,
            output_dir=self.cleaned_dir,
            prefix="cleaned_",
            create_dirs=True,
        )
        result = MetadataProcessor().delete_metadata(upload_path, cleaned_path)
        if not result:
            return {
                "status": "failed",
                "filename": os.path.basename(upload_path),
                "original_metadata": original_metadata,
                "original_metadata_count": len(original_metadata),
                "cleaned_metadata": {},
                "cleaned_metadata_count": 0,
                "warnings": processing_warnings(upload_path),
                "error": "metadata_removal_failed",
            }

        cleaned_metadata = _safe_json(MetadataProcessor().view_metadata(result) or {})
        token = uuid.uuid4().hex
        output_filename = os.path.basename(result)
        self.downloads[token] = DownloadRecord(result, output_filename)
        return {
            "status": "success",
            "filename": os.path.basename(upload_path),
            "output_filename": output_filename,
            "download_url": f"/api/download/{token}",
            "original_metadata": original_metadata,
            "original_metadata_count": len(original_metadata),
            "cleaned_metadata": cleaned_metadata,
            "cleaned_metadata_count": len(cleaned_metadata),
            "warnings": processing_warnings(upload_path),
            "checksums": {
                f"input_{checksum_algorithm}": get_file_checksum(
                    upload_path,
                    checksum_algorithm,
                ),
                f"output_{checksum_algorithm}": get_file_checksum(
                    result,
                    checksum_algorithm,
                ),
            },
        }

    def download_record(self, token: str) -> Optional[DownloadRecord]:
        record = self.downloads.get(token)
        if not record or not os.path.exists(record.file_path):
            return None
        return record

    def file_record(self, collection: str, filename: str) -> DownloadRecord:
        file_path = self._stored_file_path(collection, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(filename)
        return DownloadRecord(file_path, os.path.basename(file_path))

    def delete_file(self, collection: str, filename: str) -> dict:
        file_path = self._stored_file_path(collection, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(filename)
        os.remove(file_path)
        self.downloads = {
            token: record
            for token, record in self.downloads.items()
            if os.path.abspath(record.file_path) != os.path.abspath(file_path)
        }
        return {
            "status": "deleted",
            "collection": collection,
            "filename": filename,
            "files": self.files_response(),
        }


def _handler_factory(app: WebApp):
    class MetadataCleanerWebHandler(BaseHTTPRequestHandler):
        server_version = "MetadataCleanerWeb/1.0"

        def log_message(self, format, *args):
            return

        def _send_bytes(
            self,
            status: HTTPStatus,
            body: bytes,
            content_type: str,
            headers: Optional[dict] = None,
        ) -> None:
            self.send_response(status.value)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: HTTPStatus, payload: dict) -> None:
            body = json.dumps(payload, default=str, sort_keys=True).encode("utf-8")
            self._send_bytes(status, body, "application/json; charset=utf-8")

        def _read_json(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                raise ValueError("request body is required")
            max_request_bytes = int(app.max_upload_bytes * 1.4) + 4096
            if content_length > max_request_bytes:
                raise ValueError("request body exceeds the configured size limit")
            raw_body = self.rfile.read(content_length)
            try:
                return json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("request body must be JSON") from exc

        def _send_file(self, record: DownloadRecord, disposition: str) -> None:
            content_type = (
                mimetypes.guess_type(record.filename)[0]
                or "application/octet-stream"
            )
            with open(record.file_path, "rb") as input_file:
                body = input_file.read()
            self._send_bytes(
                HTTPStatus.OK,
                body,
                content_type,
                headers={
                    "Content-Disposition": (
                        f'{disposition}; filename="{record.filename}"'
                    )
                },
            )

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/":
                self._send_bytes(
                    HTTPStatus.OK,
                    HTML_PAGE.encode("utf-8"),
                    "text/html; charset=utf-8",
                )
                return
            if path == "/api/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if path == "/api/files":
                self._send_json(HTTPStatus.OK, app.files_response())
                return
            if path.startswith("/api/files/"):
                try:
                    collection, filename = _parse_file_route(path)
                    self._send_file(app.file_record(collection, filename), "inline")
                except ValueError as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                except FileNotFoundError:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "file_not_found"})
                return
            if path.startswith("/api/download/"):
                token = unquote(path.rsplit("/", 1)[-1])
                record = app.download_record(token)
                if record is None:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "download_not_found"})
                    return
                self._send_file(record, "attachment")
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self):
            try:
                path = urlparse(self.path).path
                payload = self._read_json()
                if path == "/api/metadata":
                    self._send_json(HTTPStatus.OK, app.metadata_response(payload))
                    return
                if path == "/api/clean":
                    algorithm = str(payload.get("checksum_algorithm") or "sha256")
                    self._send_json(
                        HTTPStatus.OK,
                        app.clean_response(payload, checksum_algorithm=algorithm),
                    )
                    return
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except Exception as exc:
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"server_error: {exc}"},
                )

        def do_DELETE(self):
            path = urlparse(self.path).path
            if not path.startswith("/api/files/"):
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            try:
                collection, filename = _parse_file_route(path)
                self._send_json(HTTPStatus.OK, app.delete_file(collection, filename))
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except FileNotFoundError:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "file_not_found"})

    return MetadataCleanerWebHandler


def run_web_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = False,
    workspace: Optional[str] = None,
) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("The web UI is local-only; use 127.0.0.1 or localhost")

    if workspace:
        Path(workspace).mkdir(parents=True, exist_ok=True)
        app = WebApp(workspace)
        server = ThreadingHTTPServer((host, port), _handler_factory(app))
        _serve(server, host, port, open_browser)
        return

    with tempfile.TemporaryDirectory(prefix="metadata-cleaner-web-") as temp_dir:
        app = WebApp(temp_dir)
        server = ThreadingHTTPServer((host, port), _handler_factory(app))
        _serve(server, host, port, open_browser)


def _serve(
    server: ThreadingHTTPServer,
    host: str,
    port: int,
    open_browser: bool,
) -> None:
    url = f"http://{host}:{port}/"
    print(f"Metadata Cleaner Web UI running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMetadata Cleaner Web UI stopped.")
    finally:
        server.server_close()


HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Metadata Cleaner</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #18212f;
      --muted: #5c687a;
      --line: #dbe2ea;
      --blue: #1f6feb;
      --green: #16833a;
      --amber: #a05a00;
      --red: #c7362f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 650;
      letter-spacing: 0;
    }
    main {
      width: min(1320px, 100%);
      margin: 0 auto;
      padding: 18px;
    }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto auto auto auto;
      gap: 10px;
      align-items: center;
      margin-bottom: 16px;
    }
    .filebox, select, button, .download, .file-action {
      min-height: 40px;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
    }
    button, .download, .file-action {
      cursor: pointer;
      font-weight: 600;
      text-decoration: none;
      white-space: nowrap;
    }
    button.primary {
      background: var(--blue);
      border-color: var(--blue);
      color: #fff;
    }
    button:disabled {
      cursor: not-allowed;
      opacity: .55;
    }
    button.danger {
      border-color: #f3b5b0;
      color: var(--red);
    }
    .status {
      min-height: 28px;
      color: var(--muted);
      margin: 0 0 14px;
    }
    .status.error { color: var(--red); }
    .status.ok { color: var(--green); }
    .compare {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: 420px;
      overflow: hidden;
    }
    .section-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
    }
    h2 {
      margin: 0;
      font-size: 15px;
      font-weight: 650;
    }
    .count {
      color: var(--muted);
      font-size: 13px;
    }
    .content {
      padding: 12px 14px 16px;
      overflow: auto;
      max-height: calc(100vh - 190px);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 8px 6px;
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
      text-transform: uppercase;
    }
    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .empty {
      color: var(--muted);
      padding: 18px 0;
    }
    .warnings {
      margin: 0 0 14px;
      padding: 10px 12px;
      background: #fff8ea;
      border: 1px solid #f0d098;
      border-radius: 6px;
      color: var(--amber);
    }
    .download-row {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      margin-bottom: 10px;
    }
    .file-browser {
      min-height: 0;
      margin: 0 0 16px;
    }
    .file-lists {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      padding: 14px;
    }
    h3 {
      margin: 0 0 8px;
      font-size: 13px;
      font-weight: 650;
    }
    .file-action {
      display: inline-flex;
      min-height: 32px;
      align-items: center;
      justify-content: center;
      padding: 5px 8px;
      font-size: 13px;
    }
    .file-actions {
      display: flex;
      justify-content: flex-end;
      gap: 6px;
    }
    @media (max-width: 820px) {
      .toolbar { grid-template-columns: 1fr; }
      .compare { grid-template-columns: 1fr; }
      .file-lists { grid-template-columns: 1fr; }
      .content { max-height: none; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Metadata Cleaner</h1>
    <span id="serverStatus" class="count">Local session</span>
  </header>
  <main>
    <div class="toolbar">
      <input class="filebox" id="fileInput" type="file">
      <select id="checksumAlgorithm" aria-label="Checksum algorithm">
        <option value="sha256">SHA-256</option>
        <option value="sha512">SHA-512</option>
        <option value="blake2b">BLAKE2b</option>
      </select>
      <button id="inspectButton" disabled>View Metadata</button>
      <button id="cleanButton" class="primary" disabled>Clean Copy</button>
      <button id="filesButton">Files</button>
    </div>
    <p id="status" class="status">Select a file to begin.</p>
    <div id="warnings"></div>
    <section id="fileBrowser" class="file-browser" hidden>
      <div class="section-head">
        <h2>Local Files</h2>
        <button id="refreshFilesButton">Refresh</button>
      </div>
      <div class="file-lists">
        <div>
          <h3>Original Uploads</h3>
          <div id="originalFiles" class="empty">No uploaded files.</div>
        </div>
        <div>
          <h3>Cleaned Copies</h3>
          <div id="cleanedFiles" class="empty">No cleaned files.</div>
        </div>
      </div>
    </section>
    <div class="compare">
      <section>
        <div class="section-head">
          <h2>Original Metadata</h2>
          <span id="originalCount" class="count">0 fields</span>
        </div>
        <div id="originalMetadata" class="content empty">No file selected.</div>
      </section>
      <section>
        <div class="section-head">
          <h2>Cleaned Metadata</h2>
          <span id="cleanedCount" class="count">0 fields</span>
        </div>
        <div id="downloadRow" class="download-row" hidden></div>
        <div id="cleanedMetadata" class="content empty">No cleaned copy yet.</div>
      </section>
    </div>
  </main>
  <script>
    const fileInput = document.getElementById('fileInput');
    const inspectButton = document.getElementById('inspectButton');
    const cleanButton = document.getElementById('cleanButton');
    const statusEl = document.getElementById('status');
    const warningsEl = document.getElementById('warnings');
    const originalEl = document.getElementById('originalMetadata');
    const cleanedEl = document.getElementById('cleanedMetadata');
    const originalCount = document.getElementById('originalCount');
    const cleanedCount = document.getElementById('cleanedCount');
    const downloadRow = document.getElementById('downloadRow');
    const checksumAlgorithm = document.getElementById('checksumAlgorithm');
    const filesButton = document.getElementById('filesButton');
    const fileBrowser = document.getElementById('fileBrowser');
    const refreshFilesButton = document.getElementById('refreshFilesButton');
    const originalFiles = document.getElementById('originalFiles');
    const cleanedFiles = document.getElementById('cleanedFiles');

    function setStatus(message, type = '') {
      statusEl.textContent = message;
      statusEl.className = `status ${type}`;
    }

    function setBusy(busy) {
      inspectButton.disabled = busy || !fileInput.files.length;
      cleanButton.disabled = busy || !fileInput.files.length;
    }

    function renderWarnings(warnings) {
      warningsEl.innerHTML = '';
      if (!warnings || !warnings.length) return;
      const box = document.createElement('div');
      box.className = 'warnings';
      box.textContent = warnings.join(' ');
      warningsEl.appendChild(box);
    }

    function renderMetadata(target, countTarget, metadata) {
      const keys = Object.keys(metadata || {});
      countTarget.textContent = `${keys.length} ${keys.length === 1 ? 'field' : 'fields'}`;
      target.innerHTML = '';
      target.classList.toggle('empty', keys.length === 0);
      if (!keys.length) {
        target.textContent = 'No metadata found.';
        return;
      }
      const table = document.createElement('table');
      table.innerHTML = '<thead><tr><th>Field</th><th>Value</th></tr></thead>';
      const tbody = document.createElement('tbody');
      keys.sort().forEach((key) => {
        const row = document.createElement('tr');
        const keyCell = document.createElement('td');
        const valueCell = document.createElement('td');
        const pre = document.createElement('pre');
        keyCell.textContent = key;
        pre.textContent = typeof metadata[key] === 'string'
          ? metadata[key]
          : JSON.stringify(metadata[key], null, 2);
        valueCell.appendChild(pre);
        row.append(keyCell, valueCell);
        tbody.appendChild(row);
      });
      table.appendChild(tbody);
      target.appendChild(table);
    }

    async function selectedFilePayload() {
      const file = fileInput.files[0];
      const buffer = await file.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      const chunkSize = 0x8000;
      for (let index = 0; index < bytes.length; index += chunkSize) {
        binary += String.fromCharCode.apply(
          null,
          bytes.subarray(index, index + chunkSize)
        );
      }
      return {
        filename: file.name,
        content_base64: btoa(binary),
        checksum_algorithm: checksumAlgorithm.value
      };
    }

    async function postJson(path, payload) {
      const response = await fetch(path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Request failed');
      return data;
    }

    async function getJson(path) {
      const response = await fetch(path);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Request failed');
      return data;
    }

    function formatBytes(size) {
      if (size < 1024) return `${size} B`;
      if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }

    function formatModified(seconds) {
      if (!seconds) return '';
      return new Date(seconds * 1000).toLocaleString();
    }

    function renderFileList(target, files, emptyText) {
      target.innerHTML = '';
      target.classList.toggle('empty', !files.length);
      if (!files.length) {
        target.textContent = emptyText;
        return;
      }

      const table = document.createElement('table');
      table.innerHTML = '<thead><tr><th>Name</th><th>Size</th><th>Modified</th><th></th></tr></thead>';
      const tbody = document.createElement('tbody');
      files.forEach((item) => {
        const row = document.createElement('tr');
        const nameCell = document.createElement('td');
        const sizeCell = document.createElement('td');
        const modifiedCell = document.createElement('td');
        const actionsCell = document.createElement('td');
        const actions = document.createElement('div');
        const viewLink = document.createElement('a');
        const deleteButton = document.createElement('button');

        nameCell.textContent = item.filename;
        sizeCell.textContent = formatBytes(item.size);
        modifiedCell.textContent = formatModified(item.modified);
        actions.className = 'file-actions';
        viewLink.className = 'file-action';
        viewLink.href = item.view_url;
        viewLink.target = '_blank';
        viewLink.rel = 'noopener';
        viewLink.textContent = 'View';
        deleteButton.className = 'file-action danger';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', async () => {
          if (!window.confirm(`Delete ${item.filename}?`)) return;
          deleteButton.disabled = true;
          try {
            const response = await fetch(item.delete_url, {method: 'DELETE'});
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Delete failed');
            renderFileList(originalFiles, data.files.originals, 'No uploaded files.');
            renderFileList(cleanedFiles, data.files.cleaned, 'No cleaned files.');
            setStatus(`Deleted ${item.filename}.`, 'ok');
          } catch (error) {
            setStatus(error.message, 'error');
          } finally {
            deleteButton.disabled = false;
          }
        });

        actions.append(viewLink, deleteButton);
        actionsCell.appendChild(actions);
        row.append(nameCell, sizeCell, modifiedCell, actionsCell);
        tbody.appendChild(row);
      });
      table.appendChild(tbody);
      target.appendChild(table);
    }

    async function loadFiles() {
      const data = await getJson('/api/files');
      renderFileList(originalFiles, data.originals, 'No uploaded files.');
      renderFileList(cleanedFiles, data.cleaned, 'No cleaned files.');
    }

    fileInput.addEventListener('change', () => {
      const hasFile = fileInput.files.length > 0;
      inspectButton.disabled = !hasFile;
      cleanButton.disabled = !hasFile;
      warningsEl.innerHTML = '';
      downloadRow.hidden = true;
      downloadRow.innerHTML = '';
      renderMetadata(originalEl, originalCount, {});
      renderMetadata(cleanedEl, cleanedCount, {});
      setStatus(hasFile ? fileInput.files[0].name : 'Select a file to begin.');
    });

    inspectButton.addEventListener('click', async () => {
      setBusy(true);
      setStatus('Reading metadata...');
      try {
        const data = await postJson('/api/metadata', await selectedFilePayload());
        renderMetadata(originalEl, originalCount, data.metadata);
        renderWarnings(data.warnings);
        if (!fileBrowser.hidden) await loadFiles();
        setStatus('Original metadata loaded.', 'ok');
      } catch (error) {
        setStatus(error.message, 'error');
      } finally {
        setBusy(false);
      }
    });

    cleanButton.addEventListener('click', async () => {
      setBusy(true);
      setStatus('Cleaning metadata copy...');
      try {
        const data = await postJson('/api/clean', await selectedFilePayload());
        renderMetadata(originalEl, originalCount, data.original_metadata);
        renderMetadata(cleanedEl, cleanedCount, data.cleaned_metadata);
        renderWarnings(data.warnings);
        downloadRow.innerHTML = '';
        if (data.download_url) {
          const link = document.createElement('a');
          link.className = 'download';
          link.href = data.download_url;
          link.textContent = `Download ${data.output_filename}`;
          downloadRow.appendChild(link);
          downloadRow.hidden = false;
        }
        if (data.status === 'success') {
          if (!fileBrowser.hidden) await loadFiles();
          setStatus('Cleaned copy created.', 'ok');
        } else {
          setStatus(data.error || 'Metadata removal failed.', 'error');
        }
      } catch (error) {
        setStatus(error.message, 'error');
      } finally {
        setBusy(false);
      }
    });

    filesButton.addEventListener('click', async () => {
      fileBrowser.hidden = !fileBrowser.hidden;
      filesButton.textContent = fileBrowser.hidden ? 'Files' : 'Hide Files';
      if (fileBrowser.hidden) return;
      setStatus('Loading local files...');
      try {
        await loadFiles();
        setStatus('Local files loaded.', 'ok');
      } catch (error) {
        setStatus(error.message, 'error');
      }
    });

    refreshFilesButton.addEventListener('click', async () => {
      setStatus('Refreshing local files...');
      try {
        await loadFiles();
        setStatus('Local files refreshed.', 'ok');
      } catch (error) {
        setStatus(error.message, 'error');
      }
    });
  </script>
</body>
</html>
"""
