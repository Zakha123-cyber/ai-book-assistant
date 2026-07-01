import "./globals.css";

export const metadata = {
  title: "AI Book Assistant",
  description: "RAG-based assistant for uploaded books.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
