# -*- coding: utf-8 -*-
#!/usr/bin/python3
##################################
# MLX90640 Thermal Camera w Raspberry Pi
##################################
import time,board,busio, traceback
import numpy as np
import adafruit_mlx90640
import datetime as dt
import cv2
import logging
import cmapy
from scipy import ndimage
import math

# Set up logging
logging.basicConfig(filename='pithermcam.log',filemode='a',
                    format='%(asctime)s %(levelname)-8s [%(filename)s:%(name)s:%(lineno)d] %(message)s',
                    level=logging.WARNING,datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

IMAGE_CENTER_X = 400
IMAGE_CENTER_Y = 300 
THERM_CENTER_X = 16
THERM_CENTER_Y = 12

r_earth = 6378000

class pithermalcam:
    # See https://gitlab.com/cvejarano-oss/cmapy/-/blob/master/docs/colorize_all_examples.md to for options that can be put in this list
    _colormap_list=['jet','bwr','seismic','coolwarm','PiYG_r','tab10','tab20','gnuplot2','brg']
    _interpolation_list =[cv2.INTER_NEAREST,cv2.INTER_LINEAR,cv2.INTER_AREA,cv2.INTER_CUBIC,cv2.INTER_LANCZOS4,5,6]
    _interpolation_list_name = ['Nearest','Inter Linear','Inter Area','Inter Cubic','Inter Lanczos4','Pure Scipy', 'Scipy/CV2 Mixed']
    _current_frame_processed=False  # Tracks if the current processed image matches the current raw image
    i2c=None
    mlx=None
    _temp_min=None
    _temp_max=None
    _raw_image=None
    _sized_raw=None
    _image=None
    _temp_image=None
    _file_saved_notification_start=None
    _displaying_onscreen=False
    _exit_requested=False
    _n = 0

    def __init__(self,use_f:bool = False, filter_image:bool = False, image_width:int=1200, 
                image_height:int=900, output_folder:str = '/home/pi/pithermalcam/saved_snapshots/'):
        self.use_f=use_f
        self.filter_image=filter_image
        self.image_width=image_width
        self.image_height=image_height
        self.output_folder=output_folder
        self._colormap_index = 0
        self._interpolation_index = 3
        self._setup_therm_cam()
        self._t0 = time.time()
        self.update_image_frame()

    def __del__(self):
        logger.debug("ThermalCam Object deleted.")

    def _setup_therm_cam(self):
        """Initialize the thermal camera"""
        # Setup camera
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)  # setup I2C
        self.mlx = adafruit_mlx90640.MLX90640(self.i2c)  # begin MLX90640 with I2C comm
        self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ  # set refresh rate
        time.sleep(0.1)

    def _c_to_f(self,temp:float):
        """ Convert temperature from C to F """
        return ((9.0/5.0)*temp+32.0)

    def get_mean_temp(self):
        """
        Get mean temp of entire field of view. Return both temp C and temp F.
        """
        frame = np.zeros((24*32,))  # setup array for storing all 768 temperatures
        while True:
            try:
                self.mlx.getFrame(frame)  # read MLX temperatures into frame var
                break
            except ValueError:
                continue  # if error, just read again

        temp_c = np.mean(frame)
        temp_f=self._c_to_f(temp_c)
        return temp_c, temp_f

    def _pull_raw_image(self):
        """Get one pull of the raw image data, converting temp units if necessary"""
        # Get image
        self._raw_image = np.zeros((24*32,))
        try:
            self.mlx.getFrame(self._raw_image)  # read mlx90640
            self._temp_min = np.min(self._raw_image)
            self._temp_max = np.max(self._raw_image)
            self._temp_image = np.uint8(np.copy(self._raw_image))
            self._temp_image.shape = (24, 32)
            self._raw_image=self._temps_to_rescaled_uints(self._raw_image,self._temp_min,self._temp_max)
            self._sized_raw = cv2.resize(self._raw_image, (800,600), interpolation=cv2.INTER_CUBIC)
            self._sized_raw = self._uints_to_rescaled_temps(self._sized_raw, self._temp_max, self._temp_min)
            self._current_frame_processed=False  # Note that the newly updated raw frame has not been processed
        except ValueError:
            print("Math error; continuing...")
            self._raw_image = np.zeros((24*32,))  # If something went wrong, make sure the raw image has numbers
            logger.info(traceback.format_exc())
        except OSError:
            print("IO Error; continuing...")
            self._raw_image = np.zeros((24*32,))  # If something went wrong, make sure the raw image has numbers
            logger.info(traceback.format_exc())

    def _process_raw_image(self):
        """Process the raw temp data to a colored image. Filter if necessary"""
        # Image processing
        # Can't apply colormap before ndimage, so reversed in first two options, even though it seems slower
        if self._interpolation_index==5:  # Scale via scipy only - slowest but seems higher quality
            self._image = ndimage.zoom(self._raw_image,25)  # interpolate with scipy
            self._image = cv2.applyColorMap(self._image, cmapy.cmap(self._colormap_list[self._colormap_index]))
        elif self._interpolation_index==6:  # Scale partially via scipy and partially via cv2 - mix of speed and quality
            self._image = ndimage.zoom(self._raw_image,10)  # interpolate with scipy
            self._image = cv2.applyColorMap(self._image, cmapy.cmap(self._colormap_list[self._colormap_index]))
            self._image = cv2.resize(self._image, (800,600), interpolation=cv2.INTER_CUBIC)
        else:
            self._image = cv2.applyColorMap(self._raw_image, cmapy.cmap(self._colormap_list[self._colormap_index]))
            self._image = cv2.resize(self._image, (800,600), interpolation=self._interpolation_list[self._interpolation_index])
        self._image = cv2.flip(self._image, 1)
        if self.filter_image:
            self._image=cv2.bilateralFilter(self._image,15,80,80)

    def _add_image_text(self):
        """Set image text content"""
        if self.use_f:
            temp_min=self._c_to_f(self._temp_min)
            temp_max=self._c_to_f(self._temp_max)
            text = f'Tmin={temp_min:+.1f}F - Tmax={temp_max:+.1f}F - FPS={1/(time.time() - self._t0):.1f} - Interpolation: {self._interpolation_list_name[self._interpolation_index]} - Colormap: {self._colormap_list[self._colormap_index]} - Filtered: {self.filter_image}'
        else:
            text = f'Tmin={self._temp_min:+.1f}C - Tmax={self._temp_max:+.1f}C - FPS={1/(time.time() - self._t0):.1f} - Interpolation: {self._interpolation_list_name[self._interpolation_index]} - Colormap: {self._colormap_list[self._colormap_index]} - Filtered: {self.filter_image}'
        cv2.putText(self._image, text, (30, 18), cv2.FONT_HERSHEY_SIMPLEX, .4, (255, 255, 255), 1)
        self._t0 = time.time()  # Update time to this pull

        # For a brief period after saving, display saved notification
        if self._file_saved_notification_start is not None and (time.monotonic()-self._file_saved_notification_start)<1:
            cv2.putText(self._image, 'Snapshot Saved!', (300,300),cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)

    def add_customized_text(self,text):
        """Add custom text to the center of the image, used mostly to notify user that server is off."""
        cv2.putText(self._image, text, (300,300),cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
        time.sleep(0.1)

    def _show_processed_image(self):
        """Resize image window and display it"""
        cv2.namedWindow('Thermal Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Thermal Image', self.image_width,self.image_height)
        cv2.imshow('Thermal Image', self._image)

    def filter_thermalobj(self, pwh, pht, latit, longi):
        imghsv = cv2.cvtColor(self._image, cv2.COLOR_BGR2HSV)
        lower_hot = np.array([0, 60, 60])
        upper_hot = np.array([32, 255, 255])
        lower_dark_red = np.array([165, 60, 60])
        upper_dark_red = np.array([ 180, 255, 255])
        thermal_mask = cv2.bitwise_or(cv2.inRange(imghsv, lower_hot, upper_hot), cv2.inRange(imghsv, lower_dark_red, upper_dark_red))
        contours, _ = cv2.findContours(thermal_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        im = np.copy(self._image)
        contour_img = np.zeros((600,800, 3), np.uint8)
        contour_img[:,:] = (245, 233, 175)
        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(im, (x,y), (x+w, y+h), (0, 255,0),2)
                M = cv2.moments(cnt)
                center_x = int(M['m10']/M['m00'])
                center_y = int(M['m01']/M['m00'])
                temp_center = self.center_max_temp_at_pt(center_y, center_x, x,y,w,h)
                center_dist_y = abs(center_y - 300)*pht
                center_dist_x = abs(center_x -400)*pwh
                new_lat = latit + (center_dist_y / r_earth)*(180/math.pi)
                new_lon = longi + (center_dist_x / r_earth)*(180/math.pi)/math.cos(latit*math.pi/180)
                cv2.putText(im, temp_center+"C at lat:"+str(new_lat)+" lon:"+str(new_lon), (center_x, center_y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                cv2.putText(im, self.temp_at_pt(y, x)+"C", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                cv2.putText(im, self.temp_at_pt(y, x+w)+"C", (x+w, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                cv2.putText(im, self.temp_at_pt(y+h, x)+"C", (x,y+h), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                cv2.putText(im, self.temp_at_pt(y+h, x+w)+"C", (x+w, y+h), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                #cv2.drawContours(contour_img, cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True), -1, (0,0,255), -1)
                cv2.drawContours(contour_img, cnt, -1, (0,0,255), 10)
                cv2.putText(contour_img, temp_center+"C", (center_x, center_y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                cv2.putText(contour_img, "lat:"+str(new_lat), (center_x, center_y+15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                cv2.putText(contour_img, "lon:"+str(new_lon), (center_x, center_y+30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
        cv2.namedWindow('Thermal Image bounded', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Thermal Image bounded', self.image_width,self.image_height)
        cv2.imwrite("./photos/"+str(self._n)+str(latit)+"-"+str(longi)+"-contour.jpg", contour_img)
        cv2.imwrite("./photos/"+str(self._n)+str(latit)+"-"+str(longi)+"-thermalbound.jpg", im)
        cv2.imwrite("./photos/"+str(self._n)+str(latit)+"-"+str(longi)+"-thermalraw.jpg", self._image)
        #self._n = self._n + 1
        cv2.imshow('Thermal Image bounded', im)
        cv2.imshow('Contours', contour_img)

    def temp_at_pt(self, y, x):
        if y == 600:
            y = 599
        y_sm = math.floor(y / 25)
        if x == 800:
            x = 799
        x_sm = math.floor(x / 25)
        #return str(self._sized_raw[y][x])
        return str(self._temp_image[y_sm][31-x_sm])
    
    def center_max_temp_at_pt(self, y, x, start_x, start_y, delta_x, delta_y):
        if y == 600:
            y = 599
        y_sm = math.floor(y / 25)
        #print(start_y)
        #print(delta_y)
        start_y = math.floor(start_y/25)
        delta_y = math.floor(delta_y/25)
        #print(start_y)
        #print(delta_y)
        if x == 800:
            x = 799
        x_sm = math.floor(x / 25)
        #print(start_x)
        #print(delta_x)
        start_x = math.floor(start_x/25)
        delta_x = math.floor(delta_x/25)
        #print(self._temp_image)
        #print(start_x)
        #print(delta_x)
        #return str(self._sized_raw[y][x])
        max = self._temp_image[y_sm][31-x_sm]
        """for val2 in range(-1, delta_y+1):
            for val1 in range(-1, delta_x+1):
                if start_x+val1 < 0:
                    val1=0
                if start_y+val2 < 0:
                    val2=0
                if start_x+val1 > 23:
                    val1-=1
                if start_y+val2 > 23:
                    val2-=1
                #print(self._temp_image[start_y+val2][32-start_x-val1])
                #print(f"row:{start_y+val2}")
                #print(f"col:{32-start_x-val1}")
                if self._temp_image[start_y+val2][32-start_x-val1] > max:
                    max = self._temp_image[start_y+val2][32-start_x-val1]"""

        return str(max)

    def _set_click_keyboard_events(self):
        """Add click and keyboard actions to image"""
        # Set mouse click events
        cv2.setMouseCallback('Thermal Image',self._mouse_click)

        # Set keyboard events
        # if 's' is pressed - saving of picture
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):  # If s is chosen, save an image to filec
            self.save_image()
        elif key == ord("c"):  # If c is chosen cycle the colormap used
            self.change_colormap()
        elif key == ord("x"):  # If c is chosen cycle the colormap used
            self.change_colormap(forward=False)
        elif key == ord("f"):  # If f is chosen cycle the image filtering
            self.filter_image = not self.filter_image
        elif key == ord("t"):  # If t is chosen cycle the units used for Temperature
            self.use_f = not self.use_f
        elif key == ord("u"):  # If t is chosen cycle the units used for temperature
            self.change_interpolation()
        elif key == ord("i"):  # If i is chosen cycle interpolation algorithm
            self.change_interpolation(forward=False)
        elif key==27:  # Exit nicely if escape key is used
            cv2.destroyAllWindows()
            self._displaying_onscreen = False
            print("Code Stopped by User")
            self._exit_requested=True

    def _mouse_click(self,event,x,y,flags,param):
        """Used to save an image on double-click"""
        global mouseX,mouseY
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.save_image()

    def _print_shortcuts_keys(self):
        """Print out a summary of the shortcut keys available during video runtime."""
        print("The following keys are shortcuts for controlling the video during a run:")
        print("Esc - Exit and Close.")
        print("S - Save a Snapshot of the Current Frame")
        print("X - Cycle the Colormap Backwards")
        print("C - Cycle the Colormap forward")
        print("F - Toggle Filtering On/Off")
        print("T - Toggle Temperature Units between C/F")
        print("U - Go back to the previous Interpolation Algorithm")
        print("I - Change the Interpolation Algorithm Used")
        print("Double-click with Mouse - Save a Snapshot of the Current Frame")

    def display_next_frame_onscreen(self, pw, ph, lat, lon):
        """Display the camera live to the display"""
        # Display shortcuts reminder to user on first run
        if not self._displaying_onscreen:
            self._print_shortcuts_keys()
            self._displaying_onscreen = True
        self.update_image_frame()
        self._show_processed_image()
        self.filter_thermalobj(pwh=pw, pht=ph, latit=lat,longi=lon)
        self._set_click_keyboard_events()

    def change_colormap(self, forward:bool = True):
        """Cycle colormap. Forward by default, backwards if param set to false."""
        if forward:
            self._colormap_index+=1
            if self._colormap_index==len(self._colormap_list):
                self._colormap_index=0
        else:
            self._colormap_index-=1
            if self._colormap_index<0:
                self._colormap_index=len(self._colormap_list)-1

    def change_interpolation(self, forward:bool = True):
        """Cycle interpolation. Forward by default, backwards if param set to false."""
        if forward:
            self._interpolation_index+=1
            if self._interpolation_index==len(self._interpolation_list):
                self._interpolation_index=0
        else:
            self._interpolation_index-=1
            if self._interpolation_index<0:
                self._interpolation_index=len(self._interpolation_list)-1

    def update_image_frame(self):
        """Pull raw temperature data, process it to an image, and update image text"""
        self._pull_raw_image()
        self._process_raw_image()
        self._add_image_text()
        self._current_frame_processed=True
        return self._image

    def update_raw_image_only(self):
        """Update only raw data without any further image processing or text updating"""
        self._pull_raw_image

    def get_current_raw_image_frame(self):
        """Return the current raw image"""
        self._pull_raw_image
        return self._raw_image

    def get_current_image_frame(self):
        """Get the processed image"""
        # If the current raw image hasn't been procssed, process and return it
        if not self._current_frame_processed:
            self._process_raw_image()
            self._add_image_text()
            self._current_frame_processed=True
        return self._image

    def save_image(self):
        """Save the current frame as a snapshot to the output folder."""
        fname = self.output_folder + 'pic_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
        cv2.imwrite(fname, self._image)
        self._file_saved_notification_start = time.monotonic()
        print('Thermal Image ', fname)

    def _temps_to_rescaled_uints(self,f,Tmin,Tmax):
        """Function to convert temperatures to pixels on image"""
        f=np.nan_to_num(f)
        norm = np.uint8((f - Tmin)*255/(Tmax-Tmin))
        norm.shape = (24,32)
        return norm
    
    def _uints_to_rescaled_temps(self, val, Tmax, Tmin):
        """Function to convert temperatures to pixels on image"""
        norm = np.uint8(val*((Tmax-Tmin)/255) + Tmin)
        norm.shape = (600,800)
        return norm

    def display_camera_onscreen(self):
        # Loop to display frames unless/until user requests exit
        while not self._exit_requested:
            try:
                self.display_next_frame_onscreen(0 ,0 ,0,0)
            # Catch a common I2C Error. If you get this too often consider checking/adjusting your I2C Baudrate
            except RuntimeError as e:
                if e.message == 'Too many retries':
                    print("Too many retries error caught, potential I2C baudrate issue: continuing...")
                    continue
                raise

if __name__ == "__main__":
    # If class is run as main, read ini and set up a live feed displayed to screen
    output_folder = '/home/pi/PiThermalCam/saved_snapshots/'

    thermcam = pithermalcam(output_folder=output_folder)  # Instantiate class
    thermcam.display_camera_onscreen()
