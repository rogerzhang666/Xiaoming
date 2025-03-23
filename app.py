from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

# 加载人设配置
def load_persona():
    with open('config/persona.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 获取系统提示信息
def get_system_prompt():
    try:
        persona = load_persona()
        return persona['system_prompt']
    except Exception as e:
        print(f"Warning: Failed to load persona config: {e}")
        return "你是王小明，一个热情好奇的年轻人。"

# 对话历史记录（简单实现，实际应用中应该使用数据库）
conversations = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        # 获取或初始化对话历史
        if conversation_id not in conversations:
            conversations[conversation_id] = [
                {"role": "system", "content": get_system_prompt()}
            ]
        
        # 添加用户消息到历史记录
        conversations[conversation_id].append({"role": "user", "content": user_message})
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': conversations[conversation_id],
            'model': 'deepseek-chat',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        ai_response = response.json()['choices'][0]['message']['content']
        
        # 添加AI回复到历史记录
        conversations[conversation_id].append({"role": "assistant", "content": ai_response})
        
        # 保持对话历史在合理长度
        if len(conversations[conversation_id]) > 10:
            # 保留system prompt和最近的对话
            conversations[conversation_id] = [
                conversations[conversation_id][0]  # system prompt
            ] + conversations[conversation_id][-9:]  # 最近的对话
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
