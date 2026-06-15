from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        # Should redirect to home after successful login
        self.assertRedirects(response, reverse('home'))
        
        # Verify session is active
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.logout_url)
        # Should redirect to login after logout
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_invalid_login(self):
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_url = reverse('admin_dashboard')
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpassword123'
        )
        
        # Create a staff/admin user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpassword123',
            is_staff=True
        )
        
    def test_guest_cannot_access_dashboard(self):
        # Guests should be redirected to login page (staff login view)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('login' in response.url)
        
    def test_regular_user_cannot_access_dashboard(self):
        # Authenticated non-staff users should also be redirected/blocked
        self.client.login(username='regularuser', password='testpassword123')
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 302)
        
    def test_staff_user_can_access_dashboard(self):
        # Staff user should get 200 OK
        self.client.login(username='staffuser', password='testpassword123')
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/admin_dashboard.html')
        
    def test_toggle_user_active_status(self):
        self.client.login(username='staffuser', password='testpassword123')
        
        # Verify initial status
        self.assertTrue(self.regular_user.is_active)
        
        # Call toggle active API
        toggle_url = reverse('admin_user_toggle_active_api', args=[self.regular_user.id])
        response = self.client.post(toggle_url)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertFalse(json_data['is_active'])
        
        # Verify database is updated
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)
        
    def test_toggle_user_staff_status(self):
        self.client.login(username='staffuser', password='testpassword123')
        
        # Verify initial status
        self.assertFalse(self.regular_user.is_staff)
        
        # Call toggle staff API
        toggle_url = reverse('admin_user_toggle_staff_api', args=[self.regular_user.id])
        response = self.client.post(toggle_url)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertTrue(json_data['is_staff'])
        
        # Verify database is updated
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_staff)

    def test_change_user_password(self):
        self.client.login(username='staffuser', password='testpassword123')
        
        # Call password change API
        change_pwd_url = reverse('admin_user_change_password_api', args=[self.regular_user.id])
        response = self.client.post(change_pwd_url, data='{"new_password": "newsecurepassword123"}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        
        # Verify password is changed by trying to log in with new password
        login_success = self.client.login(username='regularuser', password='newsecurepassword123')
        self.assertTrue(login_success)
