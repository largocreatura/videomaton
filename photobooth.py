#!/usr/bin/env python

import os
import glob
import time
import traceback
from time import sleep
import RPi.GPIO as GPIO
import picamera
import atexit
import sys
import socket
import pygame
import pytumblr
import config
from signal import alarm, signal, SIGALRM, SIGKILL

####################################################################
############################ VARIABLES #############################
####################################################################

button1_pin = 23 # pin START
button2_pin = 22 # pin UPLOAD
button3_pin = 21 # pin SAVE LOCAL
button4_pin = 17 # pin EXIT PROGRAM
button5_pin = 27 # pin SHUTDOWN

post_online = 0 # UPLOAD: 1. NO UPLOAD: 0
total_pics = 1 # N PICS
capture_delay = 1 # DELAY btw pics
prep_delay = 1 # number of seconds at step 1 as users prep to have photo taken
gif_delay = 50 # GIF DELAY btw pics
restart_delay = 2 # TIME FINISH MSG

monitor_w =  800
monitor_h = 480
transform_x = 640 # how wide to scale the jpg when replaying
transfrom_y = 281 # how high to scale the jpg when replaying
offset_x = 240 # how far off to left corner to display photos
offset_y =  272 # how far off to left corner to display photos
replay_delay = 1 # how much to wait in-between showing pics on-screen after taking
replay_cycles = 1 # how many times to show each photo on-screen after taking

test_server = 'www.google.com'
real_path = os.path.dirname(os.path.realpath(__file__))

# Setup tumblr OAuth Client
client = pytumblr.TumblrRestClient(
    config.consumer_key,
    config.consumer_secret,
    config.oath_token,
    config.oath_secret,
);

#####################################################################
############################ GPIO CONFIG ############################
#####################################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setup(button1_pin, GPIO.IN,GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN,GPIO.PUD_UP) 
GPIO.setup(button3_pin, GPIO.IN,GPIO.PUD_UP) 
GPIO.setup(button4_pin, GPIO.IN,GPIO.PUD_UP)
GPIO.setup(button5_pin, GPIO.IN,GPIO.PUD_UP)

####################################################################
############################ FUNCTIONS #############################
####################################################################

def cleanup():
    print('Ended abruptly')
    GPIO.cleanup()
    atexit.register(cleanup)

def exitGame():
    print("Exit Program...")
    time.sleep(1)
    GPIO.cleanup()
    sys.exit()

def shutDown():
    print("Shutdown Pi...")
    time.sleep(1)
    GPIO.cleanup()
    os.system("sudo halt")
    
def is_connected():
  try:
    # see if we can resolve the host name -- tells us if there is a DNS listening
    host = socket.gethostbyname(test_server)
    # connect to the host -- tells us if the host is actually reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False    

def init_pygame():
    pygame.init()
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    pygame.display.set_caption('Photo Booth Pics')
    pygame.mouse.set_visible(False) #hide the mouse cursor	
    return pygame.display.set_mode(size, pygame.FULLSCREEN)

def show_image(image_path):
    screen = init_pygame()
    img=pygame.image.load(image_path) 
    img = pygame.transform.scale(img,(monitor_w,monitor_h))
    screen.blit(img,(offset_x,offset_y))
    pygame.display.flip()

def display_pics(jpg_group):
    # this section is an unbelievable nasty hack - for some reason Pygame
    # needs a keyboardinterrupt to initialise in some limited circs (second time running)

    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    signal(SIGALRM, alarm_handler)
    alarm(3)
    try:
        screen = init_pygame()
        alarm(0)
        
    except Alarm:
        raise KeyboardInterrupt
    for i in range(0, replay_cycles): #show pics a few times
        for i in range(1, total_pics+1):
            filename = config.file_path+jpg_group+"-0"+str(i)+".jpg"
	    show_image(filename);
	    time.sleep(replay_delay);
  

def start_photobooth():
    
