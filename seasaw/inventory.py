import hashlib
import getpass

thread_count = 6
base_port = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % (49152 - 10000) + 10000
