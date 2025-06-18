from flask import Blueprint, jsonify, request
from src.services import mongodb_service

financial_bp = Blueprint('financial_bp', __name__)

@financial_bp.route('/financial/<string:emiten>', methods=['GET'])
def get_financial_report(emiten):
    """
    API endpoint to get financial report data for a specific emiten.
    Accepts emiten with or without .JK suffix (e.g., AALI.JK or AALI).
    Accepts 'year' query parameter (2021-2025).
    """
    year = request.args.get('year')
    valid_years = [str(y) for y in range(2021, 2026)]

    if year and year not in valid_years:
        return jsonify({"error": f"Invalid year specified. Valid years are: {', '.join(valid_years)}"}), 400

    # Strip .JK suffix if present for database query
    base_emiten = emiten.upper().replace('.JK', '')
    
    # Ensure DB connection
    if mongodb_service.financial_report_collection is None:
        mongodb_service.connect_db()
        if mongodb_service.financial_report_collection is None:
            return jsonify({"error": "Database connection failed"}), 500
    
    data = mongodb_service.get_financial_report_data(base_emiten, year)
    
    if data:
        # Add .JK suffix to the EntityCode in the response
        if 'EntityCode' in data:
            data['EntityCode'] = f"{data['EntityCode']}.JK"
        return jsonify(data)
    else:
        message = f"No financial report found for emiten {emiten}"
        if year:
            message += f" for the year {year}"
        return jsonify({"message": message}), 404