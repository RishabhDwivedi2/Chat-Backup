// /app/(pages)/admin/dashboard/page.tsx

"use client"

import React, { useEffect, useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import AnimatedBeamDemo from "@/components/custom/admin/dashboard/animated-beam";
import { useRouter } from "next/navigation";

interface AdminData {
  company_name: string;
  assistant_email: string | null;
  admin_first_name: string;
}

export default function DashboardPage() {
  const [isOpen, setIsOpen] = useState(true);
  const [adminData, setAdminData] = useState<AdminData | null>(null);
  const router = useRouter();

  useEffect(() => {
    const storedData = sessionStorage.getItem('adminData');
    if (!storedData) {
      console.log('No admin data found in session storage');
      router.push('/admin/login');
      return;
    }

    try {
      const parsedData = JSON.parse(storedData);
      setAdminData(parsedData);
    } catch (error) {
      console.error('Error parsing admin data:', error);
      router.push('/admin/login');
    }
  }, [router]);

  const formatCompanyName = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '')
      .trim();
  };

  const getEmailInstruction = () => {
    if (!adminData) return '';
    
    const formattedCompanyName = formatCompanyName(adminData.company_name);
    const assistantEmail = adminData.assistant_email || 'your assigned assistant email';
    
    return (
      <>
        To continue our services, please create an email id{' '}
        <span className="font-bold">
          aiassistant@{formattedCompanyName}.com
        </span>
        {' '}and forward it to{' '}
        <span className="font-bold">
          {assistantEmail}
        </span>.
      </>
    );
  };

  return (
    <div className="relative">
      {/* <AnimatedBeamDemo /> */}
      
      <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
        <AlertDialogContent className="max-w-md font-poppins">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-2xl font-bold">
              Welcome, {adminData?.admin_first_name || 'Admin'}!
            </AlertDialogTitle>
            <AlertDialogDescription className="text-lg space-y-4">
              <p>
                Thank you for accessing the admin dashboard. We're excited to have you here!
              </p>
              <p>
                {getEmailInstruction()}
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="sm:justify-center">
            <AlertDialogAction 
              className="w-24"
              onClick={() => {
                sessionStorage.clear();
                localStorage.removeItem('adminToken');
                router.push("/admin/login");
              }}
            >
              Exit
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}