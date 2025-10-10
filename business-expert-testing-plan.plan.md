# Auto-Logout & Session Management Implementation

## Overview

Implement automatic logout after inactivity period and proper session management for all authenticated users (Admin, Business Expert). Ensure users work with real data tied to their credentials and sessions expire appropriately.

## Test User Credentials

### Admin User:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`
- **Access**: Full system administration

### Business Expert User:
- **Username**: `business_expert`
- **Password**: `expert123`
- **Role**: `business_expert`
- **Access**: Provider management and application review

## Current State Analysis

### Frontend (✅ Already Exists):
- **`src/services/auth.ts`**: JWT token management, localStorage storage
- **`src/components/ProtectedRoute.tsx`**: Authentication checks on route navigation
- **Token Expiration Check**: `isTokenExpired()` method exists
- **Token Refresh**: `refreshUser()` and `ensureValidToken()` methods exist

### Backend (✅ Already Exists):
- **`backend/routes/auth.py`**: Login/logout endpoints
- **JWT Token**: 24-hour expiration (line 60)
- **`/api/me` endpoint**: Get current user data

### Missing Features (❌ Need Implementation):
1. **Auto-logout on inactivity** (no user activity tracking)
2. **Global activity monitoring** (mouse, keyboard events)
3. **Periodic session validation** (background checks)
4. **Session timeout warnings** (before forcing logout)
5. **Protected route re-validation** (only checks on mount)

## Implementation Plan

### Phase 1: Frontend - Activity Tracking & Auto-Logout

#### 1.1 Create Activity Monitor Service

Create `src/services/activityMonitor.ts`:

```typescript
class ActivityMonitor {
  private lastActivityTime: number = Date.now();
  private inactivityTimeout: number = 30 * 60 * 1000; // 30 minutes
  private warningTimeout: number = 25 * 60 * 1000; // 25 minutes (5 min warning)
  private checkInterval: number = 60 * 1000; // Check every 1 minute
  private intervalId: NodeJS.Timeout | null = null;
  private onInactivity?: () => void;
  private onWarning?: () => void;
  
  // Track user activity
  // Auto-logout on timeout
  // Warning before logout
}
```

**Key Features:**
- Track mouse/keyboard/touch events
- Configurable timeout periods
- Warning callback before logout
- Start/stop monitoring
- Reset activity timer on user action

#### 1.2 Create Session Manager Service

Create `src/services/sessionManager.ts`:

```typescript
class SessionManager {
  private activityMonitor: ActivityMonitor;
  private validationInterval: NodeJS.Timeout | null = null;
  
  // Initialize activity monitoring
  // Periodic token validation
  // Handle logout
  // Session warning UI
}
```

**Key Features:**
- Integrates with AuthService
- Periodic JWT validation (every 5 minutes)
- Activity-based monitoring
- Graceful logout handling
- Toast notifications for warnings

#### 1.3 Update Auth Service

Enhance `src/services/auth.ts`:

```typescript
// Add methods:
- startSession(): void
- endSession(): void
- validateSession(): Promise<boolean>
- getSessionDuration(): number
- updateActivity(): void
```

**Enhancements:**
- Track session start time
- Track last activity time
- Store activity timestamp in localStorage
- Validate on API calls

#### 1.4 Create Session Context/Hook

Create `src/contexts/SessionContext.tsx`:

```typescript
interface SessionContextType {
  isActive: boolean;
  timeUntilLogout: number;
  extendSession: () => void;
  logout: () => void;
}
```

**Purpose:**
- Global session state
- UI components can show session status
- Extend session functionality
- Manual logout

### Phase 2: Global Integration

#### 2.1 App-Level Integration

Update `src/App.tsx`:

```typescript
import { SessionProvider } from '@/contexts/SessionContext';

<SessionProvider>
  <Router>
    {/* routes */}
  </Router>
</SessionProvider>
```

#### 2.2 Protected Route Enhancement

Update `src/components/ProtectedRoute.tsx`:

- Add periodic re-validation (every route change)
- Check activity on mount
- Integrate with SessionContext
- Show warning UI before timeout

#### 2.3 Dashboard Integration

Update all authenticated dashboards:
- `src/pages/AdminDashboard.tsx`
- `src/pages/business-expert/BusinessExpertDashboard.tsx`

Add session status indicator:
```typescript
<SessionStatus /> // Shows time until logout
```

### Phase 3: Backend Enhancements

#### 3.1 Token Expiration Configuration

Update `backend/routes/auth.py`:

```python
# Make token expiration configurable
TOKEN_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Optionally: Add refresh token mechanism
REFRESH_TOKEN_EXPIRATION_DAYS = 7
```

#### 3.2 Session Validation Endpoint

Add to `backend/routes/auth.py`:

```python
@bp.route("/validate-session", methods=["POST"])
@token_required
def validate_session(current_user):
    """Validate current session and optionally extend it"""
    # Return user data + token validity
    # Optionally issue new token
```

#### 3.3 Activity Logging (Optional)

Add user activity logging:
- Last login time
- Last activity time
- Login history
- Session duration tracking

### Phase 4: UI/UX Enhancements

#### 4.1 Session Warning Modal

Create `src/components/SessionWarningModal.tsx`:

```typescript
// Show 5 minutes before logout
// Countdown timer
// "Continue Working" button (resets timer)
// "Logout Now" button
```

#### 4.2 Session Status Indicator

Create `src/components/SessionStatus.tsx`:

```typescript
// Small badge in header/sidebar
// Shows active session time
// Warning icon when near timeout
// Click to extend session
```

#### 4.3 Logout Feedback

Enhance logout experience:
- Toast notification: "خروج به دلیل عدم فعالیت"
- Redirect to login with message
- Remember intended destination
- Auto-redirect after re-login

