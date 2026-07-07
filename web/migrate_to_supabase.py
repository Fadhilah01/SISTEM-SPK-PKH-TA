import os
import sys
import argparse

# Tambahkan direktori saat ini ke path pencarian modul
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, make_transient
from models_db import db, User, CalonPenerima, HasilKeputusan

def main():
    parser = argparse.ArgumentParser(description="Migrasi database SQLite ke Supabase PostgreSQL")
    parser.add_argument("--url", help="URL database PostgreSQL Supabase (free transaction pooler URI)")
    args = parser.parse_args()

    # Muat file .env secara otomatis jika ada
    base_dir = os.path.abspath(os.path.dirname(__file__))
    env_file = os.path.join(base_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    os.environ[key] = val

    # Ambil URL koneksi dari argument atau env
    postgres_uri = args.url or os.environ.get("DATABASE_URL")
    if not postgres_uri:
        print("ERROR: URL database PostgreSQL tidak ditemukan.")
        print("Gunakan argumen --url atau set environment variable DATABASE_URL.")
        sys.exit(1)

    # Standarisasi skema postgres (ubah postgres:// ke postgresql:// untuk SQLAlchemy)
    if postgres_uri.startswith("postgres://"):
        postgres_uri = postgres_uri.replace("postgres://", "postgresql://", 1)

    # Lokasi database SQLite lokal
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sqlite_uri = f"sqlite:///{os.path.join(base_dir, 'spk_pkh.db')}"

    print("=== INISIALISASI MIGRASI DATABASE ===")
    print(f"Sumber (SQLite): {sqlite_uri}")
    # Sembunyikan credential saat mencetak target URL
    masked_url = postgres_uri
    if "@" in postgres_uri:
        parts = postgres_uri.split("@")
        driver_host = parts[0].split("//")
        masked_url = f"{driver_host[0]}//******:******@{parts[1]}"
    print(f"Tujuan (Supabase Postgres): {masked_url}")
    print("---------------------------------------")

    # Koneksi ke SQLite
    try:
        sqlite_engine = create_engine(sqlite_uri)
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print("[OK] Berhasil terhubung ke SQLite.")
    except Exception as e:
        print(f"[FAIL] Gagal menghubungkan ke SQLite: {e}")
        sys.exit(1)

    # Koneksi ke Postgres
    try:
        pg_engine = create_engine(postgres_uri)
        PgSession = sessionmaker(bind=pg_engine)
        pg_session = PgSession()
        print("[OK] Berhasil terhubung ke PostgreSQL (Supabase).")
    except Exception as e:
        print(f"[FAIL] Gagal menghubungkan ke PostgreSQL (Supabase): {e}")
        sys.exit(1)

    # Membuat tabel di Postgres jika belum ada
    try:
        print("Membuat skema tabel di PostgreSQL...")
        db.metadata.create_all(bind=pg_engine)
        print("[OK] Skema tabel berhasil dibuat/diverifikasi.")
    except Exception as e:
        print(f"[FAIL] Gagal membuat skema tabel: {e}")
        sys.exit(1)

    # Migrasi Data
    try:
        print("Mengambil data dari SQLite...")
        users = sqlite_session.query(User).all()
        calons = sqlite_session.query(CalonPenerima).all()
        hasils = sqlite_session.query(HasilKeputusan).all()
        print(f"[OK] Ditemukan {len(users)} user, {len(calons)} calon penerima, dan {len(hasils)} hasil keputusan.")

        # 1. Migrasi Users
        if users:
            print("Memigrasikan tabel 'users'...")
            for u in users:
                sqlite_session.expunge(u)
                make_transient(u)
                pg_session.add(u)
            pg_session.commit()
            print(f"[OK] {len(users)} user berhasil dipindahkan.")

        # 2. Migrasi CalonPenerima
        if calons:
            print("Memigrasikan tabel 'calon_penerima'...")
            for c in calons:
                sqlite_session.expunge(c)
                make_transient(c)
                pg_session.add(c)
            pg_session.commit()
            print(f"[OK] {len(calons)} calon penerima berhasil dipindahkan.")

        # 3. Migrasi HasilKeputusan
        if hasils:
            print("Memigrasikan tabel 'hasil_keputusan'...")
            for h in hasils:
                sqlite_session.expunge(h)
                make_transient(h)
                pg_session.add(h)
            pg_session.commit()
            print(f"[OK] {len(hasils)} hasil keputusan berhasil dipindahkan.")

        # Atur ulang sequence ID di Postgres
        print("Mengatur ulang sequence ID primary key di PostgreSQL...")
        sequences = [
            ("users", "id"),
            ("calon_penerima", "id"),
            ("hasil_keputusan", "id")
        ]
        for table, col in sequences:
            res = pg_session.execute(text(f"SELECT MAX({col}) FROM {table}")).scalar()
            if res is not None:
                # pg_get_serial_sequence membutuhkan nama tabel dan nama kolom
                pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), {res})"))
        pg_session.commit()
        print("[OK] Sequence ID primary key berhasil diatur ulang.")

        print("\nMIGRASI SELESAI DENGAN SUKSES!")

    except Exception as e:
        pg_session.rollback()
        print(f"\n[ERROR] Terjadi kesalahan selama migrasi: {e}")
        sys.exit(1)
    finally:
        sqlite_session.close()
        pg_session.close()

if __name__ == "__main__":
    main()
