import dask
import time
import socket
import dask.distributed

# from dask_jobqueue import SLURMCluster
# cluster = SLURMCluster(
# queue='fast.q', # or std.q, preempt.q, gpu.q...
# project="",
# cores=1, #  up to 24
# memory="10 GB" # up to 240 on merced.
# )

hostname = socket.gethostname()
if hostname.startswith('merced') or hostname.startswith('mrcd'):
    from dask_jobqueue import SLURMCluster
    cluster = SLURMCluster(...)
else:
    cluster = None

from dask.distributed import Client
if __name__ == '__main__':
    client = Client(cluster)
    cluster.scale(2)

def wait_period(amount):
    time.sleep(1)
    return amount + 1

from dask.distributed import progress
futures = client.map(wait_period, range(1000))
progress(futures)


