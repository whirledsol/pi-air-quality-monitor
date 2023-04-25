from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, render_template

class FlaskClient():
    
    app = Flask(__name__)

    def __init__(self):
        cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'

        self.app.run(debug=True, use_reloader=False, host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))

    @app.route('/')
    def index():
        """Index page for the application"""
        context = {
            'historical': reconfigure_data(aqm.get_last_n_measurements()),
        }
        return render_template('index.html', context=context)


    @app.route('/api/')
    @cross_origin()
    def api():
        """Returns historical data from the sensor"""
        context = {
            'historical': reconfigure_data(aqm.get_last_n_measurements()),
        }
        return jsonify(context)


    @app.route('/api/now/')
    def api_now():
        """Returns latest data from the sensor"""
        context = {
            'current': aqm.get_measurement(),
        }
        return jsonify(context)
    


