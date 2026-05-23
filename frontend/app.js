document.addEventListener("DOMContentLoaded", () => {
    const profileSelector = document.getElementById("profile-selector");
    const newProfileInput = document.getElementById("new-profile-name");
    const btnCreateProfile = document.getElementById("btn-create-profile");
    
    const promptInput = document.getElementById("prompt-input");
    const btnSendPrompt = document.getElementById("btn-send-prompt");
    const responseOutput = document.getElementById("response-output");
    
    // Carregar Perfis na inicialização
    async function loadProfiles() {
        try {
            const res = await fetch("/api/settings/profiles");
            const data = await res.json();
            
            profileSelector.innerHTML = "";
            data.available_profiles.forEach(prof => {
                const option = document.createElement("option");
                option.value = prof;
                option.textContent = prof;
                if (prof === data.active_profile) option.selected = true;
                profileSelector.appendChild(option);
            });
        } catch (err) {
            console.error("Erro ao carregar perfis:", err);
            profileSelector.innerHTML = '<option>Erro de Conexão</option>';
        }
    }

    // Trocar Perfil
    async function changeProfile(profileName) {
        btnCreateProfile.disabled = true;
        btnCreateProfile.textContent = "Reiniciando...";
        
        try {
            const res = await fetch("/api/settings/profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ profile_name: profileName })
            });
            const data = await res.json();
            if (data.status === "success") {
                newProfileInput.value = "";
                await loadProfiles();
            }
        } catch (err) {
            alert("Erro ao trocar perfil: " + err.message);
        } finally {
            btnCreateProfile.disabled = false;
            btnCreateProfile.textContent = "Criar / Trocar";
        }
    }

    btnCreateProfile.addEventListener("click", () => {
        const newName = newProfileInput.value.trim();
        const selectedName = profileSelector.value;
        const targetProfile = newName !== "" ? newName : selectedName;
        
        if (targetProfile) {
            changeProfile(targetProfile);
        }
    });

    profileSelector.addEventListener("change", () => {
        changeProfile(profileSelector.value);
    });

    // Enviar Prompt
    btnSendPrompt.addEventListener("click", async () => {
        const promptText = promptInput.value.trim();
        if (!promptText) return;

        const routeSelected = document.querySelector('input[name="route"]:checked').value;
        const apiUrl = `/api/ultragemineai/${routeSelected}`;

        // UI Loading State
        btnSendPrompt.disabled = true;
        btnSendPrompt.querySelector("span").textContent = "Gerando...";
        btnSendPrompt.querySelector(".spinner").classList.remove("hidden");
        responseOutput.textContent = "I.A. processando sua solicitação...\nIsso pode levar alguns minutos dependendo do tamanho do prompt.";

        try {
            const res = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: promptText })
            });
            const data = await res.json();
            
            if (res.ok) {
                responseOutput.textContent = data.response;
            } else {
                responseOutput.textContent = `Erro da API: ${data.detail}`;
            }
        } catch (err) {
            responseOutput.textContent = `Erro de Rede: ${err.message}`;
        } finally {
            btnSendPrompt.disabled = false;
            btnSendPrompt.querySelector("span").textContent = "Enviar Prompt";
            btnSendPrompt.querySelector(".spinner").classList.add("hidden");
        }
    });

    // Iniciar
    loadProfiles();
});
