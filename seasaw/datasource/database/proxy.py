import subprocess


def start(credential_path):
    proxy = subprocess.Popen([
        './cloud_sql_proxy.amd64',
        '-instances=true-vista-164318:us-east1:seasaw' + "=tcp:3306",
        '-credential_file=' + credential_path,
        '&'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proxy.stdout.readline()
        if len(line) > 5:
            print(line)
            if "Ready for new connections" in line.decode():
                print("Proxy established")
                break
            elif "bind" in line.decode():
                print("Proxy was already running")
                break
