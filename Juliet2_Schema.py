
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, create_engine, event

Base = declarative_base()

engine = create_engine('sqlite:///C:\\Users\\Andrew\\Desktop\\Juliet2.db', echo=False, connect_args={'check_same_thread': False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Cases(Base):
    __tablename__ = 'Cases'
    model_id = Column(Integer, primary_key =True)
    file_name = Column(String, primary_key=True)
    file_content = Column(Text)
    cwe = Column(String)
    vulnerability_location = Column(String)

class VLW(Base):
    __tablename__ = 'VLW'
    file_name = Column(String, primary_key=True)
    cwe = Column(String)
    cwe_int = Column(Integer)
    vulnerability_location = Column(Integer)
    vlw_content = Column(Text)
    offset = Column(Integer)
    model_id = Column(Integer)    
    
class VLW2(Base):
    __tablename__ = 'VLW2'
    file_name = Column(String, primary_key=True)
    cwe = Column(String)
    cwe_int = Column(Integer)
    vulnerability_location = Column(Integer)
    vlw_content = Column(Text)
    offset = Column(Integer)
    model_id = Column(Integer)    

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
Juliet2 = Session()