         .include "def.asm"

main:    mov  r0, 0
         mov  r1, 0
         mov  r2, 255
         mov  r3, @ssd
         mov  r4, @btn
         mov  r5, 6
         str  r0, [r3]   ; Initialize display counter

loop:    mov  r0, r1     ; Save prevous input register status into r0
         ldr  r1, [r4]  ; Read current input register status into r1

         xor  r0, r0, r2 ; Invert r0
         and  r0, r0, r1 ; Detect positive edge (r1 & ~r0)
         and  r0, r0, r5 ; Test for BTN_EAST
         bz   @loop      ; If no edge, continue loop
         call @incr      ; Jump to subroutine
         b    @loop      ; Wait for next edge

         .org 0x80
incr:    push r0
         ldr  r0, [r3] ; Read display counter
         add  r0, r0, 1  ; Increment
         str  r0, [r3] ; Write back display counter
         pop  r0
         ret
