from flask import Blueprint, jsonify, request
from src.services import mongodb_service

stock_bp = Blueprint('stock_bp', __name__)

@stock_bp.route('/stock/<string:emiten>', methods=['GET'])
def get_stock_info(emiten):
    """
    API endpoint to get stock data.
    Accepts 'period' query parameter (daily, weekly, monthly, quarterly, yearly, 1y, 3y, 5y, all).
    Defaults to 'all' if not specified.
    """
    period = request.args.get('period', 'all').lower()
    valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly', '1y', '3y', '5y', 'all']

    if period not in valid_periods:
         return jsonify({"error": f"Invalid period specified. Valid periods are: {', '.join(valid_periods)}"}), 400

    # Ensure DB connection is attempted if not already connected
    if mongodb_service.stock_collection is None:
        mongodb_service.connect_db()
        if mongodb_service.stock_collection is None:
             return jsonify({"error": "Database connection failed"}), 500

    data = mongodb_service.get_stock_data(emiten.upper(), period)  # Ensure emiten is uppercase if stored like 'AALI.JK'

    if data is None:
        return jsonify({"error": "Failed to retrieve or process stock data"}), 500
    elif not data:
         return jsonify({"message": f"No data found for emiten {emiten} with period {period}"}), 404
    else:
        return jsonify(data)
