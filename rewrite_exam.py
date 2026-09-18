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

# 1) 删除旧的真题 JS 块（从精确注释行到该块结束于 </script> 前）
start_marker = "// ===== EXAM (真题生词库"
start = html.find(start_marker)
if start != -1:
    end = html.rfind("</script>")
    # 找到 EXAM 块结束的最后一个 document.addEventListener 之后；直接截到 </script>
    html = html[:start] + html[end:]
    print("已删除旧真题 JS 块")
else:
    print("未发现旧真题 JS 块（首次插入）")

# 2) 在最后一个 </script> 前插入新块
end = html.rfind("</script>")
if end == -1:
    print("!! 未找到 </script>")
    sys.exit(1)
html = html[:end] + "\n" + new_js + "\n" + html[end:]

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("真题 JS 块已插入，字符数:", len(new_js))