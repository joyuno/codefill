'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Redirect to the new onboarding flow
export default function SignupPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/onboarding');
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-muted-foreground">Redirecting...</p>
    </div>
  );
}
