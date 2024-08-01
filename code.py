import board
import digitalio
import analogio
import wifi
import socketpool
import json
import time
from adafruit_httpserver import Server, Request, JSONResponse, POST
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, neopixel
import re

#setup stemma-qt


# Define the I2C bus
i2c = board.STEMMA_I2C()

# Define the expected I2C address of your STEMMA board
STEMMA_ADDRESS = 0x60  # Replace with the correct address if different

def scan_for_device(address):
    while True:
        try:
            i2c.try_lock()
            devices = i2c.scan()
            i2c.unlock()
            if address in devices:
                print(f"Device found at address 0x{address:02X}")
                return True
            else:
                print("Device not found. Retrying...")
                time.sleep(1)  # Wait for 1 second before retrying
        except Exception as e:
            print(f"Error during scan: {e}")
            time.sleep(1)  # Wait for 1 second before retrying

# Scan for the STEMMA board
print("Scanning for STEMMA board...")
if scan_for_device(STEMMA_ADDRESS):
    print("STEMMA board detected. Proceeding with initialization...")
    # Your initialization code here, e.g.:
    # ss = seesaw.Seesaw(i2c, addr=STEMMA_ADDRESS)
else:
    print("Failed to detect STEMMA board")
i2c = board.STEMMA_I2C()

ss = seesaw.Seesaw(i2c, addr=0x60)
neo_pin = 15

# Set up lock
lock = digitalio.DigitalInOut(board.D13) #LED to test onboard LED
lock.direction = digitalio.Direction.OUTPUT

#setup light
light_1 = digitalio.DigitalInOut(board.A1)
light_1.direction = digitalio.Direction.OUTPUT

#setup light
light_2 = digitalio.DigitalInOut(board.D32)
light_2.direction = digitalio.Direction.OUTPUT

#setup light
light_3 = digitalio.DigitalInOut(board.D33)#D13
light_3.direction = digitalio.Direction.OUTPUT

#setup light
light_4 = digitalio.DigitalInOut(board.D27)
light_4.direction = digitalio.Direction.OUTPUT

door_position = analogio.AnalogIn(board.A3)
# door_position.direction = digitalio.Direction.INPUT

WIFI_SSID = 'BUBS-2'
WIFI_PASSWORD = '12345678'

LED_SECTION_MULTIPLIER = 13;
MAX_LED_SECTIONS = 10;

def connect_to_wifi():
    print("Connecting...")
    pixels = neopixel.NeoPixel(ss, neo_pin, 240, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)
    pixels.fill(0x00ff00)
    pixels.show()
    # wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wifi.radio.ipv4_address:
        print('Attempting Reconnect...')
        try:
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        except Exception as e:
            print(e)
        time.sleep(2)
    time.sleep(2)
    pixels.fill(0x000000)
    pixels.show()    

    print(wifi.radio.ipv4_address)
    return True


connect_to_wifi()

# Set up the web server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=True)

#returns welcome message
@server.route("/")
def base(request: Request):
    content = {"message": "Welcome to door-lock Control API"}
    return JSONResponse(request, content)

#this returns lock status by reading pin A0
@server.route("/door/status")
def lock_status(request: Request):
    status = "Locked" if lock.value else "Unlocked"


    return JSONResponse(request, {"status": status})

#this returns door position by reading limit switch on pin A1
@server.route("/door/position")
def lock_status(request: Request):
    
    print((door_position.value * 3.3) / 65536)
    status = "Closed" if ((door_position.value * 3.3) / 65536) > 2.5 else "Open"

    return JSONResponse(request, {"status": status})
    
#this returns door position by reading limit switch on pin A1
@server.route("/light/status")
def light_status(request: Request):
    status_light_1 = "On" if light_1.value else "Off"
    status_light_2 = "On" if light_2.value else "Off"
    status_light_3 = "On" if light_3.value else "Off"
    status_light_4 = "On" if light_4.value else "Off"
    return JSONResponse(request, {
        "rear": status_light_1,
        "front": status_light_2,
        "right": status_light_3,
        "left": status_light_4
    })

#this triggers lock and returns value
@server.route("/door/toggle")
def toggle_led(request: Request):
    lock.value = not lock.value
    status = "Locked" if lock.value else "Unlocked"

    return JSONResponse(request, {"status": status})

