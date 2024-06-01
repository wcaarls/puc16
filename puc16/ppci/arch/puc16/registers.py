""" PUC16 registers """

from ..registers import Register, RegisterClass
from ... import ir


class PUC16Register(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map[num]

r0 = PUC16Register("r0", num=0)
r1 = PUC16Register("r1", num=1)
r2 = PUC16Register("r2", num=2)
r3 = PUC16Register("r3", num=3)
r4 = PUC16Register("r4", num=4)
r5 = PUC16Register("r5", num=5)
r6 = PUC16Register("r6", num=6)
r7 = PUC16Register("r7", num=7)
r8 = PUC16Register("r8", num=8)
r9 = PUC16Register("r9", num=9)
r10 = PUC16Register("r10", num=10)
r11 = PUC16Register("r11", num=11)
r12 = PUC16Register("r12", num=12)
fp = PUC16Register("r13", num=13, aka=("fp",))
sp = PUC16Register("r14", num=14, aka=("sp",))
pc = PUC16Register("r15", num=15, aka=("pc",))

PUC16Register.registers = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, fp, sp, pc]
num_reg_map = {r.num: r for r in PUC16Register.registers}
alloc_registers = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11]

register_classes = [
    RegisterClass(
        "reg",
        [ir.i8, ir.u8, ir.i16, ir.u16, ir.ptr],
        PUC16Register,
        alloc_registers,
    )
]

caller_save = [r0, r1, r2, r3, r4, r9, r10, r11]
callee_save = [r5, r6, r7, r8]
