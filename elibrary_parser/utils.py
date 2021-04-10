import csv


def save_common_publications(data_path, date_from, date_to, publications):

    save_path = data_path / "common_publications"
    save_path.mkdir(exist_ok=True)

    dates_csv = str(date_from) + '-' + str(date_to) + "_publications.csv"

    csv_path = save_path / dates_csv

    with open(csv_path, 'a', encoding="utf8", newline='') as csvfile:
        wr = csv.writer(csvfile, delimiter=';')
        for publication in set.intersection(*publications):
            saving_publication = [
                publication.title,
                publication.authors,
            ]
            wr.writerow(saving_publication)