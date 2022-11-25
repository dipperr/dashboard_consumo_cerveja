from dateutil.parser import parse
from datetime import datetime
import numpy as np
import pandas as pd
import pickle
import requests

from database import DB
from querys import use_database, select_data
from map_dates import *


class Temperature:
    def __init__(self):
        self.__url = 'https://apitempo.inmet.gov.br/condicao/capitais/'

    def __query(self, date):
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        elif isinstance(date, str):
            date = parse(date, dayfirst=True).strftime('%Y-%m-%d')
        else:
            raise Exception('Formato inválido!!!')

        r = requests.get(self.__url + date)
        r.raise_for_status()
        return r.json()

    def get_temperature(self, date, cidade='campo grande'):
        """
        Consulta a previsão do tempo na api do INMET.
        O formato da data de entrada pode ser tanto um
        objeto datetime como uma data formatada no padrão
        brasileiro "dia/mes/ano"
        """

        r_date = self.__query(date)
        for i in r_date:
            if i['CAPITAL'] == cidade.upper():
                return dict(
                    cidade=i['CAPITAL'].lower(),
                    data=date.replace('/', '-') if isinstance(date, str) else date.strftime('%d-%m-%Y'),
                    tmin=i['TMIN18'].replace('*', ''), tmax=i['TMAX18'].replace('*', ''),
                    pmax=i['PMAX12'].replace('*', '')
                )


class Model:
    def __init__(self, path_model):
        self.__path_model = path_model

    def load_model(self):
        """carrega o modelo de regressão linear"""
        with open(self.__path_model, 'rb') as f:
            m = pickle.load(f)
        return m

    def predict(self, temp, precip, date):
        """date deve ser um objeto datetime"""
        fds = days_wk[date.strftime('%a')]
        x = np.array([temp, precip, fds]).reshape(1, -1)
        m = self.load_model()
        return m.predict(x)


class FormatNum:
    @staticmethod
    def format_float(num):
        """adiciona o separador de milhar em números float"""
        i, d = str(num).split('.')[0], str(num).split('.')[-1]
        i = format(int(i), ',d').replace(',', '.')
        return i + ',' + d

    @staticmethod
    def format_int(num):
        """adiciona o separador de milhar em números int"""
        return format(int(num), ',d').replace(',', '.')


class LoadDframe:
    """responsável por ler os dados do banco de dados e tratá-los"""

    def load(self, path_df):
        db = DB()
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(use_database)
        cursor.execute(select_data)
        dframe = pd.DataFrame(
            cursor.fetchall(), columns=['data', 'temp_media', 'temp_min', 'temp_max', 'chuva', 'fds', 'consumo']
        )
        cursor.close()
        conn.close()
        return self.transform_data(dframe)

    def transform_data(self, dframe):
        dframe['data'] = pd.to_datetime(dframe['data'], dayfirst=True)
        dframe['fds'] = dframe['fds'].map(weekend)
        dframe['mes'] = dframe['data'].apply(lambda d: d.strftime('%b')).map(months)
        dframe['dia'] = dframe['data'].apply(lambda d: d.strftime('%a')).map(days)
        dframe['fds'] = dframe['fds'].astype('category')
        dframe['dif_consumo'] = dframe.consumo.diff().round(decimals=2)
        dframe['dif_pct_consumo'] = dframe.consumo.pct_change().round(decimals=2)
        dframe.set_index(keys='data', inplace=True)
        return dframe
