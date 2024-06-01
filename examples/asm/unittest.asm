; Unit tests for 16-bit ENG1448 processor
; When successful, halts at instruction 254, showing 0b01010101
; When unsuccessful, halts at instruction 255, showing test number (1-38)

       .macro setled
       mov  r12, 0x05
       mov  r13, $0
       str  r13, [r12]
       .endmacro

       .equ const1, 0x55A5
       .equ const2, 0xAA5A

.section data

       .org 3
       .dw  12, 13, 1234, 0x55, "w", "test"

data1: .dw  @const1
data2: .dw  @const2
tmp1:  .dw  0
tmp2:  .dw  0

.section code

; Preparation
main:  setled 1
       mov  r4, low(@const1)
       mov  r5, low(@const1)
       movt r5, high(@const1)
       mov  r10, low(@const2)
       movt r10, high(@const2)

; Jump
j1:    setled 2
       jmp  @b1
       jmp  @err

; Unconditional branch
b1:    setled 3
       b    @b2
       jmp  @err
b2:    jmp  @mov1
       jmp  @err

; Move immediate
mov1:  setled 4
       mov  r0, low(@const1)
       sub  r11, r4, r0
       bz   @movt1
       jmp  @err

; Move immediate top
movt1: setled 5
       mov  r0, low(@const2)
       movt r0, high(@const2)
       sub  r11, r10, r0
       bz   @mov2
       jmp  @err

; Move register
mov2:  setled 6
       mov  r0, r10
       sub  r11, r0, r10
       bz   @ldr1
       jmp  @err

; Load from address
ldr1:  setled 7
       mov  r1, low(@data1)
       movt r1, high(@data1)
       ldr  r0, [r1]
       sub  r11, r5, r0
       bz   @ldr2
       jmp  @err

; Load with positive immediate offset
ldr2:  setled 8
       ldr  r0, [r1, 1]
       sub  r11, r10, r0
       bz   @ldr3
       jmp  @err

; Load with negative immediate offset
ldr3:  setled 9
       mov  r1, low(@data2)
       movt r1, high(@data2)
       ldr  r0, [r1, -1]
       sub  r11, r5, r0
       bz   @str1
       jmp  @err

; Store to address
str1:  setled 10
       mov  r1, low(@tmp1)
       movt r1, high(@tmp1)
       str  r10, [r1]
       ldr  r0, [r1]
       sub  r11, r10, r0
       bz   @str2
       jmp  @err

; Store with positive immediate offset
str2:  setled 11
       mov  r1, low(@tmp1)
       movt r1, high(@tmp1)
       str  r5, [r1, 1]
       ldr  r0, [r1, 1]
       sub  r11, r5, r0
       bz   @str3
       jmp  @err

; Store with negative immediate offset
str3:  setled 12
       mov  r1, low(@tmp2)
       movt r1, high(@tmp2)
       str  r10, [r1, -1]
       ldr  r0, [r1, -1]
       sub  r11, r10, r0
       bz   @push1
       jmp  @err

; Push to stack
push1: setled 13
       mov  r1, low(8190)
       movt r1, high(8190)
       push r5
       sub  r11, r1, r14
       bz   @push2
       jmp  @err
push2: ldr  r0, [r14, 1]
       sub  r11, r5, r0
       bz   @pop1
       jmp  @err

; Pop from stack
pop1:  setled 14
       mov  r1, low(8191)
       movt r1, high(8191)
       mov  r14, r1
       push r10
       pop  r0
       sub  r11, r10, r0
       bz   @pop2
       jmp  @err
pop2:  sub  r11, r1, r14
       bz   @add1
       jmp  @err

; Add two registers
add1:  setled 15
       mov  r1, 0xFF
       movt r1, 0xFF
       add  r0, r5, r10
       sub  r11, r1, r0
       bz   @add2
       jmp  @err

; Add constant to register
add2:  setled 16
       mov  r1, 0xAA
       movt r1, high(@const1)
       add  r0, r5, 0x05
       sub  r11, r1, r0
       bz   @sub1
       jmp  @err

; Subtract two registers
sub1:  setled 17
       mov  r1, 0x55
       sub  r0, r10, r5
       sub  r11, r1, r0
       bz   @sub2
       jmp  @err

; Subtract constant from register
sub2:  setled 18
       mov  r1, 0x50
       sub  r0, r5, 0x05
       sub  r11, r1, r0
       bz   @done
       jmp  @err

done:  jmp  @succ       

       .org 0xFEB

succ:  setled 0x55
ends:  b    @ends

       .org 0xFEF

err:   b    @err
