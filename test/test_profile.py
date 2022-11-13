from django.core import mail
from django.urls import reverse
from django.utils import timezone

from test.util.test import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    def testProfile(self):
        self.assertGet(reverse('profile'))

    def testProfilePost(self):
        self.assertPost(reverse('profile'), {'iban': 'CH29 0900 0000 9000 1480 3',
                                             'email': 'test@juntagrico.org',
                                             'addr_street': 'addr_street',
                                             'addr_zipcode': ' 1234',
                                             'addr_location': 'addr_location',
                                             'phone': 'phone'})

    def testCancelMembership(self):
        self.assertGet(reverse('cancel-membership'))

    def testCancelMembershipPost(self):
        data = {
            'message': 'message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }
        self.assertPost(reverse('cancel-membership'), code=302, data=data)
        self.member.refresh_from_db()
        self.assertTrue(self.member.canceled)
        self.assertEqual(self.member.usable_shares_count, 0)

    def testCancelMembershipPostWithUnpaidShares(self):
        data = {
            'message': 'message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member6, data=data)
        self.member6.refresh_from_db()
        self.assertTrue(self.member6.canceled)
        self.assertEqual(self.member6.usable_shares_count, 0)

    def testCancelMembershipNonCoopPost(self):
        data = {
            'message': 'message',
            'iban': ''
        }
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member3, data=data)
        self.member3.refresh_from_db()
        self.assertTrue(self.member3.inactive)

    def testDeactivateMembership(self):
        # must first cancel and pay back the shares
        for share in self.member.active_shares:
            share.cancelled_date = timezone.now().date()
            share.termination_date = timezone.now().date()
            share.payback_date = timezone.now().date()
            share.save()
        # and delete the subscription
        self.member.subscription_current.delete()
        self.assertPost(reverse('member-deactivate', args=(self.member.pk,)), code=302)
        self.member.refresh_from_db()
        self.assertTrue(self.member.inactive)

    def testConfirmEmail(self):
        self.assertGet(reverse('send-confirm'))
        self.assertEqual(len(mail.outbox), 1)

    def testChangePassword(self):
        self.assertGet(reverse('password'))

    def testChangePasswordPost(self):
        self.assertPost(reverse('password'), {'password': 'password',
                                              'passwordRepeat': 'password'})

    def testNewPassword(self):
        self.assertGet(reverse('password_reset'))
        self.assertEqual(len(mail.outbox), 0)

    def testNewPasswordPost(self):
        self.assertPost(reverse('password_reset'), {'email': 'email3@email.org'}, code=302)
        self.assertEqual(len(mail.outbox), 1)

    def testLogout(self):
        self.assertGet(reverse('logout'), code=302)
