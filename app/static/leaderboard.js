

async function build_leaderboard() {
    const res = await fetch("/api/leaderboard");
    const data = await res.json();
    if (res.ok && data.success) {
        const leaderboardDiv = document.createElement("div");
        leaderboardDiv.id = "leaderboardDiv";

        const list = document.createElement("ol");
        data.leaderboard.forEach(user => {
            const listItem = document.createElement("li");
            listItem.textContent = `${user.username} - ${user.presses} presses`;
            list.appendChild(listItem);
        });
        leaderboardDiv.appendChild(list);
        document.body.appendChild(leaderboardDiv);
    } else {
        alert("Error loading leaderboard: " + data.error);
    }
    
}

build_leaderboard();