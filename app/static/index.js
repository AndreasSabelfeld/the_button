// Author: Andreas Sabelfeld
// Date: Tue 19th August 2025

const socket = io(window.location.origin);

const button = document.getElementById("theButton");

const registerOverlay = document.getElementById("registerOverlay");
const usernameInput = document.getElementById("registerUsernameInput");

const loginOverlay = document.getElementById("loginOverlay");
const loginUsernameInput = document.getElementById("loginUsernameInput");
const profileOverlay = document.getElementById("profileOverlay");
const areYouSureOverlay = document.getElementById("areYouSureOverlay");

let userId; 
let currentUsername;

socket.on("update", () => {
    load_presses();
});

document.querySelector('nav a[href="#register"]').addEventListener("click", (e) => {
    e.preventDefault();
    registerOverlay.style.display = "flex";
});

document.getElementById("closeRegisterOverlayBtn").addEventListener("click", () => {
    registerOverlay.style.display = "none";
});

document.getElementById("registerBtn").addEventListener("click", async () => {
    const username = usernameInput.value.trim();
    if (!username) return alert("Please enter a username");

    const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username })
    });

    const data = await res.json();
    if (res.ok && data.success) {
        alert("User registered!");
        showCurrentUser(username);  
        registerOverlay.style.display = "none";
        usernameInput.value = "";
    } else {
        alert("Error: " + data.error);
    }
});

document.querySelector('nav a[href="#login"]').addEventListener("click", (e) => {
    e.preventDefault();
    loginOverlay.style.display = "flex";
});

document.getElementById("closeLoginOverlayBtn").addEventListener("click", () => {
    loginOverlay.style.display = "none";
});

document.getElementById("loginBtn").addEventListener("click", async () => {
    const username = loginUsernameInput.value.trim();
    if (!username) return alert("Please enter a username");

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username })
    });

    const data = await res.json();
    if (data.success) {
        alert("Login successful!");
        showCurrentUser(username);  
        loginOverlay.style.display = "none";
        loginUsernameInput.value = "";
    } else {
        alert("Error: " + data.error);
    }
});

document.querySelector('a[href="#profile"]').addEventListener("click", (e) => {
    e.preventDefault();
    profileOverlay.style.display = "flex";
    getPersonalPresses();
});

document.getElementById("closeProfileOverlayBtn").addEventListener("click", () => {
    profileOverlay.style.display = "none";
});

document.getElementById("deleteAccBtn").addEventListener("click", () => {
    areYouSureOverlay.style.display = "flex";
});

document.getElementById("finalDeleteBtn").addEventListener("click", () => {
    deleteAccount();
    areYouSureOverlay.style.display = "none";
});

document.getElementById("closeSureOverlayBtn").addEventListener("click", () => {
    areYouSureOverlay.style.display = "none";
});

button.addEventListener("click", async () => {
    if (!userId) return alert("Please log in first");

    await fetch(`/press/${userId}`, { method: "POST" });
});

async function deleteAccount() {
    if (!userId) return alert("Please log in first");
    const res = await fetch(`/delete_account/${userId}`, { method: "DELETE" });
    if (res.ok) {
        alert("Account deleted successfully");
        localStorage.removeItem("username");
        localStorage.removeItem("user_id");
        currentUsername = "";
        userId = null;
        document.getElementById("currentUser").textContent = "Not logged in";
        document.getElementById("currentUserOverlay").textContent = "";
        document.getElementById("profileUserId").textContent = "";
        load_presses();
    } else {
        const data = await res.json();
        alert("Error deleting account: " + data.error);
    }
}

async function getPersonalPresses() {
    if (!userId) return alert("Please log in first");

    try {
        const res = await fetch(`/get_user_presses/${userId}`);
        if (!res.ok) throw new Error("Failed to fetch personal clicks");

        const data = await res.json();
        document.getElementById("personalClicks").textContent = data.presses || 0;
    } catch (err) {
        console.error(err);
        alert("Error fetching personal clicks");
    }
}

async function showCurrentUser(username) {
    currentUsername = username; // save the username
    localStorage.setItem("username", username);
    userId = await fetchUserId(username); // fetch user ID asynchronously
    localStorage.setItem("user_id", userId);
    document.getElementById("currentUser").textContent = "Logged in as: " + username;
    document.getElementById("currentUserOverlay").textContent = username;
}

async function fetchUserId(username) {
    try {
        const res = await fetch(`/get_user_id/${encodeURIComponent(username)}`);
        if (!res.ok) throw new Error("User not found");

        const data = await res.json();
        return data.id; // this is the user ID
    } catch (err) {
        console.error(err);
        return null;
    }
}

async function load_presses() {
    const res = await fetch("/num");
    const data = await res.json();

    const container = document.getElementById("num");
    container.textContent = data.total_presses;
}

userId = localStorage.getItem("user_id") || null;
currentUsername = localStorage.getItem("username") || "";
showCurrentUser(currentUsername);

load_presses();

