#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
# <copyright file="objects.py" company="Invariance Pte">
#  Copyright (C) 2018 Invariance Pte. All rights reserved.
#  The use of this source code is governed by the license as found in the LICENSE.md file.
#  http://www.invariance.com
# </copyright>
# -------------------------------------------------------------------------------------------------

from inv_trader.model.enums import Venue, Resolution, QuoteType, OrderSide
from inv_trader.model.objects import Symbol, Tick, BarType, Bar
from inv_trader.model.order import OrderFactory
from inv_trader.model.events import Event
from inv_trader.model.identifiers import Label, OrderId, PositionId
from inv_trader.strategy import TradeStrategy
from inv_indicators.average.ema import ExponentialMovingAverage
from test_kit.objects import ObjectStorer

GBPUSD_FXCM = Symbol('GBPUSD', Venue.FXCM)


class TestStrategy1(TradeStrategy):
    """"
    A simple strategy for unit testing.
    """

    def __init__(self):
        """
        Initializes a new instance of the TestStrategy1 class.
        """
        super().__init__(label='UnitTests', order_id_tag='TS01')
        self.object_storer = ObjectStorer()

        self.gbpusd_1sec_mid = BarType(GBPUSD_FXCM,
                                       1,
                                       Resolution.SECOND,
                                       QuoteType.MID)

        self.ema1 = ExponentialMovingAverage(10)
        self.ema2 = ExponentialMovingAverage(20)

        self.register_indicator(self.gbpusd_1sec_mid, self.ema1, self.ema1.update, Label('ema1'))
        self.register_indicator(self.gbpusd_1sec_mid, self.ema2, self.ema2.update, Label('ema2'))

        self.position_id = None

    def on_start(self):
        self.object_storer.store('custom start logic')

    def on_tick(self, tick: Tick):
        self.object_storer.store(tick)

    def on_bar(
            self,
            bar_type: BarType,
            bar: Bar):

        self.object_storer.store((bar_type, Bar))

        if bar_type == self.gbpusd_1sec_mid:
            if self.ema1.value > self.ema2.value:
                buy_order = OrderFactory.market(
                    Symbol('GBPUSD', Venue.FXCM),
                    OrderId('O123456'),
                    'TestStrategy1_E',
                    OrderSide.BUY,
                    100000)

                self.submit_order(buy_order, PositionId(str(buy_order.id)))
                self.position_id = buy_order.id

            elif self.ema1.value < self.ema2.value:
                sell_order = OrderFactory.market(
                    Symbol('GBPUSD', Venue.FXCM),
                    OrderId('O123456'),
                    'TestStrategy1_E',
                    OrderSide.SELL,
                    100000)

                self.submit_order(sell_order, PositionId(str(sell_order.id)))
                self.position_id = sell_order.id

    def on_event(self, event: Event):
        self.object_storer.store(event)

    def on_stop(self):
        self.object_storer.store('custom stop logic')

    def on_reset(self):
        self.object_storer.store('custom reset logic')
