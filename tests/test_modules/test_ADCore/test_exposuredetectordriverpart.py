import unittest
from mock import MagicMock, ANY, call

from scanpointgenerator import LineGenerator, CompoundGenerator

from malcolm.core import call_with_params, Context
from malcolm.modules.ADCore.parts import ExposureDetectorDriverPart


class TestExposureDetectorDriverPart(unittest.TestCase):

    def setUp(self):
        self.context = MagicMock(spec=Context)
        self.o = call_with_params(
            ExposureDetectorDriverPart, readoutTime=0.002, name="m", mri="mri")
        list(self.o.create_attributes())

    def test_configure(self):
        params = MagicMock()
        xs = LineGenerator("x", "mm", 0.0, 0.5, 3, alternate=True)
        ys = LineGenerator("y", "mm", 0.0, 0.1, 2)
        params.generator = CompoundGenerator([ys, xs], [], [], 0.1)
        completed_steps = 0
        steps_to_do = 6
        part_info = ANY
        self.o.configure(
            self.context, completed_steps, steps_to_do, part_info, params)
        assert self.context.mock_calls == [
            call.unsubscribe_all(),
            call.block_view('mri'),
            call.block_view().put_attribute_values_async(dict(
                imageMode="Multiple",
                numImages=steps_to_do,
                arrayCounter=completed_steps,
                arrayCallbacks=True)),
            call.block_view().exposure.put_value_async(0.1 - 0.002),
            call.block_view().put_attribute_values_async().append(ANY),
            call.wait_all_futures(ANY),
            call.block_view().start_async()]

    def test_run(self):
        update_completed_steps = MagicMock()
        self.o.start_future = MagicMock()
        self.o.done_when_reaches = MagicMock()
        self.o.run(self.context, update_completed_steps)
        assert self.context.mock_calls == [
            call.block_view('mri'),
            call.block_view().arrayCounter.subscribe_value(
                update_completed_steps, self.o),
            call.wait_all_futures(self.o.start_future),
            call.block_view().when_value_matches(
                'arrayCounter', self.o.done_when_reaches, timeout=0.1)
        ]

    def test_abort(self):
        self.o.abort(self.context)
        assert self.context.mock_calls == [
            call.block_view('mri'),
            call.block_view().stop()]