from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.blocked: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        hidden = "display:none" in attributes.get("style", "").replace(" ", "").lower()
        if tag in {"head", "script", "style", "svg", "noscript", "ix:header", "ix:hidden", "ix:resources"} or hidden:
            self.blocked.append(tag)
        elif not self.blocked and tag in {"p", "div", "br", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.blocked:
            self.blocked.remove(tag)
        elif not self.blocked and tag in {"p", "div", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.blocked:
            self.parts.append(data)


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_file: str
    chunk_index: int
    text: str
    section: str | None


def extract_html_text(path: Path) -> str:
    parser = _TextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def chunk_text(text: str, source_file: str, max_chars: int = 1400, overlap: int = 200) -> list[DocumentChunk]:
    if max_chars <= overlap:
        raise ValueError("max_chars must exceed overlap")
    normalized = re.sub(r"\s+", " ", text).strip()
    chunks: list[DocumentChunk] = []
    start = 0
    index = 0
    while start < len(normalized):
        end = min(len(normalized), start + max_chars)
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary
        content = normalized[start:end].strip()
        chunks.append(DocumentChunk(f"{source_file}:{index}", source_file, index, content, None))
        if end == len(normalized):
            break
        start = max(0, end - overlap)
        index += 1
    return chunks


def chunks_from_file(path: Path) -> list[DocumentChunk]:
    return chunk_text(extract_html_text(path), path.name)