#this triggers light and returns value
@server.route("/light/toggle/on")
def toggle_light1(request: Request):
    light_1.value = True
    light_2.value = True
    light_3.value = True
    light_4.value = True
    status = "On"

    return JSONResponse(request, {"status": status})

@server.route("/light/toggle/off")
def toggle_light1(request: Request):
    light_1.value = False
    light_2.value = False
    light_3.value = False
    light_4.value = False
    status = "Off"

    return JSONResponse(request, {"status": status})
    

#this triggers light and returns value
@server.route("/light/toggle/rear")
def toggle_light1(request: Request):
    light_1.value = not light_1.value
    status = "On" if light_1.value else "Off"

    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light/toggle/front")
def toggle_light2(request: Request):
    light_2.value = not light_2.value
    status = "On" if light_2.value else "Off"

    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light/toggle/right")
def toggle_light3(request: Request):
    light_3.value = not light_3.value
    status = "On" if light_3.value else "Off"
   
    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light/toggle/left")
def toggle_light4(request: Request):
    light_4.value = not light_4.value
    status = "On" if lock.value else "Off"

    return JSONResponse(request, {"status": status})

@server.route("/strip/toggle/off")
def toggle_strip_off(request: Request):
    num_pixels = 240 
    pixels = neopixel.NeoPixel(ss, neo_pin, num_pixels, brightness=0.0, auto_write=False, pixel_order=neopixel.RGBW)
    pixels.fill(0x000000)
    pixels.show()
    # Turn off All 240 LEDS
    return JSONResponse(request, {"status": "Off"})

@server.route("/strip/toggle/on")
def toggle_strip(request: Request):
    num_pixels = 240 
    pixels = neopixel.NeoPixel(ss, neo_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)
    pixels.fill(0xffffff)
    pixels.show()
    # Toggle on all LEDs First

    return JSONResponse(request, {"status": "On"})
    
@server.route("/strip/toggle/section", POST)
def toggle_section(request: Request):
    def is_valid_rgb_hex(value):
        # Define the pattern for a 6-digit hexadecimal color code
        values_since_regex_wont_work = set('abcdefABCDEF0123456789')
    
        # Check if the input is None or not exactly 6 characters long
        if value is None or len(value) != 6:
            return False
        
        # Check each character in the input string
        for letter in value:
            if letter not in values_since_regex_wont_work:
                return False
        
        return True

    section = request.form_data.get('section')
    color = str(request.form_data.get('color'))
    blink = request.form_data.get('blink')
    brightness = request.form_data.get('brightness')
    print(section, color, blink, brightness)
    try:
        brightness = float(brightness)
    except Exception as e:
        return JSONResponse(request, {"error": "Brightness is not a valid float"},  status=[400, '400'])
    if brightness > 1.0 or brightness < 0.0:
        return JSONRespnse(request, {"error": "Brightness value must be between 0.0 and 1.0"},  status=[400, '400'])
    try:
        section = int(section)
    except Exception as e:
         return JSONResponse(request, {"error": "Section is not a valid integer"},  status=[400, '400'])
    if blink == 'True' or blink == 'true':
        blink = True
    elif blink == 'False' or blink == 'false':
        blink = False
    else:
        return JSONResponse(request, {"error": "Blink is not a valid bool (True/False)"},  status=[400, '400'])
    
    if blink:
        blinking_speed = request.form_data.get('blinking_speed')
        try:
            blinking_speed = int(blinking_speed)
        except Exception as e:
             return JSONResponse(request, {"error": "Blinking speed is not a valid integer for seconds"},  status=[400, '400'])
    if section > 9 or section < 0:
        return JSONResponse(request, {"error": "Section does not exist"},  status=[400, '400'])
        
    result = is_valid_rgb_hex(color)
    print(result)
    if result == False:
        return JSONResponse(request, {"error": "Not a valid Hexcode colour (RRGGBB)"}, status=[400, '400'])
    color = '0x'+color

    pixels = neopixel.NeoPixel(ss, neo_pin, brightness=brightness, auto_write=False, pixel_order=neopixel.RGBW)

    starting_pixel = (section+1)*LED_SECTION_MULTIPLIER
    ending_pixel = starting_pixel+13
    for x in range(starting_pixel, ending_pixel):
        pixels[x] = color
    pixels.show()

    
    
        
print(f"Starting server on http://{wifi.radio.ipv4_address}:9999")
server.serve_forever(port=9999)
