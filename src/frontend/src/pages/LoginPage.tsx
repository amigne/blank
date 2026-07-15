import type { FormEvent } from "react";

import "../styles/LoginPage.css";
import logo from "../assets/hero.png";

interface LoginCredentials {
  username: string;
  password: string;
}

export default function LoginPage() {
  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);

    const credentials: LoginCredentials = {
      username: String(formData.get("username") ?? ""),
      password: String(formData.get("password") ?? ""),
    };

    console.log(credentials);
  };

  return (
    <main className="login-page">
      <section className="login-panel login-panel--branding">
        <div className="login-logo-container">
          <img
            className="login-logo"
            src={logo}
            alt="Logo de l’application"
          />
        </div>

        <footer className="login-copyright">
          © 2026, Nom de l’entreprise
        </footer>
      </section>

      <section className="login-panel login-panel--form">
        <div className="login-form-container">
          <h1 className="login-title">Login</h1>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-field">
              <label htmlFor="username">Username</label>

              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">Password</label>

              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
              />
            </div>

            <button className="login-button" type="submit">
              Login
            </button>
          </form>

          <nav className="login-links" aria-label="Account links">
            <a href="/signup">Sign up</a>
            <a href="/lost-password">Lost password?</a>
          </nav>
        </div>
      </section>
    </main>
  );
}