import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import setup_malcolm_paths

import unittest
from mock import MagicMock, call, ANY

# logging
# import logging
# logging.basicConfig(level=logging.DEBUG)

# module imports
from malcolm.core.controller import Controller


class TestController(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        params = Controller.MethodMeta.prepare_input_map(mri="mri1")
        self.c = Controller(MagicMock(), {}, params)
        self.b = self.c.block

    def test_init(self):
        self.c.process.add_block.assert_called_once_with(self.b, self.c)
        self.assertEqual({}, self.c.parts)

        self.assertEqual(
            self.b["state"].meta.typeid, "malcolm:core/ChoiceMeta:1.0")
        self.assertEqual(self.b.state, "Disabled")
        self.assertEqual(
            self.b["status"].meta.typeid, "malcolm:core/StringMeta:1.0")
        self.assertEqual(self.b.status, "Disabled")
        self.assertEqual(
            self.b["busy"].meta.typeid, "malcolm:core/BooleanMeta:1.0")
        self.assertEqual(self.b.busy, False)

    def test_set_writeable_methods(self):
        m = MagicMock()
        m.name = "configure"
        self.c.register_child_writeable(m, "Ready")
        self.assertEqual(self.c.children_writeable['Ready'][m], True)

    def make_part_tasks(self, hook, func):
        task = MagicMock()
        func_name = "configure"
        part = MagicMock()
        part.name = "test_part"
        part.method_metas = {}
        setattr(part, func_name, func)
        part_tasks = {part: task}
        hook_queue = self.c.process.create_queue.return_value

        def side_effect():
            task_return = task.define_spawn_function.call_args[0][0]
            task_return()
            return hook_queue.put.call_args[0][0]

        hook_queue.get.side_effect = side_effect

        hook.find_hooked_functions.return_value = {part: func_name}
        self.c.hook_names = {hook: "test_hook"}
        return part_tasks

    def test_run_hook(self):
        hook = MagicMock()
        func = MagicMock()
        func.return_value = {"foo": "bar"}
        part_tasks = self.make_part_tasks(hook, func)
        result = self.c.run_hook(hook, part_tasks)
        self.assertEquals(result, dict(test_part=dict(foo="bar")))

    def test_run_hook_raises(self):
        hook = MagicMock()
        func = MagicMock(side_effect=Exception("Test Exception"))
        part_tasks = self.make_part_tasks(hook, func)

        with self.assertRaises(Exception) as cm:
            self.c.run_hook(hook, part_tasks)
        self.assertIs(func.side_effect, cm.exception)
        #TODO: test hook_queue.put/get mechanism

if __name__ == "__main__":
    unittest.main(verbosity=2)
