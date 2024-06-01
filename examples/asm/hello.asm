       .include "def.asm"
       .include "macros.asm"

; Write welcome message
main:  mov  r0, 7
       mov  r1, low(@msg1)
       movt r1, high(@msg1)
       call @writemsg ; Write 7 characters from @msg1 to lcd

halt:  b    @halt

; Write message to LCD.
; r0 contains message length
; r1 contains message address
writemsg:
       add  r0, r0, r1; Set r0 to one past final character
wloop: ldr  r2, [r1]  ; Get character to write
       writelcd r2    ; Write character to LCD
       add  r1, r1, 1 ; Advance
       sub  r2, r1, r0;
       bnz  @wloop    ; Loop until last character was sent
       ret            ; ret

.section data
       .org 0x10      ; Jump over memory-mapped I/O
msg1:  .dw "welcome"
