import struct
import os

def parse_line(line):
    """Parse uma linha e retorna o tipo, valor e tamanho."""
    line = line.strip()
    if not line:
        return None

    parts = line.split(' ', 1)
    if len(parts) < 2:
        return None

    type_char = parts[0].lower()
    values = parts[1].split(',')

    return type_char, values

def process_line(type_char, values):
    """Converte uma linha em binário com base no tipo."""
    data = b""
    if type_char == 'i':  # Inteiro 32 bits
        for value in values:
            data += struct.pack('<i', int(value))
    elif type_char == 'f':  # Float 32 bits
        for value in values:
            data += struct.pack('<f', float(value))
    elif type_char == 'c':  # Caráter código
        for value in values:
            data += struct.pack('B', int(value))
    elif type_char == 's':  # String até o fim da linha
        for value in values:
            encoded = value.replace("\\n", "\n").replace("\\r", "\r").encode('utf-8')
            data += encoded
    elif type_char == 'z':  # Zeros (buffer de tamanho)
        for value in values:
            data += b'\x00' * int(value)
    elif type_char == 'h':  # Valor hexadecimal
        for value in values:
            data += bytes.fromhex(value)
    elif type_char == 'b':  # Conteúdo de ficheiro
        for value in values:
            with open(value.strip(), 'rb') as file:
                data += file.read()
    else:
        raise ValueError(f"Tipo desconhecido: {type_char}")

    return data

def main():
    input_file = input("Insira o nome do ficheiro de entrada (.txt): ").strip()
    if not os.path.isfile(input_file):
        print("Ficheiro não encontrado!")
        return

    output_file = os.path.splitext(input_file)[0] + ".dat"

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    if not lines:
        print("O ficheiro está vazio.")
        return

    # Processa a primeira linha para obter a tabela de índices
    table_line = lines.pop(0).strip()
    index_count = int(table_line)
    indices = [0] * index_count  # Tabela de índices inicializada com 0

    binary_data = b""
    offsets = []

    for line in lines:
        if not line.strip():
            continue  # Ignorar linhas vazias

        offsets.append(len(binary_data))  # Armazena o offset do início
        parsed = parse_line(line)
        if not parsed:
            continue

        type_char, values = parsed
        binary_data += process_line(type_char, values)

    # Atualiza os índices no binário
    binary_table = struct.pack(f'<{len(offsets)}I', *offsets)

    with open(output_file, 'wb') as outfile:
        outfile.write(binary_table)  # Grava a tabela de índices
        outfile.write(binary_data)   # Grava os dados binários

    # Exibir os offsets
    print("Tabela de índices (em hexadecimal):")
    for i, offset in enumerate(offsets):
        print(f"Índice {i}: {hex(offset)}")

    print(f"Ficheiro binário gravado como: {output_file}")

if __name__ == "__main__":
    main()

