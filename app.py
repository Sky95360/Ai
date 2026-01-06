from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import requests
import time
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

chat_history = []

class AdvancedAI:
    def __init__(self):
        # Free AI APIs
        self.apis = {
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "huggingface": "https://api-inference.huggingface.co/models/gpt2",
            "localai": "http://localhost:8080/v1/chat/completions"  # If you run LocalAI
        }
        
        # Simple fallback responses
        self.fallback_responses = {
            "hello": "Hello! I'm your AI Assistant connected to multiple AI models! 🤖",
            "hi": "Hi there! I can answer almost anything using real AI APIs.",
            "how are you": "I'm powered by multiple AI services and ready to help!",
            "your name": "I'm Advanced AI - I connect to GPT, DeepSeek, and other models!",
            "what can you do": "I can answer questions, write code, explain concepts, translate, summarize, and more!",
            "default": "Let me think about that... I'm connecting to AI services for the best answer!"
        }
    
    def get_deepseek_response(self, message):
        """Get response from DeepSeek API (free tier)"""
        try:
            # DeepSeek Free API (you need an API key from their website)
            headers = {
                "Authorization": "Bearer sk-your-deepseek-api-key-here",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
        except:
            return None
    
    def get_huggingface_response(self, message):
        """Get response from Hugging Face (free)"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            headers = {"Authorization": "Bearer hf_your_huggingface_token"}
            
            payload = {
                "inputs": f"<s>[INST] {message} [/INST]",
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['generated_text']
            return None
        except:
            return None
    
    def get_openai_compatible(self, message):
        """Try local AI or other OpenAI-compatible APIs"""
        try:
            # Try LocalAI if running locally
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
            
            # You can try different free endpoints
            endpoints = [
                "http://localhost:8080/v1/chat/completions",
                "https://openrouter.ai/api/v1/chat/completions",
                "https://api.deepinfra.com/v1/openai/chat/completions"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, json=data, timeout=10)
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                except:
                    continue
            return None
        except:
            return None
    
    def get_web_search_answer(self, message):
        """Use web search to get answers (simulated)"""
        import random
        knowledge_base = {
            "who is the president of usa": "As of 2024, the President of the United States is Joe Biden.",
            "what is python": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
            "what is ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines.",
            "how to learn programming": "Start with Python, practice daily, build projects, and join coding communities.",
            "what is flask": "Flask is a lightweight WSGI web application framework in Python.",
            "best programming language": "Python is great for beginners, JavaScript for web, C++ for performance.",
            "what is machine learning": "ML is a subset of AI that enables systems to learn from data without explicit programming.",
            "how to deploy on render": "Push code to GitHub, connect to Render, configure build command, and deploy.",
            "what is github": "GitHub is a platform for version control and collaboration on code.",
            "how to use termux": "Termux is an Android terminal. Install packages with pkg install, run Python scripts.",
            "what is chatgpt": "ChatGPT is an AI chatbot developed by OpenAI using the GPT architecture.",
            "how to make money online": "Learn skills, freelance, build apps, create content, or teach online.",
            "best ai models": "GPT-4, Claude, Gemini, Llama, Mistral, and DeepSeek are top AI models.",
            "how to code in python": "Install Python, use VS Code, learn basics, practice with projects.",
            "what is deep learning": "Deep learning uses neural networks with multiple layers for complex pattern recognition.",
            "future of ai": "AI will transform healthcare, education, automation, and create new job opportunities.",
            "how to train ai model": "Collect data, preprocess, choose algorithm, train, validate, and deploy.",
            "what is neural network": "Neural networks are computing systems inspired by biological neural networks.",
            "difference between ai and ml": "AI is broader concept, ML is subset that enables machines to learn from data.",
            "how to start with ai": "Learn Python, study math basics, take online courses, build simple projects."
        }
        
        message_lower = message.lower()
        for key in knowledge_base:
            if key in message_lower:
                return knowledge_base[key]
        
        # If no match, generate intelligent response
        responses = [
            f"Based on my knowledge: {message} is an interesting topic. I recommend researching authoritative sources for detailed information.",
            f"I understand you're asking about {message}. This is a complex topic that requires detailed explanation. Would you like me to break it down?",
            f"Regarding {message}: I can provide general information. For specific details, you might want to consult specialized resources.",
            f"That's a great question about {message}! The answer depends on context. Could you specify what aspect you're interested in?",
            f"I have information about {message}. Would you like a brief overview or specific details?"
        ]
        return random.choice(responses)
    
    def generate_response(self, message):
        """Main method to generate AI response"""
        message = message.strip()
        if not message:
            return "Please enter a message!"
        
        # Check for simple greetings first
        message_lower = message.lower()
        for key in self.fallback_responses:
            if key != "default" and key in message_lower:
                return self.fallback_responses[key]
        
        print(f"🔍 Processing: {message}")
        
        # Try to get response from AI APIs (in order of preference)
        response = None
        
        # 1. Try DeepSeek API
        response = self.get_deepseek_response(message)
        if response:
            return f"🤖 (DeepSeek): {response}"
        
        # 2. Try Hugging Face
        response = self.get_huggingface_response(message)
        if response:
            return f"🤖 (Mistral): {response}"
        
        # 3. Try OpenAI-compatible
        response = self.get_openai_compatible(message)
        if response:
            return f"🤖 (AI Model): {response}"
        
        # 4. Use knowledge base with web search simulation
        response = self.get_web_search_answer(message)
        return f"📚 (Knowledge Base): {response}"

ai = AdvancedAI()

# API Routes (same as before but with improved AI)
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
        start_time = time.time()
        ai_response = ai.generate_response(user_message)
        response_time = round(time.time() - start_time, 2)
        
        # Store in history
        chat_history.append({
            'user': user_message,
            'ai': ai_response,
            'timestamp': time.time(),
            'response_time': response_time
        })
        
        # Keep only last 100 messages
        if len(chat_history) > 100:
            chat_history.pop(0)
        
        return jsonify({
            'response': ai_response,
            'status': 'success',
            'response_time': f"{response_time}s",
            'history_length': len(chat_history),
            'timestamp': datetime.now().isoformat()
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
        'service': 'Advanced AI Assistant',
        'version': '2.0.0',
        'messages_processed': len(chat_history),
        'ai_backends': ['Knowledge Base', 'Web Search Sim', 'API Ready'],
        'supported_queries': [
            'Programming help',
            'General knowledge',
            'Tech explanations',
            'Learning guidance',
            'Career advice'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/configure', methods=['POST'])
def configure():
    """Allow configuring API keys"""
    data = request.get_json()
    # In production, store in database
    return jsonify({
        'status': 'configuration_updated',
        'message': 'API configuration endpoint ready'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Advanced AI Assistant starting on port {port}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🤖 Mode: Multi-Backend AI (Knowledge Base + APIs)")
    print("🌐 Web Interface: http://localhost:{port}")
    print("🔧 API Endpoints: /api/chat, /api/status, /api/configure")
    print("💡 Tip: Add API keys for real AI model access")
    app.run(host='0.0.0.0', port=port, debug=False)
