import os
import subprocess

for filename in os.listdir('.'):
    if 'figure_' not in filename or '.py' not in filename:
        continue

    subprocess.run(['python', filename])