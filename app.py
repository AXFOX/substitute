import tkinter as tk
from tkinter import filedialog
import DataProcessing as dp
# -*- coding: utf-8 -*-


# 预定义的字幕句子和文稿句子数组
subtitle_sentences=[]
manuscript_sentences=[]


# 打开待处理字幕文件并读取内容
def open_file_1():
    file_path = filedialog.askopenfilename()  # 弹出文件选择对话框
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:  # 指定utf-8编码读取文件
            content = file.read()
        text_box1.delete(1.0, tk.END)  # 清空文本框内容
        global subtitle_sentences
        # 提取字幕内容部分
        subtitle_sentences = [subtitle[1] for subtitle in dp.extract_subtitles_lines(content)]  
        #print(subtitle_sentences)
        # 插入每个字幕句子到文本框
        text_box1.insert(tk.END, "\n".join(subtitle_sentences) + "\n")
    else:
        return



# 打开原始稿件文本并读取内容 处理并展示分割后的文稿句子
def open_file_2():
    file_path = filedialog.askopenfilename()  # 弹出文件选择对话框
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:  # 指定utf-8编码读取文件
            content = file.read()
        text_box2.delete(1.0, tk.END)  # 清空文本框内容
        text_box2.insert(tk.END, content)  # 将文件内容插入到文本框中
        dp.Manuscript = content
        global manuscript_sentences
        if chk_var.get()==True:
            #使用RWKV分句
            manuscript_sentences = dp.chat_with_model(dp.messages, dp.chat_completions_api_url) #分割后的文稿句子数组
        else:
             #使用第三方模型分句
            manuscript_sentences = dp.third_party_split(content,None,1)
           
        text_box2.delete(1.0, tk.END)  # 清空文本框内容
        text_box2.insert(tk.END, "\n".join(manuscript_sentences or []) + "\n")
        #print(manuscript_sentences) #打印文稿句子数组
    if not file_path:
        return



# 清空待处理字幕数组文本框
def clear_text():
    text_box1.delete(1.0, tk.END)


app = tk.Tk()  # 创建主窗口
app.title("Substitute 一款基于RWKV AI00Server的字幕AI替换工具")  # 设置窗口标题

frame = tk.Frame(app)  # 创建一个框架，用于放置按钮
frame.pack(pady=20, side=tk.RIGHT)  # 将框架放置在右侧，并添加垂直间距

# 创建“选择文件1”按钮，点击时调用 open_file_1 函数
btn_file_1 = tk.Button(frame, text="选择.ass字幕文件", command=open_file_1)
btn_file_1.pack(pady=5)  # 设置按钮的垂直间距

# 创建“选择文件2”按钮，点击时调用 open_file_2 函数
btn_file_2 = tk.Button(frame, text="选择已有文稿", command=open_file_2)
btn_file_2.pack(pady=5)

# 创建“清空待处理字幕数组”按钮，点击时调用 clear_text 函数
btn_clear = tk.Button(frame, text="Clear Text", command=clear_text)
btn_clear.pack(pady=5)

# 创建“退出”按钮，点击时退出程序
btn_exit = tk.Button(frame, text="Exit", command=app.quit)
btn_exit.pack(pady=5)

# 创建“RWKV分句”候选框，点击时勾选
chk_var = tk.BooleanVar()
chk_rwkv = tk.Checkbutton(frame, text="RWKV分句", variable=chk_var)
chk_rwkv.pack(pady=5)


# 创建文本框，用于显示待处理字幕数组
text_box1 = tk.Text(app, wrap='word', width=50, height=15)
text_box1.pack(pady=20, side=tk.LEFT)  # 将文本框放置在左侧，并添加垂直间距

# 创建文本框，用于显示原始稿件文本
text_box2 = tk.Text(app, wrap='word', width=50, height=15)
text_box2.pack(pady=20, side=tk.LEFT)  # 将文本框放置在左侧，并添加垂直间距



