import os
import shutil
import time
import pickle

from imgurpython import ImgurClient


client_id = "d770cc9eea99c6f"


def start(password):
    imgur_client = ImgurClient(client_id, password)

    if imgur_client.credits['UserRemaining'] is 0:
        return 1

    videos = os.listdir("/datastore/captured_frames/")
    videos = [video for video in videos if os.path.exists("/datastore/captured_frames/" + video + "/meta")]

    for video in videos:
        print("imguruploader - Uploading frames to imgur for video " + video)
        if os.path.exists("/datastore/imgur_processed/" + video):
            shutil.rmtree("/datastore/imgur_processed/" + video)

        os.makedirs("/datastore/imgur_processed/" + video)

        if os.path.exists("/datastore/captured_frames/" + video + "/meta"):
            shutil.copy2("/datastore/captured_frames/" + video + "/meta", "/datastore/imgur_processed/" + video)
        else:
            # scraping process has not finished yet, continue
            continue

        urls = {}
        for i in range(1, 6):
            frame_path = "/datastore/captured_frames/" + video + "/" + str(i) + ".jpg"
            if os.path.exists(frame_path):
                time.sleep(30)  # because of rate limits
                print("imguruploader - Uploading frame " + str(i) + " for " + video)
                result = imgur_client.upload_from_path(frame_path)
                result_url = result['link']
                urls[i] = result_url[19:]

        pickle.dump(urls, open("/datastore/imgur_processed/" + video + "/frame_urls", "wb"))
        shutil.rmtree("/datastore/captured_frames/" + video)

        print("imguruploader - Finished uploading frames to imgur for video " + video)

    return 0
