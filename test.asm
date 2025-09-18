
    # Programa de prueba RISC-V
    main:
        addi x1, x0, 10      # x1 = 10
        addi x2, x0, 20      # x2 = 20
        add x3, x1, x2       # x3 = x1 + x2
        sub x4, x3, x1       # x4 = x3 - x1
        
        # Test de load/store
        sw x3, 0(sp)         # store x3 en stack
        lw x5, 0(sp)         # load desde stack
        
        # Test con offset negativo
        sw x4, -4(sp)        # store con offset negativo
        lw x6, -4(sp)        # load con offset negativo
        
    loop:
        beq x1, x0, end      # if x1 == 0, goto end
        addi x1, x1, -1      # x1--
        j loop               # goto loop
        
    end:
        nop                  # pseudo-instruccion
        mv x7, x3            # pseudo-instruccion: x7 = x3
    