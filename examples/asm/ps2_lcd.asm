       .include "def.asm"
       .include "macros.asm"

; Write welcome message
main:  mov  r0, 7
       movw r1, @msg1
       call @writemsg ; Write 7 characters from @msg1 to lcd

; Echo PS/2 characters to LCD
loop:  waitkb r0      ; Read character from keyboard
       mov  r1, 0x0D  ; Compare to enter key
       sub  r1, r0, r1;
       bz   @clear    ; If enter, clear LCD
       writelcd r0    ; Otherwise, write to LCD
       b    @loop
clear:mov   r0, 0
       clearlcd r0    ; Clear LCD
       b    @loop

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
msg1:  .dw "welcome"
