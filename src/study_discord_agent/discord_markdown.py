import re


def discord_safe_markdown(text: str) -> str:
    lines = text.splitlines()
    rendered: list[str] = []
    index = 0
    while index < len(lines):
        if _is_table_start(lines, index):
            headers = _parse_cells(lines[index])
            rows: list[list[str]] = []
            index += 2
            while index < len(lines) and _is_table_row(lines[index]):
                rows.append(_parse_cells(lines[index]))
                index += 1
            rendered.extend(_render_table(headers, rows))
            continue
        rendered.append(lines[index])
        index += 1
    return "\n".join(rendered)


def _is_table_start(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and _is_table_row(lines[index])
        and _is_separator_row(lines[index + 1])
    )


def _is_table_row(line: str) -> bool:
    cells = _parse_cells(line)
    return len(cells) >= 2


def _is_separator_row(line: str) -> bool:
    cells = _parse_cells(line)
    return len(cells) >= 2 and all(
        re.fullmatch(r":?-{3,}:?", cell.strip()) is not None for cell in cells
    )


def _parse_cells(line: str) -> list[str]:
    stripped = line.strip()
    if "|" not in stripped:
        return []
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    bullets: list[str] = []
    normalized_headers = [_normalize_header(header) for header in headers]
    for row in rows:
        pairs = [
            (header, cell)
            for header, cell in zip(normalized_headers, row, strict=False)
            if header and cell
        ]
        if not pairs:
            continue
        bullets.append("- " + "; ".join(f"{header}: {cell}" for header, cell in pairs))
    return bullets


def _normalize_header(header: str) -> str:
    return " ".join(header.split()).rstrip(":")
