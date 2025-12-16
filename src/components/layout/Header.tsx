import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Code2, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  const location = useLocation();
  const isLoggedIn = location.pathname !== '/login' && location.pathname !== '/signup';

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div className="flex h-16 items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <Code2 className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold tracking-tight">
            Code<span className="text-primary">Quest</span>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {isLoggedIn ? (
            <>
              <div className="hidden items-center gap-2 rounded-full bg-secondary px-3 py-1.5 sm:flex">
                <Zap className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">2,450 XP</span>
              </div>
              <Link to="/mypage">
                <Button variant="outline" size="sm">
                  My Page
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Log In
                </Button>
              </Link>
              <Link to="/signup">
                <Button size="sm">Sign Up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
}
