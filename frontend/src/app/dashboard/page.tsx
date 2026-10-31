import AppSidebar from "@/components/app-sidebar";

const sections = [
  {
    title: "Company monitoring",
    description: "Company records and monitoring tools will appear here.",
  },
  {
    title: "Risk assessments",
    description: "Assessment workflows and history will appear here.",
  },
  {
    title: "Financial records",
    description: "Financial record summaries will appear here.",
  },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#f5f7fb] md:flex">
      <AppSidebar />
      <div className="min-w-0 flex-1">
        <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8 lg:px-10 lg:py-11">
          <header className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#5471a6]">
              Overview
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[#14213d]">
              Your workspace
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              The AEGIS dashboard shell is ready. Connect the API to view your workspace information.
            </p>
          </header>

          <section aria-label="Dashboard sections" className="grid gap-4 lg:grid-cols-3">
            {sections.map((section) => (
              <article
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40"
                key={section.title}
              >
                <div className="mb-7 flex h-9 w-9 items-center justify-center rounded-lg bg-[#edf2fa]">
                  <span aria-hidden="true" className="h-2 w-2 rounded-full bg-[#5471a6]" />
                </div>
                <h2 className="text-base font-semibold text-[#14213d]">{section.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">{section.description}</p>
                <p className="mt-5 border-t border-slate-100 pt-4 text-xs font-medium text-slate-400">
                  Not connected
                </p>
              </article>
            ))}
          </section>

          <footer className="mt-8 rounded-xl border border-dashed border-slate-300 bg-white/70 px-5 py-6 text-center">
            <p className="text-sm font-medium text-slate-700">No workspace data is loaded.</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">
              This placeholder does not include sample company or risk information.
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
}
