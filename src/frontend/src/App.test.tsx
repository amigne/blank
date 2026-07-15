import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

describe("App", () => {
  it("renders the main heading", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: /get started/i }),
    ).toBeInTheDocument();
  });

  it("renders all section headings", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: /documentation/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /connect with us/i }),
    ).toBeInTheDocument();
  });

  it("renders the counter button and increments on click", async () => {
    render(<App />);

    const button = screen.getByRole("button", { name: /count is 0/i });
    expect(button).toBeInTheDocument();

    await userEvent.click(button);
    expect(button).toHaveTextContent("Count is 1");

    await userEvent.click(button);
    expect(button).toHaveTextContent("Count is 2");
  });

  it("renders navigation links with correct href and security attributes", () => {
    render(<App />);

    const links = [
      { name: /explore vite/i, href: "https://vite.dev/" },
      { name: /learn more/i, href: "https://react.dev/" },
      { name: /github/i, href: "https://github.com/vitejs/vite" },
      { name: /discord/i, href: "https://chat.vite.dev/" },
      { name: /x\.com/i, href: "https://x.com/vite_js" },
      { name: /bluesky/i, href: "https://bsky.app/profile/vite.dev" },
    ];

    for (const { name, href } of links) {
      const link = screen.getByRole("link", { name });
      expect(link).toHaveAttribute("href", href);
      expect(link).toHaveAttribute("target", "_blank");
      expect(link).toHaveAttribute("rel", "noopener noreferrer");
    }
  });

  it("renders images with appropriate alt text", () => {
    render(<App />);
    expect(screen.getByAltText("React logo")).toBeInTheDocument();
    expect(screen.getByAltText("Vite logo")).toBeInTheDocument();
  });
});