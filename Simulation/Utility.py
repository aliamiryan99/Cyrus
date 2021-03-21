import os
import pandas as pd
from Simulation.Config import Config


def one_csv_to_h5(input_file, format='table'):
    df = pd.read_csv(input_file)

    output_file = os.path.splitext(os.path.basename(input_file))[0] + '.h5'

    df.to_hdf(output_file, key='key', mode='w', format=format)


def csv_to_h5(input_path, output_file=None, format='table'):
    output_file = os.path.splitext(os.path.basename(input_path))[0] + '.h5'
    for dirpath, dirnames, files in os.walk(input_path):

        for file in files:
            file_name = dirpath + '/' + file
            # print(file_name)
            try:
                df = pd.read_csv(file_name)

                df.to_hdf(output_file, key='df', mode='a', format=format)

            except ValueError:
                print(file_name)



def csv_to_df(csv_files: list, date_format='%d.%m.%Y %H:%M:%S.%f'):
    """
    Get a list of csv files, load them and parse date column(s)...
    Returns:
        a list of pandas Data-frames.
    """
    data_frames = []
    parse_date = lambda x: pd.datetime.strptime(x, date_format)
    if Config.DEBUG:
        print('\nLoading csv Data:')
    for f in csv_files:
        try:
            df = pd.read_csv(f)
        except:
            df = pd.read_excel(f)

        if 'Local time' in df.columns:
            df.rename(columns={'Local time': 'GMT'}, inplace=True)
        if 'Gmt time' in df.columns:
            df.rename(columns={'Gmt time': 'GMT'}, inplace=True)
        if 'Time' in df.columns:
            df.rename(columns={'Time': 'GMT'}, inplace=True)
        if 'GMT' in df.columns:
            try:
                df['GMT'] = pd.to_datetime(df['GMT'], format=date_format)
            except:
                df['GMT'] = pd.to_datetime(df['GMT'])
        df = df.sort_values(['GMT'])
        df = df.reset_index()
        data_frames.append(df)
        if Config.DEBUG:
            print(f'  {f}')
    if Config.DEBUG:
        print()
    #dv;ldffddfg
    return data_frames