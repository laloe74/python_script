# 
# 将本地诗歌网页的HTML文件批量转换成Markdown格式
# pip install html2markdown beautifulsoup4
#

import glob
import html2markdown
import sys
import os
import re
import html
from bs4 import BeautifulSoup

# 获取用户桌面的路径
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

# 设置输入和输出目录
input_directory = os.path.join(desktop_path, 'from')
output_directory = os.path.join(desktop_path, 'to')

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def remove_html_tags_and_special_chars(text):
    """使用正则表达式去除HTML标签，并替换特殊字符"""
    text = re.sub(r'&nbsp;', ' ', text)  # 替换&nbsp;为一个空格
    text = re.sub(r'&lt;', '<', text)    # 替换&lt;为
    text = re.sub(r'&gt;', '>', text)    # 替换&gt;为>
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_html_to_md(src_path):
    file_name = os.path.basename(src_path)
    md_name = file_name.replace("html", "md")
    md_path = os.path.join(output_directory, md_name)
    
    with open(src_path, 'r', encoding="utf-8") as sw:
        html_content = sw.read()

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        h2_tag = soup.find('h2')
        
        if h2_tag:
            first_div = h2_tag.find_next('div')
            if first_div:
                # 保留第一个 <div> 标签中的内容
                html_content = str(first_div)
        
        # 删除所有 <br> 标签
        html_content = re.sub(r'<br\s*/?>', '', html_content)

        # 将 HTML 实体转换为正常字符
        html_content = html.unescape(html_content)

        md_str = html2markdown.convert(html_content)
        
        # 进一步处理 Markdown 内容
        cleaned_md = remove_html_tags_and_special_chars(md_str)
        
        with open(md_path, "w", encoding="utf-8") as fo:
            fo.write(cleaned_md)
            print(f"Converted and processed {file_name} to {md_name}")

if __name__ == "__main__":
    for html_file in glob.glob(os.path.join(input_directory, "*.html")):
        convert_html_to_md(html_file)
    print("All files have been processed.")