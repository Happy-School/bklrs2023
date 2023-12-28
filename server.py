from datetime import datetime
import json
from multiprocessing import Process
import os
import time
from flask_socketio import SocketIO
from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from WebServer.config import ApplicationConfig
from WebServer.models import db, User
from openfx_api.OpenFxApi import OpenFxApi
from openfx_api.NewsApi import AlphaVantageApi
from bot.bot import TradingBot
from infrastructure.db.mongoDb import MongoDB



class UserAuthentication:
    def __init__(self, app, cors, db):
        self.app = app
        self.bcrypt = Bcrypt(app)
        self.cors = cors
        self.server_session = Session(app)
        self.db = db

        with app.app_context():
            try:
                self.db.create_all()
                print('Tables created successfully')
            except Exception as e:
                print(f'Error creating tables: {str(e)}')

    def get_current_user(self):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.filter_by(id=user_id).first()
        return jsonify({
            "id": user.id,
            "email": user.email
        })

    def register_user(self):
        email = request.json["email"]
        password = request.json["password"]

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            return jsonify({"error": "User already exists"}), 409

        hashed_password = self.bcrypt.generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        self.db.session.add(new_user)
        self.db.session.commit()

        session["user_id"] = new_user.id

        return jsonify({
            "id": new_user.id,
            "email": new_user.email
        })

    def login_user(self):
        email = request.json["email"]
        password = request.json["password"]

        user = User.query.filter_by(email=email).first()

        if user is None:
            return jsonify({"error": "Unauthorized"}), 401

        if not self.bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Unauthorized"}), 401

        session["user_id"] = user.id

        return jsonify({
            "id": user.id,
            "email": user.email
        })

    def logout_user(self):
        if "user_id" in session:
            session.pop("user_id")
            return "Logged out successfully", 200
        else:
            return "Unauthorized", 401

def run_bot():
    t_bot = TradingBot()
    t_bot.turn_on_bot()


bot_process = None

def read_log_lines_b(log_file_path, last_position):
    new_lines = []
    with open(log_file_path, 'r') as log_file:
        if last_position >= 0:
            log_file.seek(last_position)
        new_lines = log_file.readlines()
        last_position = log_file.tell() 

    return new_lines, last_position

def generate_log():
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file_path = f'./logs/main_{current_date}.log'
    last_position = 0

    while True:
        if not os.path.exists(log_file_path):
            time.sleep(1)
            continue

        new_lines, last_position = read_log_lines_b(log_file_path, last_position)

        for line in new_lines:
            data = json.dumps(line.strip())
            socketio.emit('log', data, namespace='/logs')


app = Flask(__name__)
app.config.from_object(ApplicationConfig)

cors = CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

db.init_app(app)
user_auth = UserAuthentication(app, cors, db)

################################### Bot Management Routes ##########################################
@app.route('/bot/settings', methods=['GET', 'PUT'])
def handle_settings():
    if request.method == 'GET':

        db = MongoDB()
        settings_document = db.find_one('Settings')

        if not settings_document:
            return jsonify({"error": "Settings not found"}), 404

        settings_document.pop('_id', None)

        formatted_settings = {
            "trade_risk": settings_document.get("trade_risk", 0),
            "pairs": {}
        }

        pairs = settings_document.get("pairs", {})
        for pair, values in pairs.items():
            formatted_settings["pairs"][pair] = {
                "n_ma": values.get("n_ma", 0),
                "n_std": values.get("n_std", 0),
                "maxspread": values.get("maxspread", 0),
                "mingain": values.get("mingain", 0),
                "riskreward": values.get("riskreward", 0)
            }

        return jsonify(formatted_settings)

    elif request.method == 'PUT':
        try:
            new_settings = request.json

            if 'pairs' not in new_settings or 'trade_risk' not in new_settings:
                return jsonify({"error": "Invalid request payload"}), 400

            new_settings['trade_risk'] = int(new_settings['trade_risk'])
            for pair, values in new_settings['pairs'].items():
                for key, value in values.items():
                    new_settings['pairs'][pair][key] = float(value)

            db = MongoDB()
            db.update_one('Settings', {}, {"$set": new_settings})

            return jsonify({"message": "Settings updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500



@app.route('/start_bot', methods=['POST'])
def start_bot():
    global bot_process
    if bot_process is None or not bot_process.is_alive():
        bot_process = Process(target=run_bot)
        bot_process.daemon = True
        bot_process.start()
        return jsonify({'message': 'Bot has been started'})
    else:
        return jsonify({'message': 'Bot is already running'})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    global bot_process
    if bot_process is not None and bot_process.is_alive():
        t_bot = TradingBot()
        t_bot.shutdown_bot()
        bot_process.terminate()
        bot_process = None
        return jsonify({'message': 'Bot has been stopped'})
    else:
        return jsonify({'message': 'Bot is not running'})

#################################### Client Authorization Routes ###############################################

@app.route("/@me")
def get_current_user():
    return user_auth.get_current_user()

@app.route("/register", methods=["POST"])
def register_user():
    return user_auth.register_user()

@app.route("/login", methods=["POST"])
def login_user():
    return user_auth.login_user()

@app.route("/logout", methods=["POST"])
def logout_user():
    return user_auth.logout_user()

############################################### OpenFx API ################################################

    
@app.route("/account", methods=['GET'])
def account():
    data = OpenFxApi().get_account_summary()
    return jsonify(data), 200, {'Content-Type': 'application/json'}

@app.route("/open_trades", methods=['GET'])
def trades():
    open_trades = OpenFxApi().get_open_trades()
    serialized_trades = [trade.to_json() for trade in open_trades]

    return jsonify(serialized_trades), 200, {'Content-Type': 'application/json'}

@app.route('/get_trade_history', methods=['GET'])
def get_trade_history():
    api = OpenFxApi()
    response = api.trade_history()

    if response is not None:
        return jsonify(response)
    else:
        return jsonify({"error": "Unable to fetch trade history"}), 500


@app.route("/pip_value", methods=['GET'])
def pip_Value():
    data = OpenFxApi().get_pip_value()
    return jsonify(data), 200, {'Content-Type': 'application/json'}

################################################# News API #############################################

@app.route('/sentiment', methods=['GET'])
def get_alpha_vantage_data():
    try:
        alpha_vantage_api = AlphaVantageApi()
        success, data = alpha_vantage_api.get_alpha_vantage_data()

        if success:
            if not data or not data.get("feed"):
                return jsonify({"error": "Limit reached or empty data"}), 400

            # Extract only specific fields and limit the number of items
            extracted_data = [
                {
                    "title": feed_item.get("title", ""),
                    "authors": feed_item.get("authors", []),
                    "summary": feed_item.get("summary", ""),
                    "source": feed_item.get("source", ""),
                    "topics": feed_item.get("topics", []),
                    "overall_sentiment_score": feed_item.get("overall_sentiment_score", 0),
                    "overall_sentiment_label": feed_item.get("overall_sentiment_label", "Neutral"),
                }
                for feed_item in data["feed"][:10]  # Limit to the first 10 items
            ]

            return jsonify(extracted_data)
        else:
            return jsonify({"error": "Failed to fetch Alpha Vantage data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


############################################### Logs ################################################

@socketio.on('connect', namespace='/logs')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=generate_log)


if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)