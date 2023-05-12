"""Pretty-print Python code to colorized, hyperlinked html.

In python, do:
    py2html.convert_files(['file1.py', 'file2.py', ...]) 
From the shell, do:
    python py2html.py *.py"""

import re, string, time, os

try:
    cmp             # Python 2
except NameError:
    def cmp(x, y):  # Python 3
        return (x > y) - (x < y)

id = r'[a-zA-Z_][a-zA-Z_0-9]*' ## RE for a Python identifier
g1, g2, g3, g4 = r'\1 \2 \3 \4'.split() ## groups for re.matches
def b(text):
    return f'<b>{text}</b>'
def i(text):
    return f'<i>{text}</i>'
def color(rgb, text):
    return f'<font color="{rgb}">{text}</font>'
def link(url, anchor):
    return f'<a href="{url}">{anchor}</a>'
def hilite(text, bg="ffff00"):
    return f'<b style="background-color:{bg}"><a name="{text}">{text}</b>'

def modulelink(module, baseurl=''):
    """Hyperlink to a module, either locally or on python.org"""
    if f'{module}.py' not in local_files:
        baseurl = 'http://www.python.org/doc/current/lib/module-'
    return link(baseurl+module+'.html', module)

def importer(m):
    "Turn text such as 'utils, math, re' into a string of HTML links."
    modules = [modulelink(mod.strip()) for mod in m.group(2).split(',')]
    return (m.group(1) + ', '.join(modules) + m.group(3))

def find1(regex, str):
    return (re.findall(regex, str) or ['&nbsp;'])[0]

def convert_files(filenames, local_filenames=None, tblfile='readme.htm'):
    "Convert files of python code to colorized HTML."
    global local_files
    local_files = local_filenames or filenames
    summary_table = {}
    for f in filenames:
        fulltext = '\n'.join(map(string.rstrip, open(f).readlines()))
        text = fulltext
        for (pattern, repl) in replacements:
            text = re.sub(pattern, repl, text)
        text = f'<<header("AIMA Python file: {f}")>><pre>{text}</pre><<footer>>'
        open(f'{f[:-3]}.htm', 'w').write(text)
        if tblfile:
            ch = find1(r'Chapters?\s+([^ \)"]*)', fulltext)
            module = f.replace('.py','')
            lines = fulltext.count('\n')
            desc = find1(r'"""(.*)\n', fulltext).replace('"""', '')
            summary_table.setdefault(ch,[]).append((module, lines, desc))
    if tblfile:
        totallines = 0
        tbl = ["<tr><th>Chapter<th>Module<th>Files<th>Lines<th>Description"]
        fmt = "<tr><td align=right>%s<th>%s<td>%s<td align=right>%s<td>%s"
        items = summary_table.items()
        items.sort(num_cmp)
        for (ch, entries) in items:
            for (module, lines, desc) in entries:
                totallines += lines
                files = link(f'{module}.py', '.py')
                if os.path.exists(f'{module}.txt'):
                    files += ' ' + link(f'{module}.txt', '.txt')
                tbl += [(fmt % (ch, link(f'{module}.html', module), files, lines, desc))]
        tbl += [fmt % ('', '', '', totallines, ''), "</table>"]
        ## Now read the tblfile, and replace the first table with tbl
        old = open(tblfile).read()
        new = re.sub("(?s)(<table border=1>)(.*)(</table>)", 
                     r'\1' + '\n'.join(tbl) + r'\3', old, 1)
        open(tblfile, 'w').write(new)

def num_cmp(x, y):
    def num(x):
        nums = re.findall('[0-9]+', x or '')
        return int(nums[0]) if nums else x

    return cmp(num(x[0]), num(y[0]))

### Above is general (more or less); below is specific to my files.

def comment(text): return i(color("green", text))

replacements = [
    (r'&', '&amp;'),
    (r'<', '&lt;'),
    (r'>', '&gt;'),
    (r'(?ms)^#+[#_]{10,} *\n', '<hr>'),
    (r"""('[^']*?'|"[^"]*?")""", comment(g1)),
    (r'(?s)(""".*?"""|' + r"'''.*?''')", comment(g1)),
    (r'(#.*)', color("cc33cc", g1)),
    (r'(?m)(^[a-zA-Z][a-zA-Z_0-9, ]+)(\s+=\s+)', hilite(g1) + g2),
    (r'(?m)(^\s*)(def\s+)(%s)' % id, g1 + b(g2) + hilite(g3)),
    (r'(?m)(^\s*)(class\s+)(%s)' % id, g1 + b(g2) + hilite(g3)),
    (r'(from\s+)([a-z]+)(\s+import)', importer),
    (r'(import\s+)([a-z, ]+)(\s|\n|$|,)', importer),
    ]

if __name__ == '__main__':
    import sys, glob
    files = []
    for arg in sys.argv[1:]:
        files.extend(glob.glob(arg))
    convert_files(files) 

## ENHANCEMENTS:
## Can get confused with """ and '''; not a problem in practice.
## Maybe we should create an index 
## Probably should switch to Doxygen
