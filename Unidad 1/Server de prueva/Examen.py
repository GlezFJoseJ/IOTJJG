from http.server import BaseHTTPRequestHandler, HTTPServer
import json

cont=0
class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, content_type="text/plain"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        self._set_response()
        respuesta = ("Todo en orden :3 \nContador actual: "+ str(cont))
        self.wfile.write(respuesta.encode())
    
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        #La informacion es extraida.
        body_json = json.loads(post_data.decode())

        # Print the complete HTTP request
        print("\n----- Incoming POST Request -----")
        print(f"Requestline: {self.requestline}")
        print(f"Headers:\n{self.headers}")
        print(f"Body:\n{post_data.decode()}")
        global cont
        if(body_json['action']=='ASC'):
            cont +=int(body_json['contador'])
        elif(body_json['action']=='DES'):
            cont -=int(body_json['contador'])
        print("-------------------------------")
        
        # Respond to the client
        #Cambios para actualizar el contador en el get (Message).
        response_data = json.dumps({"message":"El contador fue actualizado", "data": post_data.decode(),"Status":"OK"})
        self._set_response("application/json")
        self.wfile.write(response_data.encode())



def run_server(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=7800):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port} Examen...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
