"""Model database untuk SPK PKH."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class CalonPenerima(db.Model):
    __tablename__ = 'calon_penerima'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    penghasilan = db.Column(db.Float, nullable=False)       # Rupiah/bulan
    pekerjaan = db.Column(db.String(50), nullable=False)
    kepemilikan_aset = db.Column(db.String(50), nullable=False)
    ibu_hamil = db.Column(db.Boolean, default=False)
    anak_usia_dini = db.Column(db.Integer, default=0)
    anak_sekolah = db.Column(db.Integer, default=0)
    disabilitas = db.Column(db.Boolean, default=False)
    lansia = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
