import { SpokeSpinner } from "@/components/ui/spinner";

export default function FullPageLoader() {
    return (
        <div className="fixed inset-0 flex items-center justify-center z-50 font-poppins">
            <div className="flex items-center gap-2">
                <SpokeSpinner size="lg" />
                <span className="text-sm font-medium text-slate-500">Loading...</span>
            </div>
        </div>
    )
}