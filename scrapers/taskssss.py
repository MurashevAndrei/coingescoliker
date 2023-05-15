def func(string):
    try:
        pr = string.split(' ')
    except:
        pr = [string]
    result = []
    for word in pr:
        print(list(word))
        res_word = list(reversed(word))
        result.append(''.join(res_word))
    result = list(reversed(result))
    r =  ' '.join(result)
    return r

#print(func('i love cats'))

def capt(text):
    res = []
    for a, i in enumerate(text):
        if i =="-" or i =="_":
            continue
        elif text[a-1] == "-" or text[a-1] == "_":
            res.append(i.upper())
        else:
            res.append(i)
    result = ''.join(res)
    return result

def count(num):
    a = len(str(num))
    res = 0
    for i in str(num):
        res = res + int(i)**a
    if int(res) == int(num):
        return True
    else:
        return False


print(count(153))
