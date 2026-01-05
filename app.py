# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app)

# Initialize AI model (simplified version - in reality you'd use more sophisticated setup)
class SimpleAI:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            # For a real application, you'd use models like:
            # GPT-2, LLaMA, or fine-tuned models
            print("Loading model...")
            # This is a simplified example - in production, use proper model loading
            self.model = "ai_model_loaded"
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def generate_response(self, prompt, max_length=500):
        """Generate AI response"""
        # This is a simplified response generator
        # In reality, you'd use actual model inference
        
        responses = {
            "hello": "Hello! How can I assist you today?",
            "who are you": "I'm an AI assistant built with Python and HTML!",
            "what is ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
            "default": f"I understand you said: '{prompt}'. As an AI, I'm here to help you with various tasks!"
        }
        
        prompt_lower = prompt.lower()
        for key in responses:
            if key in prompt_lower and key != "default":
                return responses[key]
        
        return responses["default"]

ai_assistant = SimpleAI()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Get AI response
    ai_response = ai_assistant.generate_response(user_message)
    
    return jsonify({
        'response': ai_response,
        'status': 'success'
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({
        'models': ['GPT-3', 'LLaMA', 'Custom Model'],
        'status': 'available'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
