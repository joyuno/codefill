import AdminUserDetailPageClient from './PageClient';

export async function generateStaticParams() {
  return [];
}

export default function AdminUserDetailPage() {
  return <AdminUserDetailPageClient />;
}
