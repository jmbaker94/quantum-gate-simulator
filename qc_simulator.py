import numpy as np
import itertools

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
        print(value)
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
        print(self.vector)

    def __getitem__(self, item):
        if item not in ['0', '1']:
            print("can't get this qbit item")
            return None
        return self._state[item]

    def __str__(self):
        return str(self.vector)

    def bind_to(self, callback):
        self._observers.append(callback)


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
        self._vector = new_state

        for i in range(len(self)):
            sums = [0, 0]
            which = 0
            for j in range(2 ** len(self)):
                if j != 0 and j % (2 ** i) == 0:
                    which = (which + 1) % 2
                sums[which] += float(new_state[j][0])
                j += 1
            self._bits[len(self) - 1 - i].vector = np.matrix([[sums[0]], [sums[1]]])

    def __str__(self):
        return str(self.vector)


def measure(state):
    if type(state) is QBit:
        state.state = str(np.random.choice(np.arange(0, 2), p=[float(x) ** 2 for x in state.vector]))
    elif type(state) is QState:
        pass


def hadamard(qbit: QBit):
    T = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            T[i][j] = 1/(2 ** (1/2)) * (-1) ** (i * j)
    qbit.vector = np.dot(T, qbit.vector)


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


#q = QBit('0')
#print(q)
#hadamard(q)
#print(q)
#hadamard(q)
#print(q)
#pauli_x(q)
#print(q)
#print("///////")
#q = QBit('0')
#hadamard(q)
#measure(q)
#print(q)
#print("//////")
#q1 = QBit('0')
#q2 = QBit('0')
#q3 = QBit('1')
#hadamard(q1)
#hadamard(q2)
#qs = QState([q1, q2, q3])
#print(qs)
#lnot(qs[2])
#print(qs)
#Toffoli(qs)
#print(qs)

#

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
