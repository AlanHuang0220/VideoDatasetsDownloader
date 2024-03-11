import socket
import time

def download_video(video_id):
    print(f"Downloading video with ID: {video_id}")
    # Simulate a video download delay
    time.sleep(10)
    print(f"Completed downloading video: {video_id}")

def client():
    server_address = ('localhost', 10000)
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        while True:
            # Request a video ID from the server
            print("Requesting video...")
            sock.sendall("request_video".encode('utf-8'))
            
            # Receive the video ID from the server
            video_id = sock.recv(1024).decode('utf-8')
            
            if video_id == "no_video":
                print("No more videos to download. Disconnecting.")
                break
            else:
                # Simulate downloading the video
                download_video(video_id)
                
                # Inform the server that the video has been downloaded
                completion_message = f"completed:{video_id}"
                sock.sendall(completion_message.encode('utf-8'))
        
    except KeyboardInterrupt:
        print("\nUser initiated disconnect.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if sock:
            try:
                print("Sending disconnect message to server...")
                sock.sendall("disconnect".encode('utf-8'))
                # Optionally wait for a response from the server before closing
                # response = sock.recv(1024).decode('utf-8')
                # print("Server response:", response)
            except Exception as e:
                print("Error during disconnect:", e)
            finally:
                print("Closing socket.")
                sock.close()
                print("Disconnected gracefully.")

if __name__ == "__main__":
    client()