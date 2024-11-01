import time



from app import create_app, Config
from flask_cors import CORS

app = create_app()
CORS(app, resources=r'/*')



if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
