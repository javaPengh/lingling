// 登录页组件：按 docs/登录页.html 原型实现，并提交账号密码到后端认证接口。
import { FormEvent, useState } from "react";
import type { LoginResponse } from "@shared/api";
import { login } from "../api/client";

interface LoginPageProps {
  /** 登录成功后把后端返回的角色分流结果交给应用入口。 */
  onLogin: (session: LoginResponse, remember: boolean) => void;
}

/** 根据登录页原型实现的账号密码登录入口。 */
export function LoginPage({ onLogin }: LoginPageProps) {
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!account.trim() || !password) {
      setError("请输入账号和密码。");
      return;
    }

    setStatus("submitting");
    try {
      const session = await login({ account: account.trim(), password });
      onLogin(session, remember);
    } catch {
      setError("账号或密码不正确，请检查后再试。");
    } finally {
      setStatus("idle");
    }
  }

  const isSubmitting = status === "submitting";

  return (
    <div className="flex min-h-screen bg-[#fbf5ec] text-[#3d342b]">
      <aside className="relative hidden w-[44%] shrink-0 overflow-hidden bg-gradient-to-br from-[#cd7e5c] to-[#b5654a] px-[60px] py-14 text-[#fcf3ea] lg:flex lg:flex-col">
        <div className="absolute -right-[150px] -top-[130px] h-[420px] w-[420px] rounded-full bg-white/10" />
        <div className="absolute -bottom-[90px] -left-[110px] h-[280px] w-[280px] rounded-full bg-white/[0.07]" />

        <div className="relative z-10 flex items-center gap-[13px]">
          <BrandMark />
          <span className="text-[26px] font-extrabold tracking-[0.01em]">灵灵老师</span>
        </div>

        <div className="relative z-10 mt-auto">
          <p className="mb-5 text-[13px] font-semibold uppercase tracking-[0.22em] opacity-80">
            WELCOME BACK
          </p>
          <h1 className="m-0 font-serif text-[40px] font-semibold leading-[1.36]">
            欢迎回来，
            <br />
            继续今天的学习
          </h1>
          <p className="mt-[22px] max-w-[330px] text-base leading-[1.75] opacity-90">
            登录灵灵老师，按你的节奏，把每一步走稳。
          </p>
        </div>

        <p className="relative z-10 mt-10 text-[13px] opacity-70">
          © 2026 灵灵老师 · 让学习更懂你
        </p>
      </aside>

      <main className="flex flex-1 items-center justify-center px-6 py-8 sm:px-12">
        <section className="w-full max-w-[380px]">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <BrandMark compact />
            <span className="text-[22px] font-extrabold">灵灵老师</span>
          </div>

          <h2 className="m-0 text-[27px] font-bold tracking-[0.01em]">登录</h2>
          <p className="mb-9 mt-2.5 text-[15px] text-[#7c7064]">输入你的账号和密码以继续</p>

          <form noValidate onSubmit={handleSubmit}>
            <div className="mb-5">
              <label className="mb-[9px] block text-[13.5px] font-semibold" htmlFor="account">
                账号
              </label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 flex -translate-y-1/2 text-[#a89c8e]">
                  <UserIcon />
                </span>
                <input
                  autoComplete="username"
                  className="h-[52px] w-full rounded-[14px] border border-[rgba(61,52,43,0.12)] bg-[#fbf6ef] px-4 pl-[46px] text-[15px] text-[#3d342b] outline-none transition placeholder:text-[#a89c8e] focus:border-[#c97b5a] focus:bg-white focus:shadow-[0_0_0_4px_rgba(201,123,90,0.22)]"
                  id="account"
                  name="account"
                  onChange={(event) => setAccount(event.target.value)}
                  placeholder="用户名 / 手机号"
                  type="text"
                  value={account}
                />
              </div>
            </div>

            <div className="mb-5">
              <label className="mb-[9px] block text-[13.5px] font-semibold" htmlFor="password">
                密码
              </label>
              <div className="relative">
                <span className="pointer-events-none absolute left-4 top-1/2 flex -translate-y-1/2 text-[#a89c8e]">
                  <LockIcon />
                </span>
                <input
                  autoComplete="current-password"
                  className="h-[52px] w-full rounded-[14px] border border-[rgba(61,52,43,0.12)] bg-[#fbf6ef] px-12 pl-[46px] text-[15px] text-[#3d342b] outline-none transition placeholder:text-[#a89c8e] focus:border-[#c97b5a] focus:bg-white focus:shadow-[0_0_0_4px_rgba(201,123,90,0.22)]"
                  id="password"
                  name="password"
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="请输入密码"
                  type={showPassword ? "text" : "password"}
                  value={password}
                />
                <button
                  aria-label={showPassword ? "隐藏密码" : "显示密码"}
                  className="absolute right-2 top-1/2 flex -translate-y-1/2 rounded-lg p-2 text-[#a89c8e] transition hover:text-[#7c7064]"
                  onClick={() => setShowPassword((value) => !value)}
                  type="button"
                >
                  <EyeIcon off={showPassword} />
                </button>
              </div>
            </div>

            <div className="mb-7 mt-1 flex items-center justify-between">
              <label className="flex cursor-pointer select-none items-center gap-[9px] text-[13.5px] text-[#7c7064]">
                <input
                  checked={remember}
                  className="sr-only"
                  onChange={(event) => setRemember(event.target.checked)}
                  type="checkbox"
                />
                <span
                  className={`flex h-[19px] w-[19px] items-center justify-center rounded-md border transition ${
                    remember
                      ? "border-[#c97b5a] bg-[#c97b5a]"
                      : "border-[rgba(61,52,43,0.12)] bg-[#fbf6ef]"
                  }`}
                >
                  {remember && <CheckIcon />}
                </span>
                记住我
              </label>
              <button className="text-[13.5px] font-semibold text-[#c97b5a] hover:text-[#b5654a]" type="button">
                忘记密码?
              </button>
            </div>

            {error && (
              <p className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </p>
            )}

            <button
              className="flex h-[53px] w-full items-center justify-center gap-[9px] rounded-[14px] bg-[#c97b5a] text-base font-bold tracking-[0.02em] text-white shadow-[0_12px_26px_rgba(201,123,90,0.32)] transition hover:-translate-y-px hover:bg-[#b5654a] hover:shadow-[0_16px_32px_rgba(201,123,90,0.38)] disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
              disabled={isSubmitting}
              type="submit"
            >
              {isSubmitting ? "正在登录…" : "登录"}
              {!isSubmitting && <span className="transition group-hover:translate-x-1">→</span>}
            </button>
          </form>

          <div className="mt-[26px] flex gap-[9px] rounded-xl border border-[rgba(61,52,43,0.07)] bg-[#fbf6ef] px-4 py-[13px] text-[12.5px] leading-6 text-[#7c7064]">
            <InfoIcon />
            <span>
              演示环境 · 可用账号 <b className="font-semibold text-[#3d342b]">xiaoyu</b> /{" "}
              <b className="font-semibold text-[#3d342b]">parent_xiaoyu</b> /{" "}
              <b className="font-semibold text-[#3d342b]">teacher_wang</b>，密码均为{" "}
              <b className="font-semibold text-[#3d342b]">123456</b>。
            </span>
          </div>

          <div className="mt-7 text-center text-[13.5px] text-[#a89c8e]">
            还没有账号?{" "}
            <button className="font-semibold text-[#c97b5a] hover:text-[#b5654a]" type="button">
              联系老师开通
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <span
      className={`relative shrink-0 rounded-full ${
        compact
          ? "h-[34px] w-[34px] bg-[radial-gradient(120%_120%_at_35%_30%,#e8b68a_0%,#c97b5a_70%)] after:bg-[#fbf5ec]"
          : "h-[38px] w-[38px] bg-white/95 after:bg-[#c97b5a]"
      } after:absolute after:bottom-[7px] after:right-1.5 after:h-[13px] after:w-[13px] after:rounded-full`}
    />
  );
}

