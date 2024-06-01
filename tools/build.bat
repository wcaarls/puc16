pyinstaller -F as.py
pyinstaller -F cc.py --add-data ppci\codegen\burg.grammar;ppci\codegen
