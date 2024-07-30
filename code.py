import board
import digitalio
import wifi
import socketpool
import json
from adafruit_httpserver import Server, Request, JSONResponse

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

# Set up the web server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=True)

#returns welcome message
@server.route("/")
def base(request: Request):
    content = {"message": "Welcome to door-lock Control API"}
    return JSONResponse(request, content)

#this returns lock status by reading pin A0
@server.route("/door_status")
def lock_status(request: Request):
    status = "Locked" if lock.value else "Unlocked"
    print ("/status")
    print (lock.value)
    return JSONResponse(request, {"status": status})

#this returns door position by reading limit switch on pin A1
@server.route("/door_position")
def lock_status(request: Request):
    status = "Closed" if door_position.value else "Open"
    print ("/door_position")
    return JSONResponse(request, {"status": status})
    
#this returns door position by reading limit switch on pin A1
@server.route("/light_status")
def light_status(request: Request):
    status_light_1 = "On" if light_1.value else "Off"
    status_light_2 = "On" if light_2.value else "Off"
    status_light_3 = "On" if light_3.value else "Off"
    status_light_4 = "On" if light_4.value else "Off"
    return JSONResponse(request, {
        "light_1": status_light_1,
        "light_2": status_light_2,
        "light_3": status_light_3,
        "light_4": status_light_4
    })

#this triggers lock and returns value
@server.route("/toggle")
def toggle_led(request: Request):
    lock.value = not lock.value
    status = "Locked" if lock.value else "Unlocked"
    print ("/toggle")
    return JSONResponse(request, {"status": status})

#this triggers light and returns value
@server.route("/light1")
def toggle_light1(request: Request):
    light_1.value = not light_1.value
    status = "On" if light_1.value else "Off"
    print ("/light1")
    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light2")
def toggle_light2(request: Request):
    light_2.value = not light_2.value
    status = "On" if light_2.value else "Off"
    print ("/light2")
    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light3")
def toggle_light3(request: Request):
    light_3.value = not light_3.value
    status = "On" if light_3.value else "Off"
    print ("/light3")
    return JSONResponse(request, {"status": status})
    
#this triggers light and returns value
@server.route("/light4")
def toggle_light4(request: Request):
    light_4.value = not light_4.value
    status = "On" if lock.value else "Off"
    print ("/light4")
    return JSONResponse(request, {"status": status})

        
print(f"Starting server on http://{wifi.radio.ipv4_address}:9090")
server.serve_forever(port=9090)
