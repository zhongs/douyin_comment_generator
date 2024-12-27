// 监听插件安装事件
chrome.runtime.onInstalled.addListener(() => {
  console.log('抖音评论生成器插件已安装');
});

// 可以在这里添加其他后台任务，比如：
// - API token的管理
// - 请求限流
// - 缓存管理等
