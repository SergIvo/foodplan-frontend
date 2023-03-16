import re


def wrap_static(name):
    rewrapped = name.replace('"', "'")
    return '"{% static ' + rewrapped + ' %}"'


def wrap_all(text, pattern=None):
    if pattern:
        matches = re.findall(r'"img/.+?"', new_cont)
    else:
        matches = re.findall(r'"img/.+?"', text)
    
    new_text = text
    for match in matches:
        new_cont = new_text.replace(match, wrap_static(new_text))
    print(f'{len(matches)} matches replaced')
    return new_text


def rewrite_file(filename):
    with open(filename, 'r') as source_file:
        content = source_file.read()
    
    new_file = wrap_all(content)
    with open(filename, 'w') as _file:
        _file.write(new_file)
        _file.close()
