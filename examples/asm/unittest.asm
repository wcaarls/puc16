; Unit tests for 16-bit ENG1448 processor
; When successful, halts at instruction 4094, showing 0b01010101
; When unsuccessful, halts at instruction 4095, showing test number (1-31)

       .macro setled
       mov  r12, 0x05
       mov  r13, $0
       str  r13, [r12]
       .endmacro

; Tests if $0 $1 $2 and !($2 $1 $0)
       .macro btest
       mov  r1, low($0)
       movt r1, high($0)
       mov  r2, low($2)
       movt r2, high($2)
       sub  r0, r1, r2
       b$1  @_good
       jmp  @err
_good: sub  r0, r2, r1
       b$1  @_bad
       b    @_done
_bad:  jmp  @err
_done:
       .endmacro

       .equ const1, 0x55A5
       .equ const2, 0xAA5A

       .equ negsmall, -1987
       .equ neglarge, -28432
       .equ possmall, 9482
       .equ poslarge, 19387

       .equ unssmall, 593
       .equ unslarge, 48128

.section data

       .org 3
       .dw  12, 13, 1234, 0x55, "W", "test"

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
b2:    jmp  @bz1
       jmp  @err

; Branch when zero
bz1:   setled 4
       mov  r0, 1
       mov  r0, r0
       bz   @bz2
       b    @bz3
bz2:   jmp  @err
bz3:   mov  r0, 0
       mov  r0, r0
       bz   @mov1
       jmp  @err

; Move immediate
mov1:  setled 5
       mov  r0, low(@const1)
       sub  r11, r4, r0
       bz   @movt1
       jmp  @err

; Move immediate top
movt1: setled 6
       mov  r0, low(@const2)
       movt r0, high(@const2)
       sub  r11, r10, r0
       bz   @mov2
       jmp  @err

; Move register
mov2:  setled 7
       mov  r0, r10
       sub  r11, r0, r10
       bz   @ldr1
       jmp  @err

; Load from address
ldr1:  setled 8
       mov  r1, low(@data1)
       movt r1, high(@data1)
       ldr  r0, [r1]
       sub  r11, r5, r0
       bz   @ldr2
       jmp  @err

; Load with positive immediate offset
ldr2:  setled 9
       ldr  r0, [r1, 1]
       sub  r11, r10, r0
       bz   @ldr3
       jmp  @err

; Load with negative immediate offset
ldr3:  setled 10
       mov  r1, low(@data2)
       movt r1, high(@data2)
       ldr  r0, [r1, -1]
       sub  r11, r5, r0
       bz   @str1
       jmp  @err

; Store to address
str1:  setled 11
       mov  r1, low(@tmp1)
       movt r1, high(@tmp1)
       str  r10, [r1]
       ldr  r0, [r1]
       sub  r11, r10, r0
       bz   @str2
       jmp  @err

; Store with positive immediate offset
str2:  setled 12
       mov  r1, low(@tmp1)
       movt r1, high(@tmp1)
       str  r5, [r1, 1]
       ldr  r0, [r1, 1]
       sub  r11, r5, r0
       bz   @str3
       jmp  @err

; Store with negative immediate offset
str3:  setled 13
       mov  r1, low(@tmp2)
       movt r1, high(@tmp2)
       str  r10, [r1, -1]
       ldr  r0, [r1, -1]
       sub  r11, r10, r0
       bz   @push1
       jmp  @err

; Push to stack
push1: setled 14
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
pop1:  setled 15
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
add1:  setled 16
       mov  r1, 0xFF
       movt r1, 0xFF
       add  r0, r5, r10
       sub  r11, r1, r0
       bz   @add2
       jmp  @err

; Add constant to register
add2:  setled 17
       mov  r1, 0xAA
       movt r1, high(@const1)
       add  r0, r5, 0x05
       sub  r11, r1, r0
       bz   @sub1
       jmp  @err

; Subtract two registers
sub1:  setled 18
       mov  r1, 0xb5
       movt r1, 0x54
       sub  r0, r10, r5
       sub  r11, r1, r0
       bz   @sub2
       jmp  @err

; Subtract constant from register
sub2:  setled 19
       mov  r1, 0xA0
       sub  r0, r4, 0x05
       sub  r11, r1, r0
       bz   @shft1
       jmp  @err

; Shift left
shft1: setled 20
       mov  r1, 0x4a
       movt r1, 0xab
       shft r0, r5, 1
       sub  r11, r1, r0
       bz   @shft2
       jmp  @err

; Shift right
shft2: setled 21
       mov  r1, 0x2d
       movt r1, 0x55
       shft r0, r10, -1
       sub  r11, r1, r0
       bz   @and1
       jmp  @err

; Bit-wise AND of two registers
and1:  setled 22
       and  r11, r5, r10
       bz   @and2
       jmp  @err
and2:  and  r11, r5, r5
       sub  r11, r11, r5
       bz   @or1
       jmp  @err

; Bit-wise OR of two registers
or1:   setled 23
       mov  r1, 255
       movt r1, 255
       or   r11, r5, r10
       sub  r11, r11, r1
       bz   @or2
       jmp  @err
or2:   or   r11, r5, r5
       sub  r11, r11, r5
       bz   @xor1
       jmp  @err

; Bit-wise XOR of two registers
xor1:  setled 24
       xor  r11, r5, r10
       sub  r11, r11, r1
       bz   @xor2
       jmp  @err
xor2:  xor  r11, r5, r1
       sub  r11, r11, r10
       bz   @bnz1
       jmp  @err

; Conditional branch nonzero
bnz1:  setled 25
       sub  r0, r5, r11
       bnz  @bnz2
       jmp  @err
bnz2:  sub  r0, r5, r5
       bnz  @bnz3
       b    @blt1
bnz3:  jmp  @err

; Conditional branch signed less than
blt1:  setled 26
       btest @neglarge, lt, @negsmall
       btest @neglarge, lt, @possmall
       btest @neglarge, lt, @poslarge
       btest @negsmall, lt, @possmall
       btest @negsmall, lt, @poslarge
       btest @possmall, lt, @poslarge

; Conditional branch signed greater than or equal
bge1:  setled 27
       btest @negsmall, ge, @neglarge
       btest @possmall, ge, @neglarge
       btest @poslarge, ge, @neglarge
       btest @possmall, ge, @negsmall
       btest @poslarge, ge, @negsmall
       btest @poslarge, ge, @possmall

; Conditional branch unsigned lower
blo1:  setled 28
       btest @unssmall, lo, @unslarge
       btest @unssmall, lo, @possmall
       btest @possmall, lo, @poslarge

; Conditional branch unsigned higher or same
bhs1:  setled 29
       btest @unslarge, hs, @unssmall
       btest @poslarge, hs, @possmall
       btest @possmall, hs, @unssmall

; Conditional branch carry set through shift
bcs1:  setled 30
       mov  r1, 0
       movt r1, 128
       shft r0, r1, 1
       bcs  @bcs2
       jmp  @err
bcs2:  shft r0, r1, -1
       bcs  @bcs3
       b    @bcc1
bcs3:  jmp @err

; Conditional branch carry clear through shift
bcc1:  setled 31
       mov  r1, 0
       movt r1, 128
       shft r0, r1, -1
       bcc  @bcc2
       jmp  @err
bcc2:  shft r0, r1, 1
       bcc  @bcc3
       b    @done
bcc3:  jmp  @err

done:  jmp  @succ       

       .org 0xFEB

succ:  setled 0x55
ends:  b    @ends

       .org 0xFEF

err:   b    @err
