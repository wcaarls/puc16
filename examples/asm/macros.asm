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
