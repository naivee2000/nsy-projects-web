"""Presentation and auth-contract regression tests; only synthetic credentials."""
import asyncio
import hashlib
import unittest
from unittest.mock import patch
from fastapi import FastAPI
import auth_gate as auth


class LoginPresentationTests(unittest.TestCase):
    def test_normal_form_is_native_and_accessible(self):
        page = auth.render_login(next_url='https://nsyprojects.com/projects').body.decode()
        self.assertIn('<html lang="en">', page)
        self.assertIn('method="post" action="/login"', page)
        for name in ('username', 'password', 'next'):
            self.assertIn(f'name="{name}"', page)
        self.assertIn('autocomplete="current-password"', page)
        self.assertIn('required aria-required="true" autofocus', page)
        self.assertNotIn('<script', page)
        self.assertNotIn('role="alert"', page)
        self.assertNotIn('{{', page)

    def test_error_is_escaped_announced_and_focused(self):
        page = auth.render_login('<script>alert("x")</script>').body.decode()
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('role="alert" tabindex="-1" autofocus', page)
        self.assertEqual(page.count('autofocus'), 1)
        self.assertEqual(page.count('aria-describedby="loginError"'), 2)

    def test_return_attribute_is_escaped(self):
        page = auth.render_login(next_url='/path?q="<value>&other=1').body.decode()
        self.assertIn('value="/path?q=&quot;&lt;value&gt;&amp;other=1"', page)

    def test_return_and_cancel_policy(self):
        for value in ('/path?x=1', 'https://nsyprojects.com/projects', 'https://dem.nsyprojects.com/'):
            self.assertEqual(auth.safe_next_url(value), value)
        for value in ('//evil.example/', 'https://evil.example/', 'javascript:alert(1)', 'http://nsyprojects.com/'):
            self.assertEqual(auth.safe_next_url(value), '/')
        self.assertEqual(auth.safe_cancel_url('https://nsyprojects.com/projects'), 'https://nsyprojects.com/projects')
        self.assertEqual(auth.safe_cancel_url('/private'), 'https://nsyprojects.com/projects')
        self.assertEqual(auth.safe_cancel_url(None), 'https://nsyprojects.com/')

    def test_real_login_and_logout_contract(self):
        import base64
        enc = lambda value: base64.urlsafe_b64encode(value).decode().rstrip('=')
        salt = b'synthetic-auth-test'
        password_hash = 'pbkdf2_sha256$1000$' + enc(salt) + '$' + enc(hashlib.pbkdf2_hmac('sha256', b'test-password', salt, 1000))
        with patch.multiple(auth, AUTH_ENABLED=True, AUTH_USERNAME='test-user', AUTH_PASSWORD_HASH=password_hash,
                            AUTH_SESSION_SECRET='test-secret', AUTH_COOKIE_DOMAIN=None, AUTH_COOKIE_SECURE=False):
            app = FastAPI()
            auth.install_auth(app)
            post = next(r.endpoint for r in app.routes if r.path == '/login' and 'POST' in r.methods)
            failed = asyncio.run(post(username='test-user', password='wrong', next='/private'))
            self.assertIn(b'Username or password is incorrect.', failed.body)
            self.assertNotIn('set-cookie', failed.headers)
            success = asyncio.run(post(username='test-user', password='test-password', next='/private'))
            self.assertEqual(success.status_code, 303)
            self.assertEqual(success.headers['location'], '/private')
            cookies = success.headers.getlist('set-cookie')
            self.assertEqual(len(cookies), 2)
            self.assertIn('HttpOnly', cookies[0])
            self.assertIn('SameSite=lax', cookies[0])
            token = cookies[0].split(';', 1)[0].split('=', 1)[1]
            self.assertTrue(auth.valid_session_token(token))
            unsafe = asyncio.run(post(username='test-user', password='test-password', next='https://evil.example/'))
            self.assertEqual(unsafe.headers['location'], '/')
            logout = next(r.endpoint for r in app.routes if r.path == '/logout')
            response = asyncio.run(logout(next='https://nsyprojects.com/'))
            self.assertEqual(response.status_code, 303)
            self.assertTrue(all('Max-Age=0' in c for c in response.headers.getlist('set-cookie')))


if __name__ == '__main__':
    unittest.main()
