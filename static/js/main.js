const form = document.getElementById("shorten-form");
const themeButton = document.getElementById("theme-toggle");
const result = document.getElementById("result");
const errorMessage = document.getElementById("errorMsg");
const shortLink = document.getElementById("short-link");
const copyButton = document.getElementById("copy-button");

function setTheme(theme) {
    document.body.classList.toggle("light-mode", theme === "light");
    themeButton.setAttribute(
        "aria-label",
        theme === "light" ? "Switch to dark mode" : "Switch to light mode",
    );
}

setTheme(localStorage.getItem("theme") || "dark");
themeButton.addEventListener("click", () => {
    const nextTheme = document.body.classList.contains("light-mode") ? "dark" : "light";
    localStorage.setItem("theme", nextTheme);
    setTheme(nextTheme);
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMessage.textContent = "";
    result.hidden = true;
    const button = document.getElementById("shortenBtn");
    button.disabled = true;
    button.textContent = "Shortening...";
    try {
        const response = await fetch("/api/shorten", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.fromEntries(new FormData(form))),
        });
        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an unexpected response. Please try again.");
        }
        if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
        shortLink.href = data.short_url;
        shortLink.textContent = data.short_url;
        result.hidden = false;
    } catch (error) {
        errorMessage.textContent = error.message || "Could not reach the server. Please try again.";
    } finally {
        button.disabled = false;
        button.textContent = "Shorten URL";
    }
});

copyButton.addEventListener("click", async () => {
    await navigator.clipboard.writeText(shortLink.href);
    copyButton.textContent = "Copied!";
    setTimeout(() => { copyButton.textContent = "Copy"; }, 1500);
});
