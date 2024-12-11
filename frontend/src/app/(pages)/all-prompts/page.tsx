'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableHeader, TableHead, TableBody, TableRow, TableCell } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { MoreHorizontal, ChevronsUpDown, Plus, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight, LifeBuoy, SquareUser, Bot, SquareTerminal, Triangle, Code2, Book, Settings2 } from 'lucide-react'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator } from '@/components/ui/dropdown-menu'
import BreadcrumbComponent from '@/components/custom/bread-crumb'
import { useRouter } from 'next/navigation'
import { useToast } from '@/hooks/use-toast'
import {
    AlertDialog,
    AlertDialogTrigger,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogCancel,
    AlertDialogAction
} from '@/components/ui/alert-dialog'
import {
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogTitle,
    DialogDescription
} from '@/components/ui/dialog'
import FullPageLoader from '@/components/custom/page-loader'
import { ToastAction } from '@/components/ui/toast'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import NavigationComponent from '@/components/custom/pg_navigation'
import HeaderComponent from '@/components/custom/pg_header'

interface Prompt {
    id: number;
    prompt_text: string;
}

export default function Panel() {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [sortAsc, setSortAsc] = useState(true);
    const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
    const [deletePromptId, setDeletePromptId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(10);
    const { toast } = useToast();
    const router = useRouter();

    useEffect(() => {
        fetchPrompts();
    }, []);

    const fetchPrompts = async () => {
        try {
            setIsLoading(true);
            const response = await fetch('http://localhost:8000/get_prompts');
            if (!response.ok) {
                throw new Error('Failed to fetch prompts');
            }
            const data = await response.json();
            setPrompts(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const totalPages = Math.ceil(prompts.length / itemsPerPage);

    const currentPrompts = prompts.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const handlePageChange = (newPage: number) => {
        if (newPage > 0 && newPage <= totalPages) {
            setCurrentPage(newPage);
        }
    };

    const sortPrompts = () => {
        const sortedPrompts = [...prompts].sort((a, b) => {
            if (sortAsc) {
                return a.prompt_text.localeCompare(b.prompt_text);
            } else {
                return b.prompt_text.localeCompare(a.prompt_text);
            }
        });
        setSortAsc(!sortAsc);
        setPrompts(sortedPrompts);
    }

    const handleView = (prompt: Prompt) => {
        setSelectedPrompt(prompt);
    };

    const deletePrompt = async (id: number) => {
        try {
            const response = await fetch(`http://localhost:8000/delete_prompt/${id}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                setPrompts(prompts.filter(p => p.id !== id));
                toast({
                    title: "Prompt deleted successfully.",
                    action: <ToastAction altText="Close">Okay</ToastAction>,
                });
            } else {
                throw new Error("Failed to delete prompt");
            }
        } catch (err: any) {
            toast({
                title: "Error deleting prompt",
                description: err.message,
                variant: 'destructive',
                action: <ToastAction altText="Close">Retry</ToastAction>,
            });
        }
    };

    if (isLoading) {
        return <FullPageLoader />;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="grid h-screen w-full pl-[56px] font-poppins">
            <NavigationComponent defaultActive='main' />
            <div className="flex flex-col">
                <HeaderComponent />
                <BreadcrumbComponent
                    items={[
                        { label: 'Main', href: '/all-prompts' }
                    ]}
                    separator=">"
                    currentPage="All Prompts"
                />
                <Card className="w-full max-w-[93vw] mx-4 my-6 shadow-lg border border-gray-300 font-poppins">
                    <CardHeader>
                        <CardTitle>Prompts</CardTitle>
                        <CardDescription>
                            List of all prompts added to the database.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex justify-between items-center mb-4">
                            <div className="flex items-center space-x-4">
                                <Input placeholder="Search prompts..." className="max-w-sm border-gray-300" />

                                <Select>
                                    <SelectTrigger className="w-[150px] border-gray-300 flex items-center">
                                        <SelectValue placeholder="Filter" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="asc">Ascending</SelectItem>
                                        <SelectItem value="desc">Descending</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <Button className="border-gray-300" onClick={() => router.push('/all-prompts/add-prompt')}>
                                <Plus className="mr-2 h-4 w-4" />
                                Add Prompt
                            </Button>
                        </div>
                        <div className="border border-gray-300 rounded-lg overflow-hidden">
                            <Table className="min-w-full text-left">
                                <TableHeader>
                                    <TableRow className="bg-gray-200">
                                        <TableHead className="w-[30px] px-4 py-2">
                                            <Checkbox />
                                        </TableHead>
                                        <TableHead
                                            className="px-4 py-2 cursor-pointer"
                                            onClick={sortPrompts}
                                        >
                                            <div className="flex items-center space-x-1">
                                                <span>Prompt</span>
                                                <ChevronsUpDown className="h-4 w-4" />
                                            </div>
                                        </TableHead>
                                        <TableHead className="px-4 py-2">View prompt</TableHead>
                                        <TableHead className="w-[30px] px-4 py-2"></TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {currentPrompts.length > 0 ? (
                                        currentPrompts.map((prompt) => (
                                            <TableRow
                                                key={prompt.id}
                                                className="hover:bg-gray-100 transition-colors duration-200"
                                            >
                                                <TableCell className="px-4 py-2">
                                                    <Checkbox />
                                                </TableCell>
                                                <TableCell className="px-4 py-2 font-medium max-w-xs overflow-hidden text-ellipsis whitespace-nowrap">
                                                    {prompt.prompt_text}
                                                </TableCell>
                                                <TableCell className="px-4 py-2">
                                                    <Dialog>
                                                        <DialogTrigger asChild>
                                                            <Button
                                                                variant="outline"
                                                                className="px-3 py-1 text-sm font-medium w-[90px] border-[1px] border-[hsl(var(--border))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2"
                                                                onClick={() => handleView(prompt)}
                                                            >
                                                                View
                                                            </Button>
                                                        </DialogTrigger>
                                                        <DialogContent className="font-poppins max-w-[800px]">
                                                            <DialogTitle>Prompt Details</DialogTitle>
                                                            <DialogDescription>
                                                                <div className="max-h-[400px] overflow-y-auto p-2">
                                                                    <p>
                                                                        <strong>ID:</strong> {selectedPrompt?.id}
                                                                    </p>
                                                                    <p>
                                                                        <strong>Prompt Text:</strong> {selectedPrompt?.prompt_text}
                                                                    </p>
                                                                </div>
                                                            </DialogDescription>
                                                        </DialogContent>
                                                    </Dialog>
                                                </TableCell>
                                                <TableCell className="px-4 py-2">
                                                    <DropdownMenu>
                                                        <DropdownMenuTrigger asChild>
                                                            <Button variant="ghost" size="icon">
                                                                <MoreHorizontal className="h-4 w-4" />
                                                            </Button>
                                                        </DropdownMenuTrigger>
                                                        <DropdownMenuContent>
                                                            <DropdownMenuLabel>Action</DropdownMenuLabel>
                                                            <DropdownMenuSeparator />
                                                            <DropdownMenuItem
                                                                onClick={() => router.push(`/all-prompts/edit-prompt/${prompt.id}`)}
                                                            >
                                                                Edit
                                                            </DropdownMenuItem>
                                                            <DropdownMenuItem onClick={() => setDeletePromptId(prompt.id)}>
                                                                Delete
                                                            </DropdownMenuItem>
                                                        </DropdownMenuContent>
                                                    </DropdownMenu>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    ) : (
                                        <TableRow>
                                            <TableCell colSpan={4} className="text-center py-10">
                                                No prompts found. <Button variant="link" onClick={() => router.push('/all-prompts/add-prompt')}>Click here to add</Button>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>

                            </Table>
                        </div>
                        <div className="flex items-center justify-between mt-4">
                            <div className="text-sm text-muted-foreground">
                                0 of {prompts.length} row(s) selected.
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="text-sm text-muted-foreground">
                                    Rows per page
                                </div>
                                <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(parseInt(value))}>
                                    <SelectTrigger className="w-[70px] border-gray-300">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="10">10</SelectItem>
                                        <SelectItem value="20">20</SelectItem>
                                        <SelectItem value="50">50</SelectItem>
                                        <SelectItem value="100">100</SelectItem>
                                    </SelectContent>
                                </Select>
                                <div className="text-sm text-muted-foreground">
                                    Page {currentPage} of {totalPages}
                                </div>
                                <div className="flex items-center space-x-2">
                                    <Button variant="outline" size="icon" onClick={() => handlePageChange(1)} disabled={currentPage === 1}>
                                        <ChevronsLeft className="h-4 w-4" />
                                    </Button>
                                    <Button variant="outline" size="icon" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>
                                        <ChevronLeft className="h-4 w-4" />
                                    </Button>
                                    <Button variant="outline" size="icon" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>
                                        <ChevronRight className="h-4 w-4" />
                                    </Button>
                                    <Button variant="outline" size="icon" onClick={() => handlePageChange(totalPages)} disabled={currentPage === totalPages}>
                                        <ChevronsRight className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Delete Confirmation AlertDialog */}
                        <AlertDialog open={deletePromptId !== null} onOpenChange={() => setDeletePromptId(null)}>
                            <AlertDialogContent className='font-poppins'>
                                <AlertDialogHeader>
                                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                        This action cannot be undone. This will permanently delete the prompt.
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <AlertDialogCancel onClick={() => setDeletePromptId(null)}>Cancel</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => { deletePrompt(deletePromptId!); setDeletePromptId(null); }}>
                                        Yes, Delete
                                    </AlertDialogAction>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
