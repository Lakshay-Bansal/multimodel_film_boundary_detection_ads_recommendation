import requests
 
# Define the URL of the Flask API
url = 'http://[IP_ADDRESS]/describe_video'
 
# Define the path to your video file
video_path = r".\Movie\Ads\Automobile Ads\Ad1_30Sec_Vechicle.mp4"
 
# Open the video file in binary mode
with open(video_path, 'rb') as video_file:
    files = {'video': video_file}
    # Send the POST request
    response = requests.post(url, files=files)
 
# Print the response from the API
print(response.json())