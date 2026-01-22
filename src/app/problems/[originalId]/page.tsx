import ProblemDetailPageClient from './PageClient';

export async function generateStaticParams() {
  return [];
}

export default function ProblemDetailPage() {
  return <ProblemDetailPageClient />;
}
