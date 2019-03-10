import app
import unittest
import json

class Base(unittest.TestCase):

	test_app = app.app.test_client()

	def get_response_as_json(self, query):		
		response = self.test_app.post('/get_flight_info', data=query, content_type='application/plaintext').get_json()
		
		print("\nquery: " + query)
		print("response: " + json.dumps(response, indent=1))

		return response

	def assertIntent(self, json, value):
		self.assertEqual(json['intent'], value)

	def assertSlot(self, json, name, value):
		self.assertEqual(json['slots'][name], value)

class TestExpectedUse(Base):

	def test_flight_query(self):
		json = self.get_response_as_json('show me flights from miami to new york')
		self.assertIntent(json, 'flight')
		self.assertSlot(json, 'fromloc.city_name', 'miami')
		self.assertSlot(json, 'toloc.city_name', 'new york')

class TestUnexpectedUse(Base):

	def test_random_query(self):
		json = self.get_response_as_json('make me a cup of coffee')
		self.assertIntent(json, 'restriction')
		self.assertEqual(len(json['slots']), 0)

	def test_non_english(self):
		json = self.get_response_as_json('me mostre voos de miami para nova iorque')
		self.assertIntent(json, 'distance')
		self.assertSlot(json, 'city_name', 'miami')

	def test_special_characters(self):
		json = self.get_response_as_json('!@£$%^&*()_+-=\{\}[]:";\'<>?,./~`')
		self.assertIntent(json, 'flight')
		self.assertEqual(len(json['slots']), 0)

	def test_empty_query(self):
		json = self.get_response_as_json('')
		self.assertEqual(json['error'], 'No query supplied.')

if __name__ == "__main__":
    unittest.main()