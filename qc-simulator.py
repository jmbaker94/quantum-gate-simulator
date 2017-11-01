import numpy as np
import itertools
from scipy import linalg


# TODO: Can speed up change of qstate after single qbit measurements by simple formulation
# TODO: a00 |00> + a01 |01> / (sqrt(|a00|^2 + |a01|^2)

class InputError(Exception):
    pass


stored_gates = {}


class QBit:
    """a|0> + b|1>"""
    def __init__(self, state='0'):
        self._state = {'0': 0, '1': 0, state: 1}
        self._vector = np.matrix([[self._state['0']], [self._state['1']]])
        self._observers = []

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in ['0', '1']:
            print("can't set qbit")
            return
        self._state = {'0': 0, '1': 0, value: 1}
        self._vector = np.matrix([[self._state['0']], [self._state['1']]])

        for c in self._observers:
            c()

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, value: np.matrix):
        self._vector = value
        self._state['0'] = float(value[0][0])
        self._state['1'] = float(value[1][0])

        for c in self._observers:
            c()

    def __getitem__(self, item):
        if item not in ['0', '1']:
            print("can't get this qbit item")
            return None
        return self._state[item]

    def __str__(self):
        return str(self.vector)

    def bind_to(self, callback):
        self._observers.append(callback)

    def __len__(self):
        return 1


class QState:
    def __init__(self, li=None):
        self._bits = []

        if type(li) is list:
            self._bits = li

        elif type(li) is int:
            for i in range(li):
                self._bits.append(QBit())
        else:
            pass

        for b in self._bits:
            b.bind_to(self.__set)

        self._vector = []
        self.__set()

    def __set(self):
        self._vector = []
        keys = list(itertools.product(['0', '1'], repeat=len(self.bits)))
        for k in keys:
            p = 1
            for i in range(len(k)):
                p *= self._bits[i][k[i]]
            self._vector.append([p])

        self._vector = np.matrix(self._vector)

    @property
    def bits(self):
        return self._bits

    def __getitem__(self, item):
        return self._bits[item]

    def add_bit(self, bit=None):
        if bit is not None:
            self.bits.append(bit)
        else:
            self.bits.append(QBit())

    def substate(self, *args):
        new_state = QState()
        for i in args:
            if type(i) is not int:
                print("Invalid argument list")
                return
        for i in args:
            new_state.add_bit(self.bits[i])
        return new_state

    def __len__(self):
        return len(self._bits)

    @property
    def vector(self):
        if len(self._vector) < 2 ** len(self):
            self.__set()
        return self._vector

    @vector.setter
    # TODO: Concern with updating here!
    def vector(self, new_state):
        # print(new_state)
        self._vector = new_state

        solve_coefficients(len(self), new_state)

        # sums = [[0, 0] * len(self)]
        # for i in range(2 ** len(self)):
        #     pass
        # for i in range(len(self)):
        #     sums = [0, 0]
        #     which = 0
        #     for j in range(2 ** len(self)):
        #         if j != 0 and j % (2 ** i) == 0:
        #             which = (which + 1) % 2
        #         sums[which] += float(new_state[j][0])
        #         j += 1
        #     self._bits[len(self) - 1 - i].vector = np.matrix([[sums[0]], [sums[1]]])

    def __str__(self):
        return str(self.vector)


def measure(state):
    if type(state) is QBit:
        state.state = str(np.random.choice(np.arange(0, 2), p=[float(x) ** 2 for x in state.vector]))
    elif type(state) is QState:
        choice = str(np.random.choice(np.arange(0, len(state) ** 2), p=[float(x[0]) ** 2 for x in state.vector]))
        state.vector = [[(lambda x: 0 if x == choice else 1)(x)] for x in list(itertools.product(['0', '1'],
                                                                                                 repeat=len(state)))]


def hadamard(q_input):
    length = 2 ** len(q_input)
    # T = linalg.hadamard(length)
    # q_input.vector = np.dot(T, q_input.vector)

    T = np.zeros((length, length))
    for i in range(length):
        for j in range(length):
            T[i][j] = 1/(2 ** (len(q_input)/2)) * (-1) ** (i * j)
    print(T)
    q_input.vector = np.dot(T, q_input.vector)


def pauli_x(qbit: QBit):
    """NOT"""
    T = np.matrix([[0, 1], [1, 0]])
    qbit.vector = np.dot(T, qbit.vector)


def lnot(qbit: QBit):
    pauli_x(qbit)


def pauli_y(qbit: QBit):
    T = np.matrix([[0, 0-1j], [1j, 0]])
    qbit.vector = np.dot(T, qbit.vector)


def swap(qstate: QState):
    pass


def Toffoli(qstate: QState):
    if len(qstate) != 3:
        print("wrong length for toffoli")
        return
    T = np.matrix([[1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 1, 0]])
    qstate.vector = np.dot(T, qstate.vector)


def build_p_vec(qbit: QBit, index, length):
    v0 = []
    w = 0
    for i in range(2 ** length):
        if i != 0 and i % 2 ** (length - index - 1) == 0:
            w = (w + 1) % 2
        v0.append([float(qbit.vector[w][0])])
    return v0


def build_t_vectors(qstate: QState):
    pvectors = []
    for i in range(len(qstate)):
        pvectors.append(build_p_vec(qstate[i], i, len(qstate)))
    return pvectors


def test_tof(qstate: QState):
    """An attempt to solve how the bits change. Unsure if this is correct"""
    if len(qstate) != 3:
        print("wrong length for toffoli")
        return
    T = np.matrix([[1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 1, 0]])

    result_vectors = []
    for v in build_t_vectors(qstate):
        result_vectors.append(np.dot(T, v))
    qstate.vector = pointwise_product(result_vectors)


def pointwise_product(args):
    vnet = []
    for i in range(len(args[0])):
        val = 1
        for j in range(len(args)):
            val *= float(args[j][i][0])
        vnet.append([val])
    return vnet


def solve_coefficients(num_input_bits, gate_result):
    """Gate result: a vector containing the output values \alpha, \beta, ..."""

    # Series of equations := {(q1_0, q2_0, q3_0): gate_result[0],
    #                         (q1_0, q2_0, q3_1): gate_result[1],
    #                           ...
    #                         (q1_1, q2_1, q3_1): gate_result[2 ** num_inputs]}

    # Find which are 0's; construct the matrix to solve later of the nonzero ones
    zero = set()
    not_zero = set()
    w = [0] * num_input_bits
    for k in range(2 ** num_input_bits):
        for i in range(len(w)):
            if k != 0 and k % 2 ** (num_input_bits - i - 1) == 0:
                w[i] = (w[i] + 1) % 2
            s = str(i) + str(w[i])
            if gate_result[k][0] == 0:
                if s not in not_zero:
                    zero.add(s)
            else:
                if s in zero:
                    zero.remove(s)
                not_zero.add(s)


"""TODO: NEED TO KEEP WORKING ON SOLVING FOR HOW IT CHANGES EACH INDIVIDUAL BIT"""

q1 = QBit('0')
q2 = QBit('1')
q3 = QBit('1')
q4 = QBit('0')
q5 = QBit('1')
q6 = QBit('1')

qs = QState([q1, q2, q3])
qs2 = QState([q4, q5, q6])

# test_tof(qs2)

Toffoli(qs)
# print(qs.vector == qs2.vector)


# measure(qs)
# print(qs)


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