# -*- coding: utf-8 -*-

import pytest

from takeoff.core import takeoff


def test_takeoff():
    assert takeoff() == 'Takeoff complete!'
