# debug_real_request.py
import requests
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 直接使用 requests 获取原始响应
headers = {
    'X-Pcombi': 'test.drama.short',
    'X-Dtas-Ttill': 'ANDROID',
    'X-Rres-Iangle': 'test_device_001',
    'X-Dstaff-Langle': 'test_distinct_001',
    'X-Rres-Langle': 'req_001',
    'X-Cspec-Vasso': 'V2',
    'X-Tove': '1780036173893',
}

payload = {
    "dper": "test_distinct_001",
    "cconce": "US",
    "sleave": "fb",
    "umai": 1
}

try:
    response = requests.post(
        'https://rptv-db-api-test.playapp365.com/api/ulov/uplace/lshin',
        headers=headers,
        json=payload,
        timeout=10
    )

    print("状态码:", response.status_code)
    print("\n响应头:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\n响应体 (前500字符):")
    print(response.text[:500])

    # 保存响应供调试
    response_file = PROJECT_ROOT / 'src' / 'core' / 'raw_response.txt'
    with response_file.open('w', encoding='utf-8') as f:
        f.write(f"Headers:\n")
        for key, value in response.headers.items():
            f.write(f"{key}: {value}\n")
        f.write(f"\nBody:\n{response.text}")

    print(f"\n✅ 响应已保存到: {response_file}")

except Exception as e:
    print(f"请求失败: {e}")
