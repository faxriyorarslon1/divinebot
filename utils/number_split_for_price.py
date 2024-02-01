def price_split(number):
    try:
        number = int(number)
        str_number = str(number)
        if len(str_number) <= 3:
            return str_number
        first = 0
        last = len(str_number) - 1
        final_str = ""
        reversed_number = ""
        # final_str += str_number[0]
        nul = 0
        while last >= first:
            final_str += str_number[last]
            nul += 1
            if nul == 3:
                final_str += " "
                nul = 0
            last -= 1
        last = len(final_str) - 1
        while last >= first:
            reversed_number += final_str[last]
            last -= 1
        return reversed_number
    except Exception:
        return number


# print(price_split(50000000.0))

"5000"
