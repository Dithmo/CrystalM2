document.addEventListener("DOMContentLoaded", () => {
    const monsterContainer = document.getElementById("monsterContainer");
    const searchInput = document.getElementById("searchInput");
    const typeFilter = document.getElementById("typeFilter");

    let monstersData = [];

    // Fetch JSON data
    fetch('monsters.json')
        .then(response => response.json())
        .then(data => {
            monstersData = data;
            renderMonsters(data);
        })
        .catch(error => {
            console.error("Error loading monsters:", error);
            monsterContainer.innerHTML = "<p>Error loading monsters data. Please ensure you are running a local web server to fetch JSON.</p>";
        });

    // Render Function
    function renderMonsters(monsters) {
        monsterContainer.innerHTML = "";

        if (monsters.length === 0) {
            monsterContainer.innerHTML = "<p>No monsters found matching your search.</p>";
            return;
        }

        monsters.forEach(monster => {
            const card = document.createElement("article");
            card.classList.add("monster-card");

            // Special styling for known Bosses or deep-dives
            if (monster.type.includes("Boss") || monster.mechanics.length > 0) {
                 card.classList.add("boss-card");
            }

            let html = `
                <h3>${monster.name} <span class="monster-id">#${monster.id}</span></h3>
                <p class="type">Type: ${monster.type}</p>
                <p><strong>Overview:</strong> ${monster.description}</p>
            `;

            if (monster.mechanics && monster.mechanics.length > 0) {
                html += `<h4>Mechanics</h4><ul>`;
                monster.mechanics.forEach(mech => {
                    html += `<li>${mech}</li>`;
                });
                html += `</ul>`;
            }

            html += `<h4>Strategy</h4><p>${monster.strategy}</p>`;

            card.innerHTML = html;
            monsterContainer.appendChild(card);
        });
    }

    // Filter Logic
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedType = typeFilter.value;

        const filtered = monstersData.filter(monster => {
            const matchesSearch = monster.name.toLowerCase().includes(searchTerm) || monster.type.toLowerCase().includes(searchTerm);
            let matchesType = true;

            if (selectedType !== "All") {
                if (selectedType === "Boss") matchesType = monster.type.includes("Boss");
                else if (selectedType === "Unique") matchesType = monster.type.includes("Unique");
                else if (selectedType === "Standard") matchesType = monster.type === "Standard";
            }

            return matchesSearch && matchesType;
        });

        renderMonsters(filtered);
    }

    // Event Listeners
    searchInput.addEventListener("input", applyFilters);
    typeFilter.addEventListener("change", applyFilters);
});