# test-notes — 04-share-a-file

Generated: 2026-06-08T10:59:00+00:00

## Step 00-goto — ok

- backend: `browser`
- observation: title='SpecterX'; url=https://app.specterx.com/

## Step 00-email — ok

- backend: `browser`
- observation: title='Login - SpecterX'; url=https://app.specterx.com/signIn

## Step 00-password — ok

- backend: `browser`
- observation: title='Login - SpecterX'; url=https://app.specterx.com/signIn

## Step 00-signin — ok

- backend: `browser`
- observation: title='Sign in - Google Accounts'; url=https://accounts.google.com/v3/signin/identifier?opparams=%253F&dsh=S-283236670%3A1780916189991079&access_type=offline&client_id=252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com&o2v=2&redirect_uri=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com%2Foauth2%2Fidpresponse&response_type=code&scope=profile+email+openid&service=lso&state=H4sIAAAAAAAAAE2S2Y6jMBBF_4XnQEwStrwl3dmmk4YskGXUigyYJQbMYraM5t-nMqOR-slVqltHpXv9S8DCVCC16JGMlzgR5Ts9N6cdvtSaMBBcGK4YCxMCjQeNSitN1RHyG41xhOIxaeoA8wLVIPBBEHGeV9PhEOe5VOXE46TsJI-lwyoOszgDFQGVx_wXMfiOD4XpTyGPWPZqSIrjBN68ZEH8d8xyksU-FLitAAgwzqR_UKmuSClhPwX-10CIgIrT7ZXyxT54d6qamLhLuo9JtJvNNi47BxsXODHITnlxv6RzWTSLw-JYFCKZvbUHg66dPNX62ectMg-3VSROfniw8YCN40hRoaRQbozRutK2i5aqSpHW0W2f0c6Oj4m9nY3NeY2XlsptvZSNLd-bTW_opmq1AVvFd-ou987z1G-W2eXoz28T-9pXV4fol-4QrJzQMg_x2lnXVuqcVNobb32w3KHVidPPR7u1wpZSjN7ts4geWbM1ns2HVtwsy_CDiuqGVyC7S0qnzZXrvA3X9R4uTuBicNMXX2ZVEq55JH3PXcIpfrLsv7MQGSylwlTWdGTIqqwbkIYwDXBSkYFQAk1TVIXoI0PEaOSKE9cYiy7WZHGCsKdqsqIG-PWHGsj16_cfOPLSBWkCAAA.H4sIAAAAAAAAAAEgAN__x7iIiENzc95XPP8C75H7EiqoaqI6qn_xjlLO0FVr19JusZNYIAAAAA.3&flowName=GeneralOAuthLite&continue=https%3A%2F%2Faccounts.google.com%2Fsignin%2Foauth%2Flegacy%2Fconsent%3Fauthuser%3Dunknown%26part%3DAJi8hAMU-ZxWnv5RGpO5ADnt2CvpjVRG7gDfIyizsDfL7oEjeE2VdO5-qh1a1a3C-D2OhocNo1K0CDSNHwgbQ_bRVEH5cYYqTulqy5AT5kHKSg_sw3RHV59yaIEODb5zjnU7bYkQqBpSESNj0jibBTCejO9aL7IMz8Zc6gZEWxl_hSjlJXs9QU6nYNqBpZnVSQhSqprHoJzFIQAKPVpqJF3xv26fFteNBRqgZct5YDNJ7Yr2Hbz-SBsMt-EpRSg_2oESYPou8JDIVuu9hY9Rc3-jr_MR8k_tzfmQ0IL4Jzv73C9yNq6M_yBwJF7kE6zD82BrjpgWZMKZh5yE2x22Qqp8Lz_aYGmonEoSSqLmgK8B4JVh1jhOv45ON2scoT6vtG27REp8GRTHKYXa7qsq4c4pO9F-dj62CbGKD3bZBKyI9a9kUK5nqLvr9nzVZGQsrfL1Cp9hJDwMx_b5vBeDhhiVkUAbo5ENDyRuP-d9R43WNYQ_2l4K3jQMHlhrCFmV0NzNP2BUOf2q%26flowName%3DGeneralOAuthFlow%26as%3DS-283236670%253A1780916189991079%26client_id%3D252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com%23&app_domain=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com&rart=ANgoxceumrBcctt3w08UPoZZjQ52ebL3uKCy8MqKvo316S1MpCbe4Ud9q59ApARfDnHXNO8q_HhcbTs1qY2nsUdQdadLy3xUZ1gbYOej4IS3mo7qZTHchmE

## Step 00-dashboard — FAIL

