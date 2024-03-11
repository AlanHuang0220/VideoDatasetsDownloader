from DataFormatter import DataFormatter
from YouTubeDownloader import YouTubeDownloader
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

if __name__ == '__main__':
    dataset_path = 'F:/dataset/pretrain_dataset/VAST27M/split_annotations/split_0.json'   # 資料集文件路徑
    download_folder = 'F:/dataset/pretrain_dataset/VAST27M/video'  # 下載影片存放位置
    df = DataFormatter.from_vast27m(dataset_path)   # 取得對應資料集的dataframe

    unique_video_ids = [url.split('=')[1] for url in df['url'].unique()]    # 取得不重複的video youtube ID
    downloader = YouTubeDownloader(download_folder)
    failed_downloads = []  # 儲存下載失敗的影片ID

    # 初始化tqdm進度條
    with tqdm(total=len(unique_video_ids), desc="Downloading videos") as progress_bar:
        with ThreadPoolExecutor(max_workers=40) as executor: # 使用ThreadPoolExecutor來創建一個線程池
            # 將下載任務提交到線程池
            future_to_video_id = {executor.submit(downloader.download_video, video_id): video_id for video_id in unique_video_ids}
            for future in as_completed(future_to_video_id):
                video_id = future_to_video_id[future]
                try:
                    success = future.result()
                    if not success:
                        failed_downloads.append(video_id)
                except Exception as exc:
                    failed_downloads.append(video_id)
                finally:
                    progress_bar.update(1) # 每次任務完成，手動更新進度條

        if failed_downloads:
            with open('failed_downloads.txt', 'w', encoding='utf-8') as f:
                for video_id in failed_downloads:
                    f.write(f"{video_id}\n")
            tqdm.write("Failed downloads list saved to failed_downloads.txt.")
        else:
            tqdm.write("All videos downloaded successfully.")