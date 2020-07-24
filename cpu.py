class CPU:
    """Main CPU class."""

    import sys

    def __init__(self):
        """Construct a new CPU."""
        # set memory with 256 bytes
        self.ram = [0] * 256

        # register
        self.reg = [0] * 8
        # intiallize the last spot in the register to the pointer of the beginning of the stack
        self.reg[7] = 0xf4
        # program counter to track
        self.pc = 0

        self.stp = self.reg[7]

        self.running = True

        self.fl = None

        self.branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b00000001: self.HLT,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b10100000: self.ADD,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010110: self.JNE,
            0b01010101: self.JEQ
        }

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MRD, MAR):
        self.ram[MAR] = MRD

    def load(self):
        """Load a program into memory."""
        # Dynamic load method
        address = 0

        with open(sys.args[1]) as f:
            for line in f:
                split_line = line.split(' ')[0].strip("/n")
                if len(split_line) == 8:
                    self.ram[address] = int(split_line, 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            num1 = self.reg[reg_a]
            num2 = self.reg[reg_b]
            if num1 < num2:
                self.fl = 0b00000100
            elif num1 > num2:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def JEQ(self):
        mask = (self.fl & 0b00000001)
        if mask == 0b00000001:
            self.JMP()
        else:
            self.pc += 2

    def JNE(self):
        mask = (self.fl & 0b00000001)
        if mask == 0b00000000:
            self.JMP()
        else:
            self.pc + 2

    def JMP(self):
        reg_address = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_address]

    def CMP(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        self.alu("CMP", num1, num2)

    def HLT(self):
        self.running = False

    def PRN(self):
        reg_address = self.ram_read(self.pc + 1)
        value = self.reg[reg_address]
        print(f'PRN -> {value}')

    def LDI(self):
        reg_address = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.reg[reg_address] = value

    def MUL(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        self.alu("MUL", num1, num2)

    def PUSH(self):
        self.stp -= 1
        reg_address = self.ram[self.pc + 1]
        value = self.reg[reg_address]
        self.ram[self.stp] = value

    def POP(self):
        reg_address = self.ram[self.pc + 1]
        value = self.ram[self.stp]
        self.reg[reg_address] = value
        self.stp += 1

    def ADD(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        self.alu("ADD", num1, num2)

    def CALL(self):
        # adding to stack to decrement the pointer
        self.stp -= 1

        return_address = self.pc + 2
        self.ram[self.stp] = return_address

        reg_index = self.ram[self.pc + 1]

        self.pc = self.reg[reg_index]

    def RET(self):
        return_address = self.ram[self.stp]

        self.pc = return_address

        self.stp += 1

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)

            if ir in self.branch_table:
                self.branch_table[ir]()
                # create a mask and then shifts
                operands = (ir & 0b11000000) >> 6

                # create mask and shifts unneeded numbers for the bit
                pc_param = (ir & 0b00010000) >> 4

                if not pc_param:

                    self.pc += operands + 1

            else:
                print(f'unknown {ir}  address {self.pc}')
                sys.exit(1)
