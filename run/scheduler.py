import os
import uuid
import boto3
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import schedule
import time
import glob
import shutil

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id='PLACE_YOUR_SECRET_KEY_ID',
                  aws_secret_access_key='PLACE_YOUR_SECRET_KEY')
bucket_name = "BUCKET_NAME"

# MongoDB connection
client = MongoClient("MONGO_CONNECTION_URL")
db = client["viton-db"]
projects_collection = db["projects"]
users_collection = db["users"]

def process_latest_project():
    try:
        # Find the latest project created with userAddedImages set to True and aiGeneratedImages set to False
        latest_project = projects_collection.find_one(
            {"userAddedImages": True, "aiGeneratedImages": False},
            sort=[("createdAt", -1)]  # Sort by createdAt in descending order
        )

        if latest_project:
            project_id = latest_project['_id']
            user_id = latest_project['userId']
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            user_name = f"{user['firstName']}{user['lastName']}-{user_id}"
            project_name = latest_project['projectName']

            # Check if project has already been processed
            if 'finalImages' in latest_project and latest_project['finalImages']:
                print(f"Project {project_id} has already been processed.")
                return

            # Create project directory if not exist
            object_id = str(project_id)
            project_folder = os.path.join("project_images", object_id)
            os.makedirs(project_folder, exist_ok=True)

            # Download model image
            model_image_url = latest_project['modelImage']
            model_image_filename = os.path.basename(model_image_url)
            model_image_folder = os.path.join(project_folder, 'modelImage')
            os.makedirs(model_image_folder, exist_ok=True)
            model_image_local_path = os.path.join(model_image_folder, f"{uuid.uuid4()}_{model_image_filename}")
            with open(model_image_local_path, 'wb') as f:
                model_image_response = requests.get(model_image_url)
                f.write(model_image_response.content)

            # Download product images
            product_image_urls = latest_project['productImages']
            for idx, product_image_url in enumerate(product_image_urls, start=1):
                product_image_filename = os.path.basename(product_image_url)
                product_image_folder = os.path.join(project_folder, f'productImages_{idx}')
                os.makedirs(product_image_folder, exist_ok=True)
                product_image_local_path = os.path.join(product_image_folder, f"{uuid.uuid4()}_{product_image_filename}")
                with open(product_image_local_path, 'wb') as f:
                    product_image_response = requests.get(product_image_url)
                    f.write(product_image_response.content)

                # Run ML model to generate images for each product image
                model_image_paths = glob.glob(os.path.join(project_folder, 'modelImage', '*.jpg'))
                product_image_folders = glob.glob(os.path.join(project_folder, 'productImages_*'))
                output_folder = os.path.join("images_output", object_id)
                os.makedirs(output_folder, exist_ok=True)
                for product_image_folder in product_image_folders:
                    product_image_paths = glob.glob(os.path.join(product_image_folder, '*.jpg'))
                    for product_image_path in product_image_paths:
                        os.system(f"python3 run_ootd.py --model_path {' '.join(model_image_paths)} --cloth_path {product_image_path} --project_id {project_id} --scale 2.0 --sample 1 --step 20 --gpu_id 0")
                
                '''model_image_files = glob.glob(os.path.join(project_folder, 'modelImage', '*.jpg'))
                output_folder = os.path.join("images_output", object_id)
                os.makedirs(output_folder, exist_ok=True)

                os.system(f"python3 run_ootd.py --model_path {' '.join(model_image_files)} --cloth_path {product_image_local_path} --project_id {project_id} --scale 2.0 --sample 1 --step 20 --gpu_id 0")'''
                # Upload generated images to S3
                s3_urls = []
                for generated_image in glob.glob("output/*.jpg"):
                    generated_image_name = f"out_{str(uuid.uuid4())[:8]}.jpg"  # Unique name for each image
                    local_file_path = os.path.join(output_folder, generated_image_name)
                    shutil.copy(generated_image, local_file_path)

                    s3_key = f"{user_name}/{project_name}-{project_id}/finalImages/{generated_image_name}"
                    s3.upload_file(local_file_path, bucket_name, s3_key)
                    print(f"Uploaded {local_file_path} to S3 bucket {bucket_name} with key {s3_key}")

                    # Construct the S3 URL for the uploaded image
                    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
                    s3_urls.append(s3_url)

                # Update MongoDB document with S3 URLs
                projects_collection.update_one(
                    {"_id": project_id},
                    {"$push": {"finalImages": {"$each": s3_urls}}}
                )

            # Update MongoDB to indicate that AI generated images are available
            projects_collection.update_one(
                {"_id": project_id},
                {"$set": {"aiGeneratedImages": True}}
            )

            print(f"Updated MongoDB document with S3 URLs for project: {project_id}")

        else:
            print("No projects found with userAddedImages set to True.")
    except Exception as e:
        print("Error:", e)

# Schedule the function to run every 5 seconds
schedule.every(5).seconds.do(process_latest_project)

while True:
    schedule.run_pending()
    time.sleep(1)
