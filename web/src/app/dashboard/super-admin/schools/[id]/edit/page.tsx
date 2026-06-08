import { SuperAdminSchoolManagement } from "@/components/super-admin/school-management";

export default async function EditSchoolPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SuperAdminSchoolManagement view="edit" schoolId={Number(id)} />;
}
