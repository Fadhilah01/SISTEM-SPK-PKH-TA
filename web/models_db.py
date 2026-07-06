"""Model database untuk SPK PKH."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'


class CalonPenerima(db.Model):
    __tablename__ = 'calon_penerima'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    penghasilan = db.Column(db.String(100), nullable=False)  # Kategori Desil (teks)
    pekerjaan = db.Column(db.String(100), nullable=False)    # Pekerjaan (teks)
    kepemilikan_aset = db.Column(db.String(100), nullable=False) # Aset (teks)
    ibu_hamil = db.Column(db.Boolean, default=False)
    anak_usia_dini = db.Column(db.Boolean, default=False)
    anak_sekolah = db.Column(db.Boolean, default=False)
    disabilitas = db.Column(db.Boolean, default=False)
    lansia = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Kolom Pencatatan Nilai Skor (1-5 untuk ordinal, 0/1 untuk biner)
    skor_penghasilan = db.Column(db.Integer, nullable=False)
    skor_pekerjaan = db.Column(db.Integer, nullable=False)
    skor_kepemilikan_aset = db.Column(db.Integer, nullable=False)
    skor_ibu_hamil = db.Column(db.Integer, nullable=False, default=0)
    skor_anak_usia_dini = db.Column(db.Integer, nullable=False, default=0)
    skor_anak_sekolah = db.Column(db.Integer, nullable=False, default=0)
    skor_disabilitas = db.Column(db.Integer, nullable=False, default=0)
    skor_lansia = db.Column(db.Integer, nullable=False, default=0)

    # Relasi ke hasil keputusan
    hasil = db.relationship('HasilKeputusan', backref='calon', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Calon {self.nama}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'alamat': self.alamat,
            'penghasilan': self.penghasilan,
            'pekerjaan': self.pekerjaan,
            'kepemilikan_aset': self.kepemilikan_aset,
            'ibu_hamil': self.ibu_hamil,
            'anak_usia_dini': self.anak_usia_dini,
            'anak_sekolah': self.anak_sekolah,
            'disabilitas': self.disabilitas,
            'lansia': self.lansia,
            'skor_penghasilan': self.skor_penghasilan,
            'skor_pekerjaan': self.skor_pekerjaan,
            'skor_kepemilikan_aset': self.skor_kepemilikan_aset,
            'skor_ibu_hamil': self.skor_ibu_hamil,
            'skor_anak_usia_dini': self.skor_anak_usia_dini,
            'skor_anak_sekolah': self.skor_anak_sekolah,
            'skor_disabilitas': self.skor_disabilitas,
            'skor_lansia': self.skor_lansia
        }


class HasilKeputusan(db.Model):
    __tablename__ = 'hasil_keputusan'

    id = db.Column(db.Integer, primary_key=True)
    id_calon = db.Column(db.Integer, db.ForeignKey('calon_penerima.id'), nullable=False)
    hasil_prediksi = db.Column(db.Boolean, nullable=False)  # True=Layak, False=Tidak
    label_prediksi = db.Column(db.String(20), nullable=False)  # "Layak" / "Tidak Layak"
    probabilitas = db.Column(db.Float, nullable=True)       # confidence score
    tanggal_prediksi = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    oleh = db.Column(db.String(50), default='Sistem')

    def __repr__(self):
        return f'<Hasil {self.label_prediksi} untuk calon #{self.id_calon}>'