############################# STEP 1 - START PROGRAM #################################
    
	show_image(real_path + "/blank.png")
	print "Get Ready"
	#show_image(real_path + "/instructions.png")
	sleep(prep_delay)

	show_image(real_path + "/blank.png")
	
	camera = picamera.PiCamera()
	pixel_width = 500 #Tumblr width GIF
	pixel_height = monitor_h * pixel_width // monitor_w
	camera.resolution = (pixel_width, pixel_height) 
	#camera.vflip = True
	camera.hflip = True
	camera.rotation = 90
	# camera.saturation = -100 # comment out this line if you want color images
	camera.start_preview()
	
	sleep(2) #warm up camera

############################ STEP 2 - TAKING PICS #################################
	
	print "Taking pics" 
	now = time.strftime("%Y-%m-%d-%H:%M:%S") #get the current date and time for the start of the filename
	try: #take the photos
		for i, filename in enumerate(camera.capture_continuous(config.file_path + now + '-' + '{counter:02d}.jpg')):
			print(filename)
			sleep(capture_delay) # pause in-between shots
			if i == total_pics-1:
				break
	finally:
		camera.stop_preview()
		camera.close()
		
########################### STEP 3 - CREATE GIF #################################
		
	print "Creating an animated gif"
	#show_image(real_path + "/uploading.png")
        print "Quieres subir tu foto a Tumblr??"
        show_image(real_path + "/choice.png")
        #sleep(6)
	answered = 0
        while(answered == 0):
            #print "While mortifero"
            if GPIO.input(button2_pin)== False:
                post_online = 1
                print "SI: " + str(post_online)
                answered = 1
            if(GPIO.input(button3_pin)== False):
                post_online = 0
                print "NO: " + str(post_online)
                answered = 1
        
	if post_online:
	    show_image(real_path + "/uploading.png")
	    sleep(6)
        else:
	    show_image(real_path + "/processing.png")
	    sleep(6)

        graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + config.file_path + now + "*.jpg " + config.file_path + now + ".gif" 
        os.system(graphicsmagick) #make the .gif

        if post_online: # turn off posting pics online in the variable declarations at the top of this document
            print "Uploading to tumblr. Please check " + config.tumblr_blog + ".tumblr.com soon."
            connected = is_connected() #check to see if you have an internet connection
            while connected: 
                try:
                    file_to_upload = config.file_path + now + ".gif"
                    client.create_photo(config.tumblr_blog, state="published", tags=["gifmaton"], data=file_to_upload)
                    break
                except ValueError:
                    print "Oops. No internect connection. Upload later."
                    try: #make a text file as a note to upload the .gif later
                        file = open(config.file_path + now + "-FILENOTUPLOADED.txt",'w')   # Trying to create a new file or open one
                        file.close()
                    except:
                        print('Something went wrong. Could not write file.')
                        sys.exit(0) # quit Python
	
########################### STEP 4 - DISPLAY GIF #################################
                        
	try:
		display_pics(now)
	except Exception, e:
		tb = sys.exc_info()[2]
		traceback.print_exception(e.__class__, e, tb)
	#pygame.quit()
	print "Done"
	
	if post_online:
		show_image(real_path + "/finished.png")
	else:
		show_image(real_path + "/finished.png")
	
	time.sleep(restart_delay)
	show_image(real_path + "/intro.png");

####################################################################
####################### MAIN PROGRAM ###############################
####################################################################

### delete files in folder on startup
##files = glob.glob(config.file_path + '*')
##for f in files:
##    os.remove(f)

print "Photo booth app running..."

show_image(real_path + "/intro.png");

while True:
    if GPIO.input(button1_pin)== False:
        time.sleep(0.2) #debounce time
        start_photobooth()
    elif GPIO.input(button4_pin) == False:
        time.sleep(0.2) #debounce time
        exitGame()
    elif GPIO.input(button5_pin) == False:
        time.sleep(0.2) #debounce time
        shutDown()
