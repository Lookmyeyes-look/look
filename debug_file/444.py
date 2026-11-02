import base64



def main():
    response_base64 = "{base64ResponseBodyString}"
    decode_base64 = bytearray(base64.b64decode(response_base64))
    secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    key_in_response_header = "114280586036259940"

    xor(decode_base64, long_to_bytes(fnv_hash(key_in_response_header + secret)))
    print(decode_base64.decode('utf-8'))


def xor(content, key):
    i = 0
    j = 0
    while i < len(content):
        content[i] ^= key[j]
        i += 1
        j = (j + 1) % len(key)


def long_to_bytes(long_value):
    result = []
    for i in range(8):
        result.append(long_value & 0xFF)
        long_value >>= 8
    return bytes(result)


def fnv_hash(data):
    p = 16777619
    hash_value = 2166136261

    for char in data:
        hash_value = ((hash_value ^ ord(char)) * p) & 0xFFFFFFFF

    hash_value = (hash_value + (hash_value << 13)) & 0xFFFFFFFF
    hash_value ^= hash_value >> 7
    hash_value = (hash_value + (hash_value << 3)) & 0xFFFFFFFF
    hash_value ^= hash_value >> 17
    hash_value = (hash_value + (hash_value << 5)) & 0xFFFFFFFF

    return abs(hash_value) if hash_value < 0x80000000 else hash_value


if __name__ == "__main__":
    main()
