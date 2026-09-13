with open(r'e:\해외에 가다\韩语单词\index.html', 'r', encoding='utf-8') as f:
    html = f.read()
print('File size:', len(html))
idx = html.find('data-nav="grammar"')
print('grammar nav index:', idx)
if idx != -1:
    print('Around nav:', html[idx-100:idx+100])
else:
    print('not found')

idx2 = html.find('const GRAMMAR_DATA')
print('GRAMMAR_DATA index:', idx2)

idx3 = html.find('function renderGrammar')
print('renderGrammar index:', idx3)
