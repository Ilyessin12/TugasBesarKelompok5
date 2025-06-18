import { redirect } from 'next/navigation';

export default function HomePage() {
  redirect('/dashboard');
  
  // This won't be reached, but Next.js requires a component to return JSX
  return null;
}