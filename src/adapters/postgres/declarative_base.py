from google.cloud.sql.connector import Connector, IPTypes

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ

from config import DB_NAME, DB_PASSWORD, DB_USER, INSTANCE_CONNECTION_NAME, ENVIRONMENT,DB_HOST, DB_PORT


class GetDB:
    def __init__(self):
        if ENVIRONMENT == "dev":
            environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./apikey.json"
            db_url = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            self.engine = create_engine(db_url)
        else: 
            connector = Connector()
            
            def getconn():
                return connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASSWORD,
                db= DB_NAME,
                ip_type=IPTypes.PRIVATE
            )

            self.engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_pre_ping=True
            )

        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self):
        return self.session_local()

    def get_engine(self):
        return self.engine

    def close(self):
        self.engine.dispose()


db1 = GetDB()
