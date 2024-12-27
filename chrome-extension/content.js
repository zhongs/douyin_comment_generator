// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getVideoInfo') {
    const videoInfo = extractVideoInfo();
    sendResponse(videoInfo);
  }
  return true; // 保持消息通道开启
});

// 从页面提取视频信息
function extractVideoInfo() {
  try {
    // 尝试多个可能的选择器来获取视频标题
    const selectors = [
      // 视频详情页
      '.video-info-detail .title',
      '.video-title-container .title',
      '.video-info-container .title',
      // 发现页
      '.xgplayer-video-title',
      '[data-e2e="video-title"]',
      // 其他可能的选择器
      '.video-meta-title',
      '.title-container',
      // 视频描述
      '.video-info-detail .desc',
      '.video-desc',
      '[data-e2e="video-desc"]'
    ];

    let title = '';
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        title = element.textContent.trim();
        if (title) break;
      }
    }

    // 如果还是没有找到标题，尝试从URL中提取信息
    if (!title) {
      const urlMatch = window.location.pathname.match(/\/video\/(\d+)/);
      if (urlMatch) {
        title = `抖音视频 ${urlMatch[1]}`;
      }
    }

    // 如果仍然没有标题，使用页面标题
    if (!title) {
      title = document.title.replace(' - 抖音', '').trim();
    }

    if (!title) {
      throw new Error('无法获取视频标题');
    }

    return {
      title: title,
      url: window.location.href
    };
  } catch (error) {
    console.error('提取视频信息失败:', error);
    return null;
  }
}
