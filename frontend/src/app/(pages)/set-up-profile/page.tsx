import { Metadata } from 'next';
import { SetUpProfile } from '@/components/custom/set-up-profile/set-up-profile'
import RetroGrid from '@/components/magicui/retro-grid';

export const metadata: Metadata = {
    title: 'Set Up Profile | Roles',
};

export default function SetUpProfilePage() {

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 font-poppins">
            <RetroGrid className="fixed inset-0 z-0" angle={65} />
            <SetUpProfile />
        </div>
    )
}