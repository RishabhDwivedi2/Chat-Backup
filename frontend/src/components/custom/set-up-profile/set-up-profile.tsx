'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { User, Briefcase, Landmark, UserCog } from 'lucide-react'
import useProfileStore from '@/store/profileStore'
import { useRouter } from 'next/navigation'
import { profileConfig, UserProfile } from '@/config/profileConfig'
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore'

const profileIcons = {
    Debtor: User,
    'FI Admin': Landmark,
    'Resohub Admin': Briefcase,
    'Deltabots Admin': UserCog,
};

export function SetUpProfile() {
    const [selectedProfile, setSelectedProfile] = useState<string>('')
    const { setProfile } = useProfileStore()
    const router = useRouter()
    const { configs } = useDynamicProfileConfigStore()

    useEffect(() => {
        const handleKeyPress = (event: KeyboardEvent) => {
            if (event.key === 'Enter' && selectedProfile) {
                handleSubmit()
            }
        }

        window.addEventListener('keydown', handleKeyPress)
        return () => {
            window.removeEventListener('keydown', handleKeyPress)
        }
    }, [selectedProfile])

    const handleSubmit = () => {
        setProfile(selectedProfile as UserProfile)
        router.push('/')
    }

    return (
        <Card className="w-full max-w-md bg-card text-card-foreground shadow-lg overflow-hidden">
            <CardHeader>
                <CardTitle className="text-2xl font-bold text-center">Set Up Profile</CardTitle>
            </CardHeader>
            <CardContent>
                <RadioGroup onValueChange={setSelectedProfile} value={selectedProfile}>
                    <div className="flex flex-col space-y-4">
                        {Object.entries(configs).map(([profile, config]) => {
                            const IconComponent = profileIcons[profile as keyof typeof profileIcons];
                            return (
                                <div key={profile} className="flex items-center space-x-2">
                                    <RadioGroupItem value={profile} id={profile} />
                                    <Label htmlFor={profile} className="flex items-center space-x-2 cursor-pointer">
                                        <IconComponent className="h-5 w-5 text-primary" />
                                        <span>{config.displayName}</span>
                                    </Label>
                                </div>
                            );
                        })}
                    </div>
                </RadioGroup>
            </CardContent>
            <CardFooter>
                <Button
                    className="w-full"
                    onClick={handleSubmit}
                    disabled={!selectedProfile}
                >
                    Continue
                </Button>
            </CardFooter>
        </Card>
    )
}