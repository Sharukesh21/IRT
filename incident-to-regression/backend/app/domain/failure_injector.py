import copy
from typing import List
from datetime import timedelta
from abc import ABC, abstractmethod

from app.domain.events import BaseDomainEvent
from app.db.models.failure import FailureScenario, FailureType

class FailureStrategy(ABC):
    @abstractmethod
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        pass

class NormalStrategy(FailureStrategy):
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        return events

class DelayStrategy(FailureStrategy):
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        delay_ms = scenario.parameters.get("delay_ms", 1000)
        target_event = scenario.target_event_type
        
        modified_events = []
        for ev in events:
            modified = copy.deepcopy(ev)
            if target_event and modified.event_type == target_event:
                # Add delay to received_at
                # Occurred at remains the original logical time
                delay_delta = timedelta(milliseconds=delay_ms)
                if modified.received_at:
                    modified.received_at += delay_delta
                else:
                    modified.received_at = modified.occurred_at + delay_delta
            modified_events.append(modified)
        return modified_events

class DuplicateStrategy(FailureStrategy):
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        count = scenario.parameters.get("count", 1)
        target_event = scenario.target_event_type
        
        modified_events = []
        for ev in events:
            modified_events.append(ev)
            if target_event and ev.event_type == target_event:
                # Duplicate the event 'count' times
                for i in range(count):
                    duplicate = copy.deepcopy(ev)
                    # The event_id MUST remain the same to be caught by idempotency checks
                    if duplicate.received_at:
                        duplicate.received_at += timedelta(milliseconds=(i+1) * 10) # slightly delayed receive
                    else:
                        duplicate.received_at = duplicate.occurred_at + timedelta(milliseconds=(i+1) * 10)
                    modified_events.append(duplicate)
        return modified_events

class OutOfOrderStrategy(FailureStrategy):
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        # For prototype simplicity, we just swap the targeted event with the one before it
        target_event = scenario.target_event_type
        
        modified_events = copy.deepcopy(events)
        for i in range(1, len(modified_events)):
            if modified_events[i].event_type == target_event:
                # Swap with previous
                modified_events[i], modified_events[i-1] = modified_events[i-1], modified_events[i]
                
                # We also logically adjust received_at so the swapped one was "received first"
                if modified_events[i-1].received_at and modified_events[i].received_at:
                    modified_events[i-1].received_at, modified_events[i].received_at = modified_events[i].received_at, modified_events[i-1].received_at
                break # Only swap the first occurrence for now
                
        return modified_events

class TimeoutStrategy(FailureStrategy):
    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        # Timeout implies the client thinks it failed, so it retries.
        # Server actually receives BOTH. This is logically identical to DUPLICATE with a larger gap.
        count = 1
        target_event = scenario.target_event_type
        delay_ms = scenario.parameters.get("timeout_ms", 5000)
        
        modified_events = []
        for ev in events:
            modified_events.append(ev)
            if target_event and ev.event_type == target_event:
                retry_event = copy.deepcopy(ev)
                if retry_event.received_at:
                    retry_event.received_at += timedelta(milliseconds=delay_ms)
                else:
                    retry_event.received_at = retry_event.occurred_at + timedelta(milliseconds=delay_ms)
                modified_events.append(retry_event)
        return modified_events

class FailureInjector:
    def __init__(self):
        self.strategies = {
            FailureType.NONE: NormalStrategy(),
            FailureType.DELAY: DelayStrategy(),
            FailureType.DUPLICATE: DuplicateStrategy(),
            FailureType.OUT_OF_ORDER: OutOfOrderStrategy(),
            FailureType.TIMEOUT: TimeoutStrategy(),
            FailureType.RETRY: TimeoutStrategy(), # Retry behaves like timeout
        }

    def apply(self, events: List[BaseDomainEvent], scenario: FailureScenario) -> List[BaseDomainEvent]:
        strategy = self.strategies.get(scenario.failure_type, NormalStrategy())
        return strategy.apply(events, scenario)
