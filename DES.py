from DES_tables import *
import SDES_tables


# Performs permutation on bit buffer with length of block_len using p_table
def P(buff, buff_len, p_table):
    # Accessing bits from LEFT to RIGHT [1, 2, 3,..., block_len]
    # Indexing starts from 1
    block_len = len(p_table)
    padding = block_len - buff_len
    mask = 2**(buff_len - 1)
    res = 0
    for i in range(1, block_len+1):
        bit_change_to_index = p_table[i-1]
        bit_change_to = mask >> (bit_change_to_index - 1) & buff
        i -= padding
        if bit_change_to_index >= i:
            change_mask = (bit_change_to << (bit_change_to_index - i))
        else:
            change_mask = (bit_change_to >> (i - bit_change_to_index))
        res |= change_mask
    return res


# Adjust buffer to specified block_len by:
# Dropping least significant bits e.g. pad(0b10001, 4) -> 0b1000
# or by shifting buff to the left e.g pad(0b111, 8) -> 0b11100000
def pad(buff, block_len):
    if buff >= 2**block_len:
        while buff // 2**(block_len - 1) != 1:
            buff >>= 1
    else:
        while buff // 2**(block_len - 1) != 1:
            buff <<= 1
    return buff


# Splits buffer size of block_len into two half
# e.g. split_buffer(0b11110001, 8) -> (0b1111, 0b1)
def split_buffer(buffer, block_len):
    shift = int(block_len / 2)
    L = buffer >> shift
    R = buffer & (2 ** shift - 1)
    return (L, R)


# Left circular shift
# e.g LCSHIFT(0b1111000, 7) -> 0b1110001
def LCSHIFT(buff, block_len):
    if buff & 2 ** (block_len - 1):
        return buff << 1 & 2**block_len - 1 | 1
    else:
        return buff << 1 & 2 ** block_len - 1


# E.g concat(0b1111, 0b10, 8) -> 0b11110010
def concat(L, R, block_len):
    return L << int(block_len / 2) | R


# Calculates the key schedule
def key_schedule(key, key_len, PCO_table, PCT_table, shifts_table):
    actual_key_len = len(PCO_table)
    key = P(key, key_len, PCO_table)
    C, D = split_buffer(key, actual_key_len)
    keys = []
    for s in range(len(shifts_table)):
        for i in range(shifts_table[s]):
            C = LCSHIFT(C, int(actual_key_len / 2))
            D = LCSHIFT(D, int(actual_key_len / 2))
        K = concat(C, D, actual_key_len)
        K = P(K, actual_key_len, PCT_table)
        keys.append(K)
    return keys


# For DES:
#   Break E(R[i-1]) xor K[i] into eight 6-bit blocks.
#   Bits 1-6 are B[1], bits 7-12 are B[2], and so on with bits 43-48 being B[8].
def break_into_B(block, block_size, b_size):
    mask = 2**b_size - 1
    B = []
    while block:
        b = block & mask
        block = block >> b_size
        B.append(b)
    B.reverse()
    while len(B) != int(block_size / b_size):
        B = [0] + B
    return B


# For DES:
#   Take the 1st and 6th bits of B[j] together as a 2-bit value (call it m),
#   indicating the row in S[j] to look in for the substitution.
#   Take the 2nd through 5th bits of B[j] together as a 4-bit value (call it n),
#   indicating the column in S[j] to find the substitution.
# Returns (m, n)
def get_row_column(b, b_size):
    first_bit_mask = 2**(b_size-1)
    r = (b & first_bit_mask) >> (b_size - 2)
    r |= b & 1
    mid_mask = (2**(b_size-2) - 1) << 1
    c = (b & mid_mask) >> 1
    return (r, c)


# Replace B[j] with S[j][m][n].
def perform_s_function(B, b_size, S):
    for j in range(len(S)):
        r, c = get_row_column(B[j], b_size)
        B[j] = S[j][r][c]
    return B


# Used to concat B[0]...B[j]
def concat_B(B, b_size):
    res = 0
    for i in range(len(B)):
        b = B[i]
        res |= b
        res = res << b_size
    return res >> b_size



