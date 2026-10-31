"use client";

import Link from "next/link";
import { useState } from "react";
import type { FormEvent } from "react";
import { registerAccount } from "@/lib/auth";

export default function RegisterPage() {
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");

    const formData = new FormData(event.currentTarget);
    const fullName = String(formData.get("full_name") ?? "").trim();
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("confirm_password") ?? "");

    if (!fullName || !email || !password || !confirmPassword) {
      setMessage("Complete all fields to create your account.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setMessage("Enter a valid email address.");
      return;
    }
    if (password !== confirmPassword) {
      setMessage("The passwords do not match.");
      return;
    }
    if (password.length < 12 || new TextEncoder().encode(password).length > 72) {
      setMessage("Your password must be between 12 and 72 UTF-8 bytes.");
      return;
    }

    setIsSubmitting(true);
    try {
      await registerAccount(fullName, email, password);
      setIsRegistered(true);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "We could not create your account. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
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
            Start with
            <br />
            a clearer view.
          </h1>
          <p className="mt-6 max-w-md text-base leading-7 text-slate-300">
            Create an AEGIS account to access your financial risk intelligence workspace.
          </p>
          <div className="mt-12 flex items-center gap-3 text-sm text-slate-300">
            <span className="h-px w-10 bg-cyan-300" />
            AEGIS Financial Risk Intelligence
          </div>
        </div>
        <p className="text-xs text-slate-400">Account registration</p>
      </section>

      <section className="flex min-h-screen flex-col px-6 py-8 sm:px-10 lg:px-14">
        <div className="lg:hidden">
          <Brand />
        </div>
        <div className="flex flex-1 items-center justify-center py-12">
          <div className="w-full max-w-md">
            {isRegistered ? (
              <div aria-live="polite" className="rounded-xl border border-emerald-200 bg-white p-6 shadow-sm">
                <p className="text-sm font-semibold text-emerald-700">ACCOUNT CREATED</p>
                <h1 className="mt-3 text-2xl font-semibold tracking-tight text-[#14213d]">
                  You&apos;re registered
                </h1>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Your account was created successfully. Sign in with your new credentials to continue.
                </p>
                <Link
                  className="mt-6 inline-flex w-full items-center justify-center rounded-lg bg-[#203b6b] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#294b84] focus:outline-none focus:ring-4 focus:ring-[#5272ad]/25"
                  href="/"
                >
                  Return to sign in
                </Link>
              </div>
            ) : (
              <>
                <p className="text-sm font-semibold text-[#5471a6]">JOIN AEGIS</p>
                <h1 className="mt-3 text-3xl font-semibold tracking-tight text-[#14213d]">
                  Create your account
                </h1>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Enter your details to register for the AEGIS workspace.
                </p>

                <form className="mt-8 space-y-4" noValidate onSubmit={handleSubmit}>
                  <div>
                    <label htmlFor="full_name" className="mb-2 block text-sm font-medium text-slate-700">
                      Full name
                    </label>
                    <input
                      autoComplete="name"
                      className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                      id="full_name"
                      maxLength={100}
                      name="full_name"
                      placeholder="Your full name"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="register_email" className="mb-2 block text-sm font-medium text-slate-700">
                      Email address
                    </label>
                    <input
                      autoComplete="email"
                      className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                      id="register_email"
                      maxLength={255}
                      name="email"
                      placeholder="name@example.com"
                      required
                      type="email"
                    />
                  </div>
                  <div>
                    <label htmlFor="register_password" className="mb-2 block text-sm font-medium text-slate-700">
                      Password
                    </label>
                    <input
                      autoComplete="new-password"
                      className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                      id="register_password"
                      name="password"
                      placeholder="At least 12 characters"
                      required
                      type="password"
                    />
                  </div>
                  <div>
                    <label htmlFor="confirm_password" className="mb-2 block text-sm font-medium text-slate-700">
                      Confirm password
                    </label>
                    <input
                      autoComplete="new-password"
                      className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                      id="confirm_password"
                      name="confirm_password"
                      placeholder="Re-enter your password"
                      required
                      type="password"
                    />
                  </div>
                  <button
                    className="w-full rounded-lg bg-[#203b6b] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#294b84] focus:outline-none focus:ring-4 focus:ring-[#5272ad]/25 disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={isSubmitting}
                    type="submit"
                  >
                    {isSubmitting ? "Creating account..." : "Create account"}
                  </button>
                  {message && (
                    <p
                      aria-live="polite"
                      className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800"
                      role="alert"
                    >
                      {message}
                    </p>
                  )}
                </form>

                <div className="mt-7 border-t border-slate-200 pt-6 text-center text-sm text-slate-500">
                  Already have an account?{" "}
                  <Link className="font-semibold text-[#294b84] hover:underline" href="/">
                    Sign in
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
        <p className="text-center text-xs text-slate-400">
          Registration creates an account; sign in separately to start a session.
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
