       .include "def.asm"
       .include "macros.asm"

       .equ vram_width, 80
       .equ vram_height, 30
       .equ vram_size, 2400
       .equ vram_start, 8192

       .equ char_CR, 13
       .equ char_0, 48
       .equ char_Z, 91

       .section data

pos_l: .dw 0
pos_x: .dw 0

greet: .dw "Hello, world: ", 0

       .section code

       mov  r0, 15
       mov  r1, 1
       str  r1, [r0]         ; Set line doubling mode

       mov  r13, @char_0
loop:  movw r11, @greet
       call @puts            ; Write greeting
       mov  r11, r13
       call @putc            ; Add a changing character
       add  r13, r13, 1
       mov  r11, @char_CR
       call @putc            ; Carriage return
       mov  r8, @char_Z
       sub  r8, r8, r13
       bnz @loop             ; Loop from 0 to Z
halt:  jmp @halt

       .section code

; Write null-terminated string to screen
; r11: address of string to write
puts:  push r5
       mov  r5, r11
puts_loop:
       ldr  r11, [r5]        ; Load character
       mov  r11, r11
       bz   @puts_done       ; Null-terminated string
       call @putc            ; Write character
       add  r5, r5, 1        ; Advance
       b    @puts_loop
puts_done:
       pop  r5
       ret

; Write character to screen
; r11: character to write
putc:  movw r0, @pos_l
       movw r1, @pos_x
       ldr  r3, [r0]         ; Current linear position
       ldr  r4, [r1]         ; Current horizontal position

       mov  r2, @char_CR     ; CR
       sub  r2, r11, r2
       bnz  @putc_scroll     ; If CR, skip rest of line
       mov  r2, @vram_width
       sub  r2, r2, r4
       add  r3, r3, r2       ; Move linear position by remaining width
       mov  r4, 0            ; Reset horizontal position

putc_scroll:
       movw r2, @vram_size
       sub  r2, r2, r3
       bnz  @putc_write     ; If end of VRAM, scroll

       movw r3, @vram_start ; Destination
       mov  r4, @vram_width
       add  r4, r3, r4      ; Source
       movw r2, @vram_size
       add  r2, r2, r3      ; Stop condition

putc_scroll_loop:
       ldr  r9, [r4]
       str  r9, [r3]
       add  r3, r3, 1
       add  r4, r4, 1
       sub  r9, r4, r2
       bnz  @putc_scroll_loop

       mov  r9, " "
putc_clear_line:
       str  r9, [r3]        ; Clear last line (starts at destination)
       add  r3, r3, 1
       sub  r4, r3, r2
       bnz  @putc_clear_line

       movw r3, @vram_size
       mov  r4, @vram_width
       sub  r3, r3, r4      ; Set current position to last line
       mov  r4, 0           ; Reset current horizontal position

putc_write:
       mov  r2, @char_CR    ; CR
       sub  r2, r11, r2
       bz   @putc_done      ; If CR, do not write
       movw r2, @vram_start
       add  r2, r2, r3
       str  r11, [r2]       ; Write character to VRAM
       add  r3, r3, 1       ; Increment linear position
       add  r4, r4, 1       ; Increment horizontal position
       mov  r2, @vram_width
       sub  r2, r2, r4
       bnz  @putc_done      ; If end of line, reset horizontal position
       mov  r4, 0
putc_done:
       str  r3, [r0]        ; Store new positions
       str  r4, [r1]
       ret
