import os
from google.cloud import storage
from dotenv import load_dotenv
from pathlib import Path
import requests
import streamlit as st
from pathlib import Path
import tempfile
import PyPDF2
import pdf_utils
import time
from reportlab.lib.utils import ImageReader
import io
import constants
from datetime import timedelta
from urllib.parse import urlparse


load_dotenv()

machine = os.getenv("MACHINE")
bucket_name = os.getenv("S3_BUCKET_NAME")

def upload_file_to_gcs(bucket_name, file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file,rewind=True)
    return blob.public_url


def upload_file_to_gcs(bucket_name, file, destination_blob_name, make_public=False, expiration_minutes=300):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload file
    blob.upload_from_file(file, rewind=True)

    if make_public:
        # Set public access if required (for logos, symbols, etc.)
        blob.make_public()
        return blob.public_url
    else:
        # Generate signed URL (temporary access)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        return url

def upload_file_to_s3(bucket_name, file_obj, destination_key, make_public=True):
    """
    Upload file object to AWS S3
    """
    # Upload directly from file-like object
    constants.s3.upload_fileobj(file_obj, bucket_name, destination_key)

    if make_public:
        constants.s3.put_object_acl(ACL="public-read", Bucket=bucket_name, Key=destination_key)
        return f"https://{bucket_name}.s3.ap-south-1.amazonaws.com/{destination_key}"
    else:
        return f"s3://{bucket_name}/{destination_key}"

# upload files    
def upload_file(file_obj,doc_name,subfolder,type,user_id):
    if machine=="local":
        os.makedirs(subfolder, exist_ok=True)
        file_path = f"{subfolder}/{type}_{user_id}_{doc_name}"

        with open(file_path, "wb") as f:
            f.write(file_obj.getbuffer())
        return file_path
    elif machine=="aws":
        file_path = f"{subfolder}/{type}_{user_id}_{doc_name}"
        blob_path = upload_file_to_s3(bucket_name, file_obj,file_path)
        return blob_path
    elif machine=="gcp":
        file_path = f"{subfolder}/{type}_{user_id}_{doc_name}"
        blob_path = upload_file_to_gcs(bucket_name, file_obj,file_path)
        return blob_path
    
def execute_query(cursor,query,params=None,machine=None):
    if params:
        query = query.replace('?','%s')
        cursor.execute(query,params)
    else:
        cursor.execute(query)

def convert_to_dict(cursor, rows):
    if not rows:
        result = []
    else:
        result = rows
    return result

def generate_signed_url(file_url: str, expiration=3600):
    """
    Generate a signed URL for a private GCS object.
    file_url: full https://storage.googleapis.com/bucket/path/file.pdf
    expiration: time in seconds (default 1 hour)
    """
    parsed = urlparse(file_url)
    # parsed.path looks like "/bucket-name/path/to/file"
    parts = parsed.path.lstrip("/").split("/", 1)
    bucket_name, blob_name = parts[0], parts[1]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(expiration=expiration)
    return url

def download_document_pdf(label: str, file_path:str, machine: str):
    if not file_path:
        st.warning(f"{label} not available.")
        return
    
    if machine == 'local':
        base_dir = Path(__file__).parent
        abs_path = base_dir / file_path
        if abs_path.exists():
            with open(abs_path, "rb") as f:
                st.download_button(label=f"Download {label}", data=f, file_name=os.path.basename(file_path),mime="application/pdf")
        else:
            st.warning(f"{label} not available.")
    elif machine == "aws":
        if file_path.startswith("http"):
            try:
                response = requests.get(file_path)
                if response.status_code == 200:
                    st.download_button(label=f"Download {label}", data=response.content, file_name=file_path.split("/")[-1], mime="application/octet-stream")
                else:
                    st.error(f"Failed to download {label} from cloud storage.")
            except Exception as e:
                st.error(f"Error downloading {label}: {str(e)}")
        else:
            st.error(f"Invalid file URL for {label}.")
    elif machine == "gcp":
        try:
            signed_url = generate_signed_url(file_path, expiration=600)
            response = requests.get(signed_url)
            if response.status_code == 200:
                st.download_button(label=f"Download {label}",data=response.content,file_name=file_path.split("/")[-1],mime="application/octet-stream")
            else:
                st.error(f"Failed to download {label} from GCS.")
        except:
            st.error(f"Invalid file URL for {label}.")