### Phase 5: Testing & Verification

#### 5.1 Unit Tests

Test files to create:
- `src/services/__tests__/activityMonitor.test.ts`
- `src/services/__tests__/sessionManager.test.ts`
- `src/services/__tests__/auth.test.ts`

#### 5.2 Integration Tests

Test scenarios:
1. Login → Wait 30 min → Auto-logout
2. Login → Activity → No logout
3. Login → 25 min → Warning shown
4. Login → Token expired → Force logout
5. Multiple tabs → Shared session

#### 5.3 Manual Testing

Test all dashboards:
- Admin dashboard
- Business Expert dashboard
- Support dashboard (if exists)

Test all protected routes:
- `/admin/*`
- `/business-expert/*`

### Phase 6: Configuration & Documentation

#### 6.1 Environment Variables

Add to `.env`:
```
# Session Management
VITE_SESSION_TIMEOUT_MINUTES=30
VITE_SESSION_WARNING_MINUTES=5
VITE_SESSION_CHECK_INTERVAL_SECONDS=60
```

#### 6.2 Documentation

Create `docs/session-management.md`:
- How session management works
- Configuration options
- Troubleshooting
- Security considerations

## Files to Create

### New Files:
1. `src/services/activityMonitor.ts` - Activity tracking
2. `src/services/sessionManager.ts` - Session orchestration
3. `src/contexts/SessionContext.tsx` - Global session state
4. `src/hooks/useSession.ts` - Session hook
5. `src/components/SessionWarningModal.tsx` - Warning UI
6. `src/components/SessionStatus.tsx` - Status indicator
7. `docs/session-management.md` - Documentation

### Files to Modify:
1. `src/services/auth.ts` - Add session methods
2. `src/components/ProtectedRoute.tsx` - Add re-validation
3. `src/App.tsx` - Add SessionProvider
4. `src/pages/AdminDashboard.tsx` - Add session status
5. `src/pages/business-expert/BusinessExpertDashboard.tsx` - Add session status
6. `src/components/business-expert/BusinessExpertSidebar.tsx` - Session indicator
7. `src/components/admin/AdminSidebar.tsx` - Session indicator
8. `backend/routes/auth.py` - Add validation endpoint (optional)

## Success Criteria

### Functional Requirements:
- ✅ User logs out after 30 minutes of inactivity
- ✅ User sees warning 5 minutes before logout
- ✅ User can extend session by clicking "Continue"
- ✅ Session validated on every route change
- ✅ Token expiration checked periodically
- ✅ Multiple tabs share same session
- ✅ Works for Admin and Business Expert roles

### Non-Functional Requirements:
- ✅ No performance impact on user interaction
- ✅ Graceful handling of network failures
- ✅ Clear user feedback on session status
- ✅ Configurable timeout periods
- ✅ Secure token handling
- ✅ No memory leaks from intervals

### User Experience:
- ✅ User understands why they were logged out
- ✅ User can see session status at all times
- ✅ User gets adequate warning before logout
- ✅ User can continue working without interruption
- ✅ Seamless re-login experience

## Implementation Priority

### High Priority (Immediate):
1. Activity Monitor Service
2. Session Manager Service
3. Session Context
4. App-level integration
5. Session Warning Modal

### Medium Priority (Soon):
6. Session Status Indicator
7. Protected Route enhancement
8. Dashboard integration
9. Backend validation endpoint

### Low Priority (Future):
10. Activity logging
11. Session history
12. Advanced analytics
13. Multi-device session management

## Security Considerations

1. **Token Storage**: Already using localStorage (consider httpOnly cookies for production)
2. **CSRF Protection**: Already handled by Flask
3. **XSS Protection**: Sanitize all user inputs
4. **Session Hijacking**: Validate token on every protected route
5. **Brute Force**: Already has rate limiting on login
6. **Token Refresh**: Consider implementing refresh tokens for long sessions

## Migration Strategy

### Step 1: Non-Breaking Changes
- Add new services without breaking existing auth
- Keep existing authService methods working
- Add SessionContext as optional feature

### Step 2: Gradual Rollout
- Enable for Business Expert dashboard first
- Monitor for issues
- Enable for Admin dashboard
- Enable for all protected routes

### Step 3: Full Deployment
- Make session management mandatory
- Remove old session handling code
- Update all protected routes

## Implementation Status

### ✅ Completed:
- [x] Create ActivityMonitor service for tracking user activity
- [x] Create SessionManager service for orchestrating session lifecycle
- [x] Create SessionContext and useSession hook for global state
- [x] Add session management methods to AuthService
- [x] Create SessionWarningModal component for timeout warnings
- [x] Create SessionStatus indicator component
- [x] Integrate SessionProvider in App.tsx
- [x] Add session status to Admin dashboard
- [x] Add session status to Business Expert dashboard
- [x] Test auto-logout after inactivity timeout
- [x] Test session warning before timeout
- [x] Fix dropdown menu buttons (profile, settings, logout)

### ⏳ Pending:
- [ ] Add periodic re-validation to ProtectedRoute
- [ ] Add session validation endpoint to backend (optional)
- [ ] Test session consistency across multiple tabs
- [ ] Complete end-to-end testing of session management

## Quick Test Guide

### Test Session Management:
1. Login with Business Expert: `business_expert` / `expert123`
2. Check SessionStatus badge in sidebar
3. Wait for activity or manually test timeout
4. Verify warning modal appears
5. Test session extension
6. Test manual logout from dropdown

### Test Dropdown Menu:
1. Click on user avatar in header
2. Test "پروفایل" → Should show "در حال توسعه" toast
3. Test "تنظیمات" → Should show "در حال توسعه" toast
4. Test "خروج" → Should logout and redirect to login
