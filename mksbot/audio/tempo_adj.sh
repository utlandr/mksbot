for i in *.wav; do ffmpeg -i Z_beep.wav -filter:a atempo=1.2 -vn ../output/Z_beep.wav; done
