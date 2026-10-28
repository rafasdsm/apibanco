import uvicorn
from database import Dbcontroller
from generate_database import generate_database
from database_test import gerar_dados
from os import system

if __name__ == "__main__":
    try:
        Dbcontroller.connect()
    except:
        generate_database()
        gerar_dados()
    finally:
        system("start apibanco_app.exe")
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
