def decrypt_caesar_cipher(ciphertext):
    possible_plaintexts = []

    for shift in range(26):  # 尝试所有可能的位移值
        decrypted_text = ''
        for char in ciphertext:
            if char.isalpha():  # 检查字符是否为字母
                # 确定字符是大写还是小写
                is_upper = char.isupper()
                # 计算基础字母（'a' 或 'A'）
                base = 'A' if is_upper else 'a'
                # 计算解密后的字符
                decrypted_char = chr((ord(char) - ord(base) - shift) % 26 + ord(base))
                # 保持原字符的大小写
                if is_upper:
                    decrypted_char = decrypted_char.upper()
                decrypted_text += decrypted_char
            else:
                # 非字母字符原样添加
                decrypted_text += char

                # 将解密后的文本添加到列表中
        possible_plaintexts.append((shift, decrypted_text.lower()))

        # 打印所有可能的明文和对应的位移值
    for shift, plaintext in possible_plaintexts:
        print(f"Shift: {shift}, Possible Plaintext: {plaintext}")

    # 测试解密


code2 = "MUDUUTTHUQCI. QEBVDFSBRPXSFPFLKLCXYBQQBOCRQROB. JWMCQNHWXDARBQXDABYRARC. "  # 假设这是密文
decrypt_caesar_cipher(code2)


# 测试代码
code = 'MUDUUTTHUQCI. '

