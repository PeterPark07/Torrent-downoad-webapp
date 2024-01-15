import os
from seedrcc import Login, Seedr

email = os.getenv('email')
password = os.getenv('pass')

seedr = Login(email, password)
response = seedr.authorize()

token = seedr.token
account = Seedr(token=token)


def clean():
    storage = account.listContents()

    for item_type in ['folders', 'files', 'torrents']:
        for item in storage.get(item_type, []):
            if item_type == 'folders':
                account.deleteFolder(item['id'])
            elif item_type == 'files':
                account.deleteFile(item['id'])
            else:
                account.deleteTorrent(item['id'])