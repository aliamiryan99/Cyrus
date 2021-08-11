import os
import pandas as pd


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
    for f in csv_files:
        try:
            df = pd.read_csv(f)
        except:
            df = pd.read_excel(f)

        if 'Local time' in df.columns:
            df.rename(columns={'Local time': 'Time'}, inplace=True)
        if 'Gmt time' in df.columns:
            df.rename(columns={'Gmt time': 'Time'}, inplace=True)
        if 'GMT' in df.columns:
            df.rename(columns={'GMT': 'Time'}, inplace=True)
        if 'Time' in df.columns:
            try:
                df['Time'] = pd.to_datetime(df['Time'], format=date_format)
            except:
                df['Time'] = pd.to_datetime(df['Time'])
        df = df.sort_values(['Time'])
        df = df.reset_index()
        data_frames.append(df)
    return data_frames