from flask import Flask, render_template
from datetime import datetime
import engineio

# set async_mode to 'threading', 'eventlet' or 'gevent' to force a mode
# else, the best mode is selected automatically from what's installed
async_mode = None

eio = engineio.Server(async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = engineio.Middleware(eio, app.wsgi_app)


@app.route('/')
def index():
    return render_template('simple.html')


@eio.on('connect')
def connect(sid, environ):
    print("connect ", sid)


@eio.on('message')
def message(sid, data):
    the_time = datetime.now().strftime("%H:%M")
    print('{time}message from'.format(time=the_time), sid, data)
    eio.send(sid, '[{0}] mensaje recibido por {1}: {2}'.format(the_time,sid,data), binary=False)



@eio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    if eio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(host='0.0.0.0', port=8080,threaded=True)
    elif eio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        from eventlet import wsgi
        wsgi.server(eventlet.listen(('', 8080)), app)
    elif eio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 8080), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 8080), app).serve_forever()
    else:
        print('Unknown async_mode: ' + eio.async_mode)
