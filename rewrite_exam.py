# -*- coding: utf-8 -*-
"""在 index.html 最后一个 </script> 之前插入真题 JS 块（幂等：先删除旧块）"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML = r"e:\해외에 가다\韩语单词\index.html"
NEW_JS = r"e:\해외에 가다\韩语单词\exam_js_new.js"

with open(HTML, "r", encoding="utf-8") as f:
    html = f.read()
with open(NEW_JS, "r", encoding="utf-8") as f:
    new_js = f.read()

# 1) 定位旧真题 JS 块（从精确注释行到 </script> 前）
start_marker = "// ===== EXAM (真题生词库"
start = html.find(start_marker)
end = html.rfind("</script>")
if end == -1:
    print("!! 未找到 </script>")
    sys.exit(1)

# 2) 截出块之前的内容，并归一化尾部空行（保证反复运行不会不断堆积空行）
if start != -1:
    prefix = html[:start].rstrip("\n")
    print("已定位旧真题 JS 块，将替换")
else:
    prefix = html[:end].rstrip("\n")
    print("未发现旧真题 JS 块（首次插入）")

# 3) 重新拼接：prefix + 空行 + 规范化后的块 + 换行 + </script> 之后的内容
block = new_js.strip("\n")
html = prefix + "\n\n" + block + "\n" + html[end:]

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("真题 JS 块已插入，字符数:", len(new_js))