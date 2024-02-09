import network
import socket
from time import sleep
import slow_servo
import machine

ssid='CoesNest'
password='4grandkids'

def webpage():
    #Template HTML
    html = f"""
            
            <!DOCTYPE html>
            <html>
            <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">

            </head>
            <body>

            <h1>Range Slider</h1>
            <p>Drag the slider to display the current value.</p>

            <div class="slidecontainer">
              <input type="range" min="0" max="180" value="90" class="slider" id="myRange">
              <p>Input Value: <span id="demo"></span></p>
              <p>Change Value: <span id="cdemo"></span></p>
            </div>

            <script>
            var slider = document.getElementById("myRange");
            var output = document.getElementById("demo");
            var coutput = document.getElementById("cdemo");
            output.innerHTML = slider.value;

            slider.oninput = function() {{
              output.innerHTML = this.value;

            }}
            slider.onchange = function() {{
              coutput.innerHTML = this.value;
              var xhr = new XMLHttpRequest();
              xhr.open("GET", "/slider?"+this.value, true);
              xhr.send();
            }}
            </script>

            </body>
            </html>
            """
    return str(html)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def serve(connection):
    #Start a web server
    servo2 = slow_servo.Slow_Servo(0)	#create servo object on pin 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print (request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request.find('slider') > -1:
            slider_val = request.split('?')[1]
            print (slider_val)
            servo2.set_angle(slider_val,1000)
        html = webpage()
        client.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(html)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()