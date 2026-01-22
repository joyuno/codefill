import PublicProfilePageClient from './PageClient';

export async function generateStaticParams() {
  return [];
}

export default function PublicProfilePage() {
  return <PublicProfilePageClient />;
}
