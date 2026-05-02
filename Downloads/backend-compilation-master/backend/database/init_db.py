from database.db import engine, Base

def init_db():
    print("START DB INIT")
    Base.metadata.create_all(bind=engine)
    print("END DB INIT")