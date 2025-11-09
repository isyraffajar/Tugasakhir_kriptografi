// Navigation Section Switching
document.querySelectorAll('.sidebar .nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();

        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

        // Add active class to clicked link
        link.classList.add('active');

        // Get section name from data attribute
        const sectionName = link.getAttribute('data-section');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            mynotes: 'Catatan Pribadi',
            myfiles: 'File Pribadi',
            mystegano: 'Sembunyikan pesan'
        };

        document.querySelector('.page-title').textContent = titles[sectionName] || 'Dashboard';

        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        document.getElementById(`${sectionName}-section`).classList.add('active');

        // --- sinkronisasi khusus untuk MyStegano ---
        if (sectionName === 'mystegano') {
            // tombol tab
            const hideTabBtn = document.getElementById('hide-tab');
            const revealTabBtn = document.getElementById('reveal-tab');

            // pastikan hanya hide-tab yang aktif secara visual di awal
            hideTabBtn.classList.add('active');
            revealTabBtn.classList.remove('active');

            // paksa Bootstrap untuk "menunjukkan" panel hide agar state internalnya sinkron
            // (butuh bootstrap.bundle.min.js sudah ter-load)
            try {
                const tabInstance = new bootstrap.Tab(hideTabBtn);
                tabInstance.show();
            } catch (err) {
                // fallback ringan: set class manual jika bootstrap belum tersedia
                document.getElementById('hide-panel').classList.add('show', 'active');
                document.getElementById('reveal-panel').classList.remove('show', 'active');
                console.warn('Bootstrap Tab API tidak tersedia, menggunakan fallback class toggle.');
            }
        }

        // Close sidebar on mobile
        const sidebar = document.querySelector('.sidebar');
        if (sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
    });
});

// Toggle Sidebar on Mobile
document.getElementById('toggleSidebar').addEventListener('click', () => {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
});

// Close sidebar when clicking outside
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');

    if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});

// Close sidebar when window is resized above 768px
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        document.querySelector('.sidebar').classList.remove('active');
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Set first nav item as active
    document.querySelector('.nav-link').classList.add('active');
    document.getElementById('dashboard-section').classList.add('active');
});

document.addEventListener("DOMContentLoaded", function () {
    const noteCards = document.querySelectorAll(".note-card");
    const noteModal = new bootstrap.Modal(document.getElementById("noteModal"));

    noteCards.forEach(card => {
        card.addEventListener("click", function () {
            // Ambil data dari card
            const noteId = this.dataset.noteId;
            const title = this.dataset.title;
            const note = this.dataset.note;

            // Isi modal
            document.getElementById("modalNoteId").value = noteId;
            document.getElementById("modalNoteTitle").value = title;
            document.getElementById("modalNoteContent").value = note;

            // Tampilkan modal
            noteModal.show();
        });
    });
});

// Tangani klik tombol titik tiga supaya tidak memicu modal
document.querySelectorAll('.btn-icon').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.stopPropagation(); // hentikan bubbling
        // di sini dropdown/hapus bisa tetap dijalankan
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));

    // Tangani klik tombol trash
    document.querySelectorAll('.btn-icon.text-danger').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation(); // supaya tidak memicu modal detail

            const noteCard = this.closest('.note-card');
            const noteId = noteCard.dataset.noteId;

            // Set note_id di modal delete
            document.getElementById("deleteNoteId").value = noteId;

            // Tampilkan modal konfirmasi hapus
            deleteModal.show();
        });
    });
});

// MyStegano - Hide Message Form
const hideMessageForm = document.getElementById("hideMessageForm")
const uploadArea = document.getElementById("uploadArea")
const imageInput = document.getElementById("imageInput")
const imagePreview = document.getElementById("imagePreview")
const previewImage = document.getElementById("previewImage")
const removeImageBtn = document.getElementById("removeImageBtn")
const messageInput = document.getElementById("messageInput")

// Upload area click handler
uploadArea.addEventListener("click", () => {
    imageInput.click()
})

// Drag and drop
uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault()
    uploadArea.style.borderColor = "#667eea"
    uploadArea.style.backgroundColor = "#f8f9ff"
})

uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.borderColor = "#ccc"
    uploadArea.style.backgroundColor = "transparent"
})

uploadArea.addEventListener("drop", (e) => {
    e.preventDefault()
    uploadArea.style.borderColor = "#ccc"
    uploadArea.style.backgroundColor = "transparent"

    const files = e.dataTransfer.files
    if (files.length > 0) {
        imageInput.files = files
        handleImageSelect()
    }
})

// Image input change handler
imageInput.addEventListener("change", handleImageSelect)

function handleImageSelect() {
    const file = imageInput.files[0]
    if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            previewImage.src = e.target.result
            imagePreview.style.display = "block"
        }
        reader.readAsDataURL(file)
    }
}

