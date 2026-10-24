
const API_URL = "http://127.0.0.1:8000";

const taskList = document.getElementById("task-list");
const taskSearchInput = document.getElementById("task-search-input");
const taskStatusFilter = document.getElementById("task-status-filter");

const taskForm = document.getElementById("task-form");
const addTaskButton = document.getElementById("add-task-button");
const deadlineInput = document.getElementById("taskDeadline");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const chatStatus = document.getElementById("chat-status");
const chatSubmit = document.getElementById("chat-submit");
const editTaskModal = document.getElementById("edit-task-modal");
const editTaskForm = document.getElementById("edit-task-form");
const editTaskId = document.getElementById("edit-task-id");
const editTaskTitle = document.getElementById("edit-task-title");
const editTaskDescription = document.getElementById("edit-task-description");
const editTaskDeadline = document.getElementById("editTaskDeadline");
const editTaskStatus = document.getElementById("edit-task-status");
const saveEditTaskButton = document.getElementById("save-edit-task");

const closeEditModalButton = document.getElementById("close-edit-modal");
const cancelEditModalButton = document.getElementById("cancel-edit-modal");

let allTasks = [];

const toastContainer = document.getElementById("toast-container");
const TOAST_DURATION = 5000;

// Semua form di halaman ini diproses lewat JavaScript.
// Blokir submit native browser agar halaman tidak melakukan reload.
document.addEventListener(
    "submit",
    (event) => {
        event.preventDefault();
    },
    true
);

