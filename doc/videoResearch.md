using this project

https://github.com/codewithpassion/mjpg-streamer
But still works with the oficial



m### take picture every 100 ms (-tl parameter)



 &

### picking the pictures up and expose them using and embedded web server

before install make sure jpeg lib is installed. If it doesnt trye:
	apt-get install libjpeg-dev

./mjpg_streamer -i "input_file.so -f /home/pi/tmp/mjpg -r" -o "output_http.so -p 8095 -w ./www"


LD_LIBRARY_PATH=./ ./mjpg_streamer -i "input_file.so -r -n pic.jpg -f /var/stream -i 1" -o "output_http.so -p 8095 -w ./www" &

## 2014/06/23
I shpuld try this new sheet


https://github.com/jacksonliam/mjpg-streamer

### should work with this simple call

export LD_LIBRARY_PATH=.
./mjpg_streamer -o "output_http.so -p 8095 -w ./www" -i "input_raspicam.so -x 640 -y 480 -fps 15 -vf -hf -quality 20 -ex night"


## 2014/10/28


export LD_LIBRARY_PATH=.
./mjpg_streamer -o "output_http.so -p 8095 -w ./www" -o "output_file.so -f pics -d 15000" -i "input_raspicam.so -x 640 -y 480 -fps 15 -vf -hf -quality 20 -ex night"

LD_LIBRARY_PATH=./ ./mjpg_streamer -i "input_file.so -r -n pic.jpg -f /var/stream -i 1" -o "output_http.so -p 8096 -w ./www" &


note 
sudo apt-get install cmake
sudo apt-get install libjpeg8-dev imagemagick libv4l-dev

LD_LIBRARY_PATH=./ ./mjpg_streamer -o "output_http.so -p 8095 -w ./www" -o "output_file.so -f /var/stream  -d 15000" -i "input_raspicam.so -x 640 -y 480 -fps 15  -quality 20 -ex night"
