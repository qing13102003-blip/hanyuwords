import re
content=open(r'e:\해외에 가다\韩语单词\index.html',encoding='utf-8').read()

# 检查setLevel函数是否只刷新首页
m=re.search(r'function setLevel\(id\)\{.*?\n\