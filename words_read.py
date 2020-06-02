import pandas as pd

def read_file(filepath):
    df = pd.read_excel(filepath)
    return df

def read_3000():
    return read_file(r'3000.xls')

def read_red():
    return read_file(r'red.xlsx')

def read_fojiao():
    return read_file(r'fojiao2.xlsx')