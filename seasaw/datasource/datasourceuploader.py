import os
import pickle
import shutil

from .database import dao


def start():g
    videos = os.listdir("/datastore/imgur_processed/")
    videos = [video for video in videos if os.path.exists("/datastore/imgur_processed/" + video + "/frame_urls")]

    if len(videos) > 0:
        print("datasourceuploader - found " + str(len(videos)) + " results to upload")
    else:
        return

    for video in videos:
        meta_loader = open("/datastore/imgur_processed/" + video + "/meta", 'rb')
        meta = pickle.load(meta_loader)
        meta_loader.close()

        frame_urls_loader = open("/datastore/imgur_processed/" + video + "/frame_urls", 'rb')
        frame_urls = pickle.load(frame_urls_loader)
        frame_urls_loader.close()

        result = {"video_title": meta["title"], "video_url": meta["url"], "frames": []}

        for f in meta["frames"]:
            frame = {"timestamp": f[1], "url": frame_urls[f[0]]}
            result["frames"].append(frame)

        print("datasourceuploader - inserting record for " + result["video_title"] + " into database")
        dao.insert_result(result)
        shutil.rmtree("/datastore/imgur_processed/" + video)

    print("datasourceuploader - finished upload " + str(len(videos)) + " results")
