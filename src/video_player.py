import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import *
import cv2
from PIL import Image, ImageTk
import os
import sys
# Add the current script's directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import pandas as pd
from utils import frame_to_time
import time
from mapping_scene_with_ads import map_scene_desc_ads
from scene_description import generate_scene_desc
from extract_30s_back_clip import generate_30s_back_scene_clips

class SimpleVideoPlayer:
    def __init__(self, root, scene_start_frames, scene_description, ads_description):
        self.scene_start_frames = scene_start_frames
        self.scene_description = scene_description
        self.ads_description = ads_description
        self.cap = None
        self.current_frame = None
        self.scene_number = 0
        self.play = True
        self.playing_ads = False
        self.ads_cap = None
        self.map_ads_index = None
        self.scene_number_updated = False

        # Frame resize new height and width
        self.new_width, self.new_height = 800, 360


        self.root = root
        self.root.title("Netflix Video Player")

        first_row_frame = tk.LabelFrame(root, text="", bg="black", fg="white", padx=15, pady=5, width=self.new_width+500, height=self.new_height+50)
        first_row_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        first_row_frame.grid_propagate(False)

        # Video Play window
        video_play_frame = tk.LabelFrame(first_row_frame, text="Video Player", bg="black", fg="white", padx=5, pady=5, width=self.new_width+50, height=self.new_height+50)
        video_play_frame.grid(row=0, column=0, padx=10, pady=5)
        video_play_frame.grid_propagate(False)

        # Define the display size of the video
        # self.video_width = 320
        # self.video_height = 240
        self.video_label = tk.Label(video_play_frame, text="Video Player", bg="gray")
        self.video_label.grid(row=0, column=0, padx=5, pady=5)


        # Create a ScrolledText widget for scene boundary65
        # Create a ScrolledText widget for scene boundary
        text_frame = tk.LabelFrame(first_row_frame, text="Scene Boundary", bg="black", fg="white", padx=5, pady=5, width=150, height=self.new_height+50)
        text_frame.grid(row=0, column=1, padx=10, pady=5)
        text_frame.grid_propagate(False)
        self.text_area = scrolledtext.ScrolledText(text_frame, width=40, height=20)
        self.text_area.pack(padx=10, pady=5)

        # Video buttons functionality
        button_frame = tk.LabelFrame(root, text="Video Buttons", bg="black", fg="white", padx=15, pady=15, width=self.new_width+500, height=80)
        button_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        button_frame.grid_propagate(False)

        self.load_video_button = tk.Button(button_frame, text="Load video", command=self.load_video)
        self.load_video_button.grid(row=0, column=0, padx=5, pady=5)

        self.next_scene_button = tk.Button(button_frame, text="Next scene", command=self.next_scene)
        self.next_scene_button.grid(row=0, column=1, padx=5, pady=5)

        self.back_30_seconds_button = tk.Button(button_frame, text="Back 30s", command=self.back_30_seconds)
        self.back_30_seconds_button.grid(row=0, column=2, padx=5, pady=5)

        self.next_30_seconds_button = tk.Button(button_frame, text="Next 30s", command=self.next_30_seconds)
        self.next_30_seconds_button.grid(row=0, column=3, padx=5, pady=5)

        self.pause_button = tk.Button(button_frame, text="pause", command=self.pause)
        self.pause_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.play_button = tk.Button(button_frame, text="play", command=self.playfunc)
        self.play_button.grid(row=0, column=5, padx=5, pady=5)


        # Present frame in a cloumn 
        scene_start_frames_string = ""
        for sf in self.scene_start_frames:
            scene_start_frames_string += f"{sf}\n"
        self.text_area.insert(tk.END, scene_start_frames)
        self.text_area.configure(state=tk.DISABLED)


        # Create a Scene description ScrolledText widget
        desc_frame = tk.LabelFrame(root, text="Description", bg="black", fg="white", padx=15, pady=15, width=self.new_width+500, height=200)
        desc_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        desc_frame.grid_propagate(False)

        scene_desc_frame = tk.LabelFrame(desc_frame, text="Scene Description", bg="black", fg="white", padx=15, pady=5)
        scene_desc_frame.grid(row=0, column=0, padx=4, pady=4)
        # scene_desc_frame.grid_propagate(False)

        self.scene_desc_frame = scrolledtext.ScrolledText(scene_desc_frame, width=65, height=5)
        self.scene_desc_frame.pack(padx=5, pady=3)

        self.scene_desc_frame.insert(tk.END, self.scene_desc_display(self.scene_description["description"].iloc[self.scene_number]))
        self.scene_desc_frame.configure(state=tk.DISABLED)

        # Create a Ads description ScrolledText widget
        ads_desc_frame = tk.LabelFrame(desc_frame, text="ads Description", bg="black", fg="white", padx=15, pady=5)
        ads_desc_frame.grid(row=0, column=1, padx=50, pady=3)
        # ads_desc_frame.grid_propagate(False)

        self.ads_desc_frame = scrolledtext.ScrolledText(ads_desc_frame, width=65, height=5)
        self.ads_desc_frame.pack(padx=5, pady=3)

        # Map all scenes with the relevant ads and gives a mapping index for a ads
        # self.map_ads_idx = map_scene_desc_ads(self.ads_description["description"].to_list(), self.scene_description["description"].to_list())
        self.map_ads_idx = map_scene_desc_ads(self.ads_description["description"], self.scene_description["description"])

        self.ads_desc_frame.insert(tk.END, self.scene_desc_display(self.ads_description["description"].iloc[self.map_ads_idx[self.scene_number]]))
        self.ads_desc_frame.configure(state=tk.DISABLED)

        
    def load_video(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.cap = cv2.VideoCapture(file_path)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.scene_start_frames[self.scene_number]-15*24)
        self.play_video()
    
    def tranform_frame(self, frame):
        # Define the position for the text (top-right corner)
        text_position = (frame.shape[1] - 450, 50)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        color = (255, 0, 0)  
        thickness = 2
        # Put the frame number text on the frame
        cv2.putText(frame, f"Frame: {self.current_frame_number}, Time: {frame_to_time(self.current_frame_number, self.cap.get(cv2.CAP_PROP_FPS))}", text_position, font, font_scale, color, thickness)
        frame = cv2.resize(frame, (self.new_width, self.new_height))
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)

        return photo

    def play_video(self):
        if self.cap is not None and self.cap.isOpened() and self.play:
            if not self.playing_ads:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                    # # Define the position for the text (top-right corner)
                    # text_position = (frame.shape[1] - 450, 50)
                    # font = cv2.FONT_HERSHEY_SIMPLEX
                    # font_scale = 0.8
                    # color = (0, 255, 255)  # Yellow color
                    # thickness = 2
                    # # Put the frame number text on the frame
                    # cv2.putText(frame, f"Frame: {self.current_frame_number}, Time: {frame_to_time(self.current_frame_number, self.cap.get(cv2.CAP_PROP_FPS))}", text_position, font, font_scale, color, thickness)
                    # frame = cv2.resize(frame, (self.new_width, self.new_height))
                    # image = Image.fromarray(frame)
                    # photo = ImageTk.PhotoImage(image=image)
                    photo = self.tranform_frame(frame)
                    self.video_label.config(image=photo)
                    self.video_label.image = photo

                    # Check if the current frame number is the desired frame to play the clip
                    # print(self.current_frame_number, self.scene_start_frames[self.scene_number])
                    if self.current_frame_number == int(self.scene_start_frames[self.scene_number]):
                        self.play_ads(self.ads_description["video_path"].iloc[self.map_ads_idx[self.scene_number]])
                        
                        # Whenever scene number updates new scene description and ads should be displayed
                        if self.scene_number < len(self.scene_start_frames):
                            self.scene_number += 1
                            self.scene_number_updated = True
                            self.update_scene_desc_box()
                            self.update_ads_desc_box()

                        elif self.scene_number > len(self.scene_start_frames):
                            print("You had viewed all the scene boundary")

                self.root.after(30, self.play_video)  # Adjust the delay to control the frame rate

    def back_30_seconds(self):
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.current_frame_number = max(0, self.current_frame_number - (30 * fps))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number)
        self.pause()
        self.show_updated_frame()
        # time.sleep(1)
        # self.play()
    
    def next_30_seconds(self):
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.current_frame_number = max(0, self.current_frame_number + (30 * fps))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_number)

    def next_scene(self):
        if not self.scene_number_updated:
            self.scene_number += 1
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.scene_number < len(self.scene_start_frames):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.scene_start_frames[self.scene_number])
            self.pause()
            self.show_updated_frame()
            # time.sleep(1)
            # self.play()

            self.update_scene_desc_box()
            self.update_ads_desc_box()

        elif self.scene_number > len(self.scene_start_frames):
            print("You had viewed all the scene boundary")
        
        self.scene_number_updated = False

    # Update the scene description in the box as soon as scene change is detected
    def update_scene_desc_box(self):
        self.scene_desc_frame.configure(state=tk.NORMAL)
        self.scene_desc_frame.delete('1.0', tk.END)
        self.scene_desc_frame.insert(tk.END, self.scene_desc_display(self.scene_description['description'].iloc[self.scene_number]))
        self.scene_desc_frame.configure(state=tk.DISABLED)
    
    def update_ads_desc_box(self):
        self.ads_desc_frame.configure(state=tk.NORMAL)
        self.ads_desc_frame.delete('1.0', tk.END)
        self.ads_desc_frame.insert(tk.END, self.scene_desc_display(self.ads_description["description"].iloc[self.map_ads_idx[self.scene_number]]))
        self.ads_desc_frame.configure(state=tk.DISABLED)

    # It just show the current readed frame for 30s back and next scene functionality
    def show_updated_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                # Function to transform frame dimension
                photo = self.tranform_frame(frame)
                self.video_label.config(image=photo)
                self.video_label.image = photo

    def pause(self):
        self.play = False
    
    def playfunc(self):
        self.play = True
        self.play_video()
    
    def scene_desc_display(self, text):
        # other method
        # first_video_desc = first_video_desc[re.search(r'ASSISTANT: ',first_video_desc).end():]
        index = text.find("ASSISTANT")
        final_text = text[index+11:]
        return final_text
    
    def play_ads(self, clip_path):
        self.playing_ads = True
        self.ads_cap = cv2.VideoCapture(clip_path)
        print(f"Playing AD number: {self.scene_number}, Path: {clip_path}, {self.ads_cap.isOpened()}")

        while self.ads_cap.isOpened():
            ret, frame = self.ads_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.new_width, self.new_height))
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                self.video_label.config(image=photo)
                self.video_label.image = photo
                self.root.update()
                time.sleep(0.033)  # Approximately 30 FPS
            else:
                break

        self.ads_cap.release()
        self.playing_ads = False
        self.play_video()  # Resume the main video
    

