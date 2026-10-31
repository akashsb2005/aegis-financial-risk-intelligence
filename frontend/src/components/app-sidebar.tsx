import Link from "next/link";

const navigation = [
  { label: "Overview", href: "/dashboard", active: true },
  { label: "Companies", href: null, active: false },
  { label: "Risk assessments", href: null, active: false },
];

export default function AppSidebar() {
  return (
    <>
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white px-5 py-7 md:flex">
        <Brand />
        <p className="mb-3 mt-12 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
          Workspace
        </p>
        <nav aria-label="Main navigation" className="space-y-1">
          {navigation.map((item) =>
            item.href ? (
              <Link
                aria-current={item.active ? "page" : undefined}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium ${
                  item.active
                    ? "bg-[#edf2fa] text-[#203b6b]"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
                }`}
                href={item.href}
                key={item.label}
              >
                <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
                {item.label}
              </Link>
            ) : (
              <span
                aria-disabled="true"
                className="flex cursor-not-allowed items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400"
                key={item.label}
              >
                <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
                {item.label}
              </span>
            ),
          )}
        </nav>
        <div className="mt-auto rounded-xl bg-[#f5f7fb] p-4">
          <p className="text-xs font-semibold text-[#203b6b]">Workspace preview</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">
            Company and assessment views will be connected in a future step.
          </p>
        </div>
      </aside>

      <header className="border-b border-slate-200 bg-white px-5 py-4 md:hidden">
        <div className="flex items-center justify-between gap-4">
          <Brand />
          <nav aria-label="Main navigation" className="flex gap-3 text-xs">
            <Link aria-current="page" className="font-semibold text-[#203b6b]" href="/dashboard">
              Overview
            </Link>
            <span aria-disabled="true" className="text-slate-400">
              Companies
            </span>
            <span aria-disabled="true" className="hidden text-slate-400 sm:inline">
              Assessments
            </span>
          </nav>
        </div>
      </header>
    </>
  );
}

function Brand() {
  return (
    <Link aria-label="AEGIS home" className="inline-flex items-center gap-3" href="/">
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#203b6b] text-sm font-bold text-white">
        A
      </span>
      <span>
        <span className="block text-sm font-bold tracking-[0.16em] text-[#14213d]">AEGIS</span>
        <span className="block text-[9px] tracking-[0.08em] text-slate-400">RISK INTELLIGENCE</span>
      </span>
    </Link>
  );
}
