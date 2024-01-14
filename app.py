from flask import Flask, render_template, request
from helper.account import account

app = Flask(__name__)

def download_torrent_from_api(magnet_link):
    add = account.addTorrent(magnetLink=magnet)
    if add['result'] == True:
        response = f"Downloading Torrent ({add['user_torrent_id']})\n\n{add['title']}\n\nTorrent hash: {add['torrent_hash']}"
    torrents = account.listContents()['torrents']
    print(torrents)
    while torrents:
        time.sleep(10)
        torrents = account.listContents()['torrents']
    folders = account.listContents()['folders']
    print(folders)

    if folders:
        for folder in folders:
            folder_id = folder['id']
            print(folder_id)
    files = account.listContents(folderId=folder_id)
    print(files)
    # and handle the response. Return a dictionary with relevant information.
    # Example response:
    # {'success': True, 'download_links': ['/download/file1', '/download/file2']}
    # or
    # {'success': False, 'error_message': 'Torrent download failed.'}
    pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        magnet_link = request.form['magnet_link']
        download_response = download_torrent_from_api(magnet_link)

        if download_response and download_response.get('success'):
            download_links = download_response.get('download_links', [])
            return render_template('index.html', download_links=download_links)
        else:
            error_message = download_response.get('error_message', 'Torrent download failed.') if download_response else 'Torrent download failed.'
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', download_links=None)

if __name__ == '__main__':
    app.run(debug=True)