function UserIcon() {
  return (
    <svg fill="none" height="18" viewBox="0 0 24 24" width="18" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
      <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg fill="none" height="18" viewBox="0 0 24 24" width="18" xmlns="http://www.w3.org/2000/svg">
      <rect height="11" rx="2" stroke="currentColor" strokeWidth="1.8" width="18" x="3" y="11" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
    </svg>
  );
}

function EyeIcon({ off }: { off: boolean }) {
  if (off) {
    return (
      <svg fill="none" height="19" viewBox="0 0 24 24" width="19" xmlns="http://www.w3.org/2000/svg">
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c6.5 0 10 7 10 7a13.2 13.2 0 0 1-2.16 2.83" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
        <path d="M6.6 6.6A13.5 13.5 0 0 0 2 11s3.5 7 10 7a9 9 0 0 0 4.4-1.1" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
        <line stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" x1="2" x2="22" y1="2" y2="22" />
      </svg>
    );
  }

  return (
    <svg fill="none" height="19" viewBox="0 0 24 24" width="19" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg fill="none" height="12" viewBox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
      <polyline points="20 6 9 17 4 12" stroke="#fff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg className="mt-px shrink-0" fill="none" height="16" viewBox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 16v-4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
      <path d="M12 8h.01" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
    </svg>
  );
}
