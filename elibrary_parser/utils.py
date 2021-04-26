import pandas as pd


def save_common_publications(data_path, date_from, date_to, publications):

    save_path = data_path / "common_publications"
    save_path.mkdir(exist_ok=True)
    dates = str(date_from) + '-' + str(date_to) + "_publications.xlsx"
    xlsxpath = save_path / dates
    common_publications = set.intersection(*publications)
    writer = pd.ExcelWriter(xlsxpath, engine='xlsxwriter', mode='w')
    df_list = []
    startrow = 0
    for publication in common_publications:
        df = pd.DataFrame({'Title':[publication.title], 'Authors': [publication.authors]})
        df_list.append(df)
    for i, df in enumerate(df_list):
        df.to_excel(writer, startrow=startrow, index=False, sheet_name='Sheet1')
        startrow += 1
    writer.save()


