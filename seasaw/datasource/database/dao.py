import pymysql


database_password = ""


def init(_database_password):
    global database_password
    database_password = _database_password


def results_query(start, end, pagination, page):
    sql = "SELECT result_ts FROM results WHERE result_ts > %s AND result_ts <= %s LIMIT %s OFFSET %s;"
    sql_result = (0,)
    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb")

    if pagination > 100:
        pagination = 100

    first_row = pagination * page

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (start, end, pagination, first_row))
            sql_result = cursor.fetchall()
    finally:
        connection.close()

    # (1491943465, 'Cockapoo puppies', 'yk0KNJLhaT0', '33IGHlg.jpg', '0:35', '8FnnXvF.jpg', '1:10', 'hlAJiUQ.png', '1:45', 'uPiO83z.png', '2:20', 'WeNuCwy.jpg', '2:49')
    results = []
    for row in sql_result:
        results.append(row[0])

    return results


def result_id_query(result_id):
    sql = "SELECT * FROM results WHERE result_ts = %s;"
    sql_result = (0,)
    connection = pymysql.connect(user="root", password=database_password, host="127.0.0.1", database="resultsdb")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, result_id)
            sql_result = cursor.fetchone()
    finally:
        connection.close()

    result = {}
    result["result_id"] = result_id
    result["video_title"] = sql_result[1]
    result["video_url"] = sql_result[2]

    frames = []
    frames.append({"url": sql_result[3], "timestamp": sql_result[4]})
    frames.append({"url": sql_result[5], "timestamp": sql_result[6]})
    frames.append({"url": sql_result[7], "timestamp": sql_result[8]})
    frames.append({"url": sql_result[9], "timestamp": sql_result[10]})
    frames.append({"url": sql_result[11], "timestamp": sql_result[12]})

    result["frames"] = frames
    return result
