import SolutionDetailPageClient from './PageClient';

export async function generateStaticParams() {
  return [];
}

export default function SolutionDetailPage() {
  return <SolutionDetailPageClient />;
}
