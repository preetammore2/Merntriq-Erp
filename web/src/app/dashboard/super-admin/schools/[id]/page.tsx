import { SuperAdminSchoolManagement } from "@/components/super-admin/school-management";

export default async function SchoolDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SuperAdminSchoolManagement view="details" schoolId={Number(id)} />;
}
