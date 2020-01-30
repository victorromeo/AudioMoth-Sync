class MockPiJuiceStatus:
    def GetStatus(self):
        return {'data': {'isFault': True, 'isButton': False, 'battery': 'CHARGING_FROM_IN', 'powerInput': 'PRESENT', 'powerInput5vIo': 'NOT_PRESENT'}, 'error': 'NO_ERROR'}

class MockPiJuice:
    def __init__(self):
        print('Mocked Power')
        self.status = MockPiJuiceStatus()

try:
    from pijuice import PiJuice
except:
    PiJuice = MockPiJuice
