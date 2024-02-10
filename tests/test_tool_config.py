from cases import Case, CaseGenerator
from faker import Faker
import unittest

from gitidtool.tool_config import (
    ToolConfigEntry,
    ToolConfigEntryFactory,
    config_to_json_str,
    json_str_to_config,
)


class TestConversion(unittest.TestCase):
    def test_config_conversion_roundtrip_single_entry(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()
        for i in range(100):
            fake.seed_instance(i)
            case = generator.generate_git(override_from_output=True)

            config: set[ToolConfigEntry] = set()
            config.add(factory.create_from_git_data_entry(case.git_data[0]))

            json_str = config_to_json_str(config)
            config2 = json_str_to_config(json_str)
            self.assertEqual(config, config2)

            json_str2 = config_to_json_str(config)
            self.assertEqual(json_str, json_str2)

            # When we change the first config, the second config does not
            # change (they aren't linked by ref)
            entry = config.pop()
            entry.name = "something totally different"
            config.add(entry)
            self.assertNotEqual(config, config2)

            # Same for the new json str relative to the second config's json
            # str
            json_str = config_to_json_str(config)
            self.assertNotEqual(json_str, json_str2)

    def test_config_conversion_roundtrip_multiple_entries(self):
        fake = Faker()
        generator = CaseGenerator(fake)
        factory = ToolConfigEntryFactory()
        for i in range(10):
            fake.seed_instance(i)

            config: set[ToolConfigEntry] = set()
            case: Case = None
            # Generate multiple git data entries and add them to the same
            # config
            for j in range(5):
                case = generator.generate_git(case, True)
                case = generator.generate_gpg(case, True)
                case = generator.generate_ssh(case, True)
                config.add(factory.create_from_git_data_entry(case.git_data[j]))

            json_str = config_to_json_str(config)
            config2 = json_str_to_config(json_str)
            self.assertEqual(config, config2)

            json_str2 = config_to_json_str(config)
            self.assertEqual(json_str, json_str2)

            # When we change the first config, the second config does not
            # change (they aren't linked by ref)
            entry = config.pop()
            entry.name = "something totally different"
            config.add(entry)
            self.assertNotEqual(config, config2)

            # Same for the new json str relative to the second config's json
            # str
            json_str = config_to_json_str(config)
            self.assertNotEqual(json_str, json_str2)