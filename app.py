from flask import Flask, render_template, request
from helper.account import account, clean
import time 

app = Flask(__name__)


def download_torrent(magnet):
    clean()

    add = account.addTorrent(magnetLink=magnet)

    if add['result'] != True:
        if add['result'] == 'not_enough_space_wishlist_full':
            return {'success': False, 'error_message': 'Max torrent size is 4GB.'}
        error_message = ' - ' + add['error'] if 'error' in add else ''
        return {'success': False, 'error_message': add['result'] + error_message}

    torrents = account.listContents()['torrents']
    title = torrents[0]['name']

    start_time = time.time()

    while torrents:
        time.sleep(3)
        progress = float(torrents[0]['progress'])
        torrents = account.listContents()['torrents']
        
        if not progress_check(start_time, progress):
            clean()
            return {'success': False, 'error_message': 'Torrent is too slow to download.'}
        
    folders = account.listContents()['folders']
    
    if folders:
        folder_id = folders[0]['id']
        files = account.listContents(folderId=folder_id)['files']
        folders = account.listContents(folderId=folder_id)['folders']
        if folders:
            for folder in folders:
                files.extend(account.listContents(folderId=folder['id'])['files'])
    else:
        files = account.listContents()['files']
    
    names = [file['name'] for file in files]
    links = [account.fetchFile(fileId=file['folder_file_id'])['url'] for file in files]
    sizes = [str((file['size'])//(1024*1024) + 1) + ' MB' for file in files]

    return {'success': True, 'download_links': links, 'file_names' : names, 'file_sizes' : sizes, 'torrent_name' : title}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        magnet_link = request.form['magnet_link']
        download_response = download_torrent(magnet_link)

        if download_response and download_response['success']:

            file_data = zip(download_response['download_links'], download_response['file_names'], download_response['file_sizes'])
            torrent_name = download_response.get('torrent_name', 'Torrent')

            return render_template('index.html', file_data=file_data, torrent_name=torrent_name)
        
        error_message = download_response.get('error_message', 'Torrent download failed.') if download_response else 'Torrent download failed.'
        return render_template('index.html', error_message=error_message)

    return render_template('index.html', file_data=None, torrent_name=None)


@app.route('/reset', methods=['GET'])
def reset():
    clean()
    return 'OK', 200


def progress_check(start_time, progress):
    if time.time() - start_time > 45 and progress < 5:
        return False
    elif time.time() - start_time > 300 and progress < 95:
        return False
    else:
        return True


if __name__ == '__main__':
    app.run(debug=True)


