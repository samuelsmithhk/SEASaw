import pymysql
import time


database_password = ""


def init(_database_password):
    global database_password
    database_password = _database_password


def results_query(start, end, pagination, page):
    sql = "SELECT result_ts FROM results WHERE result_ts > %s AND result_ts <= %s LIMIT %s OFFSET %s;"
    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb",
                                 charset="utf8mb4")

    if pagination > 100:
        pagination = 100

    first_row = pagination * page

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (start, end, pagination, first_row))
            sql_result = cursor.fetchall()
    finally:
        connection.close()

    results = []
    for row in sql_result:
        results.append(row[0])

    return results


def result_id_query(result_id):
    sql = "SELECT * FROM results WHERE result_ts = %s;"
    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb",
                                 charset="utf8mb4")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, result_id)
            sql_result = cursor.fetchone()
    finally:
        connection.close()

    result = {"result_id": result_id, "video_title": sql_result[1], "video_url": sql_result[2]}

    frames = [{"url": sql_result[3], "timestamp": sql_result[4]}, {"url": sql_result[5], "timestamp": sql_result[6]},
              {"url": sql_result[7], "timestamp": sql_result[8]}, {"url": sql_result[9], "timestamp": sql_result[10]},
              {"url": sql_result[11], "timestamp": sql_result[12]}]

    result["frames"] = frames
    return result


def which_results_exist(results):
    format_strings = ','.join(['%s'] * len(results))
    sql = "SELECT video_url FROM results WHERE video_url IN (%s);"
    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb",
                                 charset="utf8mb4")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql % format_strings, tuple(results))
            sql_result = cursor.fetchall()
    finally:
        connection.close()

    return list(sql_result)


def insert_result(result):
    result_ts = int(time.time())
    video_title = result["video_title"]
    video_url = result["video_url"]

    frame1_url = ""
    frame1_time = ""
    frame2_url = ""
    frame2_time = ""
    frame3_url = ""
    frame3_time = ""
    frame4_url = ""
    frame4_time = ""
    frame5_url = ""
    frame5_time = ""

    if len(result["frames"]) > 0:
        frame1_url = result["frames"][0]["url"]
        frame1_time = result["frames"][0]["timestamp"]

    if len(result["frames"]) > 1:
        frame2_url = result["frames"][1]["url"]
        frame2_time = result["frames"][1]["timestamp"]

    if len(result["frames"]) > 2:
        frame3_url = result["frames"][2]["url"]
        frame3_time = result["frames"][2]["timestamp"]

    if len(result["frames"]) > 3:
        frame4_url = result["frames"][3]["url"]
        frame4_time = result["frames"][3]["timestamp"]

    if len(result["frames"]) > 4:
        frame5_url = result["frames"][4]["url"]
        frame5_time = result["frames"][4]["timestamp"]

    sql = "INSERT INTO results VALUES (" + str(result_ts) + ", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb",
                                 charset="utf8mb4")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (video_title, video_url, frame1_url, frame1_time, frame2_url, frame2_time, frame3_url,
                                 frame3_time, frame4_url, frame4_time, frame5_url, frame5_time))
            connection.commit()
            sql_result = cursor.fetchall()
    finally:
        connection.close()

    print("dao - insert of video " + video_url + " complete")
