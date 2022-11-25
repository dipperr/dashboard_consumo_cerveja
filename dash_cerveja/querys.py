create_database = "CREATE DATABASE IF NOT EXISTS bar"
use_database = "USE bar"
create_table = """CREATE TABLE IF NOT EXISTS venda_cerveja (data varchar(20), temp_media double, temp_min double,
temp_max double, chuva double, fds int, consumo int)"""
insert_data = """INSERT INTO venda_cerveja(data, temp_media, temp_min, temp_max, chuva, fds, consumo)
VALUES(%s, %s, %s, %s, %s, %s, %s)"""
select_data = "SELECT * FROM venda_cerveja"
