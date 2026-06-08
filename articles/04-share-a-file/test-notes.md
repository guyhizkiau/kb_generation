# test-notes — 04-share-a-file

Generated: 2026-06-08T08:00:55+00:00

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
- observation: title='Sign in - Google Accounts'; url=https://accounts.google.com/v3/signin/identifier?opparams=%253F&dsh=S269643133%3A1780905399722850&access_type=offline&client_id=252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com&o2v=2&redirect_uri=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com%2Foauth2%2Fidpresponse&response_type=code&scope=profile+email+openid&service=lso&state=H4sIAAAAAAAAAE2RW4-iQBCF_wvPgnihFd9GUUfUkfE24GZCWrqB1oZuoUGHyf73LXezyTxVVerUl5M63xrWRhqt9IjmqsBc74TXj3q_xn410FraGZZzIRJOYYhgQNdygIamSeqBUKbJerSuYqxuZgUCAoJUKVmO2m0spVFKGilaPIxIZO2SJTnLQUVBFQnyJMY_8Yk2-qXJVOTPgWaYcaiyEDH7uxaS5oxAg-8lAAGmhPEPalQlLQxMMuB_trT0aSPdyGzxZa34Zrlg_HY4usvjvSns2JPOYBIBh4GMiVil-wVzCjLO5eVarGUzd5pZXXp8Rt7zN-Rxz19n4vEOFxe42HUtBO0VWnfdWK-M6x_Y9wV6jPkwCdywu1bcp8E-ZbdtlF7UtGfurMBWfGod00WYhPOSqeDLUdcJ6vqbpUeORXV0Nm8T7D6mLza6r0_n_XF4YSfHfrnks2Z-CPMVSVypJ9v7gSqvjndLFYSJtPPxI1jVaKFUPK59dRrPPa_wN9SN76_DbZTfELsE6S4BxxwcwzeJ_nxWaeBKpcbP3A2c4Ubk_z8LkcFRpo06g6Fpm1bPtiENbRRjXtKWVgBtcEbdiPSxTs400vsm6el2Z0j0KOr3kImtDkVdYNSQ6-fvPweW0eRpAgAA.H4sIAAAAAAAAAAEgAN__x8xfayxM4cCTYNfcbah0gafw29yqc_9KdqutgTOOWJ36nhQ-IAAAAA.3&flowName=GeneralOAuthLite&continue=https%3A%2F%2Faccounts.google.com%2Fsignin%2Foauth%2Flegacy%2Fconsent%3Fauthuser%3Dunknown%26part%3DAJi8hANoUOmsrgr7R9uZHQ3ssuzuat939cgb2aFqOt6dfnqCURFe7NGUIFypXbUoUw-AyEJMC2WSZQxGdeZ94FDuPtBMMDEfRwIo5M8lMNDYqkQ6jC0CEv8DbXpX3qoMWPzsTJsKLJrUbAx_yfz3zQ5_zersQGkouLBMjsHfcvvKH-pkrBOpu6hdHgRC3fHQh-cQ06muY0Zo1gmfGidGZcZOG8-T54e5dfuCH3CaPfRmrtTBnhl5INJS2u52z4Q4cCGQsw3Q3dc0UEXzqI4Sd3l361NuA_U63r2SEProuQKDmfzvs_F_g3aPUEUS8leQK5L6Ipxg7FyBobwWEXuMMoua1NuD7-BE7eEEO_cGnLd7BtPASRZ9ptrJqAY2JUmAPKIjn9foougv1ffGT0xLmHN9iOAhuTo_Jtuu5bxQATwP91LfFKiRAidBWNSstzx3UbadBryzrz0m3XiKJfzT94NVPNg-1XulRT9AOm9OcRvCi-T1clVTZnCOTlv-wtUI1vM_umQdpiR9%26flowName%3DGeneralOAuthFlow%26as%3DS269643133%253A1780905399722850%26client_id%3D252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com%23&app_domain=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com&rart=ANgoxcdCLzGTI6HfsLVVvSdyONuBI3rZODlF41xODeROVZ0SEH6NjER-k5KvatKUrFvTIlXTFrJEpLgg89jzfUZ7MQUJpVGEPRBQZOFBJzDnKnAu1VxgMaQ

