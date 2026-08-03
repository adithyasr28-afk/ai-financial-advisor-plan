import "./globals.css";
import Sidebar from "./components/Sidebar";

export const metadata = {
  title: "Fincast — AI Financial Advisor",
  description:
    "Multi-agent financial research: news, fundamentals, valuation, risk, technicals, portfolio, and macro.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 min-w-0 px-8 py-8 max-w-[1400px]">{children}</main>
        </div>
      </body>
    </html>
  );
}
