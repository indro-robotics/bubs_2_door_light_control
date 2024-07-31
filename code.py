import board
import digitalio
import wifi
import socketpool
import json
import time
from adafruit_httpserver import Server, Request, JSONResponse, POST
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, neopixel

#setup stemma-qt
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
light_2 = digitalio.DigitalInOut(board.A5)
light_2.direction = digitalio.Direction.OUTPUT

#setup light
light_3 = digitalio.DigitalInOut(board.D33)#D13
light_3.direction = digitalio.Direction.OUTPUT

#setup light
light_4 = digitalio.DigitalInOut(board.D27)
light_4.direction = digitalio.Direction.OUTPUT

door_position = digitalio.DigitalInOut(board.A2)
door_position.direction = digitalio.Direction.INPUT

WIFI_SSID = 'BUBS-2'
WIFI_PASSWORD = '12345678'

def connect_to_wifi():
    print("Connecting...")
    #wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wifi.radio.ipv4_address:
        print('Attempting Reconnect...')
        try:
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        except Exception as e:
            print(e)
        time.sleep(2)

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
    status = "Closed" if door_position.value else "Open"

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
def toggle_strip(request: Requst):
    num_pixels = 240 
    pixels = neopixel.NeoPixel(ss, neo_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)
    pixels.fill(0xffffff)
    pixels.show()
    # Toggle on all LEDs First

    return JSONResponse(request, {"status": "On"})
    
    
        
print(f"Starting server on http://{wifi.radio.ipv4_address}:9090")
server.serve_forever(port=9090)
