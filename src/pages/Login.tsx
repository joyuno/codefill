import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Code2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Login = () => {
  const { toast } = useToast();
  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); toast({ title: 'Prototype Only', description: 'Authentication is not available.' }); };
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-sm space-y-6">
        <div className="text-center"><Link to="/" className="inline-flex items-center gap-2"><div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary"><Code2 className="h-5 w-5 text-primary-foreground" /></div><span className="text-2xl font-bold">Code<span className="text-primary">Quest</span></span></Link><p className="mt-2 text-muted-foreground">Welcome back!</p></div>
        <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-card p-6"><div className="space-y-2"><Label htmlFor="email">Email</Label><Input id="email" type="email" placeholder="you@example.com" className="bg-secondary" /></div><div className="space-y-2"><Label htmlFor="password">Password</Label><Input id="password" type="password" placeholder="••••••••" className="bg-secondary" /></div><Button type="submit" className="w-full">Log In</Button></form>
        <p className="text-center text-sm text-muted-foreground">Don't have an account? <Link to="/signup" className="text-primary hover:underline">Sign up</Link></p>
      </motion.div>
    </div>
  );
};

export default Login;
