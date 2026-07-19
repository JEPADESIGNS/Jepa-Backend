"""Simple PDF export helpers for JEPA Site Manager reports."""

from __future__ import annotations

from pathlib import Path


def _escape_pdf_text(value: str) -> str:
    return value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def generate_report_pdf(output_path: str | Path, project_name: str, client: str, report_date: str, summary: str) -> bool:
    """Create a tiny PDF report file for the supplied project details.

    The implementation intentionally uses a minimal PDF structure so the feature
    works without adding third-party dependencies while preserving the Phase 1
    reporting workflow in the desktop app.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        'JEPA Site Manager - Daily Report',
        f'Project: {project_name}',
        f'Client: {client or "N/A"}',
        f'Date: {report_date}',
        '',
        'Summary:',
        summary or 'No summary provided.',
    ]

    text_stream = '\n'.join(lines)

    # Build a minimal valid PDF with one page using Helvetica text.
    objects = []
    objects.append('<< /Type /Catalog /Pages 2 0 R >>')
    objects.append('<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
    objects.append('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>')
    objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')

    escaped_text = _escape_pdf_text(text_stream)
    content = (
        'BT\n'
        '/F1 10 Tf\n'
        '72 760 Td\n'
        f'({escaped_text}) Tj\n'
        'ET'
    )
    content_bytes = content.encode('latin-1', errors='ignore')
    objects.append(f'<< /Length {len(content_bytes)} >>\nstream\n{content_bytes.decode("latin-1")}\nendstream')

    pdf_parts = ['%PDF-1.4']
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len('\n'.join(pdf_parts).encode('latin-1')))
        pdf_parts.append(f'{index} 0 obj\n{obj}\nendobj')

    xref_position = len('\n'.join(pdf_parts).encode('latin-1'))
    pdf_parts.append('xref')
    pdf_parts.append(f'0 {len(objects) + 1}')
    pdf_parts.append('0000000000 65535 f ')

    for offset in offsets[1:]:
        pdf_parts.append(f'{offset:010d} 00000 n ')

    pdf_parts.append('trailer')
    pdf_parts.append(f'<< /Size {len(objects) + 1} /Root 1 0 R >>')
    pdf_parts.append(f'startxref\n{xref_position}\n%%EOF')

    out_path.write_bytes('\n'.join(pdf_parts).encode('latin-1'))
    return out_path.exists()
