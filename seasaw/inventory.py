
ports = [
    25280,  # datasource
    25281,  # datasource
    25282,  # indexer
    25283,  # indexer
    25284,  # frontend
    25285,  # frontend
]

DATA_PARTITIONS = 2
DATA_SERVERS = []
for i in range(0,DATA_PARTITIONS):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[i]))

INDEX_PARTITION = 2
INDEX_SERVERS = []
for i in range(0,INDEX_PARTITION):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + i]))

FRONTEND_PARTITION = 2
FRONTEND_SERVERS = []
for i in range(0,FRONTEND_PARTITION):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + INDEX_PARTITION + i]))
