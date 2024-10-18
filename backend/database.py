from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///todo.db')

engine = create_engine(DATABASE_URL)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)



#  curl.exe --location --request POST "http://localhost:8080/realms/todo-app/protocol/openid-connect/token" --header "Content-Type: application/x-www-form-urlencoded" --data-urlencode "grant_type=password" --data-urlencode "client_id=todo-client" --data-urlencode "username=testuser" --data-urlencode "password=password"

# keycloak access token: eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMGM4NWRiMy1mMzcxLTRlZWUtODU3NC1hOGJmOWExZjkwMTAifQ.eyJleHAiOjAsImlhdCI6MTcyODk3NDQ1OSwianRpIjoiODdkM2IyNjEtMzA1NS00M2Q3LWFjZjMtYmVlN2I3Y2UwYjA2IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy90b2RvLWFwcCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9yZWFsbXMvdG9kby1hcHAiLCJ0eXAiOiJSZWdpc3RyYXRpb25BY2Nlc3NUb2tlbiIsInJlZ2lzdHJhdGlvbl9hdXRoIjoiYXV0aGVudGljYXRlZCJ9.hOr40i3jlWds1uTgw48RMgOooQBXzgQ9VEQ3H0T175Q


# stripe publishable key: pk_test_51P14z1SF4qZUZgy06Lfocdd2oHppXl8OsZGEhUelZAneBOl8q9T6fQLKMkf0GXlLvo0ZTx8lhMvE3copYcuGS6wo00UqUdlVXS
# stripe secret key: sk_test_51P14z1SF4qZUZgy0JmcGRib2D7wQOD8ChcV6da7cTDc7KG2wRveIBknprYh5lzgA7UrE9MOH5itXX8qQFmkE9RGU00BmOuqufv

# roles = keycloak_admin.get_client_roles(client_id="88433a40-e9e9-419b-ae5b-0b061f1cb823")