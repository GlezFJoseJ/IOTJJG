import sqlite3
from datetime import datetime


class DBStorage:
    def __init__(self, db_name = "data.db"):
        self.db_name = db_name
        self.db = None
        self.cursor = None

    def connect(self):
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()

    def disconnect(self):
        self.db.close()

    def create_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS mediciones (id INTEGER PRIMARY KEY AUTOINCREMENT, valor_luminosidad INTEGER, fecha TIMESTAMP)")

    def insert(self, luminosidad):
        fecha = datetime.now()
        self.cursor.execute(
            "INSERT INTO mediciones (valor_luminosidad, fecha) VALUES (?,?)", (luminosidad, fecha))
        self.db.commit()

    def get_measurements_by_time(self, start_date, end_date):
        self.cursor.execute("SELECT * FROM mediciones WHERE fecha >= ? AND fecha <= ?", (start_date, end_date))
        # self.cursor.execute("SELECT * FROM mediciones")
        labels = []
        luminities = []

        for row in self.cursor.fetchall():
            luminities.append(row[1])
            labels.append(row[2])

        return {
            "labels": labels,
            "luminities": luminities,
        }

    def get_all_measurements(self):
        self.cursor.execute("SELECT * FROM mediciones")
        labels = []
        luminities = []

        for row in self.cursor.fetchall():
            labels.append(row[2])
            luminities.append(row[1])

        return {
            "labels": labels,
            "luminities": luminities,
        }


if __name__ == "__main__":
    db = DBStorage("data.db")
    db.connect()
    db.create_table()
    db.insert(100)
    print(db.get_all_measurements())
    db.disconnect()
