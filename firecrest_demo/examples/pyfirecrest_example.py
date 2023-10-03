import firecrest as f7t
import os
import time


# Get the values from the env or set them directly in your file
CLIENT_ID = os.environ.get("FIRECREST_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FIRECREST_CLIENT_SECRET")
AUTH_TOKEN_URL = os.environ.get("AUTH_TOKEN_URL")
FIRECREST_URL = os.environ.get("FIRECREST_URL")

# Setup the auth object
auth = f7t.ClientCredentialsAuth(
    CLIENT_ID, CLIENT_SECRET, AUTH_TOKEN_URL
)

# Setup the client object
client = f7t.Firecrest(
    firecrest_url=FIRECREST_URL,
    authorization=auth
)

systems = client.all_systems()
print(systems)

## Exercise:

FIRECREST_SYSTEM = os.environ.get("FIRECREST_SYSTEM")
FIRECREST_SYSTEM_WORK_DIR = os.environ.get("FIRECREST_SYSTEM_WORK_DIR")

import json

print("1. Get the different parameters of our deployment")
print(json.dumps(client.parameters(), indent=4))

print("2. Get the username of the user")
print(json.dumps(client.whoami(machine=FIRECREST_SYSTEM), indent=4))

print("3. List all microservices and their status")
print(json.dumps(client.all_services(), indent=4))

print("4. List the contents of a directory")
from pathlib import Path
work_dir_path = Path(FIRECREST_SYSTEM_WORK_DIR)
print(json.dumps(client.list_files(machine=FIRECREST_SYSTEM, target_path=work_dir_path), indent=4))

print("5. Upload and download \"small\" files")
to_upload_path = Path("./examples/hello_world.txt").resolve(strict=True)
client.simple_upload(
    machine=FIRECREST_SYSTEM,
    source_path=to_upload_path,
    target_path=work_dir_path,
)

# ... check file has been uploaded
files_in_work_dir = client.list_files(machine=FIRECREST_SYSTEM, target_path=work_dir_path)
filenames = [f["name"] for f in files_in_work_dir]
print(f"Files in {work_dir_path}: {filenames}")
print(f"Is {to_upload_path.name} in {work_dir_path} on the remote system?")
print(to_upload_path.name in filenames)

# ... view contents of file
file_contents = client.view(
    machine=FIRECREST_SYSTEM,
    target_path=work_dir_path / to_upload_path.name
)
print("Uploaded file contents:")
print(file_contents)

# ... download the file
download_dir_path = (Path.cwd() / "output_tmpdir").resolve()
download_dir_path.mkdir(exist_ok=True)

source_path = work_dir_path / to_upload_path.name
target_path = download_dir_path / to_upload_path.name

print(f"Downloading from {source_path} on {FIRECREST_SYSTEM} to {target_path} locally")

client.simple_download(
    machine=FIRECREST_SYSTEM,
    source_path=source_path,
    target_path=target_path,
)

print("6. Submit a job")
print("7. [Optional] Submit a job and poll until the it is finished")
job_script_path = Path.cwd() / "examples" / "script.sh"
job_submit_obj = client.submit(
    machine=FIRECREST_SYSTEM,
    job_script=job_script_path,
    local_file=True
)

while True:
    job_queue_obj = client.poll(
        machine=FIRECREST_SYSTEM,
        jobs=[job_submit_obj["jobid"]]
    )[0]

    print(f"Current state: {job_queue_obj['state']}")

    if job_queue_obj["state"] != "COMPLETED":
        time.sleep(5)
        continue
        
    break
    
output_file_contents = client.view(
    machine=FIRECREST_SYSTEM,
    target_path=job_submit_obj["job_file_out"]
)

print(f"Contents of {job_submit_obj['job_file_out']}:")
print(output_file_contents)
