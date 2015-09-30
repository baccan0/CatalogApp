from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.functions import current_date, current_time, now

 
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80))
    picture = Column(String(250))
    last_login = Column(DateTime,default = now())
    datetime = Column(DateTime)
    @property
    def time_str(self):
        return "".join([str(self.last_login.year), '-', 
                        str(self.last_login.month), '-',
                        str(self.last_login.day), '-',
                        str(self.last_login.hour), '-',
                        str(self.last_login.minute), '-',
                        str(self.last_login.second),])
    @property
    def serialize(self):
        return {
            "id"          : self.id,
            "name"        : self.name,
            "email"       : self.email,
            "picture"     : self.picture,
            "last_login"  : self.time_str,
                }

class Catalog(Base):
    __tablename__ = 'catalog'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)
    last_edit = Column(DateTime, default= now())
    @property
    def time_str(self):
        return "".join([str(self.last_edit.year), '-', 
                        str(self.last_edit.month), '-',
                        str(self.last_edit.day), '-',
                        str(self.last_edit.hour), '-',
                        str(self.last_edit.minute), '-',
                        str(self.last_edit.second),])
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'user_id'      : self.user_id,
           'last_edit'    : self.time_str, 
       }

 
class Item(Base):
    __tablename__ = 'item'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(1000))
    picture = Column(String(250))
    catalog_id = Column(Integer,ForeignKey('catalog.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    last_edit = Column(DateTime,default = now())
    user = relationship(User)
    catalog = relationship(Catalog)
    @property
    def time_str(self):
        return "".join([str(self.last_edit.year), '-', 
                        str(self.last_edit.month), '-',
                        str(self.last_edit.day), '-',
                        str(self.last_edit.hour), '-',
                        str(self.last_edit.minute), '-',
                        str(self.last_edit.second),])
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'           : self.name,
           'description'    : self.description,
           'id'             : self.id,
           'picture'        : self.picture,
           'catalog_id'     : self.catalog_id,
           'user_id'        : self.user_id,
           'last_edit'      : self.time_str,
       }



engine = create_engine('sqlite:///catlog.db')
 

Base.metadata.create_all(engine)
