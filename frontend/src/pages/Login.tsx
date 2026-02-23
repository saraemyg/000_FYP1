import { useState } from "react";
import { useNavigate } from "react-router-dom";
import LoginForm from "../components/Auth/LoginForm";
import Logo from "../components/Auth/Logo";

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  const handleSubmit = (username: string, password: string) => {
    if (username === "admin" && password === "admin123") {
      onLogin();
      navigate("/security-cam");
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* ===== Gradient Background ===== */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950" />

      {/* ===== Soft Glow Effects ===== */}
      <div className="absolute top-[-150px] left-[-150px] w-[400px] h-[400px] bg-blue-600/30 rounded-full blur-3xl" />
      <div className="absolute bottom-[-150px] right-[-150px] w-[400px] h-[400px] bg-indigo-600/30 rounded-full blur-3xl" />

      {/* ===== Login Card ===== */}
      <div className="relative z-10 w-full max-w-md px-6">
        <div className="bg-white/10 backdrop-blur-2xl border border-white/20 shadow-2xl rounded-2xl p-10">
          <div className="flex justify-center mb-6">
            <Logo />
          </div>

          <h2 className="text-2xl font-bold text-center text-white mb-2">
            Log In
          </h2>

          <p className="text-sm text-center text-gray-300 mb-6">
            ! Safety is important !
          </p>

          <LoginForm onSubmit={handleSubmit} error={error} />

          <p className="text-xs text-center text-gray-400 mt-6">
            © FYP1 Prototype
          </p>
        </div>
      </div>
    </div>
  );
}
