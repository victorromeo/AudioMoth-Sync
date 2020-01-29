#!/usr/bin/env python3

import os
from datetime import datetime, timezone, timedelta
from lib.config import cfg
from statistics import mean

latest_event = None
event_queue = []

class event():

    first_trigger:datetime
    last_trigger:datetime

    id:int

    def __init__(self):
        
        global latest_event, event_queue

        self.first_trigger = self.get_now()
        self.last_trigger = self.first_trigger

        self.id = cfg.getOrAddInt('event','next_id', 1)
        
        # Increment the config, so the next event gets the next id
        cfg.update('event','next_id', self.id + 1)

        with open(f'{cfg.paths.logs}/event.log','a+') as events:
            events.write(f'{self.id} {self.first_trigger.isoformat()} {cfg.name}\n')

        latest_event = self
        event_queue = []

    def enqueue(self, movement: int):
        global event_queue

        if self.has_ended():
            return False

        self.last_trigger = self.get_now()

        event_queue.append(movement)
        if len(event_queue) > cfg.event.event_queue_length:
            event_queue.pop(0)

        return True

    def get_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def get_event_start(self) -> datetime:
        # The date and time of files to associate with this event
        # should be related to the first event sample, but offset
        # so we can get earlier records also
        return self.first_trigger + timedelta(cfg.event.event_start_offset_sec)

    def get_event_stop(self) -> datetime:
        # The date and time of files to associate with this event 
        # should be related to when the last motion sample event 
        # was recorded, but offset, so we can get later records also
        return self.last_trigger + timedelta(cfg.event.event_stop_offset_sec)

    def get_seconds_until_stop(self):
        return (self.get_now() - self.get_event_stop()).total_seconds()

    def has_full_event_queue(self):
        # Full queue is when the queue has sufficient samples to determine 
        #  whether activity is still occurring
        return len(event_queue) >= cfg.event.event_queue_length

    def has_event_motion(self):
        # 'Motion' is when the average number of readings exceeds a threshold
        return mean(event_queue) > cfg.event.event_threshold_inactive

    def has_ended(self):
        return self.get_event_stop() < self.get_now() \
            and (self.has_full_event_queue() and not self.has_event_motion())
