from django.test import TestCase
from django.core.urlresolvers import reverse
from lrs import models, views
import datetime
from django.utils.timezone import utc
import hashlib
import urllib
from os import path
import base64
import json

class ActivityStateTests(TestCase):
    url = reverse(views.activity_state)
    testagent = '{"name":"test","mbox":"mailto:test@example.com"}'
    otheragent = '{"name":"other","mbox":"mailto:other@example.com"}'
    activityId = "http://www.iana.org/domains/example/"
    activityId2 = "http://www.google.com"
    stateId = "the_state_id"
    stateId2 = "state_id_2"
    stateId3 = "third_state_id"
    stateId4 = "4th.id"
    registrationId = "some_sort_of_reg_id"
    content_type = "application/json"

    def setUp(self):
        self.username = "test"
        self.email = "mailto:test@example.com"        
        self.password = "test"
        self.auth = "Basic %s" % base64.b64encode("%s:%s" % (self.username, self.password))
        form = {'username':self.username,'email': self.email,'password':self.password,'password2':self.password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")

        self.activity = models.activity(activity_id=self.activityId)
        self.activity.save()

        self.activity2 = models.activity(activity_id=self.activityId2)
        self.activity2.save()

        self.testparams1 = {"stateId": self.stateId, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams1))
        self.teststate1 = {"test":"put activity state 1","obj":{"agent":"test"}}
        self.put1 = self.client.put(path, self.teststate1, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.testparams2 = {"stateId": self.stateId2, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams2))
        self.teststate2 = {"test":"put activity state 2","obj":{"agent":"test"}}
        self.put2 = self.client.put(path, self.teststate2, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.testparams3 = {"stateId": self.stateId3, "activityId": self.activityId2, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams3))
        self.teststate3 = {"test":"put activity state 3","obj":{"agent":"test"}}
        self.put3 = self.client.put(path, self.teststate3, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.testparams4 = {"stateId": self.stateId4, "activityId": self.activityId2, "agent": self.otheragent}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams4))
        self.teststate4 = {"test":"put activity state 4","obj":{"agent":"other"}}
        self.put4 = self.client.put(path, self.teststate4, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

    def tearDown(self):
        self.client.delete(self.url, self.testparams1, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.client.delete(self.url, self.testparams2, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.client.delete(self.url, self.testparams3, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.client.delete(self.url, self.testparams4, Authorization=self.auth, X_Experience_API_Version="0.95")

    def test_put(self):
        self.assertEqual(self.put1.status_code, 204)
        self.assertEqual(self.put1.content, '')

        self.assertEqual(self.put2.status_code, 204)
        self.assertEqual(self.put2.content, '')

        self.assertEqual(self.put3.status_code, 204)
        self.assertEqual(self.put3.content, '')

        self.assertEqual(self.put4.status_code, 204)
        self.assertEqual(self.put4.content, '')
     
    def test_put_with_registrationId(self):
        testparamsregid = {"registrationId": self.registrationId, "stateId": self.stateId, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsregid))
        teststateregid = {"test":"put activity state w/ registrationId","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststateregid, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        # also testing get w/ registration id
        r = self.client.get(self.url, testparamsregid, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststateregid
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())
        # and tests delete w/ registration id
        del_r = self.client.delete(self.url, testparamsregid, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(del_r.status_code, 204)

    def test_put_without_auth(self):
        testparamsregid = {"registrationId": self.registrationId, "stateId": self.stateId, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsregid))
        teststateregid = {"test":"put activity state w/ registrationId","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststateregid, content_type=self.content_type, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 401)

    def test_put_etag_conflict_if_none_match(self):
        teststateetaginm = {"test":"etag conflict - if none match *","obj":{"agent":"test"}}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams1))
        r = self.client.put(path, teststateetaginm, content_type=self.content_type, If_None_Match='*', Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(r.status_code, 412)
        self.assertEqual(r.content, 'Resource detected')

        r = self.client.get(self.url, self.testparams1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % self.teststate1
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

    def test_put_etag_conflict_if_match(self):
        teststateetagim = {"test":"etag conflict - if match wrong hash","obj":{"agent":"test"}}
        new_etag = '"%s"' % hashlib.sha1('wrong etag value').hexdigest()
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams1))
        r = self.client.put(path, teststateetagim, content_type=self.content_type, If_Match=new_etag, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(r.status_code, 412)
        self.assertIn('No resources matched', r.content)

        r = self.client.get(self.url, self.testparams1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % self.teststate1
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

    def test_put_etag_no_conflict_if_match(self):
        teststateetagim = {"test":"etag no conflict - if match good hash","obj":{"agent":"test"}}
        new_etag = '"%s"' % hashlib.sha1('%s' % self.teststate1).hexdigest()
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams1))
        r = self.client.put(path, teststateetagim, content_type=self.content_type, If_Match=new_etag, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.content, '')

        r = self.client.get(self.url, self.testparams1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststateetagim
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())    

    def test_put_etag_missing_on_change(self):
        teststateetagim = {'test': 'etag no conflict - if match good hash', 'obj': {'agent': 'test'}}
        path = '%s?%s' % (self.url, urllib.urlencode(self.testparams1))
        r = self.client.put(path, teststateetagim, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(r.status_code, 409)
        self.assertIn('If-Match and If-None-Match headers were missing', r.content)
        
        r = self.client.get(self.url, self.testparams1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % self.teststate1
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

    def test_put_without_activityid(self):
        testparamsbad = {"stateId": "bad_state", "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsbad))
        teststatebad = {"test":"put activity state BAD no activity id","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststatebad, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 400)
        self.assertIn('activityId parameter is missing', put1.content)

    
    def test_put_without_agent(self):
        testparamsbad = {"stateId": "bad_state", "activityId": self.activityId}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsbad))
        teststatebad = {"test":"put activity state BAD no agent","obj":{"agent":"none"}}
        put1 = self.client.put(path, teststatebad, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 400)
        self.assertIn('agent parameter is missing', put1.content)

    
    def test_put_without_stateid(self):
        testparamsbad = {"activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsbad))
        teststatebad = {"test":"put activity state BAD no state id","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststatebad, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 400)
        self.assertIn('stateId parameter is missing', put1.content)

    # Also tests 403 forbidden status
    def test_get(self):
        username = "other"
        email = "mailto:other@example.com"
        password = "test"
        auth = "Basic %s" % base64.b64encode("%s:%s" % (username, password))
        form = {'username':username,'email': email,'password':password,'password2':password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")        

        r = self.client.get(self.url, self.testparams1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % self.teststate1
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        r2 = self.client.get(self.url, self.testparams2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r2.status_code, 200)
        state2_str = '%s' % self.teststate2
        self.assertEqual(r2.content, state2_str)
        self.assertEqual(r2['etag'], '"%s"' % hashlib.sha1(state2_str).hexdigest())
        
        r3 = self.client.get(self.url, self.testparams3, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r3.status_code, 200)
        state3_str = '%s' % self.teststate3
        self.assertEqual(r3.content, state3_str)
        self.assertEqual(r3['etag'], '"%s"' % hashlib.sha1(state3_str).hexdigest())

        r4 = self.client.get(self.url, self.testparams4, X_Experience_API_Version="0.95", Authorization=auth)
        self.assertEqual(r4.status_code, 200)
        state4_str = '%s' % self.teststate4
        self.assertEqual(r4.content, state4_str)
        self.assertEqual(r4['etag'], '"%s"' % hashlib.sha1(state4_str).hexdigest())

        r5 = self.client.get(self.url, self.testparams3, X_Experience_API_Version="0.95", Authorization=auth)
        self.assertEqual(r5.status_code, 403)

    def test_get_ids(self):
        params = {"activityId": self.activityId, "agent": self.testagent}
        r = self.client.get(self.url, params, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.stateId, r.content)
        self.assertIn(self.stateId2, r.content)
        self.assertNotIn(self.stateId3, r.content)
        self.assertNotIn(self.stateId4, r.content)
     
    def test_get_with_since(self):
        state_id = "old_state_test"
        testparamssince = {"stateId": state_id, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamssince))
        teststatesince = {"test":"get w/ since","obj":{"agent":"test"}}
        updated =  datetime.datetime(2012, 6, 12, 12, 00).replace(tzinfo=utc)
        put1 = self.client.put(path, teststatesince, content_type=self.content_type, updated=updated.isoformat(), Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamssince, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststatesince
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        since = datetime.datetime(2012, 7, 1, 12, 00).replace(tzinfo=utc)
        params2 = {"activityId": self.activityId, "agent": self.testagent, "since": since}
        r = self.client.get(self.url, params2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.stateId, r.content)
        self.assertIn(self.stateId2, r.content)
        self.assertNotIn(state_id, r.content)
        self.assertNotIn(self.stateId3, r.content)
        self.assertNotIn(self.stateId4, r.content)

        del_r = self.client.delete(self.url, testparamssince, Authorization=self.auth, X_Experience_API_Version="0.95")
        
    def test_get_with_since_and_regid(self):
        # create old state w/ no registration id
        state_id = "old_state_test_no_reg"
        testparamssince = {"stateId": state_id, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamssince))
        teststatesince = {"test":"get w/ since","obj":{"agent":"test","stateId":state_id}}
        updated =  datetime.datetime(2012, 6, 12, 12, 00).replace(tzinfo=utc)
        put1 = self.client.put(path, teststatesince, content_type=self.content_type, updated=updated.isoformat(), Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamssince, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststatesince
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        # create old state w/ registration id
        regid = 'test_since_w_regid'
        state_id2 = "old_state_test_w_reg"
        testparamssince2 = {"registrationId": regid, "activityId": self.activityId, "agent": self.testagent, "stateId":state_id2}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamssince2))
        teststatesince2 = {"test":"get w/ since and registrationId","obj":{"agent":"test","stateId":state_id2}}
        put2 = self.client.put(path, teststatesince2, content_type=self.content_type, updated=updated.isoformat(), Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put2.status_code, 204)
        self.assertEqual(put2.content, '')

        r2 = self.client.get(self.url, testparamssince2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r2.status_code, 200)
        state2_str = '%s' % teststatesince2
        self.assertEqual(r2.content, state2_str)
        self.assertEqual(r2['etag'], '"%s"' % hashlib.sha1(state2_str).hexdigest())

        # create new state w/ registration id
        state_id3 = "old_state_test_w_new_reg"
        testparamssince3 = {"registrationId": regid, "activityId": self.activityId, "agent": self.testagent, "stateId":state_id3}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamssince3))
        teststatesince3 = {"test":"get w/ since and registrationId","obj":{"agent":"test","stateId":state_id3}}
        put3 = self.client.put(path, teststatesince3, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put3.status_code, 204)
        self.assertEqual(put3.content, '')

        r3 = self.client.get(self.url, testparamssince3, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r3.status_code, 200)
        state3_str = '%s' % teststatesince3
        self.assertEqual(r3.content, state3_str)
        self.assertEqual(r3['etag'], '"%s"' % hashlib.sha1(state3_str).hexdigest())

        # get no reg ids set w/o old state
        since1 = datetime.datetime(2012, 7, 1, 12, 00).replace(tzinfo=utc)
        params = {"activityId": self.activityId, "agent": self.testagent, "since": since1}
        r = self.client.get(self.url, params, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.stateId, r.content)
        self.assertIn(self.stateId2, r.content)
        self.assertNotIn(state_id, r.content)
        self.assertNotIn(self.stateId3, r.content)
        self.assertNotIn(self.stateId4, r.content)

        # get reg id set w/o old state
        since2 = datetime.datetime(2012, 7, 1, 12, 00).replace(tzinfo=utc)
        params2 = {"registrationId": regid, "activityId": self.activityId, "agent": self.testagent, "since": since2}
        r = self.client.get(self.url, params2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn(state_id3, r.content)
        self.assertNotIn(state_id2, r.content)
        self.assertNotIn(self.stateId, r.content)
        self.assertNotIn(self.stateId2, r.content)
        self.assertNotIn(self.stateId3, r.content)
        self.assertNotIn(self.stateId4, r.content)
        
        self.client.delete(self.url, testparamssince, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.client.delete(self.url, testparamssince2, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.client.delete(self.url, testparamssince3, Authorization=self.auth, X_Experience_API_Version="0.95")

        
    def test_get_without_activityid(self):
        params = {"stateId": self.stateId, "agent": self.testagent}
        r = self.client.get(self.url, params, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 400)
        self.assertIn('activityId parameter is missing', r.content)

    
    def test_get_without_agent(self):
        params = {"stateId": self.stateId, "activityId": self.activityId}
        r = self.client.get(self.url, params, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 400)
        self.assertIn('agent parameter is missing', r.content)

    
    def test_delete_without_activityid(self):
        testparamsregid = {"registrationId": self.registrationId, "stateId": self.stateId, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsregid))
        teststateregid = {"test":"delete activity state w/o activityid","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststateregid, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamsregid, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststateregid
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        f_r = self.client.delete(self.url, {"registrationId": self.registrationId, "stateId": self.stateId, "agent": self.testagent}, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(f_r.status_code, 400)
        self.assertIn('activityId parameter is missing', f_r.content)

        del_r = self.client.delete(self.url, testparamsregid, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(del_r.status_code, 204)

    
    def test_delete_without_agent(self):
        testparamsregid = {"registrationId": self.registrationId, "stateId": self.stateId, "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsregid))
        teststateregid = {"test":"delete activity state w/o agent","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststateregid, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamsregid, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststateregid
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        f_r = self.client.delete(self.url, {"registrationId": self.registrationId, "stateId": self.stateId, "activityId": self.activityId}, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(f_r.status_code, 400)
        self.assertIn('agent parameter is missing', f_r.content)

        del_r = self.client.delete(self.url, testparamsregid, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(del_r.status_code, 204)

    
    def test_delete_set(self):
        testparamsdelset1 = {"registrationId": self.registrationId, "stateId": "del_state_set_1", "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsdelset1))
        teststatedelset1 = {"test":"delete set #1","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststatedelset1, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamsdelset1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststatedelset1
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        testparamsdelset2 = {"registrationId": self.registrationId, "stateId": "del_state_set_2", "activityId": self.activityId, "agent": self.testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparamsdelset2))
        teststatedelset2 = {"test":"delete set #2","obj":{"agent":"test"}}
        put1 = self.client.put(path, teststatedelset2, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, testparamsdelset2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % teststatedelset2
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        f_r = self.client.delete(self.url, {"registrationId": self.registrationId, "agent": self.testagent, "activityId": self.activityId}, Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(f_r.status_code, 204)

        r = self.client.get(self.url, testparamsdelset1, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 404)
        self.assertIn('no activity', r.content)

        r = self.client.get(self.url, testparamsdelset2, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(r.status_code, 404)
        self.assertIn('no activity', r.content)

    def test_ie_cors_put_delete(self):
        username = "another test"
        email = "mailto:anothertest@example.com"
        password = "test"
        auth = "Basic %s" % base64.b64encode("%s:%s" % (username, password))
        form = {'username':username,'email': email,'password':password,'password2':password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")


        testagent = '{"name":"another test","mbox":"mailto:anothertest@example.com"}'
        sid = "test_ie_cors_put_delete_set_1"
        sparam1 = {"stateId": sid, "activityId": self.activityId, "agent": testagent}
        path = '%s?%s' % (self.url, urllib.urlencode({"method":"PUT"}))
        sparam1['content'] = {"test":"test_ie_cors_put_delete","obj":{"actor":"another test"}}
        sparam1['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        sparam1['Authorization'] = auth
        put1 = self.client.post(path, sparam1, content_type='application/x-www-form-urlencoded', X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)
        self.assertEqual(put1.content, '')
        
        r = self.client.get(self.url, {"stateId": sid, "activityId": self.activityId, "agent": testagent}, X_Experience_API_Version="0.95", Authorization=auth)
        self.assertEqual(r.status_code, 200)
        state1_str = '%s' % sparam1['content']
        self.assertEqual(r.content, state1_str)
        self.assertEqual(r['etag'], '"%s"' % hashlib.sha1(state1_str).hexdigest())

        dparam = {"agent": testagent, "activityId": self.activityId}
        dparam['Authorization'] = auth
        dparam['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        path = '%s?%s' % (self.url, urllib.urlencode({"method":"DELETE"}))
        f_r = self.client.post(path, dparam, content_type='application/x-www-form-urlencoded', X_Experience_API_Version="0.95")
        self.assertEqual(f_r.status_code, 204)

    def test_agent_is_group(self):
        username = "the group"
        email = "mailto:the.group@example.com"
        password = "test"
        auth = "Basic %s" % base64.b64encode("%s:%s" % (username, password))
        form = {'username':username,'email': email,'password':password,'password2':password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")

        ot = "Group"
        name = "the group"
        mbox = "mailto:the.group@example.com"
        members = [{"name":"agent1","mbox":"mailto:agent1@example.com"},
                    {"name":"agent2","mbox":"mailto:agent2@example.com"}]
        testagent = json.dumps({"objectType":ot, "name":name, "mbox":mbox,"member":members})
        testparams1 = {"stateId": "group.state.id", "activityId": self.activityId, "agent": testagent}
        path = '%s?%s' % (self.url, urllib.urlencode(testparams1))
        teststate1 = {"test":"put activity state using group as agent","obj":{"agent":"group of 2 agents"}}
        put1 = self.client.put(path, teststate1, content_type=self.content_type, Authorization=self.auth, X_Experience_API_Version="0.95")

        self.assertEqual(put1.status_code, 204)

        get1 = self.client.get(self.url, {"stateId":"group.state.id", "activityId": self.activityId, "agent":testagent}, X_Experience_API_Version="0.95", Authorization=auth)
        self.assertEqual(get1.status_code, 200)
        st = '%s' % teststate1
        self.assertEqual(get1.content, st)

        delr = self.client.delete(self.url, testparams1, Authorization=auth, X_Experience_API_Version="0.95")
        self.assertEqual(delr.status_code, 204)        