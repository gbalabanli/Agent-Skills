# Build Brief: Auth Sign-in to Dashboard Flow

## 1. Overview
- **Feature**: Authentication sign-in flow
- **Goal**: User enters credentials and lands on dashboard after successful login.
- **Primary path**: Login form submit -> auth API success -> dashboard route.

## 2. Screen Inventory

### screen_login - Login Screen
- **Image**: `references/examples/screens/screen-login.svg`
- **Summary**: Form with email, password, and Sign In CTA.
- **Notes**: Desktop-focused layout.

### screen_dashboard - Dashboard Home
- **Image**: `references/examples/screens/screen-dashboard.svg`
- **Summary**: Post-login landing page with personalized welcome header.
- **Notes**: Requires profile data fetch.

## 3. Interactive Elements

### screen_login
1. **a_login_email** (`input`)
- Label: Email Input
- Region: x=0.29, y=0.33, w=0.41, h=0.08
- Behavior: User types email; validate format on blur.
- Expected Result: Valid/invalid state in form.
- Component Hint: `TextField(email)`
- Dev Notes: Inline validation message below field.
- Priority: high

2. **a_login_password** (`input`)
- Label: Password Input
- Region: x=0.29, y=0.44, w=0.41, h=0.08
- Behavior: User types password.
- Expected Result: Masked value stored in form state.
- Component Hint: `PasswordField`
- Dev Notes: Minimum 8 chars, optional Caps Lock warning.
- Priority: high

3. **a_login_submit** (`submit`)
- Label: Sign In Button
- Region: x=0.29, y=0.57, w=0.41, h=0.09
- Behavior: Submits email+password to login API.
- Expected Result: Route to dashboard on success, error banner on failure.
- Component Hint: `PrimaryButton`
- Dev Notes: Disable while pending; retry strategy for transient failures.
- Priority: high
- Target Screen: `screen_dashboard`

### screen_dashboard
1. **a_dashboard_welcome** (`view`)
- Label: Welcome Header
- Region: x=0.11, y=0.12, w=0.52, h=0.1
- Behavior: Displays user-specific greeting.
- Expected Result: Updates after profile fetch resolves.
- Component Hint: `HeroHeader`
- Dev Notes: Use loading skeleton while waiting for profile data.
- Priority: medium

## 4. Navigation Flow
1. `screen_login.a_login_submit` -> `screen_dashboard`
- Transition note: Submit success route transition to `/dashboard`.

## 5. Implementation Notes
- Shared form state should include touched/error metadata for validation UX.
- Authentication submit path needs explicit loading and failure states.
- Dashboard must guard route until session token is available.

## 6. Open Questions
- Should login support social providers on first release?
- Should failed login attempts trigger lockout messaging?
