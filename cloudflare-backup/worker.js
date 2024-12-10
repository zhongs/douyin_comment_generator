export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // 构建转发到 Vercel 的 URL
    const vercelUrl = new URL(url.pathname + url.search, `https://${env.VERCEL_URL}`);
    
    // 创建新的请求，保持原始请求的方法和头部信息
    const modifiedRequest = new Request(vercelUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: 'follow',
    });

    try {
      // 转发请求到 Vercel
      const response = await fetch(modifiedRequest);
      
      // 创建新的响应，添加必要的 CORS 和缓存头
      const modifiedResponse = new Response(response.body, response);
      
      // 添加 CORS 头
      modifiedResponse.headers.set('Access-Control-Allow-Origin', '*');
      
      // 设置缓存策略
      modifiedResponse.headers.set('Cache-Control', 'public, max-age=3600');
      
      return modifiedResponse;
    } catch (error) {
      return new Response(`Error: ${error.message}`, { status: 500 });
    }
  },
};
