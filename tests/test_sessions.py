import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

import app


class BrowserIsolationTests(unittest.TestCase):
    def test_private_drafts_and_ownership(self):
        form = dict(observer_name='Alice', profstaff='Yes', room='Tinker Toys',
                    round='Round 1', candidate='Private Candidate', teamwork='2',
                    initiative='3', personal_rep='4', work_with='Yes', comments='Private notes')
        with patch.dict(app._browser_drafts, {}, clear=True), patch.object(
            app, 'candidate_data', return_value=([['Private Candidate'], [], []], None)
        ), TestClient(app.app, base_url='https://testserver') as alice, TestClient(
            app.app, base_url='https://testserver'
        ) as bob:
            saved = alice.post('/submit', data=form)
            self.assertEqual(saved.status_code, 200)
            self.assertIn('Private notes', saved.text)
            self.assertIn('Private notes', alice.get('/').text)
            bob_home = bob.get('/')
            self.assertNotIn('Private notes', bob_home.text)
            self.assertNotIn('Edit this observation', bob_home.text)
            self.assertEqual(bob_home.headers['cache-control'], 'no-store')
            self.assertIn('HttpOnly', saved.headers['set-cookie'])
            self.assertIn('Secure', saved.headers['set-cookie'])
            draft = app._browser_drafts[alice.cookies.get(app.SESSION_COOKIE)][0]
            obs_id = draft['id']
            self.assertEqual(bob.post('/submit', data=dict(form, edit_id=obs_id, comments='Changed')).status_code, 404)
            self.assertEqual(bob.post(f'/delete/{obs_id}').status_code, 404)
            sheet = Mock()
            with patch.object(app, 'get_sheet', return_value=sheet):
                bob.post('/final-submit')
                sheet.append_rows.assert_not_called()
                alice.post('/final-submit')
                self.assertEqual(sheet.append_rows.call_args.args[0][0][9], 'Private notes')
            self.assertEqual(draft['comments'], 'Private notes')
            self.assertEqual(alice.post('/submit', data=dict(form, edit_id=obs_id, comments='Updated')).status_code, 200)
            self.assertEqual(draft['comments'], 'Updated')
            self.assertEqual(alice.post(f'/delete/{obs_id}').status_code, 200)
            self.assertEqual(app._browser_drafts[alice.cookies.get(app.SESSION_COOKIE)], [])
