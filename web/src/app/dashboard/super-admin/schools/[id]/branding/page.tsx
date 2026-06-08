import { SuperAdminSchoolManagement } from "@/components/super-admin/school-management";

export default async function SchoolBrandingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SuperAdminSchoolManagement view="branding" schoolId={Number(id)} />;
}
