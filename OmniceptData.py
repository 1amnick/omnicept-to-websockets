import asyncio
import subprocess
import websockets
from time import sleep

connected_clients = []
running = False
hr = 0
hrv = 0.0000
cl = 0.000000

async def send_data(process):

    global hr, hrv, cl
    for line in process.stdout:
        sleep(0.25)
        # Read a line of output from the stdout stream
        line = process.stdout.readline()
        # If the line is empty, the stream has closed
        if not line:
            break

    # Print the line
        print(line)
        if line.startswith(b'Heart Rate: ('):
            s = line.decode('ascii')
            hr = int(s[s.find('(')+1:s.find(')')])

        if line.startswith(b'Heart Rate Variability: ('):
            s = line.decode('ascii')
            hrv = s[s.find('(sdnn ')+6:s.find(',')]

        if line.startswith(b'CognitiveLoad: (Prediction: '):
            s = line.decode('ascii')
            cl = s[s.find('Prediction: ')+12:s.find(',')]
        print('sending: ' + str(hr) + ',' + str(hrv) + ',' + str(cl))
        for client in connected_clients:
            await client.send(str(hr) + ',' + str(hrv) + ',' + str(cl))
            await asyncio.sleep(0.1)


def program_loader(process):
    print('loading program with sockets')
    while True:
        # Read a line of output from the stdout stream
        line = process.stdout.readline()
         # If the line is empty, the stream has closed
        if not line:
            print('nothing')
            break
        # Check for a prompt
        if line.startswith(b'[2] Request Latest'):
            # Write data to the stdin stream
            process.stdin.write(b'1\n')
            print('writing a 1 with a newline')

            # Flush the stdin stream to ensure the data is sent
            process.stdin.flush()
            break
    while True:
    # Read a line of output from the stdout stream
        line = process.stdout.readline()
    # If the line is empty, the stream has closed
        if not line:
            print('nothing')
            break

    # Check for a prompt
        if line.startswith(b'    (Log file will rollover into a new file when 2000000 characters is reached. Stops logging at 50 files)\r\n'):
            # Write data to the stdin stream
            process.stdin.write(b'\n')
            print('writing a nothing with a newline')

            # Flush the stdin stream to ensure the data is sent
            process.stdin.flush()
            break
    while True:
        # Read a line of output from the stdout stream
        line = process.stdout.readline()
            # If the line is empty, the stream has closed
        if not line:
            print('nothing')
            break
        # Check for a prompt
        if line.startswith(b'    \'s\' for subscription result list'):
            # Write data to the stdin stream
            process.stdin.write(b'h hrv c\n')
            # Flush the stdin stream to ensure the data is sent
            process.stdin.flush()
            break

async def websocket_handler(websocket):
    print('New Connection')
    global running, connected_clients, process
    try:
        if not running:
          # *********************************************************************************************************** replace client id ******************** and access key too *******************************
            process = subprocess.Popen(['C:\\Program Files\\HP\\HP Omnicept\\bin\\OmniceptConsole.exe',  '--clientId', 'ClientID goes here', '--accessKey', 'access key goes here', '--licenseModel', '4', 'h', 'hrv', 'c'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            program_loader(process)
            running = True
            connected_clients.append(websocket)
            await send_data(process)
        else:
            connected_clients.append(websocket)
            await send_data(process)
    except websockets.exceptions.ConnectionClosed:
        connected_clients.remove(websocket)
        print(f"Connection with {websocket.remote_address} closed.")



async def main():
    print('main')
    # Start a WebSocket server
    async with websockets.serve(websocket_handler, 'localhost', 8675):
        await asyncio.Future()
    print('after server')
    
    # Run the server indefinitely
   # await server.wait_closed()

    running = False
    print('done')

# Run the main function
print('start script')
connected_clients = []
running = False
print('init vars')
asyncio.run(main())
