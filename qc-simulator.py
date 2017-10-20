import numpy as np


class InputError(Exception):
    pass


stored_gates = {}


class QBit:
    """a|0> + b|1>"""
    def __init__(self, state='0'):
        self._state = {'0': 0, '1': 0, state: 1}
        self._vector = np.matrix([[self._state['0']], [self._state['1']]])

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, value: np.matrix):
        self._vector = value

    def __str__(self):
        return str(self.vector)


def hadamard(qbit: QBit):
    T = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            T[i][j] = 1/(2 ** (1/2)) * (-1) ** (i * j)
    qbit.vector = np.dot(T, qbit.vector)


q = QBit('0')
print(q)
hadamard(q)
print(q)
hadamard(q)
print(q)


"""
class QState:
    a_1|x_1> + a_2|x_2> + ... + a_n|x_n>
    def __init__(self, init_state='0', num_qbits=1):
        if len(init_state) > num_qbits:
            num_qbits = len(init_state)
        self.state = {}
        keys = list(itertools.product(['0', '1'], repeat=num_qbits))

        for k in keys:
            if init_state.ljust(num_qbits, '0') == ''.join(k):
                self.state[k] = 1
            else:
                self.state[k] = 0

    def __len__(self):
        return int(np.log2(len(self.state.keys())))


k = QBit('1')
print(k._state)


def hadamard_gate(ket: QState):
    Performs the generalized Hadamard transform on a ket of arbitrary length
    if ('hadamard', len(ket)) in stored_gates:
        T = stored_gates[('hadamard', len(ket))]
    else:
        T = np.zeros((2 ** len(ket), 2 ** len(ket)))
        for i in range(2 ** len(ket)):
            for j in range(2 ** len(ket)):
                T[i][j] = 1/(2 ** (len(ket)/2)) * (-1) ** (i * j)
    print(T)
    return np.transpose(ket.state).dot(T)



"""
