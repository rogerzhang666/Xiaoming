import json
import sqlite3
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any, Optional
import os

class MemorySystem:
    def __init__(self, db_path: str = "memories.db", config_path: str = "config/memory_rules.json"):
        self.db_path = db_path
        self.config_path = config_path
        self.load_config()
        self.init_database()

    def load_config(self):
        """加载记忆系统配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建记忆表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            priority INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            confidence_score REAL NOT NULL
        )
        ''')

        # 创建对话历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
        ''')

        conn.commit()
        conn.close()

    def extract_memories(self, message: str, user_id: str) -> List[Dict[str, Any]]:
        """从消息中提取记忆"""
        memories = []
        
        # 遍历所有记忆类型的触发词
        for memory_type, triggers in self.config['memory_triggers'].items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    # 提取包含触发词的完整句子
                    sentences = re.split('[。！？.!?]', message)
                    for sentence in sentences:
                        if trigger.lower() in sentence.lower():
                            memory = {
                                'type': memory_type,
                                'content': sentence.strip(),
                                'created_at': datetime.now(),
                                'priority': self.config['memory_types'][memory_type]['priority'],
                                'retention_days': self.config['memory_types'][memory_type]['retention_days'],
                                'user_id': user_id,
                                'confidence_score': 0.8  # 可以根据具体规则调整
                            }
                            memories.append(memory)

        # 限制每条消息提取的记忆数量
        max_memories = self.config['memory_extraction_rules']['max_memories_per_message']
        return sorted(memories, key=lambda x: x['priority'])[:max_memories]

    def store_memory(self, memory: Dict[str, Any]):
        """存储记忆到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = memory['created_at'] + timedelta(days=memory['retention_days'])

        cursor.execute('''
        INSERT INTO memories (type, content, created_at, expires_at, priority, user_id, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory['type'],
            memory['content'],
            memory['created_at'],
            expires_at,
            memory['priority'],
            memory['user_id'],
            memory['confidence_score']
        ))

        conn.commit()
        conn.close()

    def get_relevant_memories(self, user_id: str, context: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """获取相关记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取未过期的记忆，按优先级排序
        cursor.execute('''
        SELECT type, content, created_at, priority
        FROM memories
        WHERE user_id = ? AND expires_at > ?
        ORDER BY priority, created_at DESC
        LIMIT ?
        ''', (user_id, datetime.now(), limit))

        memories = [{
            'type': row[0],
            'content': row[1],
            'created_at': row[2],
            'priority': row[3]
        } for row in cursor.fetchall()]

        conn.close()
        return memories

    def store_conversation(self, user_id: str, role: str, content: str):
        """存储对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO conversations (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (user_id, role, content, datetime.now()))

        conn.commit()
        conn.close()

    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT role, content, timestamp
        FROM conversations
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (user_id, limit))

        history = [{
            'role': row[0],
            'content': row[1],
            'timestamp': row[2]
        } for row in cursor.fetchall()]

        conn.close()
        return history[::-1]  # 返回按时间正序的历史记录

    def format_memories_for_prompt(self, memories: List[Dict[str, Any]]) -> str:
        """将记忆格式化为提示信息"""
        if not memories:
            return ""

        prompt = "根据我对你的了解：\n"
        for memory in memories:
            prompt += f"- {memory['content']}\n"
        return prompt
