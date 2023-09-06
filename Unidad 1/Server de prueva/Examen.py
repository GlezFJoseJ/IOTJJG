from http.server import BaseHTTPRequestHandler, HTTPServer
import json

cont=0
cambios=0
class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, content_type="text/plain"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    #Metodo para estraer la informacion si es que se requiere
    def do_GET(self):
        self._set_response()
        #Se crea una variable para despues mandar la informacion.
                    #Texto extra que agrege   | Informacion del contador en string      Convercion de datos int-String
        respuesta = ("Todo en orden :3 \n       Contador actual: "+                     str(cont))
        #La informacion de la variable se pasa a "imprimir" 
        self.wfile.write(respuesta.encode())
    
    #Metodo para cuando se recive informacion en el servidor
    def do_POST(self):
        #Proceso inicial que permite la extracion de la informacion recivida.
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        #La informacion es extraida.
        body_json = json.loads(post_data.decode())

        # Print the complete HTTP request
        #Al recivir informacion el servidor manda lo siguiente
        print("\n----- Incoming POST Request -----")
        print(f"Requestline: {self.requestline}")
        print(f"Headers:\n{self.headers}")
        print(f"Body:\n{post_data.decode()}")
        global cambios
        #Variable para el uso del contador que se modifica segun lo que se mande.
        global cont
        #If que ve lo que se mando y dependiendo si es ascendente o desendente
        if(body_json['action']=='ASC'):
            #La informacion del contador se actualiza y se agrega |     Se convierte de Texto a Int 
            cont +=                                                     int(body_json['quantity'])
            cambios+=1
        elif(body_json['action']=='DES'):
            #La informacion del contador se actualiza y se quita |     Se convierte de Texto a Int
            cont -=                                                    int(body_json['quantity'])
            cambios+=1
        print("-------------------------------")
        
        # Respond to the client
        #Cambios para actualizar el contador en el get (Message).
        response_data = json.dumps({"message":"El contador fue actualizado", "data": post_data.decode(),"Status":"OK"})
        self._set_response("application/json")
        self.wfile.write(response_data.encode())



def run_server(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=7800):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port} de examen...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
