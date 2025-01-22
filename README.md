
## 关于本项目
依赖AI00 Server （RWKV）驱动，暂不支持调用其他模型。
~~当前仅适用于Linux 用户。~~

## 使用方式
```shell
git clone https://github.com/AXFOX/substitute
cd substitute
python3 ./app.py
```
在此之前，确保你已经下载了ai00 且启用了api/oai/embeds功能。
### 如何启用embeds功能？
你需要取消几行注释
参见：https://rwkv.cn/ai00/Ai00-API#apioaiembeds
ai00server默认使用了镜像站，无需担心模型下载困难。
依次选择待处理的kdenlive .ass字幕文件和文稿，点击test选择文件以保存。
当前已知的问题是原始字幕分句错乱可能导致新字幕连续重复，通常不会明显影响正常观看，有空了继续优化相关内容。

## 为什么是RWKV？
~~如果OpenAI现在以MIT协议公开ChatGPT的全部数据和训练过程，也许我会考虑用ChatGPT。~~
自由软件用户们需要一个不受限于Nvdia CUDA和AMD ROCm亦或者别的什么硬件公司开发的某某框架限制的通用AI加速选项，
现在我们找到了————Vulkan。
还需要一个允许任何用户不受限制使用的AI模型，我们找到了RWKV。
----
感谢在本项目开发过程中提供指导和帮助的各位大佬
@cgisky1980
@LeoLin4258
以及众多热心的群友。
谢谢！❤️

# To-Do List
佛系，想写就写，不想写了玩游戏。
## 优化功能
- [x] Windows 平台支持  
- [ ] 其他大语言模型支持  
- [ ] 更好的 GUI  

## 其他可能的改进
- [ ] 提供多平台安装包（如 macOS、Linux）    
- [ ] 支持自定义配置 
- [ ] 提供暗黑模式和主题切换  
- [ ] 添加用户反馈入口  
