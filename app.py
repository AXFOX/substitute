import tkinter as tk
from tkinter import filedialog
import DataProcessing as dp
# -*- coding: utf-8 -*-


# 预定义的字幕句子和文稿句子数组
subtitle_sentences=[]
manuscript_sentences=[]
subtitle_time_info=[]

# 打开待处理字幕文件并读取内容
def open_file_1():
    file_path = filedialog.askopenfilename()  # 弹出文件选择对话框
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:  # 指定utf-8编码读取文件
            content = file.read()
        text_box1.delete(1.0, tk.END)  # 清空文本框内容
        global subtitle_sentences,subtitle_time_info
        # 提取字幕内容部分
        subtitle_sentences = [subtitle[1] for subtitle in dp.extract_subtitles(content)]  
        # 提取字幕时间信息部分
        subtitle_time_info = [subtitle[0] for subtitle in dp.extract_subtitles(content)] 
        #print(subtitle_time_info)
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
            manuscript_sentences = dp.third_party_split(content,36,1)
           
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

# 创建 "合并重复字幕" 候选框，点击时勾选
chk_merge_duplicates = tk.BooleanVar()
chk_merge = tk.Checkbutton(frame, text="合并重复字幕", variable=chk_merge_duplicates)
chk_merge.pack(pady=5)

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
    subtitles_embeddings = get_subtitles_embeddings()  # 返回 [(字幕句子, 嵌入向量), ...]
    manuscripts_embeddings = get_manuscripts_embeddings()  # 返回 [(文稿句子, 嵌入向量), ...]

    # 存储结果：字幕句子、最相似的文稿句子、相似度
    similar_pairs = []

    # 遍历每个字幕句子及其嵌入向量
    for subtitle_sentence, subtitle_embedding in subtitles_embeddings:
        max_similarity = -1  # 初始化最大相似度
        most_similar_sentence = None  # 保存最相似的文稿句子

        # 遍历每个文稿句子及其嵌入向量，计算相似度
        for manuscript_sentence, manuscript_embedding in manuscripts_embeddings:
            try:
                # 计算余弦相似度
                similarity = dp.cosine_similarity(subtitle_embedding, manuscript_embedding)
                # 如果相似度大于最大相似度，则更新
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_sentence = manuscript_sentence
            except Exception as e:
                print(f"Error calculating similarity: {e}")

        # 将当前字幕句子及其最相似文稿句子和相似度添加到结果列表
        similar_pairs.append((subtitle_sentence, most_similar_sentence, max_similarity))

    return similar_pairs

##
# 创建新列表替换原字幕内容[（其他信息，新字幕），...]
##

def replace_subtitles():
    # 用于存储替换后的字幕
    replaced_subtitles = []
    # 获取相似度计算结果
    similar_pairs = get_similarity()
    
    # 遍历每个字幕句子
    for i, time_info in enumerate(subtitle_time_info):
        subtitle, most_similar_sentence, similarity = similar_pairs[i]
        # 如果最相似的文稿句子不为空
        if most_similar_sentence is not None:
            # 将字幕句子替换为最相似的文稿句子
            replaced_subtitles.append((time_info, most_similar_sentence))
        else:
            # 如果最相似的文稿句子为空，则保留原字幕句子
            replaced_subtitles.append((time_info, subtitle))
    # 如果勾选了“合并重复字幕”
    if chk_merge_duplicates.get():
        replaced_subtitles = dp.merge_repeated_subtitles(replaced_subtitles)
    return replaced_subtitles
##   
# 保存替换后的字幕
##
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".ass", filetypes=[("ASS files", "*.ass"), ("All files", "*.*")])
    if file_path:
        replaced_subtitles = replace_subtitles()
        with open(file_path, 'w', encoding='utf-8') as file:
            # 写入subtitle_other_info作为文件开头
            file.write(dp.other_info + "\n")
            print(dp.other_info)
            # 写入替换后的字幕内容
            for time_info, new_subtitle in replaced_subtitles:
                new_subtitle = new_subtitle.replace('\n', '')  # 删除换行符
                file.write(f"{time_info}{new_subtitle}\n")
    

def test():
    #test1=get_manuscripts_embeddings()
    test1=save_file()
    #print(test1)
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
