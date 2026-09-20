import requests
 
# Define the URL of the Flask API
url = 'http://10.222.109.63:8084/describe_video'
 
# Define the path to your video file
video_path = r"C:\Users\NH3183\OneDrive - Brane Enterprises Pvt Limited\Desktop\Netflix Poc\Ads\Automobile Ads\Ad1_30Sec_Vechicle.mp4"
 
# Open the video file in binary mode
with open(video_path, 'rb') as video_file:
    # Define the files to be uploaded
    files = {'video': video_file}
   
    # Send the POST request
    response = requests.post(url, files=files)
 
# Print the response from the API
print(response.json())