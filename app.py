from flask import Flask, render_template, request
from helper.account import account, clean
from helper.database import log
import time 
import pytz
from datetime import datetime

app = Flask(__name__)

def log_request(request, magnet_link, torrent, success):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    user_agent = request.headers.get('User-Agent', 'N/A')

    log.insert_one({
        'timestamp': timestamp,
        'success': success,
        'ip': ip,
        'user_agent': user_agent,
        'magnet_link': magnet_link,
        'status': torrent
    })

def download_torrent(magnet):
    clean()

    add = account.addTorrent(magnetLink=magnet)

    if add['result'] != True:
        if add['result'].startswith('not_enough_space') :
            return {'success': False, 'error_message': 'Maximum torrent size is 4.5 GB.'}
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

# add functionality to view all files, in all folders, with folder names somehow .
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
        if not 'magnet' in magnet_link and not 'Magnet' in magnet_link:
            error_message = 'Invalid magnet link provided.'
            log_request(request, magnet_link, error_message, 0)
            return render_template('index.html', error_message=error_message)

            
        download_response = download_torrent(magnet_link)

        if download_response and download_response['success']:

            file_data = zip(download_response['download_links'], download_response['file_names'], download_response['file_sizes'])
            torrent_name = download_response.get('torrent_name', 'Torrent')

            log_request(request, magnet_link, torrent_name, 1)
            return render_template('index.html', file_data=file_data, torrent_name=torrent_name)
        
        error_message = download_response.get('error_message', 'Torrent download failed.') if download_response else 'Torrent download failed.'
        log_request(request, magnet_link, error_message, 0)
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

