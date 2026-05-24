document.addEventListener("DOMContentLoaded", () => {
    const profileSelector = document.getElementById("profile-selector");
    const newProfileInput = document.getElementById("new-profile-name");
    const btnCreateProfile = document.getElementById("btn-create-profile");
    const btnDeleteProfile = document.getElementById("btn-delete-profile");
    const btnLoginProfile = document.getElementById("btn-login-profile");
    
    const promptInput = document.getElementById("prompt-input");
    const btnSendPrompt = document.getElementById("btn-send-prompt");
    const responseOutput = document.getElementById("response-output");
    const loginStatusBadge = document.getElementById("login-status-badge");
    
    function updateLoginBadge(isLoggedIn) {
        loginStatusBadge.style.display = "inline-block";
        if (isLoggedIn) {
            loginStatusBadge.textContent = "Logado ✅";
            loginStatusBadge.style.background = "#d4edda";
            loginStatusBadge.style.color = "#155724";
        } else {
            loginStatusBadge.textContent = "Deslogado ❌";
            loginStatusBadge.style.background = "#f8d7da";
            loginStatusBadge.style.color = "#721c24";
        }
    }
    
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
            
            if (data.active_profile) {
                updateLoginBadge(data.is_logged_in);
            }
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
                updateLoginBadge(data.is_logged_in);
            }
        } catch (err) {
            alert("Erro ao trocar perfil: " + err.message);
        } finally {
            btnCreateProfile.disabled = false;
            btnCreateProfile.textContent = "Criar / Trocar";
        }
    }

    btnCreateProfile.addEventListener("click", async () => {
        let newName = newProfileInput.value.trim();
        if (!newName) return;
        
        // Garante que o nome tenha o prefixo correto para ser reconhecido pelo backend
        if (!newName.startsWith("chrome_profile")) {
            newName = "chrome_profile_" + newName;
        }
        
        btnCreateProfile.disabled = true;
        btnCreateProfile.textContent = "Criando...";
        
        try {
            const res = await fetch("/api/settings/profile/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ profile_name: newName })
            });
            const data = await res.json();
            
            if (res.ok && data.status === "success") {
                newProfileInput.value = "";
                await loadProfiles();
                profileSelector.value = newName;
                changeProfile(newName); // Ativa o perfil que acabou de ser criado
            } else {
                alert(`Erro ao criar perfil: ${data.detail || data.message}`);
            }
        } catch (err) {
            alert(`Erro de rede: ${err.message}`);
        } finally {
            btnCreateProfile.disabled = false;
            btnCreateProfile.textContent = "Criar Novo Perfil";
        }
    });

    btnLoginProfile.addEventListener("click", async () => {
        const targetProfile = profileSelector.value;
        if (!targetProfile || targetProfile === "loading") return;
        
        btnLoginProfile.disabled = true;
        btnLoginProfile.textContent = "Aguardando login no navegador...";
        
        try {
            const res = await fetch(`/api/settings/login/${targetProfile}`, {
                method: "POST"
            });
            const data = await res.json();
            
            if (res.ok) {
                alert(data.message);
                await loadProfiles(); // Reload to update login status
            } else {
                alert(`Erro ao logar: ${data.detail}`);
            }
        } catch (err) {
            alert(`Erro de rede: ${err.message}`);
        } finally {
            btnLoginProfile.disabled = false;
            btnLoginProfile.textContent = "Fazer Login (Abrir Chrome)";
        }
    });

    btnDeleteProfile.addEventListener("click", async () => {
        const targetProfile = profileSelector.value;
        if (!targetProfile || targetProfile === "loading") return;
        
        if (!confirm(`Tem certeza que deseja EXCLUIR o perfil: ${targetProfile}? Isso apagará a pasta permanentemente.`)) {
            return;
        }
        
        btnDeleteProfile.disabled = true;
        btnDeleteProfile.textContent = "Excluindo...";
        try {
            const res = await fetch(`/api/settings/profile/${targetProfile}`, {
                method: "DELETE"
            });
            const data = await res.json();
            
            if (res.ok) {
                alert(data.message);
                await loadProfiles();
            } else {
                alert(`Erro: ${data.detail}`);
            }
        } catch (err) {
            alert(`Erro de rede: ${err.message}`);
        } finally {
            btnDeleteProfile.disabled = false;
            btnDeleteProfile.textContent = "Excluir Perfil Selecionado";
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
