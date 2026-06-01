---
title: Set or reset your password
audience: end-user
estimated-reading-time: 3 min
last-validated: 2026-05-27
specterx-build: live production tenant at app.specterx.com (no public build identifier exposed in the UI as of capture)
---

# Set or reset your password

Use this article to set a SpecterX password for the first time after your administrator invites you, or to reset your password if you have forgotten it. The procedure is the same in both cases: you trigger an email, enter the code, and choose a new password.

If your organization signs in to SpecterX through Google Workspace, Microsoft / Entra ID, or Okta, you do not use this flow at all. The **If you sign in with SSO** section below explains what to do instead.

## Before you start

You need:

- A SpecterX account. Your administrator creates the account; self-service sign-up is not available. If you have not been invited yet, SpecterX shows "You must be invited before you can sign in" and the procedure below will not work.
- Access to the inbox of the email address your administrator registered. The code goes to that address.
- Your organization's SpecterX sign-in URL. Most users go to `https://app.specterx.com`; some organizations use a tenant-specific subdomain such as `https://yourorg.specterx.com`.

## Steps

1. Go to your SpecterX sign-in URL and click **Reset password** under the **Sign In** button.

   ![SpecterX sign-in page with the Reset password link below the Sign In button](screenshots/01-sign-in-with-reset-link.png)

2. On the **Reset password** page, type the email address registered to your SpecterX account in the **Enter your email** field, then click **Reset**.

   ![The Reset password page with the email field and the Reset button](screenshots/03-reset-page-step1.png)

   SpecterX sends a 6-digit verification code to that email address. The code is valid for one hour.

3. Open the email and copy the code. The message comes from an `@specterx.com` sender. If you do not see it within a minute or two, check your spam or junk folder.

4. Back on the SpecterX page, the title changes to **Create New Password**. Type the code in the **Enter the code** field.

   If you did not receive the code, click **Didn't get the code? Resend Code**. You can request a new code once every 60 seconds. Each new request invalidates the previous code.

5. In the password field below the code, type your new password. SpecterX checks the password as you type. All five rules must turn green before the **Change Password** button becomes active:

   - At least 8 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 number
   - At least 1 special character. Allowed special characters: `! @ # $ % ^ & * ( ) _ ~ -`

6. Click **Change Password**. SpecterX confirms with the message "Your password has been successfully changed" and returns you to the sign-in page. Sign in with your email address and the new password.

## If you sign in with SSO

If your organization uses Google Workspace, Microsoft / Entra ID, or Okta to sign you in to SpecterX, the password you use to access SpecterX is the one stored with your identity provider, not with SpecterX. The **Reset password** link on the SpecterX sign-in page does not change that password.

To reset an SSO password, use your identity provider's own self-service tools, or contact whoever manages identity at your organization. After your identity provider accepts your new credentials, sign in to SpecterX as you normally would.

## Troubleshooting

### The reset email never arrives

Check your spam or junk folder first. If it is not there:

- Confirm you entered the email address your administrator registered. SpecterX does not tell you whether an address is registered; if you enter a typo or an unregistered address, the page silently looks the same.
- Add `@specterx.com` to your email allowlist or address book and try again.
- If you still do not receive the code after several minutes, contact your administrator. Your account may not be fully provisioned yet.

### "Wrong code" or the code is rejected

The code is six digits. After three wrong attempts SpecterX returns you to the sign-in page and you have to request a new code. Click **Reset password** again, request a fresh code, and use the newest one you received. The previous codes stop working.

### The code expired

Codes expire one hour after they are sent. Start over: click **Reset password** on the sign-in page and request a new code.

### Your administrator has disabled self-service reset

Some organizations require an administrator to reset passwords on behalf of users. If you click **Reset** and nothing happens, or if you cannot find the **Reset password** link on your organization's sign-in page, contact your administrator and ask them to reset your password for you.

### You never received the activation email after your account was created

The first-time activation email uses the same delivery path as the reset email. Check the same places (inbox, spam, address allowlist). If it is not there, ask your administrator to resend it from the admin console.

### You see "You must be invited before you can sign in"

Your email address is not associated with an active SpecterX account. Contact whoever manages SpecterX at your organization and ask them to invite you.

## What this article doesn't cover

- Changing your password while you are signed in. SpecterX has no in-app change-password screen for end users; the **Reset password** flow above is the only path.
- Resetting an administrator's password for the SpecterX admin portal (`admin.specterx.com`). That is a separate flow in a separate application.
- Resetting a password stored at your identity provider (Google, Microsoft, Okta). Use your provider's own tools.

## Related articles

- [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html)
- What is SpecterX?

---

*Last validated against the live SpecterX production tenant at `app.specterx.com` on 2026-05-27.*
