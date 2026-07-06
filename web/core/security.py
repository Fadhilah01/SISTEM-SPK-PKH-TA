"""
Security Headers Middleware — inject security headers ke setiap response.
Juga berisi helper untuk validasi file upload dan input.

Didaftarkan di app.py, berjalan sebagai after_request handler.
"""
import os
import re
from flask import g


# ─── Content Security Policy ───
# Mengizinkan CDN Bootstrap, Chart.js, dan Bootstrap Icons
# 'unsafe-inline' diperlukan untuk Bootstrap dan beberapa inline style
_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self'"
)

_SECURITY_HEADERS = {
    'Content-Security-Policy': _CSP,
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    'X-Permitted-Cross-Domain-Policies': 'none',
    'Cross-Origin-Opener-Policy': 'same-origin',
}


def register_security_headers(app):
    """Daftarkan middleware setelah request untuk inject security headers."""

    @app.after_request
    def add_security_headers(response):
        for header, value in _SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ─── File Upload Validation ───

# Magic bytes signatures untuk file Excel/CSV
_FILE_SIGNATURES = {
    # OLE2 (xls): D0 CF 11 E0 A1 B1 1A E1
    'xls': bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]),
    # Office Open XML (xlsx): PK\x03\x04 (ZIP format)
    'xlsx': bytes([0x50, 0x4B, 0x03, 0x04]),
    # CSV bisa plain text — tidak ada magic bytes spesifik
}

ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}
ALLOWED_MIMES = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.csv_alt': 'text/plain',  # CSV kadang dikirim sebagai text/plain
}


def validate_file_upload(file_storage):
    """
    Validasi file upload berdasarkan ekstensi, MIME type, dan magic bytes (untuk Excel).

    Parameters
    ----------
    file_storage : werkzeug.FileStorage

    Returns
    -------
    (is_valid: bool, error_msg: str)
    """
    if not file_storage or not file_storage.filename:
        return False, "Tidak ada file yang dipilih."

    filename = file_storage.filename
    ext = os.path.splitext(filename)[1].lower()

    # 1. Cek ekstensi
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Format file '{ext}' tidak didukung. Gunakan: .xlsx, .xls, .csv"

    # 2. Cek MIME type dari header Content-Type
    mime = file_storage.content_type or ''
    allowed_mime_values = list(ALLOWED_MIMES.values())
    if mime and mime not in allowed_mime_values and ext != '.csv':
        return False, f"MIME type '{mime}' tidak valid untuk file {ext}."

    # 3. Cek magic bytes untuk Excel (gunakan tanda tangan bytes awal)
    # Simpan posisi file saat ini, baca 8 byte pertama, lalu reset
    if ext in ('.xlsx', '.xls'):
        original_pos = file_storage.stream.tell()
        file_storage.stream.seek(0)
        header = file_storage.stream.read(8)
        file_storage.stream.seek(original_pos)

        if ext == '.xlsx' and not header.startswith(b'PK\x03\x04'):
            return False, "File .xlsx tidak valid (bukan ZIP/OOXML format)."
        if ext == '.xls' and not header.startswith(_FILE_SIGNATURES['xls']):
            return False, "File .xls tidak valid (bukan OLE2 format)."

    return True, ""


# ─── Input Sanitization & Validation ───


def validate_text_length(text, field_name, max_length):
    """Validasi panjang teks tidak melebihi batas."""
    if text and len(text) > max_length:
        return False, f"{field_name} maksimal {max_length} karakter."
    return True, ""


def sanitize_html(text):
    """Hapus tag HTML dasar dari input teks untuk cegah XSS."""
    if not text:
        return text
    # Hapus <script>, <iframe>, <object>, <embed>, <applet>
    clean = re.sub(r'<[\s]*(script|iframe|object|embed|applet|link|style|meta)[^>]*>.*?</\1>', '', text, flags=re.I|re.DOTALL)
    # Hapus tag HTML standalone yang mencurigakan
    clean = re.sub(r'<[\s]*(script|iframe|object|embed|applet|link|style|meta)[^>]*/?>', '', clean, flags=re.I)
    return clean
