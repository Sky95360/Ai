from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
import random
import subprocess
import re
import threading
import sqlite3
from datetime import datetime
from datetime import timedelta

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('ai_bot.db')
    c = conn.cursor()
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender TEXT,
                  message TEXT,
                  response TEXT,
                  timestamp DATETIME,
                  status TEXT)''')
    
    # Auto-reply rules
    c.execute('''CREATE TABLE IF NOT EXISTS auto_replies
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  keyword TEXT,
                  response TEXT,
                  enabled INTEGER DEFAULT 1)''')
    
    # Add default auto-replies
    default_replies = [
        ("hello", "Hello! This is Sky's AI Assistant. Sky is currently offline. I'll notify them of your message. 📱"),
        ("hi", "Hi there! Sky is away right now. I'm their AI assistant. How can I help?"),
        ("urgent", "⚠️ URGENT MESSAGE DETECTED! I've sent an emergency notification to Sky."),
        ("call", "📞 Call request noted. Sky will call you back when available."),
        ("meeting", "📅 Meeting request received. I'll add it to Sky's calendar."),
        ("help", "🆘 Help request! I'm alerting Sky immediately."),
        ("emergency", "🚨 EMERGENCY! Sending immediate alert to Sky!")
    ]
    
    c.executemany("INSERT OR IGNORE INTO auto_replies (keyword, response) VALUES (?, ?)", default_replies)
    
    conn.commit()
    conn.close()

init_db()

class WhatsAppAutoResponder:
    def __init__(self):
        self.your_number = "+254748529340"
        self.admin_numbers = ["+254748529340"]  # Your number as admin
        self.auto_reply_enabled = True
        self.check_interval = 30  # seconds
        self.response_thread = None
        
    def start_auto_responder(self):
        """Start background thread to check and respond to messages"""
        if not self.response_thread:
            self.response_thread = threading.Thread(target=self._monitor_messages, daemon=True)
            self.response_thread.start()
            print("🤖 WhatsApp Auto-Responder STARTED")
    
    def _monitor_messages(self):
        """Background thread to monitor incoming messages"""
        while True:
            try:
                self.check_and_reply()
            except Exception as e:
                print(f"Auto-responder error: {e}")
            time.sleep(self.check_interval)
    
    def check_incoming_messages(self):
        """Check for new incoming WhatsApp messages"""
        try:
            # Get last 20 messages from Termux SMS inbox
            cmd = 'termux-sms-inbox -l 20'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            new_messages = []
            
            if result.returncode == 0:
                messages = result.stdout.strip().split('\n\n')
                
                for msg in messages:
                    lines = msg.split('\n')
                    msg_data = {}
                    
                    for line in lines:
                        if 'Number:' in line:
                            msg_data['sender'] = line.split(': ')[1].strip()
                        elif 'Body:' in line:
                            msg_data['body'] = line.split(': ')[1].strip()
                        elif 'Received:' in line:
                            msg_data['received'] = line.split(': ')[1].strip()
                    
                    if 'sender' in msg_data and 'body' in msg_data:
                        # Skip messages from yourself
                        if msg_data['sender'] != self.your_number:
                            # Check if message is already processed
                            if not self.is_message_processed(msg_data):
                                new_messages.append(msg_data)
                                self.save_message_to_db(msg_data)
            
            return new_messages
            
        except Exception as e:
            print(f"Error checking messages: {e}")
            return []
    
    def is_message_processed(self, msg_data):
        """Check if message already exists in database"""
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        c.execute('''SELECT COUNT(*) FROM messages 
                     WHERE sender = ? AND message = ? AND timestamp > datetime('now', '-1 hour')''',
                  (msg_data['sender'], msg_data['body']))
        
        count = c.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def save_message_to_db(self, msg_data):
        """Save incoming message to database"""
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO messages (sender, message, timestamp, status)
                     VALUES (?, ?, datetime('now'), 'received')''',
                  (msg_data['sender'], msg_data['body']))
        
        conn.commit()
        conn.close()
        
        # Send notification
        self.send_notification(f"📩 New message from {msg_data['sender']}: {msg_data['body'][:50]}...")
    
    def get_auto_reply(self, message):
        """Get appropriate auto-reply based on message content"""
        message_lower = message.lower()
        
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        # Check for keyword matches
        c.execute("SELECT response FROM auto_replies WHERE enabled = 1")
        all_replies = c.fetchall()
        
        for reply in all_replies:
            if reply[0] in message_lower:
                conn.close()
                return reply[1]
        
        # Default auto-reply
        default_responses = [
            "Thanks for your message! Sky is currently unavailable. I'll make sure they see this when they're back. ⏰",
            "Sky is away right now. This is their AI assistant. Your message has been saved and will be reviewed soon. 📋",
            "I've received your message! Sky is offline at the moment but will respond when available. ✨",
            "Message received! Sky is not currently online. I'm keeping track of all messages for them. 📱",
            "Hello! This is Sky's AI bot. Sky is away, but I'll notify them about your message. 🚀"
        ]
        
        conn.close()
        return random.choice(default_responses)
    
    def check_and_reply(self):
        """Check for new messages and send auto-replies"""
        if not self.auto_reply_enabled:
            return
        
        new_messages = self.check_incoming_messages()
        
        for msg in new_messages:
            sender = msg['sender']
            message = msg['body']
            
            # Don't auto-reply to yourself or admins
            if sender in self.admin_numbers:
                continue
            
            # Get auto-reply
            reply = self.get_auto_reply(message)
            
            # Send auto-reply
            self.send_whatsapp(sender, reply)
            
            # Log the reply
            self.log_reply(sender, message, reply)
            
            # Send urgent alerts for specific keywords
            urgent_keywords = ['emergency', 'urgent', 'help', '911', 'sos']
            if any(keyword in message.lower() for keyword in urgent_keywords):
                self.send_urgent_alert(sender, message)
    
    def send_whatsapp(self, number, message):
        """Send WhatsApp message"""
        try:
            cmd = f'termux-sms-send -n "{number}" "{message}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Auto-reply sent to {number}")
                return True
            return False
        except:
            return False
    
    def send_notification(self, message):
        """Send notification to Termux"""
        try:
            cmd = f'termux-notification -t "🤖 AI Assistant" -c "{message}"'
            subprocess.run(cmd, shell=True)
        except:
            pass
    
    def send_urgent_alert(self, sender, message):
        """Send urgent alert to admin"""
        alert_msg = f"🚨 URGENT MESSAGE!\nFrom: {sender}\nMessage: {message}\nTime: {datetime.now().strftime('%H:%M:%S')}"
        
        # Send to all admin numbers
        for admin in self.admin_numbers:
            self.send_whatsapp(admin, alert_msg)
            self.send_notification(f"Urgent message from {sender}")
    
    def log_reply(self, sender, original_msg, reply):
        """Log auto-reply to database"""
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        c.execute('''UPDATE messages SET response = ?, status = 'replied'
                     WHERE sender = ? AND message = ? AND response IS NULL
                     ORDER BY timestamp DESC LIMIT 1''',
                  (reply, sender, original_msg))
        
        conn.commit()
        conn.close()
    
    def add_auto_reply(self, keyword, response):
        """Add new auto-reply rule"""
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        c.execute("INSERT INTO auto_replies (keyword, response) VALUES (?, ?)", (keyword, response))
        
        conn.commit()
        conn.close()
        return True
    
    def get_message_history(self):
        """Get message history from database"""
        conn = sqlite3.connect('ai_bot.db')
        c = conn.cursor()
        
        c.execute('''SELECT sender, message, response, timestamp, status 
                     FROM messages 
                     ORDER BY timestamp DESC 
                     LIMIT 50''')
        
        messages = []
        for row in c.fetchall():
            messages.append({
                'sender': row[0],
                'message': row[1],
                'response': row[2],
                'timestamp': row[3],
                'status': row[4]
            })
        
        conn.close()
        return messages

