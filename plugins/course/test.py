import fitz
import os
import re
from datetime import datetime, timedelta
import requests

url = 'https://jw.njcit.cn/jwglxt/kbcx/xskbcx_cxXsShcPdf.html?doType=list'
response = requests.get(url, stream=True)

# 检查请求是否成功
if response.status_code == 200:
    full_path = os.path.join('.', 'data', '课表.pdf')
    if os.path.exists(os.path.join('.', 'data', '课表.pdf')):
        os.remove(os.path.join('.', 'data', '课表.pdf'))

    with open(full_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # 过滤掉空的chunks
                file.write(chunk)
