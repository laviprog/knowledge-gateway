import { ThemeProvider } from "next-themes";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "@/App";
import "@/index.css";

// biome-ignore lint/style/noNonNullAssertion: the #root element always exists in index.html
createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<ThemeProvider
			attribute="class"
			defaultTheme="system"
			enableSystem
			disableTransitionOnChange
		>
			<App />
		</ThemeProvider>
	</StrictMode>,
);
