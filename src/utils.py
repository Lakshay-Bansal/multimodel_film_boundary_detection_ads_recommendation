def frame_to_time(frame_number, fps):
    total_seconds = frame_number / fps
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def timestamp_to_frame_number(timestamp, fps):
    # Split timestamp into hours, minutes, seconds, and milliseconds
    hours, minutes, seconds_millis = timestamp.split(':')
    seconds, millis = seconds_millis.split('.')
    
    # Convert each part to integers
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    millis = int(millis)
    
    # Convert the timestamp to total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds + millis / 1000.0
    
    # Convert total seconds to frame number
    frame_number = total_seconds * fps
    
    return int(frame_number)

if __name__ == '__main__':
    print(frame_to_time(4532, 23))

    # Given timestamps and fps
    # timestamps = ["00:52:53.962", "00:56:32.889", "00:58:27.337", "01:04:07.135"]
    timestamps  = ["00:30:01.000",	"00:33:49.000", "00:33:49.000",	"00:34:04.000", "00:34:04.000",	"00:34:21.000", "00:34:21.000",	"00:36:12.000", "00:36:12.000",	"00:37:38.000", "00:37:39.000",	"00:41:42.000", "00:41:44.000",	"00:43:43.000", "00:43:43.000",	"01:01:25.000", "01:01:31.000",	"01:05:27.000", "01:05:27.000",	"01:05:44.000", "01:05:44.000",	"01:24:23.000", "01:24:23.000",	"01:25:21.000", "01:25:21.000",	"01:25:43.000", "01:25:46.000",	"01:31:08.000"]
    fps = 23.98
    # Convert each timestamp to frame number
    frame_numbers = [timestamp_to_frame_number(ts, fps) for ts in timestamps]
    # Print the results
    for ts, fn in zip(timestamps, frame_numbers):
        print(f"Timestamp: {ts} -> Frame Number: {fn}")