def get_subtitles_embeddings():
        subtitles_embeddings = []
        for sentence in subtitle_sentences:
            embedding = dp.get_embeds(sentence)
            subtitles_embeddings.append((sentence, embedding))  # 向列表中创建并添加元组[（句子,嵌入式向量), ...]
        return subtitles_embeddings
def get_manuscripts_embeddings():
        manuscripts_embeddings = []
        if manuscript_sentences is None:
            return []
        for sentence in manuscript_sentences:
            embedding = dp.get_embeds(sentence)
            manuscripts_embeddings.append((sentence, embedding))
        #print(manuscripts_embeddings)
        return manuscripts_embeddings

def get_similarity():
        # 获取字幕和文稿的嵌入向量
        subtitles_embeddings = get_subtitles_embeddings()  # 返回 [(句子, 嵌入向量), ...]
        manuscripts_embeddings = get_manuscripts_embeddings()  # 返回 [(句子, 嵌入向量), ...]
        # 存储结果：字幕句子、最相似的文稿句子、相似度
        similar_pairs = []
        #初始化循环次数
        round = 0 
        index = 0
        # 遍历每个字幕句子及其嵌入向量
        for index in subtitles_embeddings:
            max_similarity = -1  # 初始化最大相似度
            most_similar_sentence = None  # 保存最相似的文稿句子
            #计算n字幕句子与n文稿句子的相似度
            index = round
            now_similarity=dp.cosine_similarity(subtitles_embeddings[index][1], manuscripts_embeddings[index][1])
            round += 1 #循环次数加1
            # 如果相似度大于最大相似度，则更新最大相似度和最相似的文稿句子
            if now_similarity > max_similarity:
                subtitle_sentence = subtitles_embeddings[index][0]
                max_similarity = now_similarity
                most_similar_sentence = manuscripts_embeddings[index][0]
                # 将结果添加到列表中
                similar_pairs.append((subtitle_sentence,most_similar_sentence,max_similarity))

        
        return similar_pairs

txt="""今天是2025年1月16日星期四 ，欢迎来到硬核灌水，以下是本期的主要内容。

Fedora 42 正在考虑将其Live安装镜像切换到 EROFS
来源： Michael Larabel

Fedora 42 计划将其 live 安装镜像的文件系统从 SquashFS 切换为 EROFS，这项提案今天已提交。当前 Fedora Linux 的 live 安装介质使用 SquashFS 文件系统，但根据这项变更提案，Fedora 42 所有由 Kiwi 制作的 live 媒体，包括 Fedora KDE Desktop、Fedora Budgie、Fedora Xfce、Fedora COSMIC 等版本，将改为使用 EROFS，同时 Fedora CoreOS 的 live 安装镜像也会采用 EROFS。提案认为 EROFS 相较于 SquashFS 更积极地进行开发，且支持更多现代文件系统特性，能够在未来得到更好的应用。EROFS 自 2019 年由华为提出以来，已经增加了许多功能和优化，尤其在移动设备、嵌入式系统和容器中得到了广泛应用。需要注意的是，这项变更仅涉及 live 安装镜像，EROFS 会作为只读文件系统使用。此变更提案仍需通过 Fedora 工程与指导委员会（FESCo）的投票批准。
小石： 为了现代化，我相信大部分人都会毫不犹豫的支持这一变化。
"""
def test():
    #test1=get_manuscripts_embeddings()
    test1=dp.third_party_split(txt)
    print(test1)
    with open("test_output.txt", "w", encoding="utf-8") as file:
        file.write(f"{test1}\n")

    print(f"test end")
    return
   


# 创建“保存文件”按钮，点击时调用 save_file 函数
#btn_save = tk.Button(frame, text="保存修改后的字幕文件", command=save_file)
#btn_save.pack(pady=5)

# 创建“测试”按钮，点击时执行测试程序
btn_test = tk.Button(frame, text="Test", command=test)
btn_test.pack(pady=5)
# 启动应用程序
app.mainloop()