function showToast(message, type = "success") {
    if (!toastContainer) {
        console.error("Elemen #toast-container tidak ditemukan.");
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icon = document.createElement("span");
    icon.className = "toast-icon";
    icon.textContent = type === "success" ? "✓" : "!";

    const content = document.createElement("div");
    content.className = "toast-content";

    const title = document.createElement("p");
    title.className = "toast-title";
    title.textContent =
        type === "success" ? "Berhasil" : "Terjadi kesalahan";

    const text = document.createElement("p");
    text.className = "toast-message";
    text.textContent = message;

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "toast-close";
    closeButton.textContent = "×";
    closeButton.setAttribute("aria-label", "Tutup notifikasi");

    content.append(title, text);
    toast.append(icon, content, closeButton);
    toastContainer.appendChild(toast);

    let timeoutId = null;
    let remainingTime = TOAST_DURATION;
    let timerStartedAt = Date.now();

    function removeToast() {
        if (timeoutId !== null) {
            clearTimeout(timeoutId);
        }
        toast.remove();
    }

    function startToastTimer() {
        timerStartedAt = Date.now();
        timeoutId = setTimeout(removeToast, remainingTime);
    }

    function pauseToastTimer() {
        if (timeoutId === null) return;

        clearTimeout(timeoutId);
        timeoutId = null;
        remainingTime = Math.max(
            0,
            remainingTime - (Date.now() - timerStartedAt)
        );
    }

    closeButton.addEventListener("click", () => {
        removeToast();
    });

    toast.addEventListener("mouseenter", pauseToastTimer);
    toast.addEventListener("mouseleave", () => {
        if (remainingTime > 0) {
            startToastTimer();
        }
    });

    startToastTimer();
}

// ========================
// STATISTIK TUGAS
// ========================

function updateTaskStatistics(tasks) {
    const counts = {
        total: tasks.length,
        pending: 0,
        in_progress: 0,
        completed: 0,
    };

    tasks.forEach((task) => {
        const status = String(task.status || "")
            .trim()
            .toLowerCase();

        if (Object.prototype.hasOwnProperty.call(counts, status)) {
            counts[status]++;
        }
    });

    document.getElementById("total-tasks").textContent = counts.total;
    document.getElementById("pending-tasks").textContent = counts.pending;
    document.getElementById("in-progress-tasks").textContent =
        counts.in_progress;
    document.getElementById("completed-tasks").textContent =
        counts.completed;
}

function formatDeadline(deadline) {
    if (!deadline) {
        return "Belum ditentukan";
    }

    const date = new Date(deadline);

    if (Number.isNaN(date.getTime())) {
        return "Format deadline tidak valid";
    }

    return date.toLocaleString("id-ID", {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

// ========================
// MEMUAT DATA TUGAS
// ========================

async function loadTasks() {
    taskList.replaceChildren();

    const loadingMessage = document.createElement("p");
    loadingMessage.textContent = "Memuat daftar tugas...";
    taskList.appendChild(loadingMessage);

    try {
        const response = await fetch(`${API_URL}/tasks`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const tasks = await response.json();

        if (!Array.isArray(tasks)) {
            throw new Error("Format data tugas tidak valid.");
        }

        allTasks = tasks;

        updateTaskStatistics(allTasks);
        renderTasks();
    } catch (error) {
        console.error("Gagal mengambil daftar tugas:", error);

        allTasks = [];
        updateTaskStatistics([]);

        taskList.replaceChildren();

        const errorMessage = document.createElement("p");
        errorMessage.textContent =
            "Gagal memuat tugas. Periksa apakah backend berjalan dan koneksi API tersedia.";

        taskList.appendChild(errorMessage);
    }
}

// ========================
// PENCARIAN DAN FILTER
// ========================

function renderTasks() {
    taskList.replaceChildren();

    const keyword = taskSearchInput.value.trim().toLowerCase();
    const selectedStatus = taskStatusFilter.value;

    const filteredTasks = allTasks.filter((task) => {
        const title = String(task.title || "").toLowerCase();
        const description = String(task.description || "").toLowerCase();
        const status = String(task.status || "pending")
            .trim()
            .toLowerCase();

        const matchesKeyword =
            title.includes(keyword) ||
            description.includes(keyword);

        const matchesStatus =
            selectedStatus === "all" ||
            status === selectedStatus;

        return matchesKeyword && matchesStatus;
    });

    if (filteredTasks.length === 0) {
        const emptyMessage = document.createElement("p");

        emptyMessage.textContent = allTasks.length === 0
            ? "Belum ada tugas. Silakan tambahkan tugas baru."
            : "Tidak ada tugas yang cocok dengan pencarian atau filter.";

        taskList.appendChild(emptyMessage);
        return;
    }

    filteredTasks.forEach((task) => {
        const card = document.createElement("article");
        card.className = "task-card";

        const header = document.createElement("div");
        header.className = "task-header";

        const title = document.createElement("h3");
        title.textContent = task.title || "Tanpa judul";

        const status = document.createElement("span");
        const taskStatus = String(task.status || "pending")
            .trim()
            .toLowerCase();

        const statusLabels = {
            pending: "Menunggu",
            in_progress: "Berlangsung",
            completed: "Selesai",
        };

        status.className = `task-status status-${taskStatus}`;
        status.textContent = statusLabels[taskStatus] || taskStatus;

        header.append(title, status);

        const description = document.createElement("p");
        description.textContent =
            task.description || "Tidak ada deskripsi.";

        const taskId = document.createElement("small");
        taskId.textContent = `ID tugas: ${task.id}`;

        const deadlineElement = document.createElement("p");
        deadlineElement.textContent = `Deadline: ${formatDeadline(task.deadline)}`;
        deadlineElement.className = "task-deadline";

        const actions = document.createElement("div");
        actions.className = "task-actions";

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.className = "edit-button";

        editButton.addEventListener("click", () => {
            openEditModal(task);
        });

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Hapus";
        deleteButton.className = "delete-button";

        deleteButton.addEventListener("click", () => {
            deleteTask(task.id);
        });

        actions.append(editButton, deleteButton);
        card.append(header, description, deadlineElement, taskId, actions);
        taskList.appendChild(card);
    });
}

taskSearchInput.addEventListener("input", renderTasks);
taskStatusFilter.addEventListener("change", renderTasks);

// ========================
// TAMBAH TUGAS
// ========================

async function handleAddTask(event) {
    event.preventDefault();

    const titleInput = document.getElementById("title");
    const descriptionInput = document.getElementById("description");

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const deadline = deadlineInput.value || null;

    if (!title) {
        alert("Judul tugas wajib diisi.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/tasks`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                title,
                description: description || null,
                deadline,
            }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Gagal menambahkan tugas."
            );
        }

        taskForm.reset();
        await loadTasks();
        showToast("Tugas berhasil ditambahkan.");
    } catch (error) {
        console.error("Gagal menambahkan tugas:", error);
        showToast(
            error.message || "Gagal menambahkan tugas.",
            "error"
        );
    }
}

taskForm.addEventListener("submit", handleAddTask);
addTaskButton.addEventListener("click", handleAddTask);

// ========================
// EDIT TUGAS
// ========================


function openEditModal(task) {
    editTaskId.value = task.id;
    editTaskTitle.value = task.title || "";
    editTaskDescription.value = task.description || "";
    editTaskDeadline.value = task.deadline
        ? task.deadline.replace(" ", "T").slice(0, 16)
        : "";
    editTaskStatus.textContent = "";

    editTaskModal.hidden = false;
    editTaskModal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");

    editTaskTitle.focus();
}

function closeEditModal() {
    editTaskModal.hidden = true;
    editTaskModal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");

    editTaskForm.reset();
    editTaskStatus.textContent = "";
    saveEditTaskButton.disabled = false;
    saveEditTaskButton.textContent = "Simpan perubahan";
}

closeEditModalButton.addEventListener("click", closeEditModal);
cancelEditModalButton.addEventListener("click", closeEditModal);

editTaskModal.addEventListener("click", (event) => {
    if (event.target === editTaskModal) {
        closeEditModal();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !editTaskModal.hidden) {
        closeEditModal();
    }
});

async function handleEditTask(event) {
    event.preventDefault();

    const taskId = editTaskId.value;
    const title = editTaskTitle.value.trim();
    const description = editTaskDescription.value.trim();
    const deadline = editTaskDeadline.value || null;

    if (!title) {
        editTaskStatus.textContent = "Judul tugas wajib diisi.";
        editTaskTitle.focus();
        return;
    }

    saveEditTaskButton.disabled = true;
    saveEditTaskButton.textContent = "Menyimpan...";
    editTaskStatus.textContent = "Sedang menyimpan perubahan...";

    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                title,
                description: description || null,
                deadline,
            }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Gagal memperbarui tugas."
            );
        }

        closeEditModal();
        await loadTasks();
        showToast("Perubahan tugas berhasil disimpan.");
    } catch (error) {
        console.error("Gagal mengedit tugas:", error);

        editTaskStatus.textContent =
            error.message || "Terjadi kesalahan saat mengedit tugas.";

        saveEditTaskButton.disabled = false;
        saveEditTaskButton.textContent = "Simpan perubahan";
    }
}

