       .include "def.asm"
       .include "macros.asm"

       writestr "Hello, world!"
halt:  b    @halt
