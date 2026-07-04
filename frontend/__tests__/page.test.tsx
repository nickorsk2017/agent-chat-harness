import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Welcome page", () => {
  it("renders the Welcome heading", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: /welcome/i })
    ).toBeInTheDocument();
  });
});
