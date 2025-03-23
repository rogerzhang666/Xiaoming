from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
import requests
import json
from memory_system import MemorySystem
import uuid
import sqlite3

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

# 初始化记忆系统
memory_system = MemorySystem()

def get_or_create_user_id():
    """获取或创建用户ID"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

# 加载人设配置
def load_persona():
    with open('config/persona.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 获取系统提示信息
def get_system_prompt(user_id):
    try:
        persona = load_persona()
        base_prompt = persona['system_prompt']
        
        # 获取相关记忆
        memories = memory_system.get_relevant_memories(user_id)
        memory_prompt = memory_system.format_memories_for_prompt(memories)
        
        # 组合提示信息
        if memory_prompt:
            return f"{base_prompt}\n\n{memory_prompt}"
        return base_prompt
    except Exception as e:
        print(f"Warning: Failed to load persona config: {e}")
        return "你是王小明，一个热情好奇的年轻人。"

@app.route('/')
def home():
    # 确保用户有唯一ID
    get_or_create_user_id()
    return render_template('index.html')

@app.route('/memories')
def view_memories():
    return render_template('memories.html')

@app.route('/api/memories')
def get_memories():
    try:
        conn = sqlite3.connect(memory_system.db_path)
        cursor = conn.cursor()
        
        # 获取所有记忆
        cursor.execute('''
        SELECT id, type, content, created_at, expires_at, priority, user_id, confidence_score
        FROM memories
        ORDER BY created_at DESC
        ''')
        memories = [{
            'id': row[0],
            'type': row[1],
            'content': row[2],
            'created_at': row[3],
            'expires_at': row[4],
            'priority': row[5],
            'user_id': row[6],
            'confidence_score': row[7]
        } for row in cursor.fetchall()]
        
        # 获取最近的记忆使用记录（从对话历史中提取）
        cursor.execute('''
        SELECT id, user_id, role, content, timestamp
        FROM conversations
        WHERE content LIKE '%根据我对你的了解%'
        ORDER BY timestamp DESC
        LIMIT 10
        ''')
        memory_usage = [{
            'id': row[0],
            'user_id': row[1],
            'role': row[2],
            'content': row[3],
            'timestamp': row[4]
        } for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            'memories': memories,
            'memory_usage': memory_usage
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = get_or_create_user_id()
        
        # 存储用户消息到对话历史
        memory_system.store_conversation(user_id, 'user', user_message)
        
        # 提取并存储记忆
        memories = memory_system.extract_memories(user_message, user_id)
        for memory in memories:
            memory_system.store_memory(memory)
        
        # 获取对话历史
        conversation_history = memory_system.get_conversation_history(user_id)
        
        # 构建消息列表
        messages = [{"role": "system", "content": get_system_prompt(user_id)}]
        messages.extend([{
            "role": msg['role'],
            "content": msg['content']
        } for msg in conversation_history])
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': messages,
            'model': 'deepseek-chat',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        ai_response = response.json()['choices'][0]['message']['content']
        
        # 存储AI回复到对话历史
        memory_system.store_conversation(user_id, 'assistant', ai_response)
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
