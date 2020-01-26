#!/usr/bin/env python3

import os
import datetime
from lib.config import cfg

latest_event = None

class event():

    when:datetime.datetime
    id:int

    @staticmethod
    def has_expired(i):
        global latest_event

        expiry = cfg.getOrAddInt('event','expiry_seconds',600)
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()

        if e is None:
           return True, 0

        diff = now - i.when

        return diff.total_seconds() > expiry, diff.total_seconds - expiry

    def __init__(self):
        
        global latest_event
        local_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
        self.when = local_time

        self.id = cfg.getOrAddInt('event','next_id', 1)
        cfg.update('event','next_id', self.id + 1)

        with open(f'{cfg.paths.logs}/event.log','a+') as events:
            events.write(f'{self.id} {self.when.isoformat()} {cfg.name}\n')

        latest_event = self