def download_file_if_url(path_or_url):
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        response = requests.get(path_or_url)
        if response.status_code == 200:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(response.content)
            tmp.flush()
            return tmp.name
        else:
            return None
    else:
        return path_or_url if os.path.exists(path_or_url) else None
    
def generate_and_download_profile_pdf(machine, terms_file_path, file_name, **profile_kwargs):

    # Step 1: Generate profile PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
        pdf_utils.generate_profile_pdf_with_disclaimers(tmpfile.name, **profile_kwargs)
        tmpfile.flush()
        base_pdf_path = tmpfile.name

    # Step 2: Handle terms file (local or GCS URL)
    terms_path_resolved = download_file_if_url(terms_file_path) if terms_file_path else None

    # Step 3: Merge if needed
    if terms_path_resolved:
        merger = PyPDF2.PdfMerger()
        merger.append(base_pdf_path)
        merger.append(terms_path_resolved)
        merged_path = base_pdf_path.replace(".pdf", "_merged.pdf")
        merger.write(merged_path)
        merger.close()
        with open(merged_path, "rb") as f:
            pdf_bytes = f.read()
        os.remove(merged_path)
    else:
        with open(base_pdf_path, "rb") as f:
            pdf_bytes = f.read()

    # Step 4: Clean up
    os.remove(base_pdf_path)
    if terms_path_resolved and terms_path_resolved != terms_file_path:
        os.remove(terms_path_resolved)  # clean up downloaded GCS file

    # Step 5: Download Button
    download_clicked = st.download_button(
        label="Download Profile",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf"
    )
    if download_clicked:
        st.session_state['profile_downloaded'] = True
        st.session_state['profile_downloaded_time'] = time.time()
        st.rerun()

    if st.session_state.get('profile_downloaded', False):
        elapsed = time.time() - st.session_state.get('profile_downloaded_time', 0)
        if elapsed < 2:
            st.success("Profile downloaded successfully!")
        else:
            st.session_state['profile_downloaded'] = False


def get_image_reader(image_path_or_url):
    try:
        if image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://"):
            response = requests.get(image_path_or_url)
            if response.status_code == 200:
                return ImageReader(io.BytesIO(response.content))
            
            elif response.status_code == 403 and "storage.googleapis.com" in image_path_or_url:
                signed_url = generate_signed_url(image_path_or_url, expiration=600)
                response = requests.get(signed_url)
                if response.status_code == 200:
                    return ImageReader(io.BytesIO(response.content))
        elif os.path.exists(image_path_or_url):
            return ImageReader(image_path_or_url)
    except Exception as e:
        st.error(f"Unable to load image.")
    return None


def display_image_from_path(photo_path, caption="Image", width=120, machine="local"):
    if not photo_path:
        st.info(f"No {caption.lower()} uploaded.")
        return

    if machine == "local":
        if os.path.exists(photo_path):
            st.image(photo_path, width=width, caption=caption)
        else:
            st.warning(f"{caption} not available.")
    elif machine=="aws":
        try:
            response = requests.get(photo_path)
            if response.status_code == 200:
                st.image(photo_path, width=width, caption=caption)
            else:
                st.warning(f"{caption} not found in cloud.")
        except Exception as e:
            st.error(f"Error loading {caption}: {e}")
    elif machine == "gcp":
        try:
            signed_url = generate_signed_url(photo_path, expiration=600)  # valid 10 min
            st.image(signed_url, width=width, caption=caption)
        except Exception as e:
            st.error(f"Error loading {caption} from GCS: {e}")

def display_photo(photo_path, caption=None, use_container_width=False, width=None):
    if not photo_path:
        st.info("No photo provided.")
        return

    if photo_path.startswith("http://") or photo_path.startswith("https://"):
        # It's a GCS or web URL
        try:
            response = requests.get(photo_path)
            if response.status_code == 200:
                st.image(photo_path, caption=caption, use_container_width=use_container_width, width=width)
            else:
                st.warning(f"Unable to load photo from URL: {photo_path}")
        except Exception as e:
            st.error(f"Error loading photo from URL: {e}")
    else:
        # Assume it's a local path
        if os.path.exists(photo_path):
            st.image(photo_path, caption=caption, use_container_width=use_container_width, width=width)
        else:
            st.warning(f"Photo not found: {photo_path}")