import { SuperAdminSchoolManagement } from "@/components/super-admin/school-management";

export default async function CreateSchoolAdminPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SuperAdminSchoolManagement view="admin" schoolId={Number(id)} />;
}
