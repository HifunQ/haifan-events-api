"""
Render 部署入口文件
"""
import os
from kimi_agent_api import app
import uvicorn

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
