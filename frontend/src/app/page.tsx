"use client";

import Link from "next/link";
import { useState } from "react";
import type { FormEvent } from "react";

export default function LoginPage() {
  const [message, setMessage] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Sign-in is not connected yet. Authentication will be added in a later step.");
  }

  return (
    <main className="grid min-h-screen bg-[#f5f7fb] lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden overflow-hidden bg-[#101c36] px-12 py-10 text-white lg:flex lg:flex-col lg:justify-between xl:px-20">
        <div className="absolute -right-32 -top-32 h-96 w-96 rounded-full border border-white/10" />
        <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full border border-white/10" />
        <Brand />
        <div className="relative max-w-xl pb-16">
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
            Financial risk intelligence
          </p>
          <h1 className="text-5xl font-semibold leading-[1.12] tracking-tight xl:text-6xl">
            Clarity for
            <br />
            complex risk.
          </h1>
          <p className="mt-6 max-w-md text-base leading-7 text-slate-300">
            A focused workspace for company financial records and risk assessments.
          </p>
          <div className="mt-12 flex items-center gap-3 text-sm text-slate-300">
            <span className="h-px w-10 bg-cyan-300" />
            AEGIS Financial Risk Intelligence
          </div>
        </div>
        <p className="text-xs text-slate-400">Application preview</p>
      </section>

      <section className="flex min-h-screen flex-col px-6 py-8 sm:px-10 lg:px-14">
        <div className="lg:hidden">
          <Brand />
        </div>
        <div className="flex flex-1 items-center justify-center py-12">
          <div className="w-full max-w-md">
            <p className="text-sm font-semibold text-[#5471a6]">WELCOME TO AEGIS</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-[#14213d]">
              Sign in to your account
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Access to the AEGIS workspace will be available when authentication is connected.
            </p>

            <form className="mt-9 space-y-5" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="email" className="mb-2 block text-sm font-medium text-slate-700">
                  Email address
                </label>
                <input
                  autoComplete="email"
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                  id="email"
                  name="email"
                  placeholder="name@example.com"
                  required
                  type="email"
                />
              </div>
              <div>
                <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-700">
                  Password
                </label>
                <input
                  autoComplete="current-password"
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  required
                  type="password"
                />
              </div>
              <button
                className="w-full rounded-lg bg-[#203b6b] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#294b84] focus:outline-none focus:ring-4 focus:ring-[#5272ad]/25"
                type="submit"
              >
                Sign in
              </button>
              {message && (
                <p aria-live="polite" className="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
                  {message}
                </p>
              )}
            </form>

            <div className="mt-8 border-t border-slate-200 pt-6 text-center text-sm text-slate-500">
              Exploring the interface?{" "}
              <Link className="font-semibold text-[#294b84] hover:underline" href="/dashboard">
                View the dashboard
              </Link>
            </div>
          </div>
        </div>
        <p className="text-center text-xs text-slate-400">
          Secure access and API integration are not configured in this preview.
        </p>
      </section>
    </main>
  );
}

function Brand() {
  return (
    <Link aria-label="AEGIS home" className="relative inline-flex items-center gap-3" href="/">
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-300 text-sm font-bold tracking-wide text-[#14213d]">
        A
      </span>
      <span>
        <span className="block text-lg font-bold tracking-[0.18em]">AEGIS</span>
        <span className="block text-[10px] tracking-[0.11em] text-slate-400">
          RISK INTELLIGENCE
        </span>
      </span>
    </Link>
  );
}
