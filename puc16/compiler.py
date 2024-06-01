"""C compiler for ENG1448 16-bit processor
   (c) 2020-2024 Wouter Caarls, PUC-Rio
"""

from io import StringIO

from .ppci.lang.c import c_to_ir
from .ppci.api import ir_to_assembly, optimize

def compile(src, opt_level):
    asm = """
.section io
btn: .dw 0
enc: .dw 0
kdr: .dw 0
udr: .dw 0
usr: .dw 0
led: .dw 0
ssd: .dw 0
ldr: .dw 0
lcr: .dw 0

.section code

add r12, r15, 2
push r12
jmp @main
loop: b @loop
"""
    ir_module = c_to_ir(src, 'puc16')
    optimize(ir_module, level=opt_level)

    ppci_asm = StringIO(ir_to_assembly([ir_module], 'puc16'))

    lbl = ''
    for l in ppci_asm.readlines():
        l = l.lstrip().rstrip()
        if l.startswith('global') or l.startswith('type') or l.startswith('ALIGN'):
            pass
        elif l.endswith(':'):
            if lbl != '':
                lbl += '\n'
            lbl += l + ' '
        elif l.startswith('.byte'):
            asm += lbl + ' .dw' + l[5:] + '\n'
            lbl = ''
        elif l.startswith('section'):
            asm += lbl + ' .' + l + '\n'
            lbl = ''
        else:
            asm += lbl + l + '\n'
            lbl = ''

    return asm
