import sys
import json


class Assembler:
    def __init__(self):
        self.instructions = {
            "LOAD_CONSTANT": 7,
            "LOAD_MEMORY": 12,
            "STORE_TO_MEMORY": 53,
            "SUBTRACT": 38,
        }

    def assemble(self, source_code):
        machine_code = []
        log = []

        for line_no, line in enumerate(source_code.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            parts = line.split()
            command = parts[0]

            if command not in self.instructions:
                raise ValueError(f"Unknown instruction '{command}' on line {line_no}")

            opcode = self.instructions[command]

            if command == "LOAD_CONSTANT":
                _, addr_b, const_c = parts
                addr_b = int(addr_b)
                const_c = int(const_c)
                encoded = (opcode << 90) | (addr_b << 63) | (const_c << 45)
                machine_code.append(encoded)
                log.append({
                    "line": line_no,
                    "instruction": line,
                    "binary": f"{encoded:096b}"
                })

            elif command == "LOAD_MEMORY":
                _, addr_b, addr_c = parts
                addr_b = int(addr_b)
                addr_c = int(addr_c)
                encoded = (opcode << 90) | (addr_b << 63) | (addr_c << 36)
                machine_code.append(encoded)
                log.append({
                    "line": line_no,
                    "instruction": line,
                    "binary": f"{encoded:096b}"
                })

            elif command == "STORE_TO_MEMORY":
                _, addr_b, addr_c = parts
                addr_b = int(addr_b)
                addr_c = int(addr_c)
                encoded = (opcode << 90) | (addr_b << 63) | (addr_c << 36)
                machine_code.append(encoded)
                log.append({
                    "line": line_no,
                    "instruction": line,
                    "binary": f"{encoded:096b}"
                })

            elif command == "SUBTRACT":
                _, addr_b, addr_c, offset_d, addr_e = parts
                addr_b = int(addr_b)
                addr_c = int(addr_c)
                offset_d = int(offset_d)
                addr_e = int(addr_e)
                encoded = (opcode << 90) | (addr_b << 63) | (addr_c << 36) | (offset_d << 28) | (addr_e << 1)
                machine_code.append(encoded)
                log.append({
                    "line": line_no,
                    "instruction": line,
                    "binary": f"{encoded:096b}"
                })

            else:
                raise ValueError(f"Unhandled instruction '{command}' on line {line_no}")

        return machine_code, log


class Interpreter:
    def __init__(self, memory_size=8192):
        self.memory = [0] * memory_size
        self.log = []

    def execute(self, machine_code):
        for index, instruction in enumerate(machine_code):
            opcode = (instruction >> 90) & 0x3F

            if opcode == 7:
                addr_b = (instruction >> 63) & 0x7FFFFFF
                const_c = (instruction >> 45) & 0x3FFFF
                self.memory[addr_b] = const_c
                self.log.append(f"[{index}] LOAD_CONSTANT: Stored {const_c} in memory[{addr_b}].")

            elif opcode == 12:
                addr_b = (instruction >> 63) & 0x7FFFFFF
                addr_c = (instruction >> 36) & 0x7FFFFFF
                self.memory[addr_b] = self.memory[addr_c]
                self.log.append(f"[{index}] LOAD_MEMORY: Loaded value from memory[{addr_c}] to memory[{addr_b}].")

            elif opcode == 53:
                addr_b = (instruction >> 63) & 0x7FFFFFF
                addr_c = (instruction >> 36) & 0x7FFFFFF
                target_addr = self.memory[addr_b]
                self.memory[target_addr] = self.memory[addr_c]
                self.log.append(f"[{index}] STORE_TO_MEMORY: Stored value {self.memory[addr_c]} at address {target_addr}.")

            elif opcode == 38:
                addr_b = (instruction >> 63) & 0x7FFFFFF
                addr_c = (instruction >> 36) & 0x7FFFFFF
                offset_d = (instruction >> 28) & 0xFF
                addr_e = (instruction >> 1) & 0x7FFFFFF
                first_operand = self.memory[addr_c + offset_d]
                second_operand = self.memory[addr_e]
                result = first_operand - second_operand
                self.memory[addr_b] = result
                self.log.append(f"[{index}] SUBTRACT: Calculated {first_operand} - {second_operand} = {result}, stored in memory[{addr_b}].")

            else:
                raise RuntimeError(f"Unknown opcode {opcode} at index {index}.")

    def get_memory_dump(self, start=0, end=4096):
        dump = {}
        for i in range(start, end):
            if self.memory[i] != 0:
                dump[f"address_{i}"] = self.memory[i]
        return dump


def main():
    if len(sys.argv) != 6:
        print("Usage: python script.py <input_file> <output_bin> <log_file> <result_json> <memory_dump_range>")
        sys.exit(1)

    input_file, binary_file, log_file, result_file, memory_range = sys.argv[1:6]
    start, end = map(int, memory_range.split('-'))

    with open(input_file, "r") as f:
        source_code = f.read()

    assembler = Assembler()
    machine_code, log = assembler.assemble(source_code)


    with open(binary_file, "wb") as f:
        for instruction in machine_code:
            f.write(instruction.to_bytes(12, byteorder='big'))
    print(f"Binary file saved to {binary_file}")


    with open(log_file, "w") as f:
        json.dump(log, f, indent=4)
    print(f"Log file saved to {log_file}")


    interpreter = Interpreter()
    try:
        interpreter.execute(machine_code)
        memory_dump = interpreter.get_memory_dump(start, end)
        with open(result_file, "w") as f:
            json.dump(memory_dump, f, indent=4)
        print(f"Memory dump saved to {result_file}")

    except RuntimeError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()