# Virtual-try-on

This project provides a virtual try-on experience by processing user-uploaded images of models and clothing items. The images are processed using machine learning models to generate a visualization of how the clothing items would look on the model.
Checkpoints

Download the necessary checkpoints from Hugging Face and place them in the OOTDiffusion/checkpoints directory.
Installation
Setting Up the GPU Server

    Update the package list:

    bash

sudo apt update

Install Anaconda:

bash

wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
mv Anaconda3-2023.03-1-Linux-x86_64.sh anaconda.sh
bash anaconda.sh
source ~/.bashrc

Clone the repository:

bash

git clone https://github.com/levihsu/OOTDiffusion
cd OOTDiffusion

Create and activate the Conda environment:

bash

conda create -n ootd python==3.10
conda activate ootd

Install the required dependencies:

bash

pip install torch==2.0.1 torchvision==0.15.2
pip install torchaudio==2.0.2
pip install -r requirements.txt

Install Git LFS:

bash

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install

Clone additional repositories:

bash

    cd checkpoints
    git clone https://huggingface.co/openai/clip-vit-large-patch14

Additional Setup

    Install missing libraries:

    bash

sudo apt-get install libgl1-mesa-dev

Install CUDA drivers:

bash

    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get -y install cuda
    sudo reboot

Running the Application

    Activate the Conda environment:

    bash

conda activate ootd

Navigate to the run directory and run the application:

bash

    cd OOTDiffusion/run
    python3 gradio_ootd.py

Running the Scheduler

    Ensure the scheduler script is in the correct directory:

    bash

cp scheduler.py /home/ubuntu/OOTDiffusion/run/

Run the scheduler:

bash

    python3 scheduler.py

Usage

To process the latest project, run the scheduler script. The scheduler will:

    Check for the latest project with user-uploaded images that have not yet been processed.
    Download the model and product images.
    Process the images using the specified machine learning models.
    Upload the generated images to AWS S3.
    Update the MongoDB database with the URLs of the generated images.

Troubleshooting
Common Errors

    libGL Error:

    bash

sudo apt-get install libgl1-mesa-dev

CUDA Driver Error:

bash

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda
sudo reboot
