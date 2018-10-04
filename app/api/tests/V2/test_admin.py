"""Test cases for admin functions"""
import base64
import ast


from .base import MainTestCase


class TestAddMealToMenu(MainTestCase):
    """Test class for admin"""
    def test_add_meal_token_missing(self):
        """Test adding meal with no token"""
        res = self.client.post('/api/v2/menu', json=self.correct_order)
        self.assertEqual('Token is missing', res.get_data(as_text=True))

    def test_add_meal_admin(self):
        """Test adding meal to the menu"""
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        self.client.post('/api/v2/menu',
                         headers={'x-access-token': final_token},
                         json={"meal_name": 'Burger',
                               "meal_price": 7.99})
        res = self.client.get('/api/v2/menu', headers={'x-access-token': final_token})
        self.assertIn('Tasty and sweet', res.get_data(as_text=True))
        res = self.client.post('/api/v2/menu',
                               headers={'x-access-token': final_token},
                               json=self.correct_order)
        self.assertIn('Meal has been added to the menu', res.get_data(as_text=True))

    def test_add_meal_twice(self):
        """Testing adding a meal twice"""
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        self.client.post('/api/v2/menu',
                         headers={'x-access-token': final_token},
                         json=self.correct_order)
        res = self.client.post('/api/v2/menu',
                               headers={'x-access-token': final_token},
                               json=self.correct_order)
        self.assertIn('The meal is already in the menu', res.get_data(as_text=True))

    def test_add_meal_wrong_data(self):
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.post('/api/v2/menu',
                               headers={'x-access-token': final_token},
                               json={"meal_desc": 'Seasoned',
                                     "meal_price": 7.99})
        self.assertIn('Please enter the correct format of keys', res.get_data(as_text=True))

    def test_add_meal_non_admin(self):
        """Test normal user adding meal to the menu"""
        self.client.post('/api/v2/auth/signup', json=self.register_user)
        user = base64.b64encode(bytes('BryanCee:Brian12', 'UTF-8')).decode('UTF-8')
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.post('/api/v2/menu',
                               headers={'x-access-token': final_token},
                               json=self.correct_order)
        self.assertIn('You are not an administrator', res.get_data(as_text=True))

    def test_get_menu(self):
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.get('/api/v2/menu', headers={"x-access-token": final_token})
        self.assertIn('There are no meals in the menu', res.get_data(as_text=True))

    def test_getting_all_orders(self):
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})
        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.get('/api/v2/orders/', headers={"x-access-token": final_token})
        self.assertEqual(b'There are no orders currently', res.get_data())

        self.client.post('/api/v2/menu',
                         headers={'x-access-token': final_token},
                         json=self.correct_order)
        self.client.post('/api/v2/users/orders',
                         headers={'x-access-token': final_token},
                         json={"meal_id": 1})
        res = self.client.get('/api/v2/orders/', headers={"x-access-token": final_token})
        self.assertIn(b'Pizza', res.get_data())

        res = self.client.get('/api/v2/orders/1', headers={"x-access-token": final_token})
        self.assertIn(b'Pizza', res.get_data())

        res = self.client.get('/api/v2/orders/254', headers={"x-access-token": final_token})
        self.assertIn(b'There is no order with that ID', res.get_data())
        self.client.post('/api/v2/auth/signup', json=self.register_user)

    def test_get_orders_non_admin(self):
        """Test normal user getting orders"""
        self.client.post('/api/v2/auth/signup', json=self.register_user)
        user = base64.b64encode(bytes('BryanCee:Brian12', 'UTF-8')).decode('UTF-8')
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.get('/api/v2/orders/', headers={"x-access-token": final_token})
        self.assertIn(b'You are not an administrator', res.get_data())
        res = self.client.get('/api/v2/orders/1', headers={"x-access-token": final_token})
        self.assertIn(b'You are not an administrator', res.get_data())

    def test_modify_order(self):
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})
        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        self.client.post('/api/v2/menu',
                         headers={'x-access-token': final_token},
                         json=self.correct_order)
        self.client.post('/api/v2/users/orders',
                         headers={'x-access-token': final_token},
                         json={"meal_id": 1})
        res = self.client.put('/api/v2/orders/1',
                              headers={'x-access-token': final_token},
                              json={"status": "complete"})
        self.assertEqual(b'The order status has been updated', res.data)
        res = self.client.put('/api/v2/orders/1',
                              headers={'x-access-token': final_token},
                              json={"status": "accepted"})
        self.assertEqual(b'Please enter the required status in the correct format: '
                         b'"status":"the_status" which can be "processing", "complete" '
                         b'"cancelled"', res.data)
        res = self.client.put('/api/v2/orders/254',
                              headers={'x-access-token': final_token},
                              json={"status": "complete"})
        self.assertEqual(b'There is no such order', res.data)

    def test_non_admin_modify_order(self):
        self.client.post('/api/v2/auth/signup', json=self.register_user)
        user = base64.b64encode(bytes('BryanCee:Brian12', 'UTF-8')).decode('UTF-8')
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + user})

        token = res.get_data(as_text=True)
        final_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.put('/api/v2/orders/1',
                              headers={'x-access-token': final_token},
                              json={"status": "complete"})
        self.assertIn('You are not an administrator', res.get_data(as_text=True))

    def test_promote_user(self):
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + self.user})
        token = res.get_data(as_text=True)
        admin_token = ast.literal_eval(token.replace(" ", ""))['Token']
        self.client.post('/api/v2/auth/signup', json=self.register_user)

        res = self.client.put('/api/v2/users/1', headers={'x-access-token': admin_token}, json={"admin": "True"})
        self.assertEqual('The user admin rights have been updated', res.get_data(as_text=True))

        res = self.client.put('/api/v2/users/254', headers={'x-access-token': admin_token}, json={"admin": "True"})
        self.assertEqual('The user does not exist', res.get_data(as_text=True))

        res = self.client.put('/api/v2/users/1', headers={'x-access-token': admin_token}, json={"admin": "not"})
        self.assertIn('Please enter the correct JSON format: "admin": "True" or "admin": "False"',
                      res.get_data(as_text=True))
        user = base64.b64encode(bytes('BryanCee:Brian12', 'UTF-8')).decode('UTF-8')
        res = self.client.post('/api/v2/auth/login', headers={'Authorization': 'Basic ' + user})
        token = res.get_data(as_text=True)
        user_token = ast.literal_eval(token.replace(" ", ""))['Token']
        res = self.client.put('/api/v2/users/1', headers={'x-access-token': user_token}, json={"admin": "True"})
        self.assertIn(b'You are not an administrator', res.data)


