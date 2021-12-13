"""
Module that implements Data Processor class.

DataProcessor helps to prepare data for a model
training.
"""

import pandas as pd
import os

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
class DataProcessor:
    """
        DataProcessor helps to prepare data for a model training.
    """
    def __init__(self, path='../data/'):
        print(CUR_DIR)
        self.path = f"{CUR_DIR}/{path}"
        self.X = None
        self.y = None

    def process_rainfalls_data(self):
        precipitaciones = pd.read_csv(self.path + 'precipitaciones.csv') #[mm]
        precipitaciones['date'] = pd.to_datetime(precipitaciones['date'], format = '%Y-%m-%d')
        precipitaciones = precipitaciones.sort_values(by = 'date',
                                                      ascending = True).reset_index(drop = True)
        precipitaciones['mes'] = precipitaciones.date.apply(lambda x: x.month)
        precipitaciones['ano'] = precipitaciones.date.apply(lambda x: x.year)
        return precipitaciones

    def process_central_bank_data(self):
        banco_central = pd.read_csv(self.path + 'banco_central.csv')
        banco_central['Periodo'] = banco_central['Periodo'].apply(lambda x: x[0:10])
        banco_central['Periodo'] = pd.to_datetime(banco_central['Periodo'],
                                                  format = '%Y-%m-%d', errors = 'coerce')
        banco_central.drop_duplicates(subset = 'Periodo', inplace = True)
        banco_central = banco_central[~banco_central.Periodo.isna()]
        cols_pib = [x for x in list(banco_central.columns) if 'PIB' in x]
        cols_pib.extend(['Periodo'])
        banco_central_pib = banco_central[cols_pib]
        banco_central_pib = banco_central_pib.dropna(how = 'any', axis = 0)

        for col in cols_pib:
            if col == 'Periodo':
                continue
            else:
                banco_central_pib[col] = banco_central_pib[col].apply(lambda x: self.convert_int(x))
        banco_central_pib.sort_values(by = 'Periodo', ascending = True)
        cols_imacec = [x for x in list(banco_central.columns) if 'Imacec' in x]
        cols_imacec.extend(['Periodo'])
        banco_central_imacec = banco_central[cols_imacec]
        banco_central_imacec = banco_central_imacec.dropna(how = 'any', axis = 0)

        for col in cols_imacec:
            if col == 'Periodo':
                continue
            else:
                banco_central_imacec[col] = banco_central_imacec[col].apply(lambda x: self.to_100(x))
                assert(banco_central_imacec[col].max()>100)
                assert(banco_central_imacec[col].min()>30)

        banco_central_imacec.sort_values(by = 'Periodo', ascending = True)
        banco_central_iv = banco_central[['Indice_de_ventas_comercio_real_no_durables_IVCM',
                                          'Periodo']]
        banco_central_iv = banco_central_iv.dropna() # -unidades? #parte 
        banco_central_iv = banco_central_iv.sort_values(by = 'Periodo', ascending = True)
        banco_central_iv['num'] = banco_central_iv.Indice_de_ventas_comercio_real_no_durables_IVCM.apply(lambda x: self.to_100(x))
        banco_central_num = pd.merge(banco_central_pib, banco_central_imacec, on = 'Periodo', how = 'inner')
        banco_central_num = pd.merge(banco_central_num, banco_central_iv,
                                     on = 'Periodo', how = 'inner')
        
        banco_central_num['mes'] = banco_central_num['Periodo'].apply(lambda x: x.month)
        banco_central_num['ano'] = banco_central_num['Periodo'].apply(lambda x: x.year)
        return banco_central_num

    def process_milk_prices_data(self):
        precio_leche = pd.read_csv(self.path + 'precio_leche.csv')
        precio_leche.rename(columns = {'Anio': 'ano', 'Mes': 'mes_pal'}, inplace = True) 
        month_parser = {"Ene": "Jan", "Abr": "Apr", "Ago": "Aug", "Dic": "Dec"}
        precio_leche.replace({"mes_pal": month_parser}, inplace=True)
        precio_leche['mes'] = pd.to_datetime(precio_leche['mes_pal'], format = '%b')
        precio_leche['mes'] = precio_leche['mes'].apply(lambda x: x.month)
        precio_leche['mes-ano'] = precio_leche.apply(lambda x: f'{x.mes}-{x.ano}', axis = 1)
        return precio_leche
    
    def process_traning_data(self):
        precipitaciones = self.process_rainfalls_data()
        banco_central_num = self.process_central_bank_data()
        precio_leche = self.process_milk_prices_data()
        
        precio_leche_pp = pd.merge(precio_leche, precipitaciones, on=['mes','ano'], how='inner')
        precio_leche_pp.drop('date', axis = 1, inplace = True)
        
        precio_leche_pp_pib = pd.merge(precio_leche_pp,
                                       banco_central_num,
                                       on=['mes','ano'], how='inner')
        precio_leche_pp_pib.drop(['Periodo',
                                  'Indice_de_ventas_comercio_real_no_durables_IVCM',
                                  'mes-ano', 'mes_pal'],
                                 axis =1,
                                 inplace = True)
        

        precio_leche_pp_pib = self.add_mean_std_shifts(precio_leche_pp_pib)
        self.X = precio_leche_pp_pib.drop(['Precio_leche'], axis = 1)
        self.y = precio_leche_pp_pib['Precio_leche']
        return self.X, self.y

    def add_mean_std_shifts(self, precio_leche_pp_pib):
        cc_cols = [x for x in precio_leche_pp_pib.columns if x not in ['ano', 'mes']]
        precio_leche_pp_pib_shift3_mean = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).mean().shift(1)
        precio_leche_pp_pib_shift3_mean.columns = [x+'_shift3_mean' for x in precio_leche_pp_pib_shift3_mean.columns]
        precio_leche_pp_pib_shift3_std = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).std().shift(1)
        precio_leche_pp_pib_shift3_std.columns = [x+'_shift3_std' for x in precio_leche_pp_pib_shift3_std.columns] 
        precio_leche_pp_pib_shift1 = precio_leche_pp_pib[cc_cols].shift(1)
        precio_leche_pp_pib_shift1.columns = [x+'_mes_anterior' for x in precio_leche_pp_pib_shift1.columns]
        
        precio_leche_pp_pib = pd.concat([precio_leche_pp_pib['Precio_leche'],
                                         precio_leche_pp_pib_shift3_mean,
                                         precio_leche_pp_pib_shift3_std,
                                         precio_leche_pp_pib_shift1], axis = 1) 
        precio_leche_pp_pib = precio_leche_pp_pib.dropna(how = 'any', axis = 0)
        return precio_leche_pp_pib
    
    def save_data(self):
        self.X.to_csv(self.path + 'X.csv', index=False)
        self.y.to_csv(self.path + 'y.csv', index=False)
    
    def convert_int(self, x):
        return int(x.replace('.', ''))

    def to_100(self, x):
        x = x.split('.')
        if x[0].startswith('1'): #es 100+
            if len(x[0]) >2:
                return float(x[0] + '.' + x[1])
            else:
                x = x[0]+x[1]
                return float(x[0:3] + '.' + x[3:])
        else:
            if len(x[0])>2:
                return float(x[0][0:2] + '.' + x[0][-1])
            else:
                x = x[0] + x[1]
                return float(x[0:2] + '.' + x[2:])