def DES_encrypt(data_block, key, encrypt=True):
    print('DataBlock = {}, Key = {}'.format(hex(data_block), hex(key)))
    data_block = P(data_block, 64, DES_IP_table)
    L, R = split_buffer(data_block, 64)
    keys = key_schedule(key, 64, DES_PCO_table, DES_PCT_table, DES_key_shifts)
    if not encrypt:
        keys.reverse()
    print('IP&Split: {} -> L={}, R={}'.format(hex(data_block), hex(L), hex(R)))
    tmp = 0
    for i in range(len(keys)):
        tmp = R
        R = P(R, 32, DES_E_table)
        R ^= keys[i]
        B = break_into_B(R, 48, 6)
        B = perform_s_function(B, 6, DES_S)
        R = concat_B(B, 4)
        R = P(R, 32, DES_PE_table)
        R = L ^ R
        L = tmp
        print('Round {}: L={}, R={}, key{}={}'.format(i+1, hex(L),
                                                      hex(R), i+1, hex(keys[i])))
    L, R = R, L
    print('Finally: L={}, R={}'.format(hex(L), hex(R)))
    block = concat(L, R, 64)
    block = P(block, 64, DES_IP_reverse_table)
    print('Result -> {}'.format(hex(block)))
    return block


def DES_decrypt(data_block, key):
    return DES_encrypt(data_block, key, encrypt=False)


# Converts string to integer
# Resulting integer will be adjusted to 64 bit value !
def string_to_data_block(text):
    res = 0
    for ch in text:
        res |= ord(ch)
        res = res << 8
    return pad(res, 64)


# Adjust key to 64 bits value
def key_adjustment(key):
    return pad(key, 64)


# Returns number of different bits
# E.g diff_count(0b101, 0b111) -> 1
#     diff_count(0b111, 0b111) -> 0
def diff_count(block1, block2):
    block = block1 ^ block2
    res = 0
    while block:
        res += block & 1
        block = block >> 1
    return res


# Switches specified bit in data_block,
# Indexing starts from 1  [1, 2, 3, 4, 5, 6]
# E. g. switch_bit('0b1010', 4, 2) -> '0b1110'
def switch_bit(data_block, block_len, bit_number):
    mask = 2**(block_len - 1)
    bit_index_mask = mask >> (bit_number - 1)
    bit_switch_with = data_block & bit_index_mask
    if bit_switch_with:
        mask = (2**(bit_number - 1) - 1) << (block_len - bit_number + 1) | (2**(block_len - bit_number) - 1)
        data_block &= mask
    else:
        data_block |= bit_index_mask
    return data_block


def SDES_encrypt(data_block, key, encrypt=True):
    print('DataBlock = {}, Key = {}'.format(bin(data_block), bin(key)))
    data_block = P(data_block, 8, SDES_tables.IP_table)
    keys = key_schedule(key, 10, SDES_tables.P10, SDES_tables.P8, SDES_tables.key_shifts)
    L, R = split_buffer(data_block, 8)
    if not encrypt:
        keys.reverse()
    print('IP&Split: {} -> L={}, R={}'.format(bin(data_block), bin(L), bin(R)))
    tmp = 0
    for i in range(len(keys)):
        tmp = R
        R = P(R, 4, SDES_tables.E)
        R ^= keys[i]
        B = break_into_B(R, 8, 4)
        B = perform_s_function(B, 4, SDES_tables.S)
        R = concat_B(B, 2)
        R = P(R, 4, SDES_tables.P4)
        R = L ^ R
        L = tmp
        print('Round {}: L={}, R={}, key{}={}'.format(i + 1, bin(L),
                                                     bin(R), i + 1, bin(keys[i])))
    L, R = R, L
    print('Finally: L={}, R={}'.format(bin(L), bin(R)))
    block = concat(L, R, 8)
    block = P(block, 8, SDES_tables.IP_reverse_table)
    print('Result -> {}'.format(bin(block)))
    return block


def SDES_decrypt(data_block, key):
    return SDES_encrypt(data_block, key, encrypt=False)

m = int('01001100', 2)
k = int('1111111111', 2)
res = SDES_encrypt(m, k)
print(bin(res))

