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
import busio
import asyncio

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

print("I2C object created")
time.sleep(1)

print("Attempting to lock I2C bus...")
if i2c.try_lock():
    print("I2C bus locked successfully")
    try:
        print("Scanning I2C bus...")
        print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])
        
        print("Attempting to initialize Seesaw...")
        i2c.unlock()
        ss = seesaw.Seesaw(i2c, addr=0x60)
        print("Seesaw initialized successfully")
    except OSError as e:
        print("Failed to initialize Seesaw:", e)
else:
    print("Failed to lock I2C bus")

print("Script completed")


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

    for section in LED_SECTIONS:
        rgb_color = hex_to_rgb('000000')
        LED_SECTIONS[section]['blinking'] = False
        LED_SECTIONS[section]["color"] = rgb_color
        LED_SECTIONS[section]["color_set"] = False
    # Turn off All 240 LEDS
    return JSONResponse(request, {"status": "Off"})

@server.route("/strip/toggle/on")
def toggle_strip(request: Request):
    num_pixels = 240 
    pixels = neopixel.NeoPixel(ss, neo_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)
    for section in LED_SECTIONS:
        rgb_color = hex_to_rgb('ffffff')
        LED_SECTIONS[section]['blinking'] = False
        LED_SECTIONS[section]["color"] = rgb_color
        LED_SECTIONS[section]["color_set"] = False
    # Toggle on all LEDs First

    return JSONResponse(request, {"status": "On"})
    
LED_SECTIONS = {
    0: {"start": 0, "end": 13, "color": None, "blinking": False},
    1: {"start": 13, "end": 26, "color": None, "blinking": False},
    2: {"start": 26, "end": 39, "color": None, "blinking": False},
    3: {"start": 39, "end": 52, "color": None, "blinking": False},
    4: {"start": 52, "end": 65, "color": None, "blinking": False},
    5: {"start": 65, "end": 78, "color": None, "blinking": False},
    6: {"start": 78, "end": 91, "color": None, "blinking": False},
    7: {"start": 91, "end": 104, "color": None, "blinking": False},
    8: {"start": 104, "end": 117, "color": None, "blinking": False},
    9: {"start": 117, "end": 130, "color": None, "blinking": False},
}

last_blink_time = 0.0
blink_state = False

pixels = neopixel.NeoPixel(ss, neo_pin, 240, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)

def is_valid_rgb_hex(value):
    values_since_regex_wont_work = set("abcdefABCDEF0123456789")
    return value is not None and len(value) == 6 and all(letter in values_since_regex_wont_work for letter in value)

def hex_to_rgb(hex_value):
    # Parse the hex string into three 2-digit hex values
    r = int(hex_value[:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:], 16)
    
    return (g, r, b)  # Return in GRB order for NeoPixel

def set_color(start, end, color):
    pixels[start:end] = [color] * (end - start)

def update_leds():
    global last_blink_time, blink_state
    current_time = time.monotonic()
    changed = False
    if current_time - last_blink_time >= 1:  # Assuming a 1-second blink interval
        last_blink_time = current_time
        blink_state = not blink_state
        for section, data in LED_SECTIONS.items():
            if data["blinking"] and data["color"] is not None:
                color = data["color"] if blink_state else (0, 0, 0)
                set_color(data['start'], data['end'], color)
                changed = True
            elif data["color"] is not None and not data.get("color_set", False):
                set_color(data['start'], data['end'], data["color"])
                data["color_set"] = True
                changed = True
    if changed:
        pixels.show()

@server.route("/strip/toggle/section", "POST")
def toggle_section(request: Request):
    section = request.form_data.get("section")
    color = str(request.form_data.get("color"))
    blink = request.form_data.get("blink")
    brightness = request.form_data.get("brightness")

    try:
        brightness = float(brightness)
        if not 0 <= brightness <= 1:
            raise ValueError
    except:
        return JSONResponse(request, {"error": "Invalid brightness value"}, status=[400, "400"])

    try:
        section = int(section)
        if section not in LED_SECTIONS:
            raise ValueError
    except:
        return JSONResponse(request, {"error": "Invalid section"}, status=[400, "400"])

    
    blink = blink.lower() == "true"

    if not is_valid_rgb_hex(color):
        return JSONResponse(request, {"error": "Invalid color format"}, status=[400, "400"])

    rgb_color = hex_to_rgb(color)
    pixels.brightness = brightness

    LED_SECTIONS[section]['blinking'] = False
    LED_SECTIONS[section]["color"] = rgb_color
    LED_SECTIONS[section]["color_set"] = False


    return JSONResponse(request, {"status": "success"})



