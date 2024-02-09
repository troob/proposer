# hello world test for cython

cimport cython

print('Hello Cython')

def f(double x):
    return x ** 2 - x


def integrate_f(double a, double b, int N):
    cdef int i
    cdef double s
    cdef double dx
    s = 0
    dx = (b - a) / N
    for i in range(N):
        s += f(a + i * dx)
    test = s * dx
    print(test)
    return test

integrate_f(1.0, 1.0, 1)