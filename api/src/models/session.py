from sqlalchemy import sql, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db import db, UuidModel


class SessionModel(UuidModel, db.Model):
    __tablename__ = 'sessions'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    user = relationship("UserModel", backref="session_user", viewonly=True)
    access_jti = db.Column(UUID(as_uuid=True), nullable=True)
    refresh_jti = db.Column(UUID(as_uuid=True), nullable=True)
    new_jti = db.Column(UUID(as_uuid=True), nullable=True)
    client = db.Column(db.String(), nullable=True)
    # ip address 45 is because max ipv6 address length is 45 chars
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=sql.func.now())

    relationships = ['user']
    additional_table_columns = ['user']

    @classmethod
    def delete_by_jti(cls, access_jti: str):
        session = cls.query.filter(cls.access_jti == access_jti).first()
        if not session:
            return False
        cls.query.filter(cls.refresh_jti == session.refresh_jti).delete()
        db.session.commit()
        return True

    def delete_child_jti(self):
        self.query.filter(self.new_jti == self.access_jti).delete()
        self.save()

    @classmethod
    def find_by_refresh_jti(cls, refresh_jti):
        return cls.query.filter(cls.refresh_jti == refresh_jti).order_by(cls.created_at.desc()).first()

    def delete_by_refresh_jti(self):
        self.query.filter(and_(SessionModel.refresh_jti == self.refresh_jti, SessionModel.id != self.id)).delete()
        self.save()

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['user_id', 'access_jti', 'refresh_jti']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        item['user'] = None
        if self.user_id:
            item['user'] = self.user.get()
        return item

