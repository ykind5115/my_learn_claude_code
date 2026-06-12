import os
import json
import httpx
from dotenv import load_dotenv
from anthropic import Anthropic

# 1. 加载 .env 配置文件
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
MODEL_ID = os.getenv("MODEL_ID", "kimi-k2.5")

# 测试用的同一个问题
SYSTEM_PROMPT = "你是一个精简的助手。"
USER_PROMPT = "请用一句话解释什么是‘魔改代码’。"

print(f"📡 目标模型: {MODEL_ID}")
print(f"🌐 目标 Base URL: {BASE_URL}")
print("-" * 60)

# =====================================================================
# 方法一：使用原生 HTTPX 请求（手动封装）
# =====================================================================
def test_raw_http():
    print("\n🚀 [方法一] 开始发起原生 HTTP 请求...")
    
    # 1. 改为 Kimi 官方原生的标准 OpenAI 协议路径
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 2. 改为 OpenAI 标准的认证头 Bearer
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 3. 改为 OpenAI 标准的请求体结构 (messages 结构一致，但去掉了 system 顶层字段)
    payload = {
        "model": MODEL_ID,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT}, # OpenAI 协议中 system 放在 messages 列表里
            {"role": "user", "content": USER_PROMPT}
        ]
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        
        print("\n📥 [HTTP 原始状态码]:", response.status_code)
        
        raw_json = response.json()
        print("\n📥 [HTTP 原始响应 JSON (Raw Data)]:")
        print(json.dumps(raw_json, indent=2, ensure_ascii=False))
        
        # 4. 改为 OpenAI 标准的解析方式
        content_text = raw_json["choices"][0]["message"]["content"]
        print(f"\n📝 [HTTP 解析出来的文本]: {content_text}")
        return raw_json
# =====================================================================
# 方法二：使用 Anthropic 官方 SDK 调用
# =====================================================================
def test_sdk():
    print("\n🚀 [方法二] 开始使用 Anthropic SDK 请求...")
    
    # 这里的凭证解析就是你之前在 _client.py 源码里看到的逻辑
    client = Anthropic(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    # 获取原始 HTTP 响应的方法是使用 .with_raw_response
    raw_response = client.messages.with_raw_response.create(
        model=MODEL_ID,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT}
        ]
    )
    
    print("\n📥 [SDK 原始状态码]:", raw_response.status_code)
    
    # 将 SDK 获取的原始响应转化为文本/JSON
    raw_json = json.loads(raw_response.text)
    print("\n📥 [SDK 原始响应 JSON (Raw Data)]:")
    print(json.dumps(raw_json, indent=2, ensure_ascii=False))
    
    # 如果用正常的 SDK 方式（非 with_raw_response），则是对象化操作：
    # message = client.messages.create(...)
    # print(message.content[0].text)
    
    content_text = raw_json["content"][0]["text"]
    print(f"\n📝 [SDK 解析出来的文本]: {content_text}")
    return raw_json

# =====================================================================
# 执行对比
# =====================================================================
if __name__ == "__main__":
    if not API_KEY or not BASE_URL:
        print("❌ 错误：请确保 .env 文件中配置了 ANTHROPIC_API_KEY 和 ANTHROPIC_BASE_URL")
        exit(1)
        
    http_data = test_raw_http()
    print("=" * 60)
    sdk_data = test_sdk()
    
    print("\n" + "="*25 + " 对比结论 " + "="*25)
    if http_data.get("id") == sdk_data.get("id") or http_data.keys() == sdk_data.keys():
        print("✅ 实验证明：两者的原始 JSON 结构、Key 键完全一致！")
        print("💡 结论：SDK 并没有改变模型的回答格式，它只是在后台帮你发了 HTTP 请求，并把这些 JSON 包装成了 Python 对象（Class）。")
    else:
        print("❓ 结构有差异，可能是上游服务对两次请求的响应有所不同。")