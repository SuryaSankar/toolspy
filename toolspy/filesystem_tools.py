from __future__ import absolute_import
import zipfile
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
from datetime import datetime, timedelta
import requests
from contextlib import contextmanager
from .collection_tools import merge
import math
from .math_tools import round_float
import sys
from PIL import Image as PImage
from PIL import ExifTags


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


def file_size_in_response_headers(resp):
    content_length = resp.headers.get('Content-Length')
    if content_length is None:
        return None
    return int(content_length)


def fetch_file_size(url):
    resp = requests.get(url, stream=True)
    return file_size_in_response_headers(resp)


def number_of_chunks(file_size, chunk_size):
    return math.ceil(file_size / chunk_size)


def absolute_progress_bar_string(
        current_bar, total_bars,
        finished_bar_symbol="=",
        pending_bar_symbol=" ",
        start_symbol="[", end_symbol="]"):
    return (
        start_symbol +
        current_bar * finished_bar_symbol +
        (total_bars - current_bar) * pending_bar_symbol +
        end_symbol)


def readable_byte_size(byte_size):
    kb = 1024
    mb = kb ** 2
    gb = kb ** 3
    if byte_size > gb:
        return "{} gb".format(
            round_float(byte_size / gb, precision=2))
    if byte_size > mb:
        return "{} mb".format(
            round_float(byte_size / mb, precision=2))
    if byte_size > kb:
        return "{} kb".format(
            round_float(byte_size / kb, precision=2))
    return "{} bytes".format(byte_size)


def download_progress_string(
        current_chunk_count, download_chunk_size, file_size):
    no_of_chunks = number_of_chunks(
        file_size, download_chunk_size)
    return "{} {} / {} downloaded".format(
        absolute_progress_bar_string(
            current_chunk_count, no_of_chunks),
        readable_byte_size(
            current_chunk_count * download_chunk_size),
        readable_byte_size(file_size)
    )


def print_backspace(n=1):
    sys.stdout.write("\b \b" * n)


def download_file(
        url, local_file_path=None, folder_path=None,
        skip_if_local_file_exists=False,
        download_chunk_size=5 * 1024**2,
        verbose=False):
    if url is None:
        return None
    if local_file_path is None:
        local_file_path = url.split('/')[-1]
    if folder_path:
        local_file_path = os.path.join(
            folder_path, local_file_path)
    if verbose:
        print("Preparing for download of {} to {}".format(
            url, local_file_path))
    if not os.path.isfile(
            local_file_path) or not skip_if_local_file_exists:
        r = requests.get(url, stream=True)
        if verbose:
            print("Connection initiated")
        current_chunk_count = 0
        file_size = file_size_in_response_headers(r)
        no_of_chunks = number_of_chunks(
            file_size, download_chunk_size)
        if verbose:
            progress_string = download_progress_string(
                current_chunk_count,
                download_chunk_size,
                file_size)
            sys.stdout.write(progress_string)
            sys.stdout.flush()
        with open(local_file_path, 'wb') as f:
            for chunk in r.iter_content(
                    chunk_size=download_chunk_size):
                if chunk:
                    current_chunk_count += 1
                    f.write(chunk)
                    if verbose:
                        print_backspace(len(progress_string))
                        progress_string = download_progress_string(
                            current_chunk_count,
                            download_chunk_size,
                            file_size)
                        sys.stdout.write(progress_string)
                        sys.stdout.flush()
        if verbose:
            print_backspace(len(progress_string))
            progress_string = "{} {} / {} downloaded".format(
                absolute_progress_bar_string(
                    no_of_chunks, no_of_chunks),
                readable_byte_size(file_size),
                readable_byte_size(file_size)
            )
            sys.stdout.write(progress_string)
            sys.stdout.flush()
            print()
    else:
        if verbose:
            print("File already present. Skipping Download")
    return local_file_path


def download_files_to_folder(urls, folder_path):
    for item in urls:
        if isinstance(item, tuple):
            url, filename = item
            download_file(
                url,
                local_file_path=filename,
                folder_path=folder_path)
        else:
            download_file(item, folder_path=folder_path)


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


def filechunks(f, chunk_size):
    chunk = []
    for l in f:
        chunk.append(l)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk

def get_exif_dict(filepath):
    img = PImage.open(filepath)
    raw_exif = img.getexif()
    exif = {
        ExifTags.TAGS[k]: v
        for k, v in raw_exif.items()
        if k in ExifTags.TAGS
    }
    return exif

