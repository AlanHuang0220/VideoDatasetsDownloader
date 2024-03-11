import socket
import threading
from tqdm import tqdm
import signal

# df = DataFormatter.from_videocc('pretrain_dataset/VideoCC/video_cc_public.csv') # 取得對應資料集的dataframe
# unique_video_ids = df['Youtube_ID'].unique()    # 取得不重複的video youtube ID
# video_status = {video_id: "Not Downloaded" for video_id in unique_video_ids} # Downloading Downloaded

video_status = {'video1': 'Not Downloaded', 'video2': 'Not Downloaded', 'video3': 'Not Downloaded'}
video_lock = threading.Lock()
client_pool = []
progress_bar = tqdm(total=len(video_status), desc="Downloading videos") #創建下載進度條

shutdown_event = threading.Event()  # 創建一個停止事件

# 追蹤每個video是誰在下載的
video_downloader = {video_id: None for video_id in video_status}

def signal_handler(signum, frame):
    tqdm.write("Signal received, shutting down server...")
    shutdown_event.set()

def assign_video(client_address):
    with video_lock:
        for video_id, status in filter(lambda item: item[1] == "Not Downloaded", video_status.items()):
            video_status[video_id] = "Downloading"
            video_downloader[video_id] = client_address  # 紀錄影片是誰在下載的
            return video_id
    return None

def client_handler(connection, client_address):
    global video_status
    while True:
        data = connection.recv(1024).decode('utf-8') if connection else ''
        if not data:
            break  # No data received or connection closed

        if data == "disconnect":
            client_pool.remove(connection) # 從client_pool中移除斷開連接的client
            progress_bar.set_postfix_str(f"Client --> {[client.getpeername() for client in client_pool]}")
            break  # 跳出，準備關閉這個連線

        elif data == "request_video":
            # 分配影片給client
            video_id = assign_video(client_address)
            connection.sendall(video_id.encode('utf-8') if video_id else 'no_video'.encode('utf-8'))

        elif data.startswith("completed:"):
            # 更新影片下載狀態
            with video_lock:
                video_id = data.split(":")[1]
                video_status[video_id] = "Downloaded"
                progress_bar.update(1)
                video_downloader[video_id] = None  # 下載完成清除downloader
                if progress_bar.n == len(video_status):
                    shutdown_event.set()  # 發送停止事件
            tqdm.write(f"{client_address} has completed downloading {video_id}")

    # Cleanup on disconnect
    with video_lock:
        for video_id, downloader in video_downloader.items():
            if downloader == client_address and video_status[video_id] == "Downloading":
                video_status[video_id] = "Not Downloaded"
                video_downloader[video_id] = None
    connection.close()

def server():
    signal.signal(signal.SIGINT, signal_handler)
    global client_pool, video_status
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    sock.bind(server_address)
    sock.listen(5)
    sock.settimeout(1)
    tqdm.write("Server is running and listening")


    while not shutdown_event.is_set():
        try:
            connection, client_address = sock.accept() # 接受新的連線
        except socket.timeout:
            continue  # 如果accept()调用超时，继续循环
        with threading.Lock():  # 確保thread安全
            client_pool.append(connection)  # 把client的ip加到pool裡面
        # tqdm.write(f"Connection from {connection.getpeername()}")
        progress_bar.set_postfix_str(f"Client --> {[client.getpeername() for client in client_pool]}")
        # 為每個client創建一個新的threading
        threading.Thread(target=client_handler, args=(connection, client_address)).start()

    # Cleanup
    for client in client_pool:
        client.close()
    sock.close()

if __name__ == "__main__":
    server()