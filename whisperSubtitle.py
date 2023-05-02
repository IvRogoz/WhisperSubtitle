import os
import whisper
import time
from pathlib import Path

from tkinter.filedialog import askopenfilename
import tkinter as tk

root = tk.Tk()
root.overrideredirect(1)
root.withdraw()

# video file path
video_path = askopenfilename()

# Whisper model options
model_type = 'small'
video_lang = 'hr'

# output file options
save_path = 'data'
_, tail = os.path.split(video_path)
tail = os.path.splitext(tail)[0]
try:
	fullIndex = tail.index('full')+4
except:
	fullIndex = 0
filename = tail[fullIndex:]
format = 'srt'

# create output directory if it doesn't exist
save_path = Path(save_path)
save_path.mkdir(exist_ok=True, parents=True)

def transcribe(video_path, save_path, filename, model_type=model_type, video_lang=video_lang):
    # load Whisper model
    model = whisper.load_model(model_type)
    
    start_time = time.time()
    # set decoding options
    options = whisper.DecodingOptions(fp16=False, language=video_lang)

    # transcribe the video
    result = model.transcribe(video_path, **options.__dict__, verbose=True)

    # calculate the duration of the transcription
    duration = time.time() - start_time

    # print the duration
    print(f"Transcription duration: {duration:.2f} seconds")

    # convert segments to subtitle format
    sub = segments_to_srt(result['segments'])

    # save the subtitle file
    sub_file = save_subtitle(sub, save_path, filename, format=format)

    print(f"Subtitle saved to {sub_file}")

def segments_to_srt(segs):
    text = []
    for i, s in enumerate(segs):
        text.append(str(i + 1))

        # format start time
        hours, remainder = divmod(s['start'], 3600)
        minutes, seconds = divmod(remainder, 60)
        timestamp_start = "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        #text.append(timestamp_start)

        # format end time
        hours, remainder = divmod(s['end'], 3600)
        minutes, seconds = divmod(remainder, 60)
        timestamp_end = "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        text.append(f"{timestamp_start} --> {timestamp_end}")

        text.append(f"{s['text'].strip()}\n")

    return "\n".join(text)

def save_subtitle(sub, save_path, filename, format='srt'):
    sub_file = save_path/f'{filename}.{format}'
    with open(sub_file, 'w', encoding='utf-8') as f:
        f.write(sub)
    return sub_file

# run the transcription and subtitle creation process
transcribe(video_path, save_path, filename, model_type, video_lang)
