import requests
import json
import numpy as np
# API 地址
api_url="http://localhost:65530"
chat_completions_api_url = api_url+"/api/oai/chat/completions"
embeddings_api_url=api_url+"/api/oai/embeds"

###
#               当前含错字幕数组
###

# 提取待处理的字幕句子 并返回字幕数组[(时间戳等信息，字幕句子),...]
def extract_subtitles_lines(ass_content):
    subtitles = []
    # 按行遍历传入的字幕内容
    for line in ass_content.splitlines():
        if line.startswith("Dialogue:"):  # 找到以Dialogue开头的行
            # 删除开头的前52个字符并将结果存入subtitles列表
            other_info=line[:52].strip()
            subtitle_text = line[52:].strip()  # 删除前52个字符并去掉两端空白
            subtitles.append((other_info,subtitle_text))
    
    return subtitles


###
#          分割原始稿件文本获得待选用字幕数组
###


def chat_with_model(messages, api_url):
    # 设置API请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 构建请求数据
    data = {
        "messages": messages,  # 对话历史记录
        "names": {
            "assistant": "Assistant",
            "user": "User"
        },
        "sampler_override": {
            "frequency_penalty": 0.3,
            "penalty": 400,
            "penalty_decay": 0.99654026,
            "presence_penalty": 0.3,
            "temperature": 1,
            "top_k": 128,
            "top_p": 0.5,
            "type": "Nucleus"
        },
        "stop": ["\n\nUser:"], 
        "stream": False,  
        "max_tokens": 1000  
    }

    # 发送POST请求
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            result = response.json()
            # 获取生成的消息内容
            generated_message = result['choices'][0]['message']['content'].strip()
            
            # 返回生成的内容
            return generated_message
        except (json.JSONDecodeError, KeyError) as e:
            return f"解析返回数据时发生错误：{e}"
    else:
        return f"请求失败，错误代码：{response.status_code}"

"""
Manuscript = 
由西部数据编写的 NVMe PCI 端点功能目标代码是即将在 Linux 6.14 内核中首发的一款有趣的新驱动程序。
在 Linux 6.14 合并窗口打开之前，Linux 块子系统的 “for-next ”分支就已经在排队了，它是使用 PCI 端点框架的新 NVMe PCI 目标驱动程序。
有了能在端点模式下运行的 PCI 控制器，就能创建 PCIe NVMe 控制器。
文档补丁详细介绍了该 NVMe 目标驱动程序的所有有趣技术细节。
该驱动程序主要用于测试目的，例如在拥有 PCIe 端点控制器的小型单板计算机上创建一个 NVMe 目标来循环文件或块设备。
也可以使用 TCP 目标来连接远程 NVMe 设备。
"""

Manuscript=""
# 示例对话历史
messages = [
    {"role": "user", "content": "将下列文本分割成适合作为字幕的短句并以数组的形式输出：\n\n今天是2025年1月16日星期四 ，欢迎来到硬核灌水，以下是本期的主要内容。\nFedora 42 正在考虑将其Live安装镜像切换到 EROFS\n来源： Michael Larabel\nFedora 42 计划将其 live 安装镜像的文件系统从 SquashFS 切换为 EROFS，这项提案今天已提交。当前 Fedora Linux 的 live 安装介质使用 SquashFS 文件系统，但根据这项变更提案，Fedora 42 所有由 Kiwi 制作的 live 媒体，包括 Fedora KDE Desktop、Fedora Budgie、Fedora Xfce、Fedora COSMIC 等版本，将改为使用 EROFS，同时 Fedora CoreOS 的 live 安装镜像也会采用 EROFS。"},
    {"role": "assistant", "content": "['今天是2025年1月16日星期四，欢迎来到硬核灌水。','以下是本期的主要内容：', 'Fedora 42 正在考虑将其Live安装镜像切换到EROFS', '来源：Michael Larabel', 'Fedora 42 计划将其live安装介质使用EROFS文件系统，这项提案今天已提交。','当前Fedora Linux的live安装介质使用SquashFS文件系统，','但根据这项变更提案，Fedora42所有由Kiwi制作的Live媒体，','包括Fedora KDE Desktop、Fedora Budgie、Fedora Xfce、FedoraCOSMIC等版本，','将改为使用EROFS，同时Fedora CoreOS的live安装介质也会采用EROFS。']"},
    {"role": "user", "content": f"将下列文本分割成适合作为字幕的短句并以数组的形式输出：\n\n{Manuscript}"}
]

# 调用函数，开始与模型对话
#result = chat_with_model(messages, api_url)

# 打印模型的回复
#print(result)



###
#       获取嵌入向量
### 
def get_embeds(text): # 返回[(句子,嵌入向量),....]
    return third_party_split(text, 510,2)

## 
#  从第三方模型获取分句结果和嵌入式向量 just=1,2,3 分别表示只返回分句结果、只返回嵌入向量、返回分句结果和嵌入向量
##
def third_party_split(text, max_tokens=48, just=3):
        # 最大 token 数 应当与Kdenlive字幕长度相同
        payload = {
            "input": text,
            "max_tokens": max_tokens,
            "prefix": "passage:"
        }
        response = requests.post(embeddings_api_url, json=payload)  # 发送POST请求
        result = []
        try:
            # 确保响应包含 "data"
            response_data = response.json()
            if "data" in response_data:
                for item in response_data["data"]:
                    # 确保 "chunks" 存在
                    if "chunks" in item:
                        for chunk in item["chunks"]:
                            text_chunk = chunk.get("chunk", "")
                            embedding = chunk.get("embed", [])[0]  # 获取嵌入向量
                            if just==2: # 如果只需要嵌入向量
                                result.append(embedding)
                            elif just==3: # 如果需要分句结果和嵌入向量
                                result.append((text_chunk, embedding))
                            else: # 如果只需要分句结果
                                result.append(text_chunk)

                return result
        except Exception as e:
            print(f"Error processing response: {e}")
            return []

# 计算余弦相似度
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1).flatten()
    vec2 = np.array(vec2).flatten()
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
