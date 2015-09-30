from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, User, Catalog, Item

engine = create_engine('sqlite:///catlog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

def test():
    itemlist = session.query(Item).all()
    for item in itemlist:
        print item.name

if __name__ == '__main__':
    test()
