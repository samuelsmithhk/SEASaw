import time
import queue
import os
import pickle

from pyvirtualdisplay import Display
from selenium import webdriver
from .database import dao


# noinspection PyBroadException
def start(seed, max_number_of_videos):
    print("scraper - Configuring environment")
    display = Display(visible=0, size=(1024, 576))
    display.start()

    print("scraper - Launching geckodriver")
    driver = webdriver.Firefox(log_path="/logs/geckodriver/geckodriver_scraper.log")

    print("scraper - Searching for " + seed)
    try:
        driver.get("https://www.youtube.com/results?search_query=" + seed)
        jobs = queue.Queue()
        results_list = driver.find_element_by_class_name("item-section")
    except Exception as e:
        print(e)
        print("scraper - search failed, taking a breather and will start scraper later")
        time.sleep(5)
        start(seed, max_number_of_videos)



    print("scraper - Search complete")

    video_ids = []

    for result in results_list.find_elements_by_tag_name("li"):
        try:
            title_element = result.find_element_by_class_name("yt-lockup-title")
            a_tag = title_element.find_element_by_tag_name("a")
            url = a_tag.get_attribute("href")
            video_id = url[url.find("=") + 1:]

            if video_id.find("list") != -1 or video_id.find("user") != -1 or video_id.find("channel") != -1:
                print("scraper - result isn't a video, skipping")
                continue

            job = [video_id, a_tag.get_attribute("title")]
            video_ids.append(video_id)
            jobs.put(job)
        except:
            continue

    print("scraper - " + str(jobs.qsize()) + " results to process")

    print("scraper - checking database for duplicates")
    block_list = dao.which_results_exist(video_ids)

    success = 0

    while not jobs.empty():
        job = jobs.get()
        print("scraper - Processing video " + job[1])
        video_id = job[0]

        try:
            if video_id.find("list") != -1 or video_id.find("user") != -1 or video_id.find("channel") != -1:
                print("scraper - result isn't a video, skipping")
                continue

            driver.get("https://youtu.be/" + video_id)

            # add top 3 related videos to job queue - if queue diminishing
            if jobs.qsize() < 50:
                video_ids = []
                related_videos = driver.find_element_by_id("watch-related")
                related_list = related_videos.find_elements_by_class_name("related-list-item-compact-video")

                for v in range(0, 5):
                    video = related_list[v].find_element_by_class_name("content-wrapper")
                    a_tag = video.find_element_by_tag_name("a")
                    url = a_tag.get_attribute("href")
                    video_id = url[url.find("=") + 1:]

                    if video_id.find("list") != -1 or video_id.find("user") != -1:
                        print("scraper - result isn't a video, skipping")
                        continue

                    job = [video_id, a_tag.get_attribute("title")]
                    video_ids.append(video_id)
                    jobs.put(job)

                print("scraper - used video page to find some more potential candidate videos")

                print("scraper - checking new videos against database for duplicates")
                block_list.extend(dao.which_results_exist(video_ids))

            if video_id in block_list:
                print("scraper - processed video " + video_id + " in the past")
                continue

            if not os.path.exists("/datastore/captured_frames/" + video_id):
                os.makedirs("/datastore/captured_frames/" + video_id)
            else:
                continue  # no point in processing a video twice

            video_length_string = driver.find_element_by_class_name("ytp-bound-time-right").get_attribute("innerText")

            minutes = 0

            if video_length_string.count(":") == 1:  # minutes
                m_str = video_length_string[0: video_length_string.find(":")]
                minutes = int(m_str)
            elif video_length_string.count(":") == 2:  # hours, we'll just skip these videos
                continue

            s_str = video_length_string[-2:]
            seconds = int(s_str)

            seconds += minutes * 60
            one_seventh = int(seconds / 7)

            attempt = 0
            meta = {'title': job[1], 'url': job[0], 'frames': []}
            for i in range(1, 6):
                try:
                    attempt += 1
                    timestamp = one_seventh * i
                    if timestamp < 60:
                        timestamp_string = str(timestamp) + "s"
                        driver.get("https://youtu.be/" + video_id + "?t=" + timestamp_string)
                    else:
                        m = str(int(timestamp / 60))
                        s = str(timestamp % 60)
                        timestamp_string = str(m) + "m" + str(s) + "s"
                        driver.get("https://youtu.be/" + video_id + "?t=" + timestamp_string)

                    fs = driver.find_element_by_class_name("ytp-fullscreen-button")
                    fs.click()
                    time.sleep(2)
                    driver.save_screenshot("/datastore/captured_frames/" + video_id + "/" + str(i) + ".jpg")
                    meta['frames'].append((i, timestamp_string))
                except:
                    if attempt <= 3:
                        i -= 1
                    else:
                        print("scraper - Saving frame " + str(i) + " for video " + video_id + " failed 3 times, moving on")
                    driver = webdriver.Firefox(log_path="/logs/geckodriver/geckodriver.log")
                    continue

                if attempt > 1:
                    print("scraper - Frame " + str(i) + " for video " + video_id
                          + " was successfully saved after " + str(attempt) + " attempts")

                    attempt = 0

            pickle.dump(meta, open("/datastore/captured_frames/" + video_id + "/meta", "wb"))

            success += 1
            print("scraper - Sucessfully scraped " + video_id + ", "
                  + str(success) + " of " + str(max_number_of_videos))
            if success >= max_number_of_videos:
                print("scraper - Scraper finished task")
                break
        except Exception as e:
            print(e)
            print("scraper - Video " + video_id + " failed, taking a breather and will try id later")
            jobs.put(job)
            time.sleep(5)
            driver = webdriver.Firefox(log_path="/logs/geckodriver/geckodriver.log")
            continue
