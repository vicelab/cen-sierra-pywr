import os
from paramiko import SSHClient
from scp import SCPClient


def upload_to_cluster(ip, basins, local_dir, remote_dir):
    # See: https://pypi.org/project/scp/

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(ip)

    with SCPClient(ssh.get_transport()) as scp:
        common_dir_local = os.path.join(local_dir, 'common')
        common_dir_remote = '/'.join([remote_dir, 'common'])
        scp.put(common_dir_local, recursive=True, remote_path=common_dir_remote)
        for basin in basins:
            basin_full_name = basin.replace('_', ' ').title() + ' River'
            basin_dir_local = os.path.join(local_dir, basin_full_name)
            basin_dir_remote = '/'.join([remote_dir, basin_full_name])
            scp.put(basin_dir_local, recursive=True, remote_path=basin_dir_remote)


if __name__ == '__main__':
    ip = '1.2.3.4'
    basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']
    local_dir = os.environ['SIERRA_DATA_PATH']
    remote_dir = '/home/user/sierra_pywr_data'
    upload_to_cluster(ip, basins, local_dir, remote_dir)
