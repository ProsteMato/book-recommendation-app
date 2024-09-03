import os
from kaggle.api.kaggle_api_extended import KaggleApi


def download_data():
    api = KaggleApi()
    api.authenticate()

    dataset = 'arashnic/book-recommendation-dataset'
    download_path = './data/dataset'
    api.dataset_download_files(dataset, path=download_path, unzip=True)

if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    download_data()