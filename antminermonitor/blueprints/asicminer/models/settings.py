from sqlalchemy import Column, Integer, String
from antminermonitor.database import Base

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    value = Column(String(100), nullable=False)
    description = Column(String(255))

    def __repr__(self):
        return "Settings(name='{}', value={}, description='{}')" \
            .format(self.name, self.value, self.description)
