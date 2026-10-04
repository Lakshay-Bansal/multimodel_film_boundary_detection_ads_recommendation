import os
import glob
import requests
import pandas as pd
import tqdm as tqdm
import re

def read_ads(video_path):
    with open(video_path, 'rb') as video_file:
        # Define the files to be uploaded
        files = {'video': video_file}
        # Send the POST request
        response = requests.post(url, files=files)
    try:
        return response.json()['description']
    except:
        return "error"

url = 'http://[IP_ADDRESS]/describe_video'
ads_dir = r'.\Movie\Ads'
file_pattern = os.path.join(ads_dir, '**', '*.mp4')
ads_files_path = glob.glob(file_pattern, recursive=True)

# for idx, file_path in enumerate(ads_files_path): 
#     print(f"{idx+1} ------------------------- {file_path}")

data = []
save_ads_description_path = os.path.join(os.getcwd(), 'ads_description.csv')

# for idx, file_path in tqdm(enumerate(list(ads_files_path)), total=len(ads_files_path), desc="Processing files"):
for idx, file_path in enumerate(ads_files_path):    
    if os.path.isfile(file_path):
        ads_desciption = read_ads(file_path)
        if ads_desciption == "error":
            continue
        ads_desciption = str(ads_desciption[re.search(r'ASSISTANT: ',ads_desciption).end():])
        print(f"Ads {idx+1} - Path: {file_path} - {ads_desciption}")
        new_entry = {'video_path': str(file_path), 'description': ads_desciption}
        data.append(new_entry)

# Save  a ads description to a file
save_ads_description_path = os.path.join(os.getcwd(), 'ads_description.csv')

df = pd.DataFrame(data, columns=['video_path', 'description'])
print(f"Stored a description for {df.shape[0]}")
df.to_csv(save_ads_description_path, index=False)