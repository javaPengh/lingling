import { useState } from "react";
import type { LoginResponse } from "@shared/api";
import { Learning } from "./pages/Learning";
import { LoginPage } from "./pages/LoginPage";
import { Report } from "./pages/Report";

/** 灵灵前端应用入口：未登录时显示登录页，登录后按账号角色分流。 */
export function App() {
  const [session, setSession] = useStateWithStorage();

  if (session === null) {
    return <LoginPage onLogin={setSession} />;
  }

  return <RoleWorkspace session={session} onLogout={() => setSession(null)} />;
}

function useStateWithStorage(): [LoginResponse | null, (value: LoginResponse | null, remember?: boolean) => void] {
  const [session, setSessionState] = useLocalSession();

  function setSession(value: LoginResponse | null, remember = true) {
    setSessionState(value);
    if (value === null) {
      window.localStorage.removeItem("lingling_login_session");
      return;
    }
    if (!remember) {
      window.localStorage.removeItem("lingling_login_session");
      return;
    }
    window.localStorage.setItem("lingling_login_session", JSON.stringify(value));
  }

  return [session, setSession];
}

function useLocalSession(): [LoginResponse | null, (value: LoginResponse | null) => void] {
  return useState<LoginResponse | null>(() => {
    const stored = window.localStorage.getItem("lingling_login_session");
    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored) as LoginResponse;
    } catch {
      window.localStorage.removeItem("lingling_login_session");
      return null;
    }
  });
}

interface RoleWorkspaceProps {
  /** 登录接口返回的账号、角色和学生范围。 */
  session: LoginResponse;

  /** 退出当前演示账号，回到登录页。 */
  onLogout: () => void;
}

/** 登录后的角色工作区，学生进入学习页，家长/老师进入报告页。 */
function RoleWorkspace({ session, onLogout }: RoleWorkspaceProps) {
  const account = session.account;
  const primaryStudent = session.students[0] ?? null;
  const isStudent = account.role === "student";
  const isTeacher = account.role === "teacher";
  const title = isStudent ? "学生学习界面" : isTeacher ? "老师报告视角" : "家长报告视角";
  const subtitle = isStudent
    ? `${primaryStudent?.name ?? account.displayName}，欢迎回来。`
    : `${account.displayName} · 可查看 ${session.students.length} 位学生`;

  return (
    <main className="min-h-screen bg-[#fbf5ec] text-ink">
      <header className="border-b border-[#eaded4] bg-white/70 px-6 py-4 backdrop-blur sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-[#c97b5a]">Lingling V0.1</p>
            <h1 className="text-2xl font-semibold text-[#3d342b]">{title}</h1>
            <p className="mt-1 text-sm text-[#7c7064]">{subtitle}</p>
          </div>
          <button
            className="rounded-xl border border-[#eaded4] bg-white px-4 py-2 text-sm font-semibold text-[#7c7064] transition hover:border-[#c97b5a] hover:text-[#b5654a]"
            onClick={onLogout}
            type="button"
          >
            切换账号
          </button>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-6 sm:px-8">
        {isStudent ? (
          <Learning student={primaryStudent} />
        ) : (
          <Report role={isTeacher ? "teacher" : "parent"} students={session.students} />
        )}
      </section>
    </main>
  );
}
