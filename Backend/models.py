from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# creating tables
Base = declarative_base()

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    vowel_recorded = Column(String)
    prediction = Column(Integer) # 0 for control, 1 for hypernasal
    confidence = Column(Float)
    audio_file_path = Column(String, nullable=True) # Path to saved audio file