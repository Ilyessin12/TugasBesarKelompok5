from flask import Flask, jsonify
from flask_cors import CORS
from src.controllers.stock_controller import stock_bp
from src.controllers.news_controller import news_bp
from src.controllers.financial_controller import financial_bp
from src.services import mongodb_service

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": False
    }
})  # Enable CORS for all routes

# Ensure DB connection is attempted when app starts
mongodb_service.connect_db()

# Register blueprints
app.register_blueprint(stock_bp, url_prefix='/api')
app.register_blueprint(news_bp, url_prefix='/api')
app.register_blueprint(financial_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        "message": "Stock Market Analysis API",
        "endpoints": {
            "Stock Data": "/api/stock/<emiten>?period=<period>",
            "News Data": "/api/news/<emiten>?limit=<limit>&skip=<skip>",
            "News Summary": "/api/news/summary/<emiten>?limit=<limit>&skip=<skip>",
            "Financial Reports": "/api/financial/<emiten>"
        },
        "examples": {
            "Stock Data": "/api/stock/AALI.JK?period=monthly",
            "News Data": "/api/news/AALI.JK?limit=10&skip=0",
            "News Summary": "/api/news/summary/AALI.JK?limit=10&skip=0",
            "Financial Reports": "/api/financial/AALI.JK"
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible on your network
    app.run(debug=True, host='0.0.0.0', port=5000)
