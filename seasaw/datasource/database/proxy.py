import subprocess


def start(credential_path):
    proxy = subprocess.Popen([
        '/home/vagrant/cloud_sql_proxy',
        '-instances=true-vista-164318:us-east1:seasaw' + "=tcp:3306",
        '-credential_file=' + credential_path,
        '&'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proxy.stdout.readline()
        if line != '':
            if "Ready for new connections" in line:
                print("Proxy established")
                break
            elif "bind" in line:
                print("Proxy was already running")
                break
