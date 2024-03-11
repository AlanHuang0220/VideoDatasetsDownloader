from pytube import YouTube
from tqdm import tqdm

class YouTubeDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder

    def download_video(self, video_id):
        resolutions = ["240p", "360p", "480p", "720p", "1080p"]
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        try:
            yt = YouTube(video_url)
            stream = None

            for resolution in resolutions:
                stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
                if stream:
                    break
            if not stream:
                stream = yt.streams.get_highest_resolution()

            file_name = f"{video_id}.mp4"
            # 下載影片
            stream.download(output_path=self.download_folder, filename=file_name)
            tqdm.write(f"Video {video_id} downloaded successfully at resolution {stream.resolution}.")
            return True # 返回True表示下载成功
        except Exception as e:
            tqdm.write(f"Failed to download video {video_id}. Error: {e}")
            return False # 返回False表示下载失敗