# Initialize auto-responder
auto_responder = WhatsAppAutoResponder()

class MultiSkillAI:
    def __init__(self):
        self.whatsapp = auto_responder
        
    def process_command(self, message):
        """Process WhatsApp-related commands"""
        message_lower = message.lower()
        
        if message_lower == "start auto responder":
            auto_responder.start_auto_responder()
            return "✅ Auto-responder STARTED! I'll now automatically reply to WhatsApp messages when you're offline."
        
        elif message_lower == "stop auto responder":
            auto_responder.auto_reply_enabled = False
            return "⏸️ Auto-responder PAUSED. Messages will not be auto-replied."
        
        elif message_lower == "auto responder status":
            status = "ACTIVE" if auto_responder.auto_reply_enabled else "PAUSED"
            return f"🤖 Auto-Responder Status: {status}\nChecking every {auto_responder.check_interval} seconds"
        
        elif "add auto reply" in message_lower:
            try:
                parts = message.split('"')
                if len(parts) >= 4:
                    keyword = parts[1]
                    response = parts[3]
                    auto_responder.add_auto_reply(keyword, response)
                    return f"✅ Added auto-reply:\nKeyword: {keyword}\nResponse: {response}"
            except:
                return "Format: add auto reply \"keyword\" \"response\""
        
        elif message_lower == "show messages":
            messages = auto_responder.get_message_history()
            if not messages:
                return "No messages in history yet."
            
            response = "📱 **Message History:**\n\n"
            for msg in messages[:5]:  # Show last 5
                response += f"**From:** {msg['sender']}\n"
                response += f"**Message:** {msg['message'][:50]}...\n"
                response += f"**Status:** {msg['status']}\n"
                response += f"**Time:** {msg['timestamp']}\n"
                if msg['response']:
                    response += f"**Reply:** {msg['response'][:50]}...\n"
                response += "---\n"
            
            return response
        
        elif "send whatsapp" in message_lower or "whatsapp to" in message_lower:
            # Extract number and message
            match = re.search(r'(\d{10,13}) (.+)', message)
            if match:
                number = match.group(1)
                msg = match.group(2)
                result = auto_responder.send_whatsapp(number, msg)
                return f"📱 Message sent to {number}: {result}"
            else:
                return "Format: send whatsapp 0748529340 Hello there"
        
        return None

