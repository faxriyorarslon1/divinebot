def product_count(params):
    product_id = ""
    length = 0
    for i in range(len(params) - 1):
        if params[i] != "a":
            product_id += params[i]
            if params[i] == "b":
                length = i
                break
    count = params[length + 1:]
    product_id = int(product_id[0:len(product_id) - 1])
    count = int(count)
    return product_id, count
