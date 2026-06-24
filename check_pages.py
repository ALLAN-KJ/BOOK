import re

with open('server/static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all pages
pages = re.findall(r'<div class="page" id="(p\d+)"[^>]*>(.*?)</div></div></div>', c, re.DOTALL)
for p_id, p_content in pages:
    print(f"\n--- {p_id} ---")
    navs = re.findall(r'<button class="pnb" onclick="((?:un)?turnPage\(\d+\))">(.*?)</button>', p_content)
    for a, b in navs:
        print(f"  {a}: {b.encode('ascii', 'ignore').decode('ascii')}")
