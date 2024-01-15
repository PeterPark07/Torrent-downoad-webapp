from flask import Flask, render_template, request
from helper.account import account, clean
import time 

app = Flask(__name__)

def download_torrent_from_api(magnet):

    clean()

    add = account.addTorrent(magnetLink=magnet)
    if add['result'] == True:
        response = f"Downloading Torrent ({add['user_torrent_id']})\n\n{add['title']}\n\nTorrent hash: {add['torrent_hash']}"
    else:
        return {'success': False, 'error_message': 'invalid link.'}

    torrents = account.listContents()['torrents']
    while torrents:
        time.sleep(3)
        torrents = account.listContents()['torrents']
    folders = account.listContents()['folders']
    print(account.listContents())

    if folders:
        for folder in folders:
            folder_id = folder['id']
    files = account.listContents(folderId=folder_id)['files']
    names = []
    links =[]
    sizes =[]
    for file in files:
        names.append(file['name'])
        links.append(account.fetchFile(fileId=file['folder_file_id'])['url'])
        sizes.append(str((file['size'])//(1024*1024) +1) + ' MB')

    return {'success': True, 'download_links': links, 'file_names' : names, 'file_sizes' : sizes}


    # {'success': False, 'error_message': 'Torrent download failed.'}
    pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        magnet_link = request.form['magnet_link']
        download_response = download_torrent_from_api(magnet_link)

        if download_response and download_response.get('success'):
            download_links = download_response.get('download_links', [])
            file_names = download_response.get('file_names', [])
            file_sizes = download_response.get('file_sizes', [])

            # Zip the lists before passing them to the template
            file_data = zip(download_links, file_names, file_sizes)
            
            return render_template('index.html', file_data=file_data)
        else:
            error_message = download_response.get('error_message', 'Torrent download failed.') if download_response else 'Torrent download failed.'
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', download_links=None)

if __name__ == '__main__':
    app.run(debug=True)
