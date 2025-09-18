# RISC-V 32-bit Assembler

## Descripción General

Este programa es un ensamblador completo para la arquitectura RISC-V de 32 bits que convierte código assembly a código máquina en formato binario y hexadecimal. Implementa las 40 instrucciones base del conjunto ISA RV32I y soporta pseudo-instrucciones para facilitar la programación.

## Características Principales

- **Soporte completo para RV32I**: Implementa todas las 40 instrucciones base
- **Pseudo-instrucciones**: Expansión automática de instrucciones complejas a instrucciones básicas
- **Manejo de labels**: Resolución automática de etiquetas y direcciones
- **Múltiples formatos de salida**: Binario, hexadecimal y texto detallado
- **Validación robusta**: Verificación de sintaxis, rangos y tipos de operandos
- **Análisis en dos pasadas**: Primera pasada para labels, segunda para generación de código

## Requisitos del Sistema

### Dependencias de Python
- Python 3.6 o superior
- Librerías estándar utilizadas:
  - `re`: Expresiones regulares para parsing
  - `sys`: Acceso a argumentos del sistema
  - `argparse`: Parsing de argumentos de línea de comandos
  - `typing`: Type hints para mejor documentación del código

### Instalación
```bash
# El programa no requiere instalación adicional
# Solo asegúrate de tener Python 3.6+
python --version
```

## Uso del Programa

### Sintaxis Básica
```bash
python assembler.py <archivo_entrada> [-o nombre_salida]
```

### Parámetros
- `archivo_entrada`: Archivo con código assembly RISC-V (extensión .s o .asm)
- `-o, --output`: Nombre base para archivos de salida (opcional, por defecto: "output")

### Ejemplos de Uso
```bash
# Ensamblar programa básico
python assembler.py programa.s

# Especificar nombre de salida personalizado
python assembler.py programa.s -o mi_programa

# Ejecutar modo de prueba
python assembler.py
```

## Arquitectura del Código

### Clase Principal: RISCVAssembler

La clase `RISCVAssembler` es el núcleo del programa y contiene toda la lógica de ensamblado.

#### Atributos Principales

##### 1. `registers: Dict[str, int]`
Mapeo de nombres de registros a números (0-31):
- **Nombres numéricos**: `x0` a `x31`
- **Nombres ABI**: `zero`, `ra`, `sp`, `gp`, `tp`, etc.
- **Registros temporales**: `t0` a `t6`
- **Registros salvados**: `s0` a `s11`
- **Registros de argumentos**: `a0` a `a7`

##### 2. `instructions: Dict[str, Dict]`
Configuración de las 40 instrucciones RV32I organizadas por tipo:
- **Tipo R**: Instrucciones registro-registro (add, sub, and, or, etc.)
- **Tipo I**: Instrucciones inmediatas (addi, lw, jalr, etc.)
- **Tipo S**: Instrucciones de almacenamiento (sw, sh, sb)
- **Tipo B**: Instrucciones de salto condicional (beq, bne, blt, etc.)
- **Tipo U**: Instrucciones con inmediato superior (lui, auipc)
- **Tipo J**: Instrucciones de salto incondicional (jal)

##### 3. `pseudo_instructions: Set[str]`
Conjunto de pseudo-instrucciones soportadas:
`nop`, `mv`, `not`, `neg`, `seqz`, `snez`, `sltz`, `sgtz`, `beqz`, `bnez`, `blez`, `bgez`, `bltz`, `bgtz`, `j`, `jr`, `ret`, `call`, `tail`, `li`, `la`

##### 4. `labels: Dict[str, int]`
Tabla de símbolos que mapea etiquetas a direcciones de memoria.

##### 5. `current_address: int`
Dirección actual durante el ensamblado (incrementa de 4 en 4).

### Métodos Principales

#### Métodos de Parsing y Utilidades

##### `parse_immediate(self, imm_str: str) -> int`
**Propósito**: Convierte strings de inmediatos a enteros.

**Parámetros**:
- `imm_str`: String que representa un valor inmediato

**Funcionalidad**:
- Soporta decimal: `123`, `-456`
- Soporta hexadecimal: `0x1A`, `-0xFF`
- Soporta binario: `0b1010`, `-0b1111`

**Retorna**: Valor entero del inmediato

##### `get_register_number(self, reg: str) -> int`
**Propósito**: Convierte nombres de registro a números.

**Parámetros**:
- `reg`: Nombre del registro (ej: "x1", "ra", "sp")

**Retorna**: Número del registro (0-31)

