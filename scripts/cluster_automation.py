import os;
import sys
import paramiko
from loguru import logger
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException 

logger.add(sys.stderr,
        format="{time} {message}",
        filter="client",
        level="INFO")

logger.add('logs/log_{time:YYYY-MM-DD}.log',
        format="{time} {level} {message}",
        filter="client",
        level="INFO")

class RemoteClient:
    """A class for executing commands on the cluster"""

    def __init__(self, host, user, password, local_path, remote_path):
        self.host = host
        self.user = user
        # self.ssh_key_filepath = ssh_key_filepath
        self.local_path = local_path
        self.remote_path = remote_path
        self.client = None
        self.scp = None
        # self.__upload_ssh_key()

    def connect_to_cluster(self, host, user, password):
        """Connects to the remote host given necessary credentials"""
        try:
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            
            self.client.connect(self, host=self.host, 
            user=self.user, password=self.password, look_for_keys=True, 
            port=22, TimeoutError=5000)
            
            logger.info('Successfully connected: you are now logged in.')
        except AuthenticationException as error:
            logger.info('Authentication failed: did you foget your password?')
            logger.error(error)
            raise error
        finally:
            return self.client

    def disconnect_from_cluster(self):
        """Disconnnects from the cluster"""
        self.client.close()
        self.scp.close()
        logger.info('logger out')

    def upload_to_cluster(self, host, basins, local_path, remote_path):
        """Uploads specific files to the cluster depending on the remote path"""
        # See: https://pypi.org/project/scp/

        with SCPClient(self.client.get_transport()) as scp:
            common_dir_local = os.path.join(local_path, 'common')
            common_dir_remote = '/'.join([remote_path, 'common'])
            scp.put(common_dir_local, recursive=True, remote_path=common_dir_remote)
            for basin in basins:
                basin_full_name = basin.replace('_', ' ').title() + ' River'
                basin_dir_local = os.path.join(local_path, basin_full_name)
                basin_dir_remote = '/'.join([remote_path, basin_full_name])
                scp.put(basin_dir_local, recursive=True, remote_path=basin_dir_remote)

    def download_from_cluster(self, host, basins, local_path, remote_path, file):
        """Downloads files from the cluster"""
        if self.conn is None:
            self.conn = self.connect()
        self.scp.get(file)

    def execute_commands(self, commands):   # pass a list parameter
        """Executes specific commands. Must be specified as the parameter"""
        if self.client is None:
            self.client = self.__connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                logger.info(f'INPUT: {cmd} | OUTPUT: {line}')

if __name__ == '__main__':
    host = os.environ.get('REMOTE_HOST')
    user = os.environ.get('REMOTE_USERNAME')
    password = os.environ.get('REMOTE_PASSWORD')
    # ssh_key_filepath = environ.get('SSH_KEY')
    basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']
    local_path = os.environ.get('SIERRA_DATA_PATH')
    remote_path = '/home/user/sierra_pywr_data'

    test_command='ls'

    remote = RemoteClient(host, user, password, local_path, remote_path)
    remote.connect_to_cluster(host, user, password)
    remote.upload_to_cluster(host, basins, local_path, remote_path)
    remote.execute_commands(test_command)
    remote.download_from_cluster(host, basins, local_path, remote_path)
    remote.disconnect_from_cluster()