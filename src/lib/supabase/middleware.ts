import { NextResponse, type NextRequest } from 'next/server';

/**
 * Middleware for request handling.
 *
 * Note: Authentication is handled client-side using JWT tokens stored in localStorage.
 * Protected route checks are done in individual pages/components using the useAuth hook.
 */
export async function updateSession(request: NextRequest) {
  // Simply pass through all requests
  // Auth protection is handled client-side via useAuth hook
  return NextResponse.next({ request });
}