##### `parse_memory_operand(self, operand: str) -> Tuple[int, int]`
**Propósito**: Parsea operandos de memoria con formato `offset(register)`.

**Parámetros**:
- `operand`: String con formato "offset(register)" (ej: "8(sp)", "-4(x1)")

**Retorna**: Tupla `(offset, register_number)`

**Regex utilizado**: `^(-?\d+|\w+)\((\w+)\)$`

##### `tokenize_line(self, line: str) -> Tuple[Optional[str], str, List[str]]`
**Propósito**: Tokeniza una línea de assembly en componentes.

**Funcionalidad**:
- Elimina comentarios (texto después de #)
- Extrae labels (texto antes de :)
- Separa instrucción de operandos
- Maneja operandos con paréntesis correctamente

**Retorna**: Tupla `(label, instruction, operands_list)`

#### Métodos de Codificación por Tipo de Instrucción

##### `encode_r_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo R (registro-registro).

**Formato**: `funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]`

**Operandos**: `rd, rs1, rs2` (ej: `add x1, x2, x3`)

##### `encode_i_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo I (inmediatas).

**Formato**: `imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]`

**Variantes manejadas**:
- Aritméticas inmediatas: `addi x1, x2, 100`
- Loads: `lw x1, 8(sp)`
- Shifts inmediatos: `slli x1, x2, 5`
- Jump and link register: `jalr x1, x2` o `jalr x1, 8(x2)`

**Rango de inmediatos**: -2048 a 2047 (12 bits con signo)

##### `encode_s_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo S (almacenamiento).

**Formato**: `imm[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]`

**Operandos**: `rs2, offset(rs1)` (ej: `sw x1, 8(sp)`)

**Particularidad**: El inmediato se divide en dos partes (bits superiores e inferiores)

##### `encode_b_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo B (saltos condicionales).

**Formato**: Inmediato codificado en orden específico para optimización de hardware

**Operandos**: `rs1, rs2, label` (ej: `beq x1, x2, loop`)

**Rango**: -4096 a +4094 bytes (múltiplos de 2)

##### `encode_u_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo U (inmediato superior).

**Formato**: `imm[31:12] | rd[11:7] | opcode[6:0]`

**Operandos**: `rd, immediate` (ej: `lui x1, 0x12345`)

**Rango**: 0 a 0xFFFFF (20 bits sin signo)

##### `encode_j_type(self, info: Dict, operands: List[str]) -> int`
**Propósito**: Codifica instrucciones tipo J (saltos incondicionales).

**Formato**: Inmediato de 20 bits reordenado para eficiencia

**Operandos**: `label` o `rd, label` (ej: `jal loop` o `jal ra, function`)

**Rango**: -1,048,576 a +1,048,574 bytes

#### Métodos de Expansión de Pseudo-instrucciones

##### `expand_pseudo_instruction(self, instruction: str, operands: List[str]) -> List[Tuple[str, List[str]]]`
**Propósito**: Expande pseudo-instrucciones a instrucciones reales.

**Ejemplos de expansión**:
- `nop` → `addi x0, x0, 0`
- `mv rd, rs` → `add rd, rs, x0`
- `li rd, imm` → `lui rd, upper` + `addi rd, rd, lower` (si es necesario)
- `beqz rs, label` → `beq rs, x0, label`
- `j label` → `jal x0, label`

**Retorna**: Lista de tuplas `(instruction, operands)` expandidas

#### Métodos de Ensamblado Principal

##### `first_pass(self, lines: List[str]) -> List[Tuple[Optional[str], str, List[str]]]`
**Propósito**: Primera pasada del ensamblador.

**Funciones**:
1. Recopila todos los labels y sus direcciones
2. Expande pseudo-instrucciones
3. Valida sintaxis básica
4. Calcula direcciones de memoria

**Retorna**: Lista de instrucciones parseadas y expandidas

##### `second_pass(self, parsed_lines: List[Tuple[Optional[str], str, List[str]]]) -> List[int]`
**Propósito**: Segunda pasada del ensamblador.

**Funciones**:
1. Genera código máquina para cada instrucción
2. Resuelve referencias a labels
3. Aplica las funciones de codificación apropiadas

**Retorna**: Lista de códigos máquina (enteros de 32 bits)

##### `assemble_file(self, input_file: str, output_base: str)`
**Propósito**: Método principal que ensambla un archivo completo.

**Proceso**:
1. Lee el archivo de entrada
2. Ejecuta primera pasada
3. Ejecuta segunda pasada
4. Genera archivos de salida

**Archivos generados**:
- `*.bin`: Código máquina binario (little-endian)
- `*.hex`: Código máquina en formato hexadecimal legible
- `*.txt`: Información detallada con assembly, binario y hex

## Instrucciones Soportadas

### Instrucciones Tipo R (Register-Register)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `add` | Suma | `add x1, x2, x3` |
| `sub` | Resta | `sub x1, x2, x3` |
| `sll` | Shift lógico izquierdo | `sll x1, x2, x3` |
| `slt` | Set less than | `slt x1, x2, x3` |
| `sltu` | Set less than unsigned | `sltu x1, x2, x3` |
| `xor` | XOR lógico | `xor x1, x2, x3` |
| `srl` | Shift lógico derecho | `srl x1, x2, x3` |
| `sra` | Shift aritmético derecho | `sra x1, x2, x3` |
| `or` | OR lógico | `or x1, x2, x3` |
| `and` | AND lógico | `and x1, x2, x3` |

### Instrucciones Tipo I (Immediate)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `addi` | Suma inmediata | `addi x1, x2, 100` |
| `slti` | Set less than immediate | `slti x1, x2, 50` |
| `sltiu` | Set less than immediate unsigned | `sltiu x1, x2, 50` |
| `xori` | XOR inmediato | `xori x1, x2, 0xFF` |
| `ori` | OR inmediato | `ori x1, x2, 0x0F` |
| `andi` | AND inmediato | `andi x1, x2, 0xF0` |
| `slli` | Shift lógico izquierdo inmediato | `slli x1, x2, 3` |
| `srli` | Shift lógico derecho inmediato | `srli x1, x2, 2` |
| `srai` | Shift aritmético derecho inmediato | `srai x1, x2, 1` |
| `lb` | Load byte | `lb x1, 8(sp)` |
| `lh` | Load halfword | `lh x1, 4(sp)` |
| `lw` | Load word | `lw x1, 0(sp)` |
| `lbu` | Load byte unsigned | `lbu x1, 8(sp)` |
| `lhu` | Load halfword unsigned | `lhu x1, 4(sp)` |
| `jalr` | Jump and link register | `jalr x1, x2` |

### Instrucciones Tipo S (Store)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `sb` | Store byte | `sb x1, 8(sp)` |
| `sh` | Store halfword | `sh x1, 4(sp)` |
| `sw` | Store word | `sw x1, 0(sp)` |

### Instrucciones Tipo B (Branch)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `beq` | Branch if equal | `beq x1, x2, loop` |
| `bne` | Branch if not equal | `bne x1, x2, end` |
| `blt` | Branch if less than | `blt x1, x2, less` |
| `bge` | Branch if greater or equal | `bge x1, x2, greater` |
| `bltu` | Branch if less than unsigned | `bltu x1, x2, less_u` |
| `bgeu` | Branch if greater or equal unsigned | `bgeu x1, x2, greater_u` |

### Instrucciones Tipo U (Upper Immediate)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `lui` | Load upper immediate | `lui x1, 0x12345` |
| `auipc` | Add upper immediate to PC | `auipc x1, 0x1000` |

### Instrucciones Tipo J (Jump)
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `jal` | Jump and link | `jal ra, function` |

### Instrucciones de Sistema
| Instrucción | Descripción | Ejemplo |
|-------------|-------------|---------|
| `ecall` | Environment call | `ecall` |
| `ebreak` | Environment break | `ebreak` |
| `fence` | Memory fence | `fence` |

## Pseudo-instrucciones

### Movimiento y Carga
| Pseudo-instrucción | Expansión | Descripción |
|--------------------|-----------|-------------|
| `nop` | `addi x0, x0, 0` | No operation |
| `mv rd, rs` | `add rd, rs, x0` | Move register |
| `li rd, imm` | `lui + addi` (si necesario) | Load immediate |
| `la rd, label` | `lui + addi` (si necesario) | Load address |

### Operaciones Lógicas
| Pseudo-instrucción | Expansión | Descripción |
|--------------------|-----------|-------------|
| `not rd, rs` | `xori rd, rs, -1` | Logical NOT |
| `neg rd, rs` | `sub rd, x0, rs` | Negate |

### Comparaciones
| Pseudo-instrucción | Expansión | Descripción |
|--------------------|-----------|-------------|
| `seqz rd, rs` | `sltiu rd, rs, 1` | Set if equal zero |
| `snez rd, rs` | `sltu rd, x0, rs` | Set if not equal zero |
| `sltz rd, rs` | `slt rd, rs, x0` | Set if less than zero |
| `sgtz rd, rs` | `slt rd, x0, rs` | Set if greater than zero |

### Saltos Condicionales
| Pseudo-instrucción | Expansión | Descripción |
|--------------------|-----------|-------------|
| `beqz rs, label` | `beq rs, x0, label` | Branch if equal zero |
| `bnez rs, label` | `bne rs, x0, label` | Branch if not equal zero |
| `blez rs, label` | `bge x0, rs, label` | Branch if less or equal zero |
| `bgez rs, label` | `bge rs, x0, label` | Branch if greater or equal zero |
| `bltz rs, label` | `blt rs, x0, label` | Branch if less than zero |
| `bgtz rs, label` | `blt x0, rs, label` | Branch if greater than zero |

### Saltos Incondicionales
| Pseudo-instrucción | Expansión | Descripción |
|--------------------|-----------|-------------|
| `j label` | `jal x0, label` | Jump |
| `jr rs` | `jalr x0, rs` | Jump register |
| `ret` | `jalr x0, ra` | Return |
| `call label` | `jal ra, label` | Call function |
| `tail label` | `jal x0, label` | Tail call |

## Formato de Archivos de Salida

### Archivo .bin
- Código máquina binario puro
- Formato little-endian
- 4 bytes por instrucción
- Listo para carga directa en memoria

### Archivo .hex
- Formato texto legible
- Una instrucción por línea
- Formato: `dirección: código_hex`
- Ejemplo:
```
00000000: 00a00093
00000004: 01400113
00000008: 002081b3
```

### Archivo .txt
- Información detallada completa
- Sección de labels con direcciones
- Para cada instrucción:
  - Dirección de memoria
  - Código assembly original
  - Representación binaria (32 bits)
  - Representación hexadecimal

## Manejo de Errores

### Validaciones Implementadas
1. **Sintaxis**: Verificación de formato de instrucciones
2. **Registros**: Validación de nombres de registro válidos
3. **Inmediatos**: Verificación de rangos según tipo de instrucción
4. **Labels**: Detección de labels duplicados y referencias no resueltas
5. **Operandos**: Verificación de número correcto de operandos por instrucción
6. **Memoria**: Validación de formato de operandos de memoria

### Mensajes de Error
- Incluyen número de línea o dirección de memoria
- Descripción específica del problema
- Contexto relevante para facilitar depuración

## Ejemplo de Uso Completo

### Código Assembly de Entrada (programa.s)
```assembly
# Programa de ejemplo
main:
    addi x1, x0, 10      # x1 = 10
    addi x2, x0, 20      # x2 = 20
    add x3, x1, x2       # x3 = x1 + x2
    
    # Pseudo-instrucciones
    li x4, 0x12345       # Load immediate grande
    mv x5, x3            # Move x3 to x5
    
loop:
    beqz x1, end         # if x1 == 0, goto end
    addi x1, x1, -1      # x1--
    j loop               # goto loop
    
end:
    nop                  # No operation
```

### Comando de Ejecución
```bash
python assembler.py programa.s -o programa_salida
```

### Salida del Programa
```
Procesando 12 líneas...
Labels encontrados: ['main', 'loop', 'end']
Generadas 9 instrucciones
Archivos generados:
  - programa_salida.bin (binario)
  - programa_salida.hex (hexadecimal)
  - programa_salida.txt (información detallada)
```

## Función de Prueba

El programa incluye una función `test_assembler()` que:
1. Crea un archivo de prueba con código assembly variado
2. Ejecuta el ensamblador completo
3. Genera archivos de salida para verificación
4. Incluye ejemplos de todas las características principales

## Notas Técnicas

### Consideraciones de Implementación
- **Endianness**: Los archivos binarios se generan en formato little-endian
- **Alineación**: Todas las instrucciones están alineadas a 4 bytes
- **Direccionamiento**: Las direcciones inician en 0x00000000
- **Labels**: Soporta caracteres alfanuméricos y underscore

### Limitaciones Conocidas
- Solo soporta el conjunto de instrucciones RV32I base
- No incluye extensiones (M, A, F, D, etc.)
- No soporta directivas del ensamblador (.data, .text, etc.)
- No maneja relocaciones para linking

### Posibles Mejoras Futuras
- Soporte para extensiones RISC-V adicionales
- Implementación de directivas del ensamblador
- Optimizaciones de pseudo-instrucciones
- Soporte para múltiples archivos fuente
- Generación de información de debug

## Contacto y Contribuciones

Este ensamblador fue desarrollado como herramienta educativa y de desarrollo para RISC-V. Para reportar bugs, sugerir mejoras o contribuir al código, se recomienda seguir las mejores prácticas de desarrollo de software libre.
