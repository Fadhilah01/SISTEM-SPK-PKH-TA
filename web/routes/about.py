"""Blueprint — Informasi sistem & metrik model."""
from flask import Blueprint, render_template
from core.auth import login_required
from core.predictor import predictor, model_loaded

about_bp = Blueprint('about', __name__)


@about_bp.route('/about')
@login_required
def index():
    """Informasi tentang sistem dan model."""
    metrics = predictor.get_metrics() if predictor else {}
    return render_template('about.html', metrics=metrics, model_loaded=model_loaded)
