from datetime import datetime, timedelta

class Power:

    def __init__(self):
        print('Initializing Power')
        self.check_at = datetime.utcnow()
        self.check_result = False

    def is_charging(self):
        return False

    def is_charged(self):
        return False
        
    def is_powered(self):
        return False
    
    def should_sleep(self):

        now = datetime.utcnow()
        if now < self.check_at:
            return self.check_result

        self.check_result = not (self.is_powered() or self.is_charged() or self.is_charging())
        self.check_at = now + timedelta(seconds = 60)

        return self.check_result
    
    def status(self):

        return {
            'is_charging': self.is_charging(),
            'is_charged': self.is_charged(),
            'is_powered': self.is_powered(),
            'sleep_check_at': self.check_at.strftime("%Y%m%d_%H%M%S"),
            'sleep_check_result': self.check_result,
            'data': {

            }
        }

from lib.dependencies.pijuice import PiJuice

class PiJuicePower(Power):
    
    pij:PiJuice

    def __init__(self):
        Power.__init__(self)
        self.pij = PiJuice()

    def is_charging(self):

        # E.g. when charging from PiJuice {'data': {'isFault': True, 'isButton': False, 'battery': 'CHARGING_FROM_IN', 'powerInput': 'PRESENT', 'powerInput5vIo': 'NOT_PRESENT'}, 'error': 'NO_ERROR'}
        # E.g. when charging from Pi      {'data': {'isFault': False, 'isButton': False, 'battery': 'CHARGING_FROM_5V_IO', 'powerInput': 'NOT_PRESENT', 'powerInput5vIo': 'WEAK'}, 'error': 'NO_ERROR'}
        
        status = self.pij.status.GetStatus()

        if status['error'] == 'NO_ERROR':

            if status['data']['powerInput'] == 'PRESENT' \
                and self.get_battery_current() < 0:
                return True

            if status['data']['powerInput5vIo'] != 'NOT_PRESENT' \
                and self.get_battery_current() < 0:
                return True

        return False

    def is_charged(self):
        return self.get_battery_voltage() > 3800
        
    def is_powered(self):
        status = self.pij.status.GetStatus()
        return status['error'] == 'NO_ERROR' \
            and status['data']['powerInput5vIo'] != 'NOT_PRESENT'

    def get_battery_current(self):
        current = self.pij.status.GetBatteryCurrent()
        if current['error']=='NO_ERROR':
            return current['data']
        
        return 0
    
    def get_battery_voltage(self):
        voltage = self.pij.status.GetBatteryVoltage()
        if voltage['error']=='NO_ERROR':
            return voltage['data']
        
        return 0

    def get_battery_voltage_min(self):
        profile = self.pij.config.GetBatteryProfile()

        if profile['error'] == 'NO_ERROR':
            return profile['data']['cutoffVoltage']
        
        return 0

    def get_battery_voltage_max(self):
        profile = self.pij.config.GetBatteryProfile()

        if profile['error'] == 'NO_ERROR':
            return profile['data']['regulationVoltage']
        
        return 0  

    def get_supply_voltage(self):
        voltage = self.pij.status.GetIoVoltage()
        if voltage['error'] == 'NO_ERROR':
            return voltage['data']

        return 0
    
    def get_supply_current(self):
        current = self.pij.status.GetIoCurrent()
        if current['error'] == 'NO_ERROR':
            return current['data']
        
        return 0

    def get_charge_level(self):
        charge_level = self.pij.status.GetChargeLevel().get('data', -1)
        return charge_level

    def should_sleep(self):
        return Power.should_sleep(self)

    def status(self):
        status = Power.status(self)
        status['data']['battery_voltage'] = self.get_battery_voltage()
        status['data']['battery_current'] = self.get_battery_current()
        status['data']['battery_voltage_min'] = self.get_battery_voltage_min()
        status['data']['battery_voltage_max'] = self.get_battery_voltage_max()
        status['data']['charge_level'] = self.get_charge_level()
        status['data']['supply_current'] = self.get_supply_current()
        status['data']['supply_voltage'] = self.get_supply_voltage()

        return status
