# ba_meta require api 7
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import json
import ba, _ba
import os

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
    def do_GET(self):
        path = self.path.strip('/')
        if path == '':
            path = 'index.html'

        if not os.path.isfile(path):
            self.send_response(404)
            self._cors()
            self.end_headers()
            self.wfile.write(b'404')
            return

        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'JSON invalido')
            return
        
        message_handler = MessageHandler(data).get_data()
        response = json.dumps(message_handler).encode() 
        print(message_handler, response)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.end_headers()
        self.wfile.write(response)

class MessageHandler:
    def __init__(self, json_data: dict):
        self.json_data = json_data
        self.execute()
    
    def get_data(self):
        return self.json_data
    
    def execute(self):
        match self.json_data.get("action", ''):
            case "get_cameras":
                return self.get_cameras()
            
            case "set_camera":
                return self.set_camera()
            
            case _:
                return {"error": "Ação desconhecida"}
    
    def set_camera(self):
        cameras = self.get_cameras()
        try:
            camera = None
            camera_id = self.json_data.get("camera_id", '')
            for camera_i in cameras:
                if camera_i.get(camera_id, ''):
                    camera = camera_i.get(camera_id, '')
                    
            if not camera:
                _ba.set_camera_manual(False)
                raise Exception("Camera ID not found")
            
                
            position = camera.get("position", (0,0,0))
            target = camera.get("target", (0,0,0))
            
            _ba.set_camera_manual(True)
            _ba.set_camera_position(*position)
            _ba.set_camera_target(*target)
        except Exception as e:
            print(e)
                
    def get_cameras(self):
        self.json_data["Cameras"] = ba.app.CameraServerDB
        return self.json_data["Cameras"]


def run_in_bs_context(call, dict_args):
    _ba.pushcall(
        ba.Call(
            lambda: call(**dict_args)
        ),
        from_other_thread = True
    )

def run():
    server = HTTPServer(('0.0.0.0', 43215), Handler)
    run_in_bs_context(
        ba.screenmessage,
        {
            "message": "Camera Server Running perfectly in port 43215",
            "color": (0,1,0)
        }
    )

    print('Servidor rodando na porta 43215')
    server.serve_forever()

def load_database():
    database = [
        {'camera1':  {'target': (0, 0, 0), 'position': (-10, 8, 10)}},
        {'camera2':  {'target': (0, 0, 0), 'position': (10, 8, 10)}},
        {'camera3':  {'target': (0, 0, 0), 'position': (-10, 8, -10)}},
        {'camera4':  {'target': (0, 0, 0), 'position': (10, 8, -10)}},
        {'camera5':  {'target': (0, 0, 0), 'position': (-2, 15, 0)}},   # topo
        {'camera6':  {'target': (0, 0, 0), 'position': (0, 20, 20)}},   # frente
        {'camera7':  {'target': (0, 0, 0), 'position': (20, 5, 0)}},   # direita
        {'camera8':  {'target': (0, 0, 0), 'position': (-20, 5, 0)}},  # esquerda
        {'camera9':  {'target': (0, 0, 0), 'position': (0, 5, -20)}},  # trás
    ]
    return database

# ba_meta export plugin
class ApiServer(ba.Plugin):
    def on_app_running(self):
        ba.app.CameraServerDB = load_database()
        ba.app.CameraServer = Thread(target=run)
        ba.timer(5, ba.app.CameraServer.start)