# Routes
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'response': 'Please send a message!', 'status': 'error'})
        
        ai = MultiSkillAI()
        
        # Process WhatsApp commands
        whatsapp_response = ai.process_command(user_message)
        if whatsapp_response:
            response = whatsapp_response
        else:
            # Regular chat responses
            responses = {
                "hello": "👋 Hello! I'm your AI Assistant with WhatsApp auto-responder!",
                "whatsapp": "📱 WhatsApp Features:\n1. Auto-reply when offline\n2. Message history\n3. Send messages\nType 'start auto responder' to begin!",
                "help": "🆘 **Commands:**\n• start auto responder\n• stop auto responder\n• auto responder status\n• add auto reply\n• show messages\n• send whatsapp [number] [message]",
                "default": "I'm your AI assistant! Try 'whatsapp' to see WhatsApp features or 'help' for commands."
            }
            
            message_lower = user_message.lower()
            response = responses["default"]
            for key in responses:
                if key in message_lower and key != "default":
                    response = responses[key]
                    break
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}', 'status': 'error'})

@app.route('/api/whatsapp/status', methods=['GET'])
def whatsapp_status():
    return jsonify({
        'auto_responder': 'ready',
        'your_number': auto_responder.your_number,
        'auto_reply_enabled': auto_responder.auto_reply_enabled
    })

@app.route('/api/whatsapp/history', methods=['GET'])
def whatsapp_history():
    messages = auto_responder.get_message_history()
    return jsonify({'messages': messages[:10]})

# Start auto-responder when app starts
@app.before_first_request
def startup():
    print("🤖 WhatsApp Auto-Responder Initializing...")
    auto_responder.start_auto_responder()
    print("✅ System READY! WhatsApp auto-replies are ACTIVE")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🤖 WHATSAPP AUTO-RESPONDER AI")
    print("=" * 60)
    print(f"📱 Your Number: {auto_responder.your_number}")
    print(f"📧 Your Email: {auto_responder.your_email}")
    print(f"🌐 Web Interface: http://localhost:{port}")
    print("🔄 Auto-Responder: ACTIVE (starts automatically)")
    print("=" * 60)
    print("💡 Commands to try in chat:")
    print("• 'start auto responder' - Begin auto-replying")
    print("• 'show messages' - View message history")
    print("• 'whatsapp' - See all WhatsApp features")
    print("• 'help' - Show all commands")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
