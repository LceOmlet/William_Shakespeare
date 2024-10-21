def number_to_uppercase_letter(n):
    n = n + 1
    if 1 <= n <= 26:
        return chr(64 + n)  # 65 ('A') = 64 + 1
    else:
        raise ValueError("输入数字必须在1到26之间")
    