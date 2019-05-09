import sqlite3
import pandas as pd

DATA_BASE_NAME = 'database.db'


def update_db(data_frame):
    connection = sqlite3.connect(DATA_BASE_NAME)
    cursor = connection.cursor()

    for index, row in data_frame.iterrows():
        garbage_can_id = row['garbageCan']
        volume = row['volume']
        time_str = row['time']
        cursor.execute(
            "INSERT INTO GarbageRecord (garbageCan, volume, time)" +
            "VALUES (?,?,?);", (garbage_can_id, volume, str(time_str))
        )

    connection.commit()
    connection.close()


def query_data(garbage_can_id):
    connection = sqlite3.connect(DATA_BASE_NAME)

    cursor = connection.cursor()
    cursor.execute("SELECT * from GarbageRecord WHERE garbageCan = ?", [garbage_can_id])
    result = cursor.fetchall()

    connection.close()
    return result


def reconstruct_db():
    database = sqlite3.connect(DATA_BASE_NAME)
    cursor = database.cursor()
    cursor.execute(
        "DROP TABLE IF EXISTS GarbageRecord "
    )
    cursor.execute(
        "CREATE TABLE GarbageRecord (" +
        "id INTEGER PRIMARY KEY NOT NULL," +
        "garbageCan TEXT NOT NULL," +
        "volume REAL NOT NULL," +
        "time DATETIME NOT NULL" +
        ")"
    )

    df = pd.DataFrame(pd.read_csv('Data.csv'))
    update_db(df)


if __name__ == '__main__':
    reconstruct_db()
