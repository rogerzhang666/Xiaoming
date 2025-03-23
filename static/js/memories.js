document.addEventListener('DOMContentLoaded', function() {
    const memoriesGrid = document.getElementById('memoriesGrid');
    const memoryUsageList = document.getElementById('memoryUsageList');

    // 格式化日期
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // 获取记忆类型的中文名称
    function getMemoryTypeName(type) {
        const typeNames = {
            'personal_info': '个人信息',
            'preferences': '偏好习惯',
            'conversation_context': '对话上下文',
            'emotional_state': '情绪状态'
        };
        return typeNames[type] || type;
    }

    // 创建记忆卡片
    function createMemoryCard(memory) {
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.innerHTML = `
            <div class="memory-type">${getMemoryTypeName(memory.type)}</div>
            <div class="memory-content">${memory.content}</div>
            <div class="memory-meta">
                <span>创建于: ${formatDate(memory.created_at)}</span>
                <span>优先级: ${memory.priority}</span>
            </div>
        `;
        return card;
    }

    // 创建记忆使用记录项
    function createUsageItem(usage) {
        const item = document.createElement('div');
        item.className = 'usage-item';
        item.innerHTML = `
            <div class="usage-timestamp">${formatDate(usage.timestamp)}</div>
            <div class="usage-content">${usage.content}</div>
        `;
        return item;
    }

    // 加载记忆数据
    async function loadMemories() {
        try {
            const response = await fetch('/api/memories');
            const data = await response.json();
            
            // 清空现有内容
            memoriesGrid.innerHTML = '';
            memoryUsageList.innerHTML = '';
            
            // 添加记忆卡片
            data.memories.forEach(memory => {
                memoriesGrid.appendChild(createMemoryCard(memory));
            });
            
            // 添加记忆使用记录
            data.memory_usage.forEach(usage => {
                memoryUsageList.appendChild(createUsageItem(usage));
            });
            
        } catch (error) {
            console.error('加载记忆数据失败:', error);
            memoriesGrid.innerHTML = '<p class="error">加载记忆数据失败，请稍后重试。</p>';
        }
    }

    // 初始加载
    loadMemories();

    // 每60秒刷新一次数据
    setInterval(loadMemories, 60000);
});
