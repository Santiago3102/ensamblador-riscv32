sum(int, int):                               # @sum(int, int)
        addi    sp, sp, -16
        sw      ra, 12(sp)
        sw      s0, 8(sp)
        addi    s0, sp, 16
        sw      a0, -12(s0)
        sw      a1, -16(s0)
        lw      a0, -12(s0)
        lw      a1, -16(s0)
        add     a0, a0, a1
        lw      s0, 8(sp)
        lw      ra, 12(sp)
        addi    sp, sp, 16
        ret
main:                                   # @main
        addi    sp, sp, -32
        sw      ra, 28(sp)
        sw      s0, 24(sp)
        addi    s0, sp, 32
        mv      a0, zero
        sw      a0, -12(s0)
        addi    a1, zero, 4
        addi    a2, zero, 5
        sw      a0, -24(s0)
        add     a0, zero, a1
        sw      a1, -28(s0)
        add     a1, zero, a2
        call    sum(int, int)
        sw      a0, -16(s0)
        addi    a1, zero, 6
        lw      a0, -28(s0)
        call    sum(int, int)
        sw      a0, -20(s0)
        lw      a0, -24(s0)
        lw      s0, 24(sp)
        lw      ra, 28(sp)
        addi    sp, sp, 32
        ret