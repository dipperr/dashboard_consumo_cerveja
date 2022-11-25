import pandas as pd

from database import DB
from querys import *


df = pd.read_csv('./dataset/Consumo_cerveja.csv', sep=';')

db = DB()

conn = db.connect()
cursor = conn.cursor()

# Create databse if not exists
cursor.execute(create_database)
cursor.execute(use_database)

# Create table if not exists
cursor.execute(create_table)

cursor.executemany(insert_data, [tuple(row) for row in df.itertuples(index=False)])
conn.commit()

cursor.close()
conn.close()
