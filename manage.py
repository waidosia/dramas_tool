from flask_cors import CORS

from app import create_app, Config

app = create_app()
CORS(app, resources=r'/*')



if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)