- backend: `browser`
- observation: timed out: Wait for the My Files page to load
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("My Files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 01-open-drawer — FAIL

- backend: `browser`
- observation: timed out: Click the Share files button to open the Share Files drawer (article step 1)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Share files").first
`
- > ⚠ couldn't verify this step.

## Step 02-upload-file — FAIL

- backend: `browser`
- observation: timed out: Upload tester/fixtures/test-document.pdf via the drawer's upload area (article step 2)
- error: `Locator.set_input_files: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("Click or drag a file to this area to upload").first
`
- > ⚠ couldn't verify this step.

## Step 03-add-recipient — FAIL

- backend: `browser`
- observation: timed out: Type the test recipient email into the Share with field and press Enter (article step 3)
- error: `Locator.fill: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_placeholder("Insert email address and click `Enter`").first
`
- > ⚠ couldn't verify this step.

## Step 04-next-policy — ok

- backend: `browser`
- observation: title=''; url=https://accounts.google.com/v3/signin/identifier?access_type=offline&app_domain=https://prod-users.auth.eu-central-1.amazoncognito.com&client_id=252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com&continue=https://accounts.google.com/signin/oauth/legacy/consent?authuser%3Dunknown%26part%3DAJi8hAMU-ZxWnv5RGpO5ADnt2CvpjVRG7gDfIyizsDfL7oEjeE2VdO5-qh1a1a3C-D2OhocNo1K0CDSNHwgbQ_bRVEH5cYYqTulqy5AT5kHKSg_sw3RHV59yaIEODb5zjnU7bYkQqBpSESNj0jibBTCejO9aL7IMz8Zc6gZEWxl_hSjlJXs9QU6nYNqBpZnVSQhSqprHoJzFIQAKPVpqJF3xv26fFteNBRqgZct5YDNJ7Yr2Hbz-SBsMt-EpRSg_2oESYPou8JDIVuu9hY9Rc3-jr_MR8k_tzfmQ0IL4Jzv73C9yNq6M_yBwJF7kE6zD82BrjpgWZMKZh5yE2x22Qqp8Lz_aYGmonEoSSqLmgK8B4JVh1jhOv45ON2scoT6vtG27REp8GRTHKYXa7qsq4c4pO9F-dj62CbGKD3bZBKyI9a9kUK5nqLvr9nzVZGQsrfL1Cp9hJDwMx_b5vBeDhhiVkUAbo5ENDyRuP-d9R43WNYQ_2l4K3jQMHlhrCFmV0NzNP2BUOf2q%26flowName%3DGeneralOAuthFlow%26as%3DS-283236670%253A1780916189991079%26client_id%3D252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com%23&dsh=S-283236670:1780916189991079&flowName=GeneralOAuthLite&o2v=2&opparams=%253F&rart=ANgoxceumrBcctt3w08UPoZZjQ52ebL3uKCy8MqKvo316S1MpCbe4Ud9q59ApARfDnHXNO8q_HhcbTs1qY2nsUdQdadLy3xUZ1gbYOej4IS3mo7qZTHchmE&redirect_uri=https://prod-users.auth.eu-central-1.amazoncognito.com/oauth2/idpresponse&response_type=code&scope=profile+email+openid&service=lso&state=H4sIAAAAAAAAAE2S2Y6jMBBF_4XnQEwStrwl3dmmk4YskGXUigyYJQbMYraM5t-nMqOR-slVqltHpXv9S8DCVCC16JGMlzgR5Ts9N6cdvtSaMBBcGK4YCxMCjQeNSitN1RHyG41xhOIxaeoA8wLVIPBBEHGeV9PhEOe5VOXE46TsJI-lwyoOszgDFQGVx_wXMfiOD4XpTyGPWPZqSIrjBN68ZEH8d8xyksU-FLitAAgwzqR_UKmuSClhPwX-10CIgIrT7ZXyxT54d6qamLhLuo9JtJvNNi47BxsXODHITnlxv6RzWTSLw-JYFCKZvbUHg66dPNX62ectMg-3VSROfniw8YCN40hRoaRQbozRutK2i5aqSpHW0W2f0c6Oj4m9nY3NeY2XlsptvZSNLd-bTW_opmq1AVvFd-ou987z1G-W2eXoz28T-9pXV4fol-4QrJzQMg_x2lnXVuqcVNobb32w3KHVidPPR7u1wpZSjN7ts4geWbM1ns2HVtwsy_CDiuqGVyC7S0qnzZXrvA3X9R4uTuBicNMXX2ZVEq55JH3PXcIpfrLsv7MQGSylwlTWdGTIqqwbkIYwDXBSkYFQAk1TVIXoI0PEaOSKE9cYiy7WZHGCsKdqsqIG-PWHGsj16_cfOPLSBWkCAAA.H4sIAAAAAAAAAAEgAN__x7iIiENzc95XPP8C75H7EiqoaqI6qn_xjlLO0FVr19JusZNYIAAAAA.3; verify('The Select Policy step heading is visible')=not-visible
- screenshot: `screenshots/04-policy-step.png`

## Step 05-open-policy-dropdown — FAIL

- backend: `browser`
- observation: timed out: Open the Choose Policy dropdown to see available policies (article step 6)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("Choose Policy").first
`
- > ⚠ couldn't verify this step.

## Step 06-select-default-policy — FAIL

- backend: `browser`
- observation: timed out: Select the default policy from the dropdown
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("Default").first
`
- > ⚠ couldn't verify this step.

## Step 07-click-share — FAIL

- backend: `browser`
- observation: timed out: Click Share to complete the share (article step 8)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Share").first
`
- > ⚠ couldn't verify this step.

## Step 08-copy-link — FAIL

- backend: `browser`
- observation: timed out: Click Copy Link to copy the protected link (article step 9)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Copy Link").first
`
- > ⚠ couldn't verify this step.

## Step 09-close-drawer — FAIL

- backend: `browser`
- observation: timed out: Close the Share Files drawer and return to My Files
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("Close").first
`
- > ⚠ couldn't verify this step.

## Step 10-open-share-permissions-drawer — FAIL

- backend: `browser`
- observation: timed out: Click the share icon on test-document.pdf to open the Share & Permissions Drawer (article 'After you share' section)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("Share").first
`
- > ⚠ couldn't verify this step.
