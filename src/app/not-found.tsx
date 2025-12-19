'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <h1 className="text-9xl font-bold text-primary">404</h1>
        <p className="mt-4 text-xl text-muted-foreground">
          Oops! Page not found
        </p>
        <Link href="/">
          <Button className="mt-8 gap-2">
            <Home className="h-4 w-4" />
            Go Home
          </Button>
        </Link>
      </motion.div>
    </div>
  );
}
