from flask import Flask, render_template, request
from helper.account import account, clean
import time 

app = Flask(__name__)

def download_torrent_from_api(magnet):

    clean()

    add = account.addTorrent(magnetLink=magnet)

    if add['result'] == True:
        title = add['title']
    else:
        return {'success': False, 'error_message': 'invalid link.'}

    torrents = account.listContents()['torrents']
    print(torrents)
    while torrents:
        time.sleep(3)
        torrents = account.listContents()['torrents']
    folders = account.listContents()['folders']
    print(account.listContents())
    
    
    if folders:
        folder_id = folders[0]['id']
        files = account.listContents(folderId=folder_id)['files']
        folders = account.listContents(folderId=folder_id)['folders']
        if folders:
            for folder in folders:
                files.extend(account.listContents(folderId=folder['id'])['files'])
    else:
        files = account.listContents()['files']
    names = []
    links =[]
    sizes =[]
    for file in files:
        names.append(file['name'])
        links.append(account.fetchFile(fileId=file['folder_file_id'])['url'])
        sizes.append(str((file['size'])//(1024*1024) +1) + ' MB')

    return {'success': True, 'download_links': links, 'file_names' : names, 'file_sizes' : sizes, 'torrent_name' : title}


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
            torrent_name = download_response.get('torrent_name', '')

            # Zip the lists before passing them to the template
            file_data = zip(download_links, file_names, file_sizes)
            
            return render_template('index.html', file_data=file_data, torrent_name=torrent_name)
        else:
            error_message = download_response.get('error_message', 'Torrent download failed.') if download_response else 'Torrent download failed.'
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', file_data=None, torrent_name=None)

@app.route('/reset', methods=['GET'])
def reset():
    clean()
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
