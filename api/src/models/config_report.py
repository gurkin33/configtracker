from sqlalchemy.dialects.postgresql import UUID

from api.db import db, UuidModel


class ConfigReportModel(UuidModel, db.Model):
    __tablename__ = 'config_reports'

    config_id = db.Column(UUID(as_uuid=True), db.ForeignKey("configs.id"), nullable=False)
    message = db.Column(db.String(4096), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['id', 'config_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    @classmethod
    def delete_all(cls):
        return cls.query.delete()
