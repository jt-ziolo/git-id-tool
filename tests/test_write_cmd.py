import logging
import unittest
from unittest.mock import patch

from faker import Faker
from gitidtool.__init__ import write
from gitidtool.tool_config import (
    ToolConfigEntry,
    ToolConfigEntryFactory,
    config_to_json_str,
)
from tests.cases import CaseGenerator


class TestWriteCmd(unittest.TestCase):
    def test_write_cmd_produces_correct_output(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        case = generator.generate_git(override_from_output=True)
        case = generator.generate_gpg(case, True)
        case = generator.generate_ssh(case, True)

        # should log the first config example as json to DEBUG
        with self.assertLogs(level=logging.DEBUG) as cm:
            with patch(
                "gitidtool.__init__._read_config",
                return_value=(case.git_data, case.gpg_data, case.ssh_data),
            ):
                write.callback("dummy", True)

                factory = ToolConfigEntryFactory()
                config: set[ToolConfigEntry] = set()
                for entry in case.git_data:
                    config.add(factory.create_from_git_data_entry(entry))
                self.assertEqual(
                    cm.output[0],
                    f"DEBUG:root:{config_to_json_str(config)}",
                )
