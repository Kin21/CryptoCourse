import math

VERBOSE = False


def verbose(fun):
    def wrapper(*args, **kwargs):
        fun_res = fun(*args, **kwargs)
        global VERBOSE
        if VERBOSE:
            print("{}({}) -> {}".format(fun.__name__, ','.join([str(i) for i in args]), str(fun_res)))
        return fun_res
    return wrapper


@verbose
def split(n, form='exp'):
    d = 2
    factors = []
    while math.pow(d, 2) <= n:
        if n % d == 0:
            factors.append(d)
            n = n // d
            d = 2
            if n == 1:
                break
        else:
            d += 1
    else:
        factors.append(n)

    match form:
        case 'list':
            return factors
        case 'exp':
            return {i: factors.count(i) for i in set(factors)}


@verbose
def el(n):
    d_res = split(n)
    res = n
    for num, power in d_res.items():
        res *= (1 - (1/num))
    return res


def evklid(a, b):
    if a < b:
        a, b = b, a
    q = a//b
    r = a - b*q
    pr_list = list()
    print('{} = {}*{} + {}'.format(a, b, q, r) )
    pr_list.append(q)
    while r != 0:
        a = b
        b = r
        q = a // b
        r = a - q*b
        print('{} = {}*{} + {}'.format(a, b, q, r) )
        pr_list.append(q)
    pr_list.pop()
    return [b, pr_list]


def _ev1(m, a):
    q = m // a
    r = m % a
    return (q, r)


def evklid2(a, m):
    print('#' + '-'*25 + '#')
    if a > m:
        a, m = m, a
    r = -1
    q = 0
    res = []
    while r != 0:
        q, r = _ev1(m, a)
        res.append([m, q, a, r])
        print('{} = {}*{} + {}'.format(m, q, a, r))
        m = a
        a = r
    print('({},{}): {}'.format(res[0][0], res[0][2], res[-2][-1]))
    print('#' + '-'*25 + '#')
    ##
    res = res[:len(res) - 1]
    res.reverse()
    for i in range(len(res)):
        m, q, a, r = res[i]
        print('{}={}-{}*{}'.format(r, m, q, a))
    print('#' + '-'*25 + '#')


def get_linear_divisor(num1: int, num2: int) -> dict:
    """
    GCD = u*num1 + v*num2
    num1 > num2
    :return: {num1: u, num2: v}
    """
    if num1 < num2:
        num1, num2 = num2, num1
    evk_result = evklid(num1, num2)
    gcd = evk_result[0]
    q_list = evk_result[1]
    u_list = [0, 1]
    for i in range(0, len(q_list)):
        u_list.append(u_list[i] + u_list[i+1]*q_list[i])
    u = u_list.pop()
    v_list = [1, ]
    if len(q_list) >= 2:
        v_list.append(q_list[1])
    for i in range(2, len(q_list)):
        v_list.append(v_list[i - 2] + q_list[i] * v_list[i - 1])
    v = v_list.pop()
    if num1*u - num2*v == gcd:
        return {num1: u, num2: -v}
    elif -num1*u + num2*v == gcd:
        return {num1: -u, num2: v}
    elif num2*u - num1*v == gcd:
        return {num1: -v, num2: u}
    elif -num2*u + num1*v == gcd:
        return {num1: v, num2: -u}


alphabet = [chr(i) for i in range(ord('A'), ord('Z')+1)]
alp_m = len(alphabet)


@verbose
def caesar_e(text, key=3):
    text = ''.join(text.strip().split(' ')).upper()
    global alphabet
    global alp_m
    cpr_text = ''
    for c in text:
        cpr_text += alphabet[(alphabet.index(c) + key) % alp_m]
    return cpr_text


@verbose
def caesar_d(text, key=3):
    global alp_m
    key = -key % alp_m
    return caesar_e(text, key)


def caesar_bf(cpr_text):
    global alp_m
    for i in range(0, alp_m+1):
        caesar_d(cpr_text, i)

@verbose
def vigenere_e(text, key):
    text = ''.join(text.strip().split(' ')).upper()
    key = key.strip().upper()
    while len(key) < len(text):
        key += key
    key_i = 0
    cpr_text = ''
    for ch in text:
        current_key = alphabet.index(key[key_i])
        cpr_text += caesar_e(ch, current_key)
        key_i += 1
    return cpr_text


@verbose
def vigenere_d(cpr_text, key):
    cpr_text = ''.join(cpr_text.strip().split(' ')).upper()
    key = key.strip().upper()
    while len(key) < len(cpr_text):
        key += key
    key_i = 0
    text = ''
    for ch in cpr_text:
        current_key = alphabet.index(key[key_i])
        text += caesar_d(ch, current_key)
        key_i += 1
    return text
