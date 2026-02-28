"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/queue", label: "Patient Queue" },
];

export function Navbar() {
    const pathname = usePathname();

    return (
        <header className="sticky top-0 z-50 h-16 bg-[#0f172a] text-white shadow-lg">
            <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6">
                {/* Logo */}
                <Link href="/dashboard" className="flex items-center gap-2.5">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500 text-sm font-bold">
                        TI
                    </div>
                    <span className="text-lg font-semibold tracking-tight">
                        TraumaInsight
                    </span>
                </Link>

                {/* Nav links */}
                <nav className="hidden items-center gap-1 sm:flex">
                    {links.map((link) => {
                        const active = pathname.startsWith(link.href);
                        return (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${active
                                        ? "bg-white/15 text-white"
                                        : "text-slate-300 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                {link.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* Right side */}
                <div className="flex items-center gap-3">
                    <span className="hidden text-xs text-slate-400 md:block">
                        Metro General Hospital — Trauma Registry
                    </span>
                    <div
                        className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold"
                        aria-label="User avatar"
                    >
                        JD
                    </div>
                </div>
            </div>
        </header>
    );
}
