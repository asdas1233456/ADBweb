"""
测试AI连接
"""
import httpx
import asyncio

async def test_connection():
    api_key = "sk-afb993040f0e4b5a8b9ce0f8523a5875"
    api_base = "https://api.deepseek.com/v1"
    
    print(f"测试连接到: {api_base}")
    print(f"API Key: {api_key[:20]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n发送测试请求...")
            response = await client.post(
                f"{api_base.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "max_tokens": 10
                }
            )
            
            print(f"\n状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                model = result.get("model", "Unknown")
                print(f"\n✅ 连接成功！")
                print(f"模型: {model}")
                return True
            else:
                print(f"\n❌ 连接失败")
                return False
                
    except httpx.TimeoutException as e:
        print(f"\n❌ 连接超时: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
