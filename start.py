# Import Flask
from flaskproj import app


# instead of using FLASK_DEBUG=1 
if __name__ == '__main__':
    app.run(debug=True)