def toggle_corner_leds(section, color, brightness, blinking_speed, blink):
    try:
        brightness = float(brightness)
    except Exception as e:
        return 400, {'error': 'Brightness value must be an Integer/Float'}
    if brightness > 1 or brightness < 0:
        return 400, {'error': 'Brightness value must be between 0.0 and 1.0'}
    try:
        blinking_speed = int(blinking_speed)
    except Exception as e:
        return 400, {'error': 'Blinking speed must be an integer'}

    if not is_valid_rgb_hex(color):
        return 400, {"error": "Invalid color format"}
    if blink.lower() == 'true':
        blink = True
    elif blink.lower() == 'false':
        blink = False
    else:
        return 400, {"error": "Blink must be True/False"}

    rgb_color = hex_to_rgb(color)
    pixels.brightness = brightness

    LED_SECTIONS[section]['blinking'] = blink
    LED_SECTIONS[section]["color"] = rgb_color
    LED_SECTIONS[section]["color_set"] = False

    if blink == False:
        rgb_color = hex_to_rgb('000000')
        LED_SECTIONS[4]["color"] = rgb_color
    
    return 200, {"status": "Success"}
    
@server.route("/strip/toggle/left/rear", "POST")
def toggle_strip_left_rear(request: Request):
    color = str(request.form_data.get("color"))
    brightness = request.form_data.get("brightness")
    blinking_speed = request.form_data.get("blinking_speed")
    blink = request.form_data.get('blink')
    
    status_code, response_data = toggle_corner_leds(4, color, brightness, blinking_speed, blink)
    return JSONResponse(request, response_data, status=[status_code, str(status_code)])

    


@server.route("/strip/toggle/left/front", 'POST')
def toggle_strip_left_front(request: Request):
    color = str(request.form_data.get("color"))
    brightness = request.form_data.get("brightness")
    blinking_speed = request.form_data.get("blinking_speed")
    blink = request.form_data.get('blink')
    
    status_code, response_data = toggle_corner_leds(0, color, brightness, blinking_speed, blink)
    return JSONResponse(request, response_data, status=[status_code, str(status_code)])
    


@server.route("/strip/toggle/right/rear", 'POST')
def toggle_strip_right_rear(request: Request):
    color = str(request.form_data.get("color"))
    brightness = request.form_data.get("brightness")
    blinking_speed = request.form_data.get("blinking_speed")
    blink = request.form_data.get('blink')
    
    status_code, response_data = toggle_corner_leds(5, color, brightness, blinking_speed, blink)
    return JSONResponse(request, response_data, status=[status_code, str(status_code)])
    

@server.route("/strip/toggle/right/front", 'POST')
def toggle_strip_right_front(request: Request):
    color = str(request.form_data.get("color"))
    brightness = request.form_data.get("brightness")
    blinking_speed = request.form_data.get("blinking_speed")
    blink = request.form_data.get('blink')
    
    status_code, response_data = toggle_corner_leds(9, color, brightness, blinking_speed, blink)
    return JSONResponse(request, response_data, status=[status_code, str(status_code)])
    


'''
Try/Catch are used to catch server errors without shutting down the entire server in the event of an issue
'''
try:
    print("Starting server on port 9999...")
    server.start(port=9999)
    last_update_time = time.monotonic()
    while True:
        server.poll()
        current_time = time.monotonic()
        if current_time - last_update_time >= 0.05:  # Update LEDs every 50ms
            update_leds()
            last_update_time = current_time
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    server.stop()
    print("Server stopped.")
