; Example macros for ENG1448 processor

; Mov for 16-bit words
; INPUT : 16-bit word in $1
; OUTPUT: Register set in $0
       .macro movw
       mov  $0, low($1)
       movt $0, high($1)
       .endmacro

; Call subroutine
; INPUT : Subroutine address in $0
; OUTPUT: None
; NOTE  : Clobbers r12
       .macro call
       add r12, pc, 2
       push r12
       jmp $0
       .endmacro

; Wait for keyboard character.
; INPUT : None
; OUTPUT: Keyboard character in $0
; NOTE  : Clobbers r12
       .macro waitkb
_wait: mov  r12, @kdr
       ldr  $0, [r12] ; Read keyboard character
       mov  $0, $0     ; Set flags
       bz   @_wait     ; Wait until nonzero
       .endmacro

; Write LCD character.
; INPUT : LCD character in $0
; OUTPUT: None
; NOTE  : Clobbers r12
       .macro writelcd
_wait: mov  r12, @ldr
       ldr  r12, [r12] ; Read LCD data
       mov  r12, r12   ; Set flags
       bnz  @_wait     ; Wait until zero
       mov  r12, @ldr
       str  $0, [r12]  ; Write character to LCD
       .endmacro

; Clear LCD.
; INPUT : LCD command in $0
; OUTPUT: None
; NOTE  : Clobbers r12
       .macro clearlcd
_wait: mov  r12, @lcr
       ldr  r12, [r12] ; Read LCD command
       mov  r12, r12   ; Set flags
       bnz  @_wait     ; Wait until zero
       mov  r12, @ldr
       str  $0, [r12]  ; Clear LCD
       .endmacro

; Write LCD string.
; INPUT : LCD string constant in $0
; OUTPUT: None
; NOTE  : Clobbers r10, r11, r12
       .macro writestr
       .section data
_data: .dw $0, 0
       .section code
       mov r11, low(@_data)
       movt r11, high(@_data)
_loop: ldr r10, [r11]
       add r10, r10, 0
       bz @_done
       writelcd r10
       add r11, r11, 1
       b @_loop
_done:
       .endmacro
