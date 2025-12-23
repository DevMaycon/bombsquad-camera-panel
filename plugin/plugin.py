# ba_meta require api 7
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import json
import ba, _ba
import os

stream_port = 43215
api_class_name = "ApiServer"
database_archive_name = "stream_database.json"
filename = __file__.split('/')[-1].replace('.py', '')

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

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.end_headers()
        self.wfile.write(response)

class MessageHandler:
    def __init__(self, json_data: dict):
        self.received_data = json_data
        self.database = ba.app.CameraServerDB
        self.execute()
    
    def get_data(self):
        return self.database
    
    def execute(self):
        match self.received_data.get("action", ''):
            case "get_cameras":
                return self.database['cameras']
            case "add_camera":
                return self.add_camera()
            case "set_camera":
                return self.set_camera()
            case _:
                return {"error": "Ação desconhecida"}
            
    def add_camera(self):
        camera_position = _ba.get_camera_position()
        camera_target = _ba.get_camera_target()
        camera_id = "camera" + str(len(self.database["cameras"]) + 1)
        
        self.database["cameras"][camera_id] = {
            "position": camera_position,
            "target": camera_target
        }
        
        ba.app.plugins.active_plugins[f"{filename}.{api_class_name}"].save_database()
    
    def set_camera(self):
        cameras = self.database["cameras"]
        try:
            camera = cameras[self.received_data.get("camera_id")]
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
                

# ba_meta export plugin
class ApiServer(ba.Plugin):
    def run_in_bs_context(self, call, dict_args):
        _ba.pushcall(
            ba.Call(
                lambda: call(**dict_args)
            ),
            from_other_thread = True
        )

    def run(self):
        server = HTTPServer(('0.0.0.0', stream_port), Handler)
        self.run_in_bs_context(
            ba.screenmessage,
            {
                "message": f"Stream Server Running in port {stream_port}",
                "color": (0,1,0)
            }
        )
        server.serve_forever()

    def default_database(self):
        default_db = {
            "cameras_animations": {},
            "cameras": {},
            "chatmessages": {},
        }
        
        return default_db

    def load_database(self):
        if not os.path.exists(database_archive_name):
            with open(database_archive_name, 'w') as f:
                default = self.default_database()
                json.dump(default, f, indent=4)
                return default
            
        with open(database_archive_name, 'r') as f:
            database = json.load(f)
            return database
        
    def save_database(self):
        with open(database_archive_name, 'w') as f:
            json.dump(ba.app.CameraServerDB, f, indent=4)
    
    def on_app_running(self):
        ba.app.CameraServerDB = self.load_database()
        ba.app.CameraServer = Thread(target=self.run)
        ba.timer(5, ba.app.CameraServer.start)
        
    def on_app_shutdown(self):
        self.save_database()
        