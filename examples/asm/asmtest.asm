        b @inst

; .org
        .org 0x5

; label, .equ
mylbl:  .equ equ1, 0x2a

; .db
.section data
        .org 0x20
        .dw 123
        .dw 0x2a
        .dw @mylbl2
        .org 0x40
mylbl2: .dw "Hello, world"
        .dw 123, 0x2a, @mylbl2, "Hello, world"

.section code

; .macro
; local labels
        .macro macro1
_loop:  b @_loop
        .endmacro
        macro1
        macro1

; .macro
; arguments
        .macro macro2
_loop:  mov r1, $0
        mov r1, $1
        macro1
        b @_loop
        .endmacro
        macro2 0xAA, 0x55

; Instructions
inst:   ldr  r1, [r2]
        ldr  r1, [r2, 1]
        str  r1, [r2]
        str  r1, [r2, 1]
        mov  r1, 12
        movt r1, 0x55
        mov  r1, "a"
        mov  r1, @equ1
        mov  r1, r2

        push r1
        pop  r1

        add r1, r2, r3
        add r1, r2, 1
        sub r1, r2, r3
        sub r1, r2, 1
        shft r1, r2, 1
        shft r1, r2, -1
        and r1, r2, r3
        or  r1, r2, r3
        xor r1, r2, r3

        b 1
        b @mylbl

        bz 1
        beq 1
        bnz 1
        bne 1
        bcs 1
        bhs 1
        bcc 1
        blo 1

        jmp 1
        ret
