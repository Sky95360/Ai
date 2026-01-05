from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Simple in-memory chat history
chat_history = []

class SimpleAI:
    def __init__(self):
        self.responses = {
            "hello": "Hello! I'm your AI Assistant running without PyTorch! 🤖",
            "hi": "Hi there! I'm in lightweight mode for better compatibility.",
            "how are you": "I'm running smoothly without heavy dependencies!",
            "your name": "I'm Simple AI - optimized for all platforms!",
            "what can you do": "I can chat with you, answer questions, and I work on both Termux and Render!",
            "who created you": "I was created by you using Python Flask!",
            "weather": "I can't check weather, but I'm always sunny to help you! ☀️",
            "time": f"Server time: {datetime.now().strftime('%H:%M:%S')}",
            "date": f"Today is: {datetime.now().strftime('%Y-%m-%d')}",
            "help": "You can ask me anything! Try: hello, time, date, weather, or just chat!",
            "bye": "Goodbye! Come back anytime! 👋",
            "thank you": "You're welcome! Happy to help! 😊",
            "what is ai": "AI is Artificial Intelligence - making machines smart!",
            "python": "Python is a great programming language! I'm built with it.",
            "flask": "Flask is a lightweight web framework for Python.",
            "termux": "Termux is an Android terminal emulator! That's where you're running me!",
            "render": "Render is a cloud platform where I can be deployed!",
            "github": "GitHub is for code hosting and version control.",
            "default": "That's interesting! I'm a lightweight AI that works everywhere - Termux, Render, and more!"
        }
    
    def generate_response(self, message):
        message_lower = message.lower().strip()
        
        # Check for specific keywords
        for key in self.responses:
            if key != "default" and key in message_lower:
                return self.responses[key]
        
        # Smart responses based on message content
        if "?" in message:
            return "Great question! In my lightweight mode, I focus on general knowledge and chat."
        elif len(message) < 3:
            return "Could you please say more? I'm listening!"
        elif any(word in message_lower for word in ["love", "like", "happy"]):
            return "That's wonderful to hear! Positive vibes are always good! 😊"
        elif any(word in message_lower for word in ["sad", "angry", "upset"]):
            return "I'm here to help if you want to talk about it."
        elif any(word in message_lower for word in ["code", "program", "script"]):
            return "I can help with coding concepts! Python is my favorite language."
        else:
            return self.responses["default"]

ai = SimpleAI()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'response': 'Please send a message!',
                'status': 'error'
            })
        
        # Get AI response
        ai_response = ai.generate_response(user_message)
        
        # Store in history
        chat_history.append({
            'user': user_message,
            'ai': ai_response,
            'timestamp': time.time(),
            'date': datetime.now().isoformat()
        })
        
        # Keep only last 50 messages
        if len(chat_history) > 50:
            chat_history.pop(0)
        
        return jsonify({
            'response': ai_response,
            'status': 'success',
            'history_length': len(chat_history),
            'mode': 'lightweight',
            'platform': 'no-pytorch'
        })
    
    except Exception as e:
        return jsonify({
            'response': f'Sorry, I encountered an error: {str(e)}',
            'status': 'error'
        })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'service': 'Simple AI Assistant',
        'version': '1.0.0',
        'messages_processed': len(chat_history),
        'platform': 'Flask',
        'ai_mode': 'Lightweight (No PyTorch)',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'Running'
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    # Return last 10 messages with formatted time
    formatted_history = []
    for msg in chat_history[-10:]:
        formatted_history.append({
            'user': msg['user'],
            'ai': msg['ai'],
            'time': datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M:%S'),
            'date': datetime.fromtimestamp(msg['timestamp']).strftime('%Y-%m-%d')
        })
    
    return jsonify({
        'history': formatted_history,
        'total': len(chat_history)
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    chat_history.clear()
    return jsonify({
        'status': 'success',
        'message': 'Chat history cleared',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def info():
    return jsonify({
        'name': 'Simple AI Assistant',
        'description': 'Lightweight chatbot without PyTorch dependencies',
        'features': [
            'Works on Termux (ARM)',
            'Works on Render (x86_64)',
            'No heavy ML dependencies',
            'Fast responses',
            'Chat history',
            'Cross-platform'
        ],
        'endpoints': {
            'GET /': 'Web interface',
            'POST /api/chat': 'Chat with AI',
            'GET /api/status': 'Service status',
            'GET /api/history': 'Chat history',
            'POST /api/clear': 'Clear history',
            'GET /api/info': 'This info'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Simple AI Assistant on port {port}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤖 Mode: Lightweight (No PyTorch)")
    print("🌐 Ready to serve at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
