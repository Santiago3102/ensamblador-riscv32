#!/usr/bin/env python3
"""
RISC-V 32-bit Assembler - VERSIÓN CORREGIDA
Convierte código assembly RISC-V a código máquina binario y hexadecimal
"""

import re
import sys
import argparse
from typing import Dict, List, Tuple, Optional

class RISCVAssembler:
    def __init__(self):
        # Mapeo de registros
        self.registers = {
            'x0': 0, 'x1': 1, 'x2': 2, 'x3': 3, 'x4': 4, 'x5': 5, 'x6': 6, 'x7': 7,
            'x8': 8, 'x9': 9, 'x10': 10, 'x11': 11, 'x12': 12, 'x13': 13, 'x14': 14, 'x15': 15,
            'x16': 16, 'x17': 17, 'x18': 18, 'x19': 19, 'x20': 20, 'x21': 21, 'x22': 22, 'x23': 23,
            'x24': 24, 'x25': 25, 'x26': 26, 'x27': 27, 'x28': 28, 'x29': 29, 'x30': 30, 'x31': 31,
            # ABI names
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4, 't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, 's1': 9, 'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15,
            'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
            's8': 24, 's9': 25, 's10': 26, 's11': 27, 't3': 28, 't4': 29, 't5': 30, 't6': 31
        }
        
        # Instrucciones RV32I (las 40 instrucciones base)
        self.instructions = {
            # Tipo R (Register-Register)
            'add':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0000000},
            'sub':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0100000},
            'sll':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b001, 'funct7': 0b0000000},
            'slt':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b010, 'funct7': 0b0000000},
            'sltu':   {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b011, 'funct7': 0b0000000},
            'xor':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b100, 'funct7': 0b0000000},
            'srl':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0000000},
            'sra':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0100000},
            'or':     {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b110, 'funct7': 0b0000000},
            'and':    {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b111, 'funct7': 0b0000000},
            
            # Tipo I (Immediate)
            'addi':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b000},
            'slti':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b010},
            'sltiu':  {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b011},
            'xori':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b100},
            'ori':    {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b110},
            'andi':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b111},
            'slli':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b001, 'funct7': 0b0000000},
            'srli':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0000000},
            'srai':   {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0100000},
            
            # Load instructions
            'lb':     {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b000},
            'lh':     {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b001},
            'lw':     {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b010},
            'lbu':    {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b100},
            'lhu':    {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b101},
            
            # Tipo S (Store)
            'sb':     {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b000},
            'sh':     {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b001},
            'sw':     {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b010},
            
            # Tipo B (Branch)
            'beq':    {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b000},
            'bne':    {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b001},
            'blt':    {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b100},
            'bge':    {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b101},
            'bltu':   {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b110},
            'bgeu':   {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b111},
            
            # Tipo U (Upper immediate)
            'lui':    {'type': 'U', 'opcode': 0b0110111},
            'auipc':  {'type': 'U', 'opcode': 0b0010111},
            
            # Tipo J (Jump)
            'jal':    {'type': 'J', 'opcode': 0b1101111},
            'jalr':   {'type': 'I', 'opcode': 0b1100111, 'funct3': 0b000},
            
            # System instructions
            'ecall':  {'type': 'I', 'opcode': 0b1110011, 'funct3': 0b000, 'imm': 0},
            'ebreak': {'type': 'I', 'opcode': 0b1110011, 'funct3': 0b000, 'imm': 1},
            
            # Fence instructions
            'fence':  {'type': 'I', 'opcode': 0b0001111, 'funct3': 0b000},
        }
        
        # Pseudo-instrucciones
        self.pseudo_instructions = {
            'nop', 'mv', 'not', 'neg', 'seqz', 'snez', 'sltz', 'sgtz',
            'beqz', 'bnez', 'blez', 'bgez', 'bltz', 'bgtz',
            'j', 'jr', 'ret', 'call', 'tail', 'li', 'la'
        }
        
        self.labels = {}  # Para almacenar labels y sus direcciones
        self.current_address = 0

    def parse_immediate(self, imm_str: str) -> int:
        """Convierte string de inmediato a entero"""
        if not imm_str:
            return 0
            
        imm_str = imm_str.strip()
        
        if not imm_str:
            return 0
        
        try:
            if imm_str.startswith('0x') or imm_str.startswith('0X'):
                return int(imm_str, 16)
            elif imm_str.startswith('0b') or imm_str.startswith('0B'):
                return int(imm_str, 2)
            elif imm_str.startswith('-0x') or imm_str.startswith('-0X'):
                return -int(imm_str[3:], 16)
            else:
                return int(imm_str)
        except ValueError:
            raise ValueError(f"Inmediato inválido: '{imm_str}'")

    def get_register_number(self, reg: str) -> int:
        """Convierte nombre de registro a número"""
        reg = reg.strip().lower()
        if reg in self.registers:
            return self.registers[reg]
        else:
            raise ValueError(f"Registro inválido: {reg}")

    def parse_memory_operand(self, operand: str) -> Tuple[int, int]:
        """
        Parsea operandos de memoria como offset(register)
        Retorna (offset, register_number)
        """
        operand = operand.strip()
        
        # Patrón para capturar offset(register)
        pattern = r'^(-?\d+|\w+)\((\w+)\)$'
        match = re.match(pattern, operand)
        
        if not match:
            raise ValueError(f"Formato de memoria inválido: {operand}")
        
        offset_str = match.group(1)
        reg_str = match.group(2)
        
        # Parsear offset
        try:
            offset = self.parse_immediate(offset_str)
        except:
            # Podría ser un label
            if offset_str in self.labels:
                offset = self.labels[offset_str]
            else:
                offset = 0  # Default para primera pasada
        
        # Parsear registro
        reg_num = self.get_register_number(reg_str)
        
        return offset, reg_num

    def encode_r_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo R"""
        if len(operands) != 3:
            raise ValueError("Instrucciones tipo R requieren 3 operandos")
        
        rd = self.get_register_number(operands[0])
        rs1 = self.get_register_number(operands[1])
        rs2 = self.get_register_number(operands[2])
        
        instruction = (info['funct7'] << 25) | (rs2 << 20) | (rs1 << 15) | \
                     (info['funct3'] << 12) | (rd << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def encode_i_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo I - VERSIÓN CORREGIDA"""
        if len(operands) < 2:
            raise ValueError("Instrucciones tipo I requieren al menos 2 operandos")
        
        rd = self.get_register_number(operands[0])
        
        # Manejar diferentes formatos de instrucciones I
        if 'funct7' in info:  # Shifts inmediatos (slli, srli, srai)
            rs1 = self.get_register_number(operands[1])
            shamt = self.parse_immediate(operands[2])
            if shamt < 0 or shamt > 31:
                raise ValueError("Shift amount debe estar entre 0 y 31")
            
            imm = (info['funct7'] << 5) | shamt
            
        elif len(operands) >= 2 and '(' in operands[-1]:  # Load instructions: lw x1, offset(x2)
            # PARSING CORREGIDO para loads
            memory_operand = operands[-1]  # El último operando es el de memoria
            
            try:
                offset, rs1 = self.parse_memory_operand(memory_operand)
                imm = offset
            except Exception as e:
                raise ValueError(f"Error parseando operando de memoria '{memory_operand}': {e}")
                
        elif len(operands) == 3:  # Instrucciones aritméticas inmediatas
            rs1 = self.get_register_number(operands[1])
            imm = self.parse_immediate(operands[2])
            
        elif len(operands) == 2:  # jalr x1, x2 o jalr x1, offset(x2)
            if '(' in operands[1]:  # jalr rd, offset(rs1)
                try:
                    offset, rs1 = self.parse_memory_operand(operands[1])
                    imm = offset
                except:
                    rs1 = self.get_register_number(operands[1])
                    imm = 0
            else:  # jalr rd, rs1
                rs1 = self.get_register_number(operands[1])
                imm = 0
            
        else:
            rs1 = 0
            imm = info.get('imm', 0)  # Para ecall, ebreak
        
        # Verificar rango del inmediato
        if imm < -2048 or imm > 2047:
            raise ValueError(f"Inmediato fuera de rango (-2048 a 2047): {imm}")
        
        # Convertir a 12 bits con signo
        imm = imm & 0xFFF
        
        instruction = (imm << 20) | (rs1 << 15) | (info['funct3'] << 12) | \
                    (rd << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def encode_s_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo S - VERSIÓN CORREGIDA"""
        if len(operands) != 2:
            raise ValueError("Instrucciones tipo S requieren 2 operandos")
        
        rs2 = self.get_register_number(operands[0])  # Registro fuente
        
        # PARSING CORREGIDO para stores
        memory_operand = operands[1]
        
        try:
            offset, rs1 = self.parse_memory_operand(memory_operand)
            imm = offset
        except Exception as e:
            raise ValueError(f"Error parseando operando de memoria '{memory_operand}': {e}")
        
        if imm < -2048 or imm > 2047:
            raise ValueError(f"Offset fuera de rango (-2048 a 2047): {imm}")
        
        # Dividir inmediato en imm[11:5] y imm[4:0]
        imm = imm & 0xFFF
        imm_high = (imm >> 5) & 0x7F
        imm_low = imm & 0x1F
        
        instruction = (imm_high << 25) | (rs2 << 20) | (rs1 << 15) | \
                    (info['funct3'] << 12) | (imm_low << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def encode_b_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo B"""
        if len(operands) != 3:
            raise ValueError("Instrucciones tipo B requieren 3 operandos")
        
        rs1 = self.get_register_number(operands[0])
        rs2 = self.get_register_number(operands[1])
        
        # Calcular offset del label
        label = operands[2]
        if label in self.labels:
            target_addr = self.labels[label]
            offset = target_addr - self.current_address
        else:
            # Si no encontramos el label, asumimos offset 0 (primera pasada)
            offset = 0
        
        if offset % 2 != 0:
            raise ValueError("Offset de branch debe ser par")
        
        if offset < -4096 or offset > 4094:
            raise ValueError(f"Offset de branch fuera de rango: {offset}")
        
        # Codificar offset en formato B
        offset = offset & 0x1FFE  # 13 bits, bit 0 siempre es 0
        
        imm_12 = (offset >> 12) & 0x1
        imm_10_5 = (offset >> 5) & 0x3F
        imm_4_1 = (offset >> 1) & 0xF
        imm_11 = (offset >> 11) & 0x1
        
        instruction = (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | \
                     (rs1 << 15) | (info['funct3'] << 12) | (imm_4_1 << 8) | \
                     (imm_11 << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def encode_u_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo U"""
        if len(operands) != 2:
            raise ValueError("Instrucciones tipo U requieren 2 operandos")
        
        rd = self.get_register_number(operands[0])
        imm = self.parse_immediate(operands[1])
        
        if imm < 0 or imm > 0xFFFFF:
            raise ValueError(f"Inmediato fuera de rango (0 a 0xFFFFF): {imm}")
        
        instruction = (imm << 12) | (rd << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def encode_j_type(self, info: Dict, operands: List[str]) -> int:
        """Codifica instrucciones tipo J"""
        if len(operands) < 1 or len(operands) > 2:
            raise ValueError("Instrucciones tipo J requieren 1 o 2 operandos")
        
        if len(operands) == 2:
            rd = self.get_register_number(operands[0])
            label = operands[1]
        else:
            rd = 1  # ra por defecto
            label = operands[0]
        
        # Calcular offset del label
        if label in self.labels:
            target_addr = self.labels[label]
            offset = target_addr - self.current_address
        else:
            offset = 0  # Primera pasada
        
        if offset % 2 != 0:
            raise ValueError("Offset de jump debe ser par")
        
        if offset < -1048576 or offset > 1048574:
            raise ValueError(f"Offset de jump fuera de rango: {offset}")
        
        # Codificar offset en formato J
        offset = offset & 0x1FFFFE
        
        imm_20 = (offset >> 20) & 0x1
        imm_10_1 = (offset >> 1) & 0x3FF
        imm_11 = (offset >> 11) & 0x1
        imm_19_12 = (offset >> 12) & 0xFF
        
        instruction = (imm_20 << 31) | (imm_19_12 << 12) | (imm_11 << 20) | \
                     (imm_10_1 << 21) | (rd << 7) | info['opcode']
        
        return instruction & 0xFFFFFFFF

    def expand_pseudo_instruction(self, instruction: str, operands: List[str]) -> List[Tuple[str, List[str]]]:
        """Expande pseudo-instrucciones a instrucciones reales"""
        pseudo_expansions = []
        
        if instruction == 'nop':
            pseudo_expansions.append(('addi', ['x0', 'x0', '0']))
        
        elif instruction == 'mv':
            if len(operands) != 2:
                raise ValueError("mv requiere 2 operandos")
            pseudo_expansions.append(('add', [operands[0], operands[1], 'x0']))
        
        elif instruction == 'not':
            if len(operands) != 2:
                raise ValueError("not requiere 2 operandos")
            pseudo_expansions.append(('xori', [operands[0], operands[1], '-1']))
        
        elif instruction == 'neg':
            if len(operands) != 2:
                raise ValueError("neg requiere 2 operandos")
            pseudo_expansions.append(('sub', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'seqz':
            if len(operands) != 2:
                raise ValueError("seqz requiere 2 operandos")
            pseudo_expansions.append(('sltiu', [operands[0], operands[1], '1']))
        
        elif instruction == 'snez':
            if len(operands) != 2:
                raise ValueError("snez requiere 2 operandos")
            pseudo_expansions.append(('sltu', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'sltz':
            if len(operands) != 2:
                raise ValueError("sltz requiere 2 operandos")
            pseudo_expansions.append(('slt', [operands[0], operands[1], 'x0']))
        
        elif instruction == 'sgtz':
            if len(operands) != 2:
                raise ValueError("sgtz requiere 2 operandos")
            pseudo_expansions.append(('slt', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'beqz':
            if len(operands) != 2:
                raise ValueError("beqz requiere 2 operandos")
            pseudo_expansions.append(('beq', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'bnez':
            if len(operands) != 2:
                raise ValueError("bnez requiere 2 operandos")
            pseudo_expansions.append(('bne', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'blez':
            if len(operands) != 2:
                raise ValueError("blez requiere 2 operandos")
            pseudo_expansions.append(('bge', ['x0', operands[0], operands[1]]))
        
        elif instruction == 'bgez':
            if len(operands) != 2:
                raise ValueError("bgez requiere 2 operandos")
            pseudo_expansions.append(('bge', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'bltz':
            if len(operands) != 2:
                raise ValueError("bltz requiere 2 operandos")
            pseudo_expansions.append(('blt', [operands[0], 'x0', operands[1]]))
        
        elif instruction == 'bgtz':
            if len(operands) != 2:
                raise ValueError("bgtz requiere 2 operandos")
            pseudo_expansions.append(('blt', ['x0', operands[0], operands[1]]))
        
        elif instruction == 'j':
            if len(operands) != 1:
                raise ValueError("j requiere 1 operando")
            pseudo_expansions.append(('jal', ['x0', operands[0]]))
        
        elif instruction == 'jr':
            if len(operands) != 1:
                raise ValueError("jr requiere 1 operando")
            pseudo_expansions.append(('jalr', ['x0', operands[0]]))
        
        elif instruction == 'ret':
            pseudo_expansions.append(('jalr', ['x0', 'ra']))
        
        elif instruction == 'call':
            if len(operands) != 1:
                raise ValueError("call requiere 1 operando")
            pseudo_expansions.append(('jal', ['ra', operands[0]]))
        
        elif instruction == 'tail':
            if len(operands) != 1:
                raise ValueError("tail requiere 1 operando")
            pseudo_expansions.append(('jal', ['x0', operands[0]]))
        
        elif instruction == 'la':
            if len(operands) != 2:
                raise ValueError("la requiere 2 operandos")
            rd = operands[0]
            label = operands[1]
            
            if label in self.labels:
                addr = self.labels[label]
                if -2048 <= addr <= 2047:
                    pseudo_expansions.append(('addi', [rd, 'x0', str(addr)]))
                else:
                    upper = (addr + 0x800) >> 12
                    lower = addr & 0xFFF
                    if lower >= 0x800:
                        lower = lower - 0x1000
                    
                    pseudo_expansions.append(('lui', [rd, str(upper & 0xFFFFF)]))
                    if lower != 0:
                        pseudo_expansions.append(('addi', [rd, rd, str(lower)]))
            else:
                pseudo_expansions.append(('addi', [rd, 'x0', '0']))
        
        elif instruction == 'li':
            if len(operands) != 2:
                raise ValueError("li requiere 2 operandos")
            
            rd = operands[0]
            imm = self.parse_immediate(operands[1])
            
            if -2048 <= imm <= 2047:
                pseudo_expansions.append(('addi', [rd, 'x0', str(imm)]))
            else:
                upper = (imm + 0x800) >> 12
                lower = imm & 0xFFF
                if lower >= 0x800:
                    lower = lower - 0x1000
                
                pseudo_expansions.append(('lui', [rd, str(upper & 0xFFFFF)]))
                if lower != 0:
                    pseudo_expansions.append(('addi', [rd, rd, str(lower)]))
        
        else:
            raise ValueError(f"Pseudo-instrucción no implementada: {instruction}")
        
        return pseudo_expansions

    def tokenize_line(self, line: str) -> Tuple[Optional[str], str, List[str]]:
        """Tokeniza una línea de assembly - VERSIÓN MEJORADA"""
        # Remover comentarios
        line = line.split('#')[0].strip()
        
        if not line:
            return None, '', []
        
        # Buscar label - CORREGIDO para manejar labels con caracteres especiales
        label = None
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            line = parts[1].strip()
        
        if not line:
            return label, '', []
        
        # Separar instrucción y operandos
        parts = line.split(None, 1)
        instruction = parts[0].lower()
        
        operands = []
        if len(parts) > 1:
            # MEJOR parsing de operandos - CORREGIDO
            operand_str = parts[1]
            
            operands = []
            current_operand = ""
            paren_count = 0
            
            for char in operand_str + ",":
                if char == ',' and paren_count == 0:
                    if current_operand.strip():
                        operands.append(current_operand.strip())
                    current_operand = ""
                else:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    current_operand += char
        
        return label, instruction, operands

    def first_pass(self, lines: List[str]) -> List[Tuple[Optional[str], str, List[str]]]:
        """Primera pasada: recopilar labels y expandir pseudo-instrucciones"""
        parsed_lines = []
        self.current_address = 0
        
        for line_num, line in enumerate(lines, 1):
            try:
                label, instruction, operands = self.tokenize_line(line)
                
                # Registrar label si existe
                if label:
                    if label in self.labels:
                        raise ValueError(f"Label duplicado: {label}")
                    self.labels[label] = self.current_address
                
                # Si hay instrucción, procesarla
                if instruction:
                    if instruction in self.pseudo_instructions:
                        # Expandir pseudo-instrucción
                        expanded = self.expand_pseudo_instruction(instruction, operands)
                        for exp_inst, exp_ops in expanded:
                            parsed_lines.append((None, exp_inst, exp_ops))
                            self.current_address += 4
                    elif instruction in self.instructions:
                        parsed_lines.append((label, instruction, operands))
                        self.current_address += 4
                    else:
                        raise ValueError(f"Instrucción desconocida: {instruction}")
                
            except Exception as e:
                raise ValueError(f"Error en línea {line_num}: {e}")
        
        return parsed_lines

    def second_pass(self, parsed_lines: List[Tuple[Optional[str], str, List[str]]]) -> List[int]:
        """Segunda pasada: generar código máquina"""
        machine_code = []
        self.current_address = 0
        
        for line_label, instruction, operands in parsed_lines:
            try:
                if instruction not in self.instructions:
                    raise ValueError(f"Instrucción no reconocida: {instruction}")
                
                info = self.instructions[instruction]
                
                if info['type'] == 'R':
                    code = self.encode_r_type(info, operands)
                elif info['type'] == 'I':
                    code = self.encode_i_type(info, operands)
                elif info['type'] == 'S':
                    code = self.encode_s_type(info, operands)
                elif info['type'] == 'B':
                    code = self.encode_b_type(info, operands)
                elif info['type'] == 'U':
                    code = self.encode_u_type(info, operands)
                elif info['type'] == 'J':
                    code = self.encode_j_type(info, operands)
                else:
                    raise ValueError(f"Tipo de instrucción desconocido: {info['type']}")
                
                machine_code.append(code)
                self.current_address += 4
                
            except Exception as e:
                addr = self.current_address
                raise ValueError(f"Error en dirección 0x{addr:08x}: {e}")
        
        return machine_code

    def assemble_file(self, input_file: str, output_base: str):
        """Ensambla un archivo completo"""
        try:
            # Leer archivo de entrada
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Procesando {len(lines)} líneas...")
            
            # Primera pasada: recopilar labels
            parsed_lines = self.first_pass(lines)
            print(f"Labels encontrados: {list(self.labels.keys())}")
            
            # Segunda pasada: generar código máquina
            machine_code = self.second_pass(parsed_lines)
            print(f"Generadas {len(machine_code)} instrucciones")
            
            # Escribir archivo binario
            with open(f"{output_base}.bin", 'wb') as f:
                for code in machine_code:
                    # Escribir como little-endian de 32 bits
                    f.write(code.to_bytes(4, byteorder='little'))
            
            # Escribir archivo hexadecimal
            with open(f"{output_base}.hex", 'w') as f:
                for i, code in enumerate(machine_code):
                    addr = i * 4
                    f.write(f"{addr:08x}: {code:08x}\n")
            
            # Escribir archivo de texto con información detallada
            with open(f"{output_base}.txt", 'w') as f:
                f.write("RISC-V Assembly to Machine Code\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("LABELS:\n")
                for label, addr in self.labels.items():
                    f.write(f"  {label}: 0x{addr:08x}\n")
                f.write("\n" + "=" * 50 + "\n\n")
                
                for i, (code, (_, instruction, operands)) in enumerate(zip(machine_code, parsed_lines)):
                    addr = i * 4
                    binary = f"{code:032b}"
                    hex_code = f"{code:08x}"
                    
                    f.write(f"Address: 0x{addr:08x}\n")
                    f.write(f"Assembly: {instruction} {', '.join(operands)}\n")
                    f.write(f"Binary:   {binary}\n")
                    f.write(f"Hex:      {hex_code}\n")
                    f.write("-" * 40 + "\n")
            
            print(f"Archivos generados:")
            print(f"  - {output_base}.bin (binario)")
            print(f"  - {output_base}.hex (hexadecimal)")
            print(f"  - {output_base}.txt (información detallada)")
            
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo {input_file}")
        except Exception as e:
            print(f"Error durante el ensamblado: {e}")

def main():
    parser = argparse.ArgumentParser(description='RISC-V 32-bit Assembler')
    parser.add_argument('input_file', help='Archivo de código assembly (.s o .asm)')
    parser.add_argument('-o', '--output', default='output', 
                       help='Nombre base para archivos de salida (default: output)')
    
    args = parser.parse_args()
    
    assembler = RISCVAssembler()
    assembler.assemble_file(args.input_file, args.output)

# Función de utilidad para testing
def test_assembler():
    """Función de prueba con código de ejemplo"""
    test_code = """
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
    """
    
    # Crear archivo de prueba
    with open('test.asm', 'w') as f:
        f.write(test_code)
    
    # Ensamblar
    assembler = RISCVAssembler()
    assembler.assemble_file('test.asm', 'test_output')
    
    print("Prueba completada. Revisa los archivos test_output.*")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Uso: python assembler.py <archivo.s|.asm> [-o output_name]")
        print("O ejecuta test_assembler() para una prueba rápida")
        
        # Ejecutar prueba si no hay argumentos
        response = input("¿Ejecutar prueba? (y/n): ")
        if response.lower().startswith('y'):
            test_assembler()
    else:
        main()