from sklearn.preprocessing import minmax_scale, StandardScaler
import numpy as np

class Test:

    def __init__(self):
        self.d = {
            'a': TestObject('guszti',1),
            'b': TestObject('pauli',2),
            'c': TestObject('danil',3)
        }

    def overwrite(self):
        for key, value in self.d.items():
            if value.name == 'danil':
                value.number = 99

class TestObject:
    def __init__(self, name, number):
        self.name = name
        self.number = number

    def __repr__(self):
        return f'<TestObject> name: {self.name} number: {self.number}'

t = Test()
t.overwrite()
print(t.d)