## Step 00-dashboard — FAIL

- backend: `browser`
- observation: timed out: Wait for My Files
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("My Files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 01 — FAIL

- backend: `browser`
- observation: timed out: Click the Share files button on the My Files page (article Step 1: Open the Share files dialog)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Share files").first
`
- > ⚠ couldn't verify this step.

## Step 02 — FAIL

- backend: `browser`
- observation: timed out: Wait for the Share files dialog to be fully open
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("dialog", name="Share files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 03 — FAIL

- backend: `browser`
- observation: timed out: Upload test-document.pdf using the file input in the Share files dialog (article Step 2: Upload your file)
- error: `Locator.set_input_files: Timeout 15000ms exceeded.
Call log:
  - waiting for locator("input[type='file']").first
`
- > ⚠ couldn't verify this step.

## Step 04 — FAIL

- backend: `browser`
- observation: timed out: Wait for test-document.pdf to finish uploading
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("test-document.pdf").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 05 — FAIL

- backend: `browser`
- observation: timed out: Type a recipient email address in the Add recipients field (article Step 3: Add a recipient)
- error: `Locator.fill: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_placeholder("Add recipients").first
`
- > ⚠ couldn't verify this step.

## Step 06 — ok

- backend: `browser`
- observation: title='Loading https://accounts.google.com/v3/signin/identifier?access_type=offline&app_domain=https://prod-users.auth.eu-central-1.amazoncognito.com&client_id=252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com&continue=https://accounts.google.com/signin/oauth/legacy/consent?authuser%3Dunknown%26part%3DAJi8hANoUOmsrgr7R9uZHQ3ssuzuat939cgb2aFqOt6dfnqCURFe7NGUIFypXbUoUw-AyEJMC2WSZQxGdeZ94FDuPtBMMDEfRwIo5M8lMNDYqkQ6jC0CEv8DbXpX3qoMWPzsTJsKLJrUbAx_yfz3zQ5_zersQGkouLBMjsHfcvvKH-pkrBOpu6hdHgRC3fHQh-cQ06muY0Zo1gmfGidGZcZOG8-T54e5dfuCH3CaPfRmrtTBnhl5INJS2u52z4Q4cCGQsw3Q3dc0UEXzqI4Sd3l361NuA_U63r2SEProuQKDmfzvs_F_g3aPUEUS8leQK5L6Ipxg7FyBobwWEXuMMoua1NuD7-BE7eEEO_cGnLd7BtPASRZ9ptrJqAY2JUmAPKIjn9foougv1ffGT0xLmHN9iOAhuTo_Jtuu5bxQATwP91LfFKiRAidBWNSstzx3UbadBryzrz0m3XiKJfzT94NVPNg-1XulRT9AOm9OcRvCi-T1clVTZnCOTlv-wtUI1vM_umQdpiR9%26flowName%3DGeneralOAuthFlow%26as%3DS269643133%253A1780905399722850%26client_id%3D252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com%23&dsh=S269643133:1780905399722850&flowName=GeneralOAuthLite&o2v=2&opparams=%253F&rart=ANgoxcdCLzGTI6HfsLVVvSdyONuBI3rZODlF41xODeROVZ0SEH6NjER-k5KvatKUrFvTIlXTFrJEpLgg89jzfUZ7MQUJpVGEPRBQZOFBJzDnKnAu1VxgMaQ&redirect_uri=https://prod-users.auth.eu-central-1.amazoncognito.com/oauth2/idpresponse&response_type=code&scope=profile+email+openid&service=lso&state=H4sIAAAAAAAAAE2RW4-iQBCF_wvPgnihFd9GUUfUkfE24GZCWrqB1oZuoUGHyf73LXezyTxVVerUl5M63xrWRhqt9IjmqsBc74TXj3q_xn410FraGZZzIRJOYYhgQNdygIamSeqBUKbJerSuYqxuZgUCAoJUKVmO2m0spVFKGilaPIxIZO2SJTnLQUVBFQnyJMY_8Yk2-qXJVOTPgWaYcaiyEDH7uxaS5oxAg-8lAAGmhPEPalQlLQxMMuB_trT0aSPdyGzxZa34Zrlg_HY4usvjvSns2JPOYBIBh4GMiVil-wVzCjLO5eVarGUzd5pZXXp8Rt7zN-Rxz19n4vEOFxe42HUtBO0VWnfdWK-M6x_Y9wV6jPkwCdywu1bcp8E-ZbdtlF7UtGfurMBWfGod00WYhPOSqeDLUdcJ6vqbpUeORXV0Nm8T7D6mLza6r0_n_XF4YSfHfrnks2Z-CPMVSVypJ9v7gSqvjndLFYSJtPPxI1jVaKFUPK59dRrPPa_wN9SN76_DbZTfELsE6S4BxxwcwzeJ_nxWaeBKpcbP3A2c4Ubk_z8LkcFRpo06g6Fpm1bPtiENbRRjXtKWVgBtcEbdiPSxTs400vsm6el2Z0j0KOr3kImtDkVdYNSQ6-fvPweW0eRpAgAA.H4sIAAAAAAAAAAEgAN__x8xfayxM4cCTYNfcbah0gafw29yqc_9KdqutgTOOWJ36nhQ-IAAAAA.3'; url=https://accounts.google.com/v3/signin/identifier?opparams=%253F&dsh=S269643133%3A1780905399722850&access_type=offline&client_id=252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com&o2v=2&redirect_uri=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com%2Foauth2%2Fidpresponse&response_type=code&scope=profile+email+openid&service=lso&state=H4sIAAAAAAAAAE2RW4-iQBCF_wvPgnihFd9GUUfUkfE24GZCWrqB1oZuoUGHyf73LXezyTxVVerUl5M63xrWRhqt9IjmqsBc74TXj3q_xn410FraGZZzIRJOYYhgQNdygIamSeqBUKbJerSuYqxuZgUCAoJUKVmO2m0spVFKGilaPIxIZO2SJTnLQUVBFQnyJMY_8Yk2-qXJVOTPgWaYcaiyEDH7uxaS5oxAg-8lAAGmhPEPalQlLQxMMuB_trT0aSPdyGzxZa34Zrlg_HY4usvjvSns2JPOYBIBh4GMiVil-wVzCjLO5eVarGUzd5pZXXp8Rt7zN-Rxz19n4vEOFxe42HUtBO0VWnfdWK-M6x_Y9wV6jPkwCdywu1bcp8E-ZbdtlF7UtGfurMBWfGod00WYhPOSqeDLUdcJ6vqbpUeORXV0Nm8T7D6mLza6r0_n_XF4YSfHfrnks2Z-CPMVSVypJ9v7gSqvjndLFYSJtPPxI1jVaKFUPK59dRrPPa_wN9SN76_DbZTfELsE6S4BxxwcwzeJ_nxWaeBKpcbP3A2c4Ubk_z8LkcFRpo06g6Fpm1bPtiENbRRjXtKWVgBtcEbdiPSxTs400vsm6el2Z0j0KOr3kImtDkVdYNSQ6-fvPweW0eRpAgAA.H4sIAAAAAAAAAAEgAN__x8xfayxM4cCTYNfcbah0gafw29yqc_9KdqutgTOOWJ36nhQ-IAAAAA.3&flowName=GeneralOAuthLite&continue=https%3A%2F%2Faccounts.google.com%2Fsignin%2Foauth%2Flegacy%2Fconsent%3Fauthuser%3Dunknown%26part%3DAJi8hANoUOmsrgr7R9uZHQ3ssuzuat939cgb2aFqOt6dfnqCURFe7NGUIFypXbUoUw-AyEJMC2WSZQxGdeZ94FDuPtBMMDEfRwIo5M8lMNDYqkQ6jC0CEv8DbXpX3qoMWPzsTJsKLJrUbAx_yfz3zQ5_zersQGkouLBMjsHfcvvKH-pkrBOpu6hdHgRC3fHQh-cQ06muY0Zo1gmfGidGZcZOG8-T54e5dfuCH3CaPfRmrtTBnhl5INJS2u52z4Q4cCGQsw3Q3dc0UEXzqI4Sd3l361NuA_U63r2SEProuQKDmfzvs_F_g3aPUEUS8leQK5L6Ipxg7FyBobwWEXuMMoua1NuD7-BE7eEEO_cGnLd7BtPASRZ9ptrJqAY2JUmAPKIjn9foougv1ffGT0xLmHN9iOAhuTo_Jtuu5bxQATwP91LfFKiRAidBWNSstzx3UbadBryzrz0m3XiKJfzT94NVPNg-1XulRT9AOm9OcRvCi-T1clVTZnCOTlv-wtUI1vM_umQdpiR9%26flowName%3DGeneralOAuthFlow%26as%3DS269643133%253A1780905399722850%26client_id%3D252727352368-np17abea36dslje10070ucmh9b8h7rib.apps.googleusercontent.com%23&app_domain=https%3A%2F%2Fprod-users.auth.eu-central-1.amazoncognito.com&rart=ANgoxcdCLzGTI6HfsLVVvSdyONuBI3rZODlF41xODeROVZ0SEH6NjER-k5KvatKUrFvTIlXTFrJEpLgg89jzfUZ7MQUJpVGEPRBQZOFBJzDnKnAu1VxgMaQ; verify('The recipient email address appears as a chip or row in the recipients list')=not-visible
- screenshot: `screenshots/06-recipient-added.png`

## Step 07 — FAIL

- backend: `browser`
- observation: timed out: Click the permission dropdown next to the recipient to open it (article Step 4: Set recipient permission level)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("combobox", name="Viewer").first
`
- > ⚠ couldn't verify this step.

## Step 08 — FAIL

- backend: `browser`
- observation: timed out: Select Viewer from the permission dropdown
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("option", name="Viewer").first
`
- > ⚠ couldn't verify this step.

## Step 09 — FAIL

- backend: `browser`
- observation: timed out: Click the security policy dropdown to open it (article Step 5: Select a security policy)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("combobox", name="Policy").first
`
- > ⚠ couldn't verify this step.

## Step 10 — FAIL

- backend: `browser`
- observation: timed out: Select the Standard security policy from the dropdown
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("option", name="Standard").first
`
- > ⚠ couldn't verify this step.

## Step 11 — FAIL

- backend: `browser`
- observation: timed out: Click the Share button to create the protected link and send notification emails (article Step 7: Complete the share)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Share").first
`
- > ⚠ couldn't verify this step.

## Step 12 — FAIL

- backend: `browser`
- observation: timed out: Wait for the share confirmation screen showing the Copy link button
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Copy link").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 13 — FAIL

- backend: `browser`
- observation: timed out: Click Copy link to copy the protected link to the clipboard (article Step 8: Copy the protected link)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Copy link").first
`
- > ⚠ couldn't verify this step.

## Step 14 — FAIL

- backend: `browser`
- observation: timed out: Close the Share files confirmation and return to My Files
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Done").first
`
- > ⚠ couldn't verify this step.

## Step 15 — FAIL

- backend: `browser`
- observation: timed out: Wait for the My Files page to be visible after closing the dialog
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("heading", name="My Files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 16 — FAIL

- backend: `browser`
- observation: timed out: Click the share icon next to test-document.pdf to open the Share & Permissions Drawer (article: After you share section)
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Manage sharing").first
`
- > ⚠ couldn't verify this step.

## Step 17 — FAIL

- backend: `browser`
- observation: timed out: Verify the Share & Permissions Drawer shows the recipient, permission level, and policy
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_role("complementary", name="Share & Permissions").first to be visible
`
- > ⚠ couldn't verify this step.
