def split(num):
    div_l  = list()
    i = 2
    while num != 1:
        if num % i == 0:
            num = num / i
            div_l.append(i)
            i = 2
        else:
            i += 1
        if i > num ** (1/2):
            div_l.append(int(num))
            break
    res = {}
    while div_l:
        res.update( {div_l[0]: div_l.count(div_l[0]) } )
        for i in range(0, div_l.count(div_l[0])):
            div_l.remove(div_l[0])
    return res

def el(num):
    d_res = split(num)
    print(d_res)
    res = num
    for num, power in d_res.items():
        res *= (1 - (1/num))
    print(res)


class PrimesFinder:
    def __init__(self):
        self.initial_primes_list = self.create_primes_list(int(1e+2), list(range(2, int(1e+4))))

    def create_primes_list(self, sqrt_num_, lst, pos = 0):
        if lst[pos] > sqrt_num_:
            return lst
        else:
            lst = list(x for x in lst if (x % lst[pos] != 0 or x == lst[pos]))
            return self.create_primes_list(sqrt_num_, lst, pos + 1)

    def is_prime(self, num):
        if num < 1e+6:
            return (num in self.initial_primes_list)

        check_to = num ** (1/2)
        for i in range(0, len(self.initial_primes_list)):
            if self.initial_primes_list[i] > check_to:
                return True
            if num % self.initial_primes_list[i] == 0 and num != self.initial_primes_list[i]:
                return False
        return -1

def Evklid(a, b):
    if a < b:
        a, b = b, a
    q = a//b
    r = a - b*q
    pr_list = list()
    print('{} = {}*{} + {}'.format(a, b, q, r) )
    pr_list.append(q)
    while  r != 0:
        a = b
        b = r
        q = a // b
        r = a - q*b
        print('{} = {}*{} + {}'.format(a, b, q, r) )
        pr_list.append(q)
    pr_list.pop()
    return [b, pr_list]


def get_linear_divisor(num1: int, num2: int) -> dict:
    """
    GCD = u*num1 + v*num2
    num1 > num2
    :return: {num1: u, num2: v}
    """
    if num1 < num2:
        num1, num2 = num2, num1
    evk_result = Evklid(num1, num2)
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




