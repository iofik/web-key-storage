from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:')

class CryptoKey(Base):
     __tablename__ = 'crypto_keys'

     id       = Column(String(length=32), primary_key=True)
     pin      = Column(String(length=32))
     key      = Column(String(length=32)) 
     attempts = Column(Integer)
     expires  = Column(DateTime)

     def __repr__(self):
        return "<CryptoKey(id='%s')>" % self.id
