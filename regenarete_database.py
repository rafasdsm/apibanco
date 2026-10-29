from os import system
from generate_data import GenerateFakeData

def reconstruct_database():
    data = Dbcontroller().open_text()["server"]

    system(f"sqlcmd -S {data["server"]} -d {data["database"]} -i site.sql -E")

    GenerateFakeData().generate_all()
