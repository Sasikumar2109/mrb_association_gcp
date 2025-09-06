from dotenv import load_dotenv
import os
import base64
import requests
import boto3

load_dotenv()

machine = os.getenv("MACHINE")
bucket_name = os.getenv("BUCKET_NAME")

photo1_path = "data/optimized_association_photos/photo1.JPG"
photo2_path = "data/optimized_association_photos/photo2.JPG"
photo3_path = "data/optimized_association_photos/photo3.JPG"
photo4_path = "data/optimized_association_photos/photo4.JPG"
photo5_path = "data/optimized_association_photos/photo5.JPG"
photo6_path = "data/optimized_association_photos/photo6.JPG"
photo7_path = "data/optimized_association_photos/photo7.JPG"
photo8_path = "data/optimized_association_photos/photo8.jpg"
photo9_path = "data/optimized_association_photos/photo9.JPG"
photo10_path = "data/optimized_association_photos/photo10.JPG"

logo_path = 'data/icons/logo.png'
hospital_symbol_path = 'data/icons/hospital_symbol.png'
sub_sign_path = 'uploads/signature'
sub_photo_path = 'uploads/photo'
sub_rnrm_path = 'uploads/rnrm'
sub_aadhar_path = 'uploads/aadhar'
sub_term_path = 'data/documents/terms_and_conditions'

if machine=="local":
    photo1 = photo1_path
    photo2 = photo1_path
    photo3 = photo1_path
    photo4 = photo1_path
    photo5 = photo1_path
    photo6 = photo1_path
    photo7 = photo1_path
    photo8 = photo1_path
    photo9 = photo1_path
    photo10 = photo1_path

elif machine=="aws":
    photo1 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo1_path}"
    photo2 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo2_path}"
    photo3 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo3_path}"
    photo4 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo4_path}"
    photo5 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo5_path}"
    photo6 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo6_path}"
    photo7 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo7_path}"
    photo8 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo8_path}"
    photo9 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo9_path}"
    photo10 = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{photo10_path}"

elif machine=="gcp":
    photo1 = f"https://storage.googleapis.com/{bucket_name}/{photo1_path}"
    photo2 = f"https://storage.googleapis.com/{bucket_name}/{photo2_path}"
    photo3 = f"https://storage.googleapis.com/{bucket_name}/{photo3_path}"
    photo4 = f"https://storage.googleapis.com/{bucket_name}/{photo4_path}"
    photo5 = f"https://storage.googleapis.com/{bucket_name}/{photo5_path}"
    photo6 = f"https://storage.googleapis.com/{bucket_name}/{photo6_path}"
    photo7 = f"https://storage.googleapis.com/{bucket_name}/{photo7_path}"
    photo8 = f"https://storage.googleapis.com/{bucket_name}/{photo8_path}"
    photo9 = f"https://storage.googleapis.com/{bucket_name}/{photo9_path}"
    photo10 = f"https://storage.googleapis.com/{bucket_name}/{photo10_path}"    


def image_url_to_base64(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode()

if machine=='local':
    logo_path = logo_path
    hospital_symbol_path = hospital_symbol_path
    logo_base64 = base64.b64encode(open(logo_path, 'rb').read()).decode()
    symbol_base64 = base64.b64encode(open(hospital_symbol_path, 'rb').read()).decode()
elif machine=="aws":
    logo_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{logo_path}"
    hospital_symbol_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{hospital_symbol_path}"
    logo_base64 = image_url_to_base64(logo_path)
    symbol_base64 = image_url_to_base64(hospital_symbol_path)
elif machine=="gcp":
    logo_path = f"https://storage.googleapis.com/{bucket_name}/{logo_path}"
    hospital_symbol_path = f"https://storage.googleapis.com/{bucket_name}/{hospital_symbol_path}"
    logo_base64 = base64.b64encode(requests.get(logo_path).content).decode()
    symbol_base64 = base64.b64encode(requests.get(hospital_symbol_path).content).decode()

      
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRECT_ACCESS")
aws_region = os.getenv("AWS_REGION")
bucket_name = os.getenv("S3_BUCKET_NAME")


s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)