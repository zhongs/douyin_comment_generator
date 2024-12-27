document.addEventListener('DOMContentLoaded', function() {
  const generateBtn = document.getElementById('generateBtn');
  const copyBtn = document.getElementById('copyBtn');
  const loading = document.getElementById('loading');
  const result = document.getElementById('result');
  const copySuccess = document.getElementById('copySuccess');

  generateBtn.addEventListener('click', async () => {
    // 显示加载状态
    loading.style.display = 'block';
    result.textContent = '';
    generateBtn.disabled = true;
    copyBtn.style.display = 'none';
    copySuccess.style.display = 'none';

    try {
      // 获取当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // 检查是否在抖音网站
      if (!tab.url.includes('douyin.com')) {
        throw new Error('请在抖音视频页面使用此插件');
      }

      // 注入content script
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });

      // 等待一小段时间确保content script加载完成
      await new Promise(resolve => setTimeout(resolve, 500));

      // 向content script发送消息获取视频信息
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'getVideoInfo' });
      
      if (!response || (!response.title && !response.url)) {
        throw new Error('无法获取视频信息');
      }

      // 调用API生成评论
      const comment = await generateComment(response.title, response.url);
      result.textContent = comment;
      
      // 显示复制按钮
      copyBtn.style.display = 'block';
    } catch (error) {
      console.error('Error:', error);
      result.textContent = `错误: ${error.message}`;
    } finally {
      loading.style.display = 'none';
      generateBtn.disabled = false;
    }
  });

  // 复制按钮点击事件
  copyBtn.addEventListener('click', async () => {
    const comment = result.textContent;
    if (!comment) return;

    try {
      await navigator.clipboard.writeText(comment);
      copySuccess.style.display = 'block';
      setTimeout(() => {
        copySuccess.style.display = 'none';
      }, 2000);
    } catch (err) {
      console.error('复制失败:', err);
      // 使用备用复制方法
      const textarea = document.createElement('textarea');
      textarea.value = comment;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      copySuccess.style.display = 'block';
      setTimeout(() => {
        copySuccess.style.display = 'none';
      }, 2000);
    }
  });
});

async function generateComment(title, url) {
  const API_ENDPOINT = 'https://proxy.hizs.top/api/generate';
  const response = await fetch(API_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: title,
      url: url
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API请求失败');
  }

  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'API返回错误');
  }
  return data.comment;
}