editTaskForm.addEventListener("submit", handleEditTask);
saveEditTaskButton.addEventListener("click", handleEditTask);

// ========================
// HAPUS TUGAS
// ========================

async function deleteTask(taskId) {
    const confirmed = confirm(
        `Apakah kamu yakin ingin menghapus tugas dengan ID ${taskId}?`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/tasks/${taskId}`,
            {
                method: "DELETE",
            }
        );

        if (!response.ok) {
            let errorMessage = "Gagal menghapus tugas.";

            try {
                const result = await response.json();
                errorMessage = result.detail || errorMessage;
            } catch {
                // Gunakan pesan default jika respons bukan JSON.
            }

            throw new Error(errorMessage);
        }

        await loadTasks();
        showToast("Tugas berhasil dihapus!");
    } catch (error) {
        console.error("Gagal menghapus tugas:", error);
        showToast(
            error.message || "Gagal menghapus tugas.",
            "error"
        );
    }
}

// ========================
// AI BUSINESS ASSISTANT
// ========================

function addChatMessage(message, sender) {
    const messageElement = document.createElement("div");

    messageElement.classList.add(
        "chat-message",
        sender === "user" ? "user-message" : "ai-message"
    );

    messageElement.textContent = message;

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleChatSubmit(event) {
    event.preventDefault();

    const message = chatInput.value.trim();

    if (!message) {
        return;
    }

    addChatMessage(message, "user");

    chatInput.value = "";
    chatInput.disabled = true;
    chatSubmit.disabled = true;
    chatStatus.textContent = "AI sedang berpikir...";

    try {
        const response = await fetch(`${API_URL}/ai/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Gagal mendapatkan jawaban dari AI."
            );
        }

        if (typeof data.reply !== "string" || !data.reply.trim()) {
            throw new Error("AI tidak memberikan jawaban.");
        }

        addChatMessage(data.reply, "ai");
        chatStatus.textContent = "";

        if (
            ["create_task", "update_task", "delete_task"].includes(
                data.action
            )
        ) {
            await loadTasks();
        }
    } catch (error) {
        console.error("Chat AI error:", error);

        chatStatus.textContent =
            "Pesan gagal diproses. Silakan coba lagi.";

        addChatMessage(
            "Maaf, terjadi kendala saat menghubungi AI. " +
            "Silakan coba kirim pertanyaan kembali.",
            "ai"
        );
    } finally {
        chatInput.disabled = false;
        chatSubmit.disabled = false;
        chatInput.focus();
    }
}

chatForm.addEventListener("submit", handleChatSubmit);
chatSubmit.addEventListener("click", handleChatSubmit);

// ========================
// INISIALISASI
// ========================

loadTasks();
