import pytest
import os
from native_fisher_py.raw_file import RawFile
from native_fisher_py.data.classes import ScanEvent, MassAnalyzer, MsOrderType, PolarityType

def test_scan_events_zoom(zoom_raw_file):
    events = zoom_raw_file.method_scan_events
    
    assert events.segments == 1
    assert events.scan_events == 2
    
    count = events.get_event_count(0)
    assert count == 2
    
    evt = events.get_event_by_segment(0, 0)
    assert isinstance(evt, ScanEvent)
    
    # Assert properties of the method scan event itself!
    assert evt.mass_analyzer == MassAnalyzer.Sector
    assert evt.ms_order == MsOrderType.Any
    assert evt.polarity == PolarityType.Negative
    # Check the second event
    evt1 = events.get_event_by_segment(0, 1)
    assert isinstance(evt1, ScanEvent)
    assert evt1.mass_analyzer == MassAnalyzer.Sector
    assert evt1.ms_order == MsOrderType.Any
    assert evt1.polarity == PolarityType.Negative

def test_scan_events_prec_range(prec_range_raw_file):
    events = prec_range_raw_file.method_scan_events
    
    assert events.segments == 1
    assert events.scan_events == 1
    
    count = events.get_event_count(0)
    assert count == 1
    
    evt = events.get_event_by_segment(0, 0)
    assert isinstance(evt, ScanEvent)
    
    # Assert properties of the method scan event itself!
    assert evt.mass_analyzer == MassAnalyzer.Sector
    assert evt.ms_order == MsOrderType.Any
    assert evt.polarity == PolarityType.Negative


def test_scan_events_angiotensin(angiotensin_raw_file):
    events = angiotensin_raw_file.method_scan_events
    
    assert events.segments == 0
    assert events.scan_events == 0


