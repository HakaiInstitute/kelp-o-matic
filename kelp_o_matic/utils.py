import os
import tempfile
import urllib.request
from pathlib import Path

from rich.progress import Progress

S3_BUCKET = "https://kelp-o-matic.s3.amazonaws.com/pt_jit"
CACHE_DIR = Path("~/.cache/kelp_o_matic").expanduser()


def lazy_load_params(object_name: str):
    object_name = object_name
    remote_url = f"{S3_BUCKET}/{object_name}"
    local_file = CACHE_DIR / object_name

    # Create cache directory if it doesn't exist
    if not CACHE_DIR.is_dir():
        CACHE_DIR.mkdir(parents=True)

    # Download file if it doesn't exist
    if not local_file.is_file():
        download_file(remote_url, local_file)

    return local_file


def download_file(url: str, filename: Path):
    # Make a request to the URL
    response = urllib.request.urlopen(url)

    # Get the total size of the file
    file_size = int(response.getheader("Content-Length"))

    # Create a task with the total file size
    with Progress(transient=True) as progress:
        task = progress.add_task(f"Downloading {filename.name}...", total=file_size)

        # Download the file
        with tempfile.NamedTemporaryFile("wb") as f:
            # Read data in chunks (e.g., 1024 bytes)
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                f.write(chunk)

                # Update progress bar
                progress.update(task, advance=len(chunk))

            # Move the file to the cache directory once downloaded
            f.flush()
            os.fsync(f.fileno())
            filename.hardlink_to(f.name)


def all_same(items):
    return all(x == items[0] for x in items)
