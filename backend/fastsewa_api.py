# fastsewa_api.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import random
import os
from datetime import datetime
import pdf_generator  # Your existing module
import smart_chat     # Your existing module

app = Flask(__name__)
CORS(app)  # Enable cross-origin for frontend

# =============================================
# API ENDPOINTS
# =============================================

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat messages from frontend"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        service = data.get('service', None)
        
        # Get response from your smart_chat module
        response = smart_chat.get_response(user_message, user_id)
        
        # Check conversation state
        current_context = smart_chat.user_context.get(user_id)
        current_service = smart_chat.active_service.get(user_id)
        
        # Check if PDF was generated
        pdf_generated = 'PDF Created Successfully' in response
        pdf_file = None
        
        if pdf_generated:
            # Extract filename from response
            lines = response.split('\n')
            for line in lines:
                if 'FastSewa_Quote_' in line and '.pdf' in line:
                    pdf_file = line.split(': ')[1]
                    break
        
        return jsonify({
            'success': True,
            'response': response,
            'context': current_context,
            'service': current_service,
            'needs_input': current_context is not None,
            'pdf_generated': pdf_generated,
            'pdf_file': pdf_file,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f"System error: {str(e)}",
            'context': None,
            'service': None,
            'needs_input': False
        }), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all available services"""
    services = []
    for code, name in smart_chat.SERVICES.items():
        icon_map = {
            "FS_BUILD": "🏗️",
            "FS_SECURE": "🛡️", 
            "FS_LEGAL": "⚖️",
            "FS_MEDICAL": "🏥",
            "FS_LAND": "📋",
            "FS_REPAIR": "🔧"
        }
        services.append({
            'id': code,
            'name': name,
            'icon': icon_map.get(code, '📌')
        })
    
    return jsonify({
        'success': True,
        'services': services,
        'total': len(services)
    })

@app.route('/api/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    """Download generated PDF"""
    try:
        filepath = os.path.join('generated_pdfs', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset user session"""
    data = request.json
    user_id = data.get('user_id')
    if user_id:
        smart_chat.reset_user_session(user_id)
        return jsonify({'success': True, 'message': 'Session reset'})
    return jsonify({'success': False, 'message': 'User ID required'}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'online',
        'services': len(smart_chat.SERVICES),
        'timestamp': datetime.now().isoformat()
    })

# =============================================
# ERROR HANDLERS
# =============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# =============================================
# STARTUP
# =============================================

if __name__ == '__main__':
    print("🚀 FastSewa Chatbot API Starting...")
    print("✅ Backend modules loaded:")
    print(f"   - Services: {len(smart_chat.SERVICES)}")
    print(f"   - PDF Generator: Ready")
    print(f"   - Chatbot: Ready")
    print("\n🌐 API Endpoints:")
    print("   POST /api/chat        - Chat with bot")
    print("   GET  /api/services    - List all services")
    print("   GET  /api/health      - Health check")
    print("\n🔗 Frontend Integration:")
    print("   Chatbot URL: http://localhost:5000/api/chat")
    
    app.run(debug=True, port=5000, host='0.0.0.0')