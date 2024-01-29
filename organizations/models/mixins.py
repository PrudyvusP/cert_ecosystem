from datetime import date

from ..extentions import db


class DateAddedCreatedMixin:
    """Миксин для моделей, создание и изменение
     которых необходимо отслеживать."""
    date_added = db.Column(db.Date, nullable=False, default=date.today)
    date_updated = db.Column(db.Date, default=date.today, onupdate=date.today)
