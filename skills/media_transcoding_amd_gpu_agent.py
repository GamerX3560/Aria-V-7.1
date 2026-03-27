#!/usr/bin/env python3

import argparse
import subprocess
import sys

def check_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: ffmpeg is not installed. Please install it to use this tool.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg failed to run. {e.stderr.decode('utf-8')}")
        sys.exit(1)

def transcode_video(input_file, output_file, codec='h264_amf', preset='fast', crf=23):
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', codec,
            '-preset', preset,
            '-crf', str(crf),
            output_file
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Transcoding successful: {output_file}")
        print(result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error during transcoding: {e.stderr.decode('utf-8')}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Media Transcoding with AMD GPU using FFmpeg')
    parser.add_argument('input_file', help='Input video file to transcode')
    parser.add_argument('output_file', help='Output video file after transcoding')
    parser.add_argument('--codec', default='h264_amf', help='Video codec to use (default: h264_amf)')
    parser.add_argument('--preset', default='fast', help='Encoding speed/quality tradeoff (default: fast)')
    parser.add_argument('--crf', type=int, default=23, help='Constant Rate Factor (default: 23)')

    args = parser.parse_args()

    check_ffmpeg_installed()
    transcode_video(args.input_file, args.output_file, args.codec, args.preset, args.crf)

if __name__ == '__main__':
    main()