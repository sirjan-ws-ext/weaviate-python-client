import unittest
import weaviate
from test.testing_util import run_rest_raise_connection_error
from requests.exceptions import ConnectionError
from test.testing_util import add_run_rest_to_mock, replace_connection
from weaviate.connect import REST_METHOD_POST, REST_METHOD_PUT
from weaviate import SEMANTIC_TYPE_ACTIONS, SEMANTIC_TYPE_THINGS
import sys
if sys.version_info[0] == 2:
    from mock import MagicMock as Mock
else:
    from unittest.mock import Mock


class TestAddThings(unittest.TestCase):

    def testcreate_thing_flawed_input(self):
        w = weaviate.Client("http://localhost:8080")
        try:
            w.data_object.create(None, "Class")
            self.fail("Thing was not given but accepted anyways")
        except TypeError:
            pass
        try:
            w.data_object.create(224345, "Class")
            self.fail("Thing is of wrong type but no error")
        except TypeError:
            pass
        try:
            w.data_object.create({'name': 'Optimus Prime'}, None)
            self.fail("Class name has wrong type")
        except TypeError:
            pass
        try:
            w.data_object.create({'name': 'Optimus Prime'}, "Transformer", 19210)
            self.fail("Uuid wrong type")
        except TypeError:
            pass
        try:
            w.data_object.create({'name': 'Optimus Prime'}, "Transformer", "1234_1234_1234_1234")
            self.fail("Uuid wrong form")
        except ValueError:
            pass
        try:
            w.data_object.create({'name': 'Optimus Prime'}, "Transformer", None, 1234)
            self.fail("weight vectors wrong type")
        except TypeError:
            pass

    def testcreate_thing_connection_error(self):
        if sys.version_info[0] == 2:
            # Test is not working on version 2 because of old mock object
            return
        w = weaviate.Client("http://semi.testing.eu:8080")
        connection_mock = Mock()  # Mock calling weaviate
        connection_mock.run_rest.side_effect = run_rest_raise_connection_error
        w._connection = connection_mock
        try:
            w.data_object.create({"name": "Alan Greenspan"}, "CoolestPersonEver")
        except ConnectionError as e:
            pass

    def test_set_vector_weigths(self):
        w = weaviate.Client("http://localhost:8081")

        # 1. Succesfully delete something
        connection_mock = Mock()
        add_run_rest_to_mock(connection_mock, {"id": 0}, status_code=200)
        replace_connection(w, connection_mock)

        # thing = "b36268d4-a6b5-5274-985f-45f13ce0c642"
        # to_thing = "a36268d4-a6b5-5274-985f-45f13ce0c642"

        thing = {"lyrics": "da da dadadada dada, da da dadadada da, da da dadadada da, da da dadadada da Tequila"}
        class_name = "KaraokeSongs"
        vector_weights = {
            "da": "1",
            "dadadada": "w + 0.5",
            "tequila": "w*15"
        }

        rest_object = {
            "class": "KaraokeSongs",
            "schema": thing,
            "vectorWeights": vector_weights
        }

        uuid = w.data_object.create(thing, class_name, None, SEMANTIC_TYPE_THINGS, vector_weights)
        self.assertEqual(uuid, str(0))
        connection_mock.run_rest.assert_called_with("/things", REST_METHOD_POST, rest_object)

    def test_generate_local_beacon(self):
        try:
            weaviate.generate_local_beacon(None)
            self.fail("TypeError expected should be str")
        except TypeError:
            pass
        try:
            weaviate.generate_local_beacon("Leeroy Jenkins")
            self.fail("Value error expected should be uuid")
        except ValueError:
            pass

        beacon = weaviate.generate_local_beacon("fcf33178-1b5d-5174-b2e7-04a2129dd35a")
        self.assertTrue("beacon" in beacon)
        self.assertEqual(beacon["beacon"], "weaviate://localhost/things/fcf33178-1b5d-5174-b2e7-04a2129dd35a")

        beacon = weaviate.generate_local_beacon("fcf33178-1b5d-5174-b2e7-04a2129dd35b", semantic_type=SEMANTIC_TYPE_ACTIONS)
        self.assertTrue("beacon" in beacon)
        self.assertEqual(beacon["beacon"], "weaviate://localhost/actions/fcf33178-1b5d-5174-b2e7-04a2129dd35b")

    def test_set_vector_weigths_action(self):
        w = weaviate.Client("http://localhost:8081")

        # 1. Succesfully delete someaction
        connection_mock = Mock()
        add_run_rest_to_mock(connection_mock, {"id": 0}, status_code=200)
        replace_connection(w, connection_mock)

        # action = "b36268d4-a6b5-5274-985f-45f13ce0c642"
        # to_action = "a36268d4-a6b5-5274-985f-45f13ce0c642"

        action = {"lyrics": "da da dadadada dada, da da dadadada da, da da dadadada da, da da dadadada da Tequila"}
        class_name = "KaraokeSongs"
        vector_weights = {
            "da": "1",
            "dadadada": "w + 0.5",
            "tequila": "w*15"
        }

        rest_object = {
            "class": "KaraokeSongs",
            "schema": action,
            "vectorWeights": vector_weights
        }

        uuid = w.data_object.create(action, class_name, None, SEMANTIC_TYPE_ACTIONS, vector_weights)
        self.assertEqual(uuid, str(0))
        connection_mock.run_rest.assert_called_with("/actions", REST_METHOD_POST, rest_object)


class TestReplaceDataObject(unittest.TestCase):

    def test_put(self):
        w = weaviate.Client("http://localhorst:8080")

        connection_mock = Mock()  # Mock calling weaviate
        add_run_rest_to_mock(connection_mock)
        replace_connection(w, connection_mock)

        w.data_object.update({"A": 2}, "Hero", "27be9d8d-1da1-4d52-821f-bc7e2a25247d")
        w.data_object.update({"A": 2}, "Hero", "f39fd3d6-9d89-4cc1-8e72-f94022d36651", semantic_type=SEMANTIC_TYPE_ACTIONS)

        connection_mock.run_rest.assert_called()

        call_args_list = connection_mock.run_rest.call_args_list
        call_args, call_kwargs = call_args_list[0]

        self.assertEqual("/things/27be9d8d-1da1-4d52-821f-bc7e2a25247d", call_args[0])
        self.assertEqual(REST_METHOD_PUT, call_args[1])

        call_args, call_kwargs = call_args_list[1]

        self.assertEqual("/actions/f39fd3d6-9d89-4cc1-8e72-f94022d36651", call_args[0])
        self.assertEqual(REST_METHOD_PUT, call_args[1])
