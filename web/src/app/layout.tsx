import type { Metadata } from "next";

import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mentriq360 ERP",
  description: "Role-based campus ERP for admissions, attendance, academics, results, resources, admit cards, fees, and reporting.",
  applicationName: "Mentriq360 ERP",
  manifest: "/manifest.json",
  icons: {
    icon: "/logo.png",
    apple: "/logo.png"
  },
  appleWebApp: {
    capable: true,
    title: "Mentriq360 ERP",
    statusBarStyle: "default"
  }
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#101828"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-page antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
