from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

# Add your chatbot modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import smart_chat
import pdf_generator

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'default')
    
    try:
        response = smart_chat.get_response(user_message, user_id)
        
        # Check for PDF generation
        pdf_generated = 'PDF Created Successfully' in response
        pdf_file = None
        
        if pdf_generated:
            # Extract filename
            lines = response.split('\n')
            for line in lines:
                if 'FastSewa_Quote_' in line and '.pdf' in line:
                    pdf_file = line.split(': ')[1].split('/')[-1]
                    break
        
        return jsonify({
            'success': True,
            'response': response,
            'pdf_generated': pdf_generated,
            'pdf_file': pdf_file
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f"Error: {str(e)}"
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)