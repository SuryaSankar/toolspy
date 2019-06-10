import zipfile
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
from datetime import datetime, timedelta
import requests
from contextlib import contextmanager
from .collection_tools import merge


def zipdir(dir_path, zip_file_path):
    zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for parent_dir, subdirs, files in os.walk(dir_path):
        parent_dir_in_zip = parent_dir[len(dir_path) + 1:]
        for subdir in subdirs:
            subdir_path = os.path.join(parent_dir, subdir)
            subdir_path_in_zip = os.path.join(parent_dir_in_zip, subdir)
            zipf.write(subdir_path, subdir_path_in_zip)
        for file in files:
            file_path = os.path.join(parent_dir, file)
            file_path_in_zip = os.path.join(parent_dir_in_zip, file)
            zipf.write(file_path, file_path_in_zip)
    zipf.close()


def download_file(url, local_file_path=None):
    if url is None:
        return None
    if local_file_path is None:
        local_file_path = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_file_path


def upload_file_to_s3(aws_access_key, aws_secret_access_key, bucket_name,
                      src_file_path, dest_file_path=None, headers=None,
                      cache_expiry_days=30):
    s3conn = S3Connection(aws_access_key, aws_secret_access_key)
    bucket = s3conn.get_bucket(bucket_name)
    k = Key(bucket)
    k.key = dest_file_path or os.path.basename(src_file_path)
    if headers is None:
        headers = {}
    max_age_seconds = cache_expiry_days * 24 * 60 * 60
    headers = merge({
        'Cache-Control': 'public, max-age={0}'.format(max_age_seconds),
        'Expires': (datetime.utcnow() + timedelta(days=cache_expiry_days)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    }, headers)
    res = k.set_contents_from_filename(src_file_path, headers)
    return res


@contextmanager
def chdir(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)