if __name__ == "__main__":
    movie_list = ["Spiderman 1.mkv", "Kung Fu Panda (2008).mp4", "Inception_720p.mp4"]
    movie_name = movie_list[0]

    root = tk.Tk()
    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry("%dx%d" % (screen_width, screen_height))
    print("Screen width and height are: ", screen_width, screen_height)

    scene_threshold_file = os.path.join(os.getcwd(), f'Movie\{movie_name}.theshold_scenes_final.txt')
    scenes_df = pd.read_csv(scene_threshold_file, sep=' ', header=None)
    scenes_df.columns = ['start_frame', 'end_frame']
    scene_start_frames = list(scenes_df["start_frame"])

    # Generate 30 sec back clips for the detected scene boundary
    # Output will be in ./result/{movie_name}_scene_clips
    if not os.path.exists( os.path.join(os.getcwd(), f'result/{movie_name}_scene_clips') ):
        print("-------------- Generating 30 sec back scene clips")
        generate_30s_back_scene_clips(movie_name)

    # Read ads and scene description csv files
    path_scene_description_csv = os.path.join(os.getcwd(), f'result\{movie_name}_scene_clips\scene_description.csv')

    if not os.path.exists( path_scene_description_csv):
        # Generate scene description file for a movie
        # Output path of csv file is ./result/{movie_name}_scene_clips/scene_description.csv
        print("------------------- Running generate scene description at the scene boundary")
        generate_scene_desc(movie_name)

    # For an update in Ads folder need to run ads_description.py once to generate ads_description.csv
    path_ads_description_csv = os.path.join(os.getcwd(), 'ads_description.csv')

    scene_description = pd.read_csv(path_scene_description_csv)
    ads_description = pd.read_csv(path_ads_description_csv)
    
    player = SimpleVideoPlayer(root, scene_start_frames, scene_description, ads_description)
    root.mainloop()


