from flask import Blueprint, jsonify
from src.services import mongodb_service

financial_bp = Blueprint('financial_bp', __name__)

@financial_bp.route('/financial/<string:emiten>', methods=['GET'])
def get_financial_report(emiten):
    """
    API endpoint to get financial report data for a specific emiten.
    Accepts emiten with or without .JK suffix (e.g., AALI.JK or AALI).
    """
    # Strip .JK suffix if present for database query
    base_emiten = emiten.upper().replace('.JK', '')
    
    # Ensure DB connection
    if mongodb_service.financial_report_collection is None:
        mongodb_service.connect_db()
        if mongodb_service.financial_report_collection is None:
            return jsonify({"error": "Database connection failed"}), 500
    
    data = mongodb_service.get_financial_report_data(base_emiten)
    
    if data is None:
        return jsonify({"error": "Failed to retrieve financial report data"}), 500
    elif not data:
        return jsonify({"message": f"No financial report found for emiten {emiten}"}), 404
    else:
        # Add .JK suffix to the EntityCode in the response
        if 'EntityCode' in data:
            data['EntityCode'] = f"{data['EntityCode']}.JK"
        return jsonify(data)