// Remove image button
removeImageBtn.addEventListener("click", () => {
    imageInput.value = ""
    imagePreview.style.display = "none"
})

// Hide message form submit 
hideMessageForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    const file = imageInput.files[0];

    if (!message || !file) return alert("Lengkapi pesan dan gambar!");

    const formData = new FormData();
    formData.append("message", message);
    formData.append("cover", file);

    try {
        const response = await fetch("/steg_hide", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errText = await response.text();
            return alert("Gagal: " + errText);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "stego.jpeg"; 
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);

        alert("Pesan berhasil disembunyikan!");
    } catch (error) {
        console.error(error);
        alert("Terjadi error saat mengirim ke server");
    }
});


// Reveal Message Form
const revealMessageForm = document.getElementById("revealMessageForm")
const uploadAreaReveal = document.getElementById("uploadAreaReveal")
const revealImageInput = document.getElementById("revealImageInput")
const revealImagePreview = document.getElementById("revealImagePreview")
const revealPreviewImage = document.getElementById("revealPreviewImage")
const removeRevealImageBtn = document.getElementById("removeRevealImageBtn")
const revealResult = document.getElementById("revealResult")
const noMessageAlert = document.getElementById("noMessageAlert")
const revealedMessage = document.getElementById("extracted-message")

// Upload area click handler for reveal
uploadAreaReveal.addEventListener("click", () => {
    revealImageInput.click()
})

// Drag and drop for reveal
uploadAreaReveal.addEventListener("dragover", (e) => {
    e.preventDefault()
    uploadAreaReveal.style.borderColor = "#667eea"
    uploadAreaReveal.style.backgroundColor = "#f8f9ff"
})

uploadAreaReveal.addEventListener("dragleave", () => {
    uploadAreaReveal.style.borderColor = "#ccc"
    uploadAreaReveal.style.backgroundColor = "transparent"
})

uploadAreaReveal.addEventListener("drop", (e) => {
    e.preventDefault()
    uploadAreaReveal.style.borderColor = "#ccc"
    uploadAreaReveal.style.backgroundColor = "transparent"

    const files = e.dataTransfer.files
    if (files.length > 0) {
        revealImageInput.files = files
        handleRevealImageSelect()
    }
})

// Image input change for reveal
revealImageInput.addEventListener("change", handleRevealImageSelect)

function handleRevealImageSelect() {
    const file = revealImageInput.files[0]
    if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            revealPreviewImage.src = e.target.result
            revealImagePreview.style.display = "block"
        }
        reader.readAsDataURL(file)
    }
}

// Remove reveal image button
removeRevealImageBtn.addEventListener("click", () => {
    revealImageInput.value = ""
    revealImagePreview.style.display = "none"
    revealResult.style.display = "none"
    noMessageAlert.style.display = "none"
})

// Reveal message form submit 
// Reveal message form submit 
revealMessageForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!revealImageInput.files[0]) {
        console.log("[DEBUG] Tidak ada file gambar dipilih");
        return alert("Pilih gambar terlebih dahulu!");
    }

    const formData = new FormData();
    formData.append("stego", revealImageInput.files[0]);

    try {
        const response = await fetch("/steg_extract", {
            method: "POST",
            body: formData
        });

        console.log("[DEBUG] Response status:", response.status);

        if (!response.ok) {
            const errText = await response.text();
            console.warn("[DEBUG] Response not OK:", errText);
            noMessageAlert.style.display = "block";
            revealResult.style.display = "none";
            return;
        }

        // Response berisi HTML dari Flask
        const text = await response.text();
        console.log("[DEBUG] Response text snippet:", text.substring(0, 200));

        // Ambil pesan dari HTML (dari template)
        const parser = new DOMParser();
        const htmlDoc = parser.parseFromString(text, "text/html");
        const msg = htmlDoc.querySelector("#extracted-message")?.textContent || "";

        console.log("[DEBUG] Extracted message:", msg);

        if (msg.trim() !== "") {
            revealedMessage.textContent = msg;
            revealResult.style.display = "block";
            noMessageAlert.style.display = "none";
        } else {
            console.warn("[DEBUG] Pesan kosong, menampilkan noMessageAlert");
            revealResult.style.display = "none";
            noMessageAlert.style.display = "block";
        }

    } catch (error) {
        console.error("[DEBUG] Terjadi error saat fetch:", error);
        alert("Terjadi error saat mengirim ke server!");
    }
});

// Copy message button
document.getElementById("copyMessageBtn")?.addEventListener("click", () => {
    const message = revealedMessage.textContent
    navigator.clipboard
        .writeText(message)
        .then(() => {
            alert("Pesan berhasil disalin ke clipboard!")
        })
        .catch((err) => {
            console.error("Gagal menyalin pesan:", err)
        })
})
