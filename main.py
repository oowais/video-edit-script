import subprocess
import os
import shutil
from tqdm import tqdm


def calculate_total_duration(clips_dict):
    """
    Calculates the total duration of the final video based on clips_dict.
    Time format: HH:MM:SS (e.g., "00:01:00" for 1 minute).
    """
    total_seconds = 0
    for filename, (start_time, end_time) in clips_dict.items():
        start_seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(start_time.split(":")))
        )
        end_seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(end_time.split(":")))
        )
        total_seconds += end_seconds - start_seconds

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def cut_video(input_file, output_file, start_time, end_time):
    """
    Cuts a video using FFmpeg with re-encoding for accurate cuts.
    Time format: HH:MM:SS (e.g., "00:01:00" for 1 minute).
    """
    command = [
        "ffmpeg",
        "-ss",
        start_time,
        "-i",
        input_file,
        "-to",
        end_time,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-avoid_negative_ts",
        "1",
        output_file,
    ]
    subprocess.run(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


def combine_videos(input_files, output_file):
    """
    Combines multiple videos into one using FFmpeg's concat protocol.
    """
    input_args = []
    for file in input_files:
        input_args.extend(["-i", file])

    filter_complex = f"concat=n={len(input_files)}:v=1:a=1"

    command = [
        "ffmpeg",
        *input_args,
        "-filter_complex",
        filter_complex,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_file,
    ]
    subprocess.run(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


def main(video_folder, clips_dict, final_output_file):
    """
    Main function to cut and combine videos.
    Time format in clips_dict: HH:MM:SS (e.g., "00:01:00" for 1 minute).
    """
    cut_files = []
    for filename, (start_time, end_time) in tqdm(
        clips_dict.items(), desc="Cutting videos", unit="file"
    ):
        input_file = os.path.join(video_folder, filename)
        output_file = os.path.join(video_folder, f"cut_{filename}")

        tqdm.write(f"Cutting {filename} from {start_time} to {end_time}...")
        cut_video(input_file, output_file, start_time, end_time)
        cut_files.append(output_file)

    if len(cut_files) == 1:
        tqdm.write("Only one file detected. Skipping combining step...")
        shutil.move(cut_files[0], final_output_file)
    else:
        tqdm.write("Combining videos...")
        combine_videos(cut_files, final_output_file)

    tqdm.write(f"Final output saved to {final_output_file}")

    for file in cut_files:
        if os.path.exists(file):
            os.remove(file)


if __name__ == "__main__":
    video_folder = r"C:\Videos"
    final_output_file = os.path.join(r"C:\Videos", "final_output.mp4")
    clips_dict = {
        # "1.mp4": ("00:00:15", "00:01:57"),
        # "2.mp4": ("00:00:15", "00:01:57"),
        # "3.mp4": ("00:00:15", "00:01:57"),
    }

    total_duration = calculate_total_duration(clips_dict)
    print(f"Total duration of the final video will be: {total_duration}")

    user_input = input("Do you want to continue? (y/n): ").strip().lower()
    if user_input != "y":
        print("Operation cancelled by the user.")
        exit()

    main(video_folder, clips_dict, final_output